from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
from bson import ObjectId
import asyncio
import json
import random

from ai_brain import AIBrain
from workflow_engine import WorkflowEngine
from websocket_manager import WebSocketManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize managers
ws_manager = WebSocketManager()
ai_brain = AIBrain()
workflow_engine = WorkflowEngine(db, ws_manager, ai_brain)

# JWT Configuration
JWT_SECRET = os.environ.get("JWT_SECRET", "default-secret-change-me")
JWT_ALGORITHM = "HS256"

app = FastAPI(title="NEXUS_AI - Autonomous Workflow Intelligence")
api_router = APIRouter(prefix="/api")

# ============ Auth Models ============
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str

# ============ Workflow Models ============
class WorkflowCreate(BaseModel):
    name: str
    workflow_type: str = "etl"  # etl, microservice, batch

class WorkflowResponse(BaseModel):
    id: str
    name: str
    workflow_type: str
    status: str
    nodes: List[Dict]
    edges: List[Dict]
    created_at: str
    metrics: Dict

# ============ Auth Helpers ============
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "type": "refresh"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user.get("role", "user")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============ Auth Routes ============
@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    email = user_data.email.lower()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_doc = {
        "email": email,
        "password_hash": hash_password(user_data.password),
        "name": user_data.name,
        "role": "user",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)
    
    response = JSONResponse(content={
        "id": user_id,
        "email": email,
        "name": user_data.name,
        "role": "user"
    })
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=86400, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    return response

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    email = user_data.email.lower()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_id = str(user["_id"])
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)
    
    response = JSONResponse(content={
        "id": user_id,
        "email": email,
        "name": user["name"],
        "role": user.get("role", "user")
    })
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=86400, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    return response

@api_router.get("/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return user

@api_router.post("/auth/logout")
async def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return response

# ============ Workflow Routes ============
@api_router.get("/workflows")
async def get_workflows(user: dict = Depends(get_current_user)):
    workflows = await db.workflows.find({}, {"_id": 0}).to_list(100)
    return workflows

@api_router.post("/workflows")
async def create_workflow(workflow: WorkflowCreate, user: dict = Depends(get_current_user)):
    workflow_data = workflow_engine.create_workflow(workflow.name, workflow.workflow_type)
    await db.workflows.insert_one(workflow_data)
    workflow_data.pop("_id", None)
    return workflow_data

@api_router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str, user: dict = Depends(get_current_user)):
    workflow = await db.workflows.find_one({"id": workflow_id}, {"_id": 0})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@api_router.post("/workflows/{workflow_id}/start")
async def start_workflow(workflow_id: str, user: dict = Depends(get_current_user)):
    workflow = await db.workflows.find_one({"id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    asyncio.create_task(workflow_engine.execute_workflow(workflow_id))
    return {"message": "Workflow execution started", "workflow_id": workflow_id}

@api_router.post("/workflows/{workflow_id}/stop")
async def stop_workflow(workflow_id: str, user: dict = Depends(get_current_user)):
    workflow_engine.stop_workflow(workflow_id)
    await db.workflows.update_one({"id": workflow_id}, {"$set": {"status": "stopped"}})
    return {"message": "Workflow stopped", "workflow_id": workflow_id}

# ============ Metrics Routes ============
@api_router.get("/metrics")
async def get_metrics(user: dict = Depends(get_current_user)):
    metrics = await db.metrics.find({}, {"_id": 0}).sort("timestamp", -1).to_list(100)
    return metrics

@api_router.get("/metrics/current")
async def get_current_metrics(user: dict = Depends(get_current_user)):
    return workflow_engine.get_current_metrics()

# ============ Alerts & Predictions Routes ============
@api_router.get("/alerts")
async def get_alerts(user: dict = Depends(get_current_user)):
    alerts = await db.alerts.find({}, {"_id": 0}).sort("timestamp", -1).to_list(50)
    return alerts

@api_router.get("/predictions")
async def get_predictions(user: dict = Depends(get_current_user)):
    predictions = await db.predictions.find({}, {"_id": 0}).sort("timestamp", -1).to_list(20)
    return predictions

# ============ Logs Routes ============
@api_router.get("/logs")
async def get_logs(user: dict = Depends(get_current_user)):
    logs = await db.logs.find({}, {"_id": 0}).sort("timestamp", -1).to_list(200)
    return logs

# ============ AI Brain Routes ============
@api_router.get("/ai/analysis")
async def get_ai_analysis(user: dict = Depends(get_current_user)):
    analysis = await db.ai_analysis.find({}, {"_id": 0}).sort("timestamp", -1).to_list(20)
    return analysis

@api_router.post("/ai/analyze-logs")
async def analyze_logs(user: dict = Depends(get_current_user)):
    logs = await db.logs.find({}, {"_id": 0}).sort("timestamp", -1).to_list(50)
    if not logs:
        return {"message": "No logs to analyze"}
    
    analysis = await ai_brain.analyze_logs(logs)
    if analysis:
        analysis["timestamp"] = datetime.now(timezone.utc).isoformat()
        await db.ai_analysis.insert_one(analysis)
        analysis.pop("_id", None)
    return analysis

# ============ Auto-Healing Routes ============
@api_router.get("/healing-actions")
async def get_healing_actions(user: dict = Depends(get_current_user)):
    actions = await db.healing_actions.find({}, {"_id": 0}).sort("timestamp", -1).to_list(50)
    return actions

@api_router.post("/healing/trigger")
async def trigger_healing(action_data: dict, user: dict = Depends(get_current_user)):
    action = {
        "id": str(uuid.uuid4()),
        "type": action_data.get("type", "restart"),
        "target": action_data.get("target", "unknown"),
        "status": "executed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "result": "Action completed successfully"
    }
    await db.healing_actions.insert_one(action)
    action.pop("_id", None)
    await ws_manager.broadcast({
        "type": "healing_action",
        "data": action
    })
    return action

# ============ WebSocket Endpoint ============
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)

# ============ Health Check ============
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@api_router.get("/")
async def root():
    return {"message": "NEXUS_AI - Autonomous Workflow Intelligence System"}

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[os.environ.get("FRONTEND_URL", "http://localhost:3000"), "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup events
@app.on_event("startup")
async def startup_event():
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.workflows.create_index("id", unique=True)
    await db.logs.create_index("timestamp")
    await db.alerts.create_index("timestamp")
    await db.metrics.create_index("timestamp")
    
    # Seed admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@nexusai.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin123!")
    existing = await db.users.find_one({"email": admin_email})
    if not existing:
        await db.users.insert_one({
            "email": admin_email,
            "password_hash": hash_password(admin_password),
            "name": "Admin",
            "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info(f"Admin user created: {admin_email}")
    
    # Write test credentials
    Path("/app/memory").mkdir(exist_ok=True)
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write(f"""# Test Credentials

## Admin User
- Email: {admin_email}
- Password: {admin_password}
- Role: admin

## Auth Endpoints
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me
- POST /api/auth/logout
""")
    
    # Start background simulation
    asyncio.create_task(workflow_engine.start_simulation())
    logger.info("NEXUS_AI System started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    workflow_engine.stop_simulation()
    client.close()
