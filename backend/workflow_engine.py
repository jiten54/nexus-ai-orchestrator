import asyncio
import random
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class WorkflowEngine:
    """Engine for managing and simulating distributed workflows"""
    
    def __init__(self, db, ws_manager, ai_brain):
        self.db = db
        self.ws_manager = ws_manager
        self.ai_brain = ai_brain
        self.running_workflows = {}
        self.simulation_running = False
        self.current_metrics = {
            "cpu": 45,
            "memory": 52,
            "latency": 120,
            "throughput": 1500,
            "error_rate": 0.5,
            "active_workers": 8,
            "queue_depth": 23
        }
    
    def create_workflow(self, name: str, workflow_type: str) -> Dict[str, Any]:
        """Create a new workflow based on type"""
        workflow_id = str(uuid.uuid4())[:8]
        
        if workflow_type == "etl":
            nodes, edges = self._create_etl_workflow(workflow_id)
        elif workflow_type == "microservice":
            nodes, edges = self._create_microservice_workflow(workflow_id)
        elif workflow_type == "batch":
            nodes, edges = self._create_batch_workflow(workflow_id)
        else:
            nodes, edges = self._create_etl_workflow(workflow_id)
        
        return {
            "id": workflow_id,
            "name": name,
            "workflow_type": workflow_type,
            "status": "idle",
            "nodes": nodes,
            "edges": edges,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "total_runs": 0,
                "success_rate": 100,
                "avg_duration": 0,
                "last_run": None
            }
        }
    
    def _create_etl_workflow(self, workflow_id: str) -> tuple:
        """Create ETL pipeline workflow nodes and edges"""
        nodes = [
            {"id": f"{workflow_id}-extract", "type": "source", "data": {"label": "Data Extract", "status": "idle"}, "position": {"x": 100, "y": 200}},
            {"id": f"{workflow_id}-validate", "type": "process", "data": {"label": "Validate", "status": "idle"}, "position": {"x": 300, "y": 100}},
            {"id": f"{workflow_id}-transform", "type": "process", "data": {"label": "Transform", "status": "idle"}, "position": {"x": 300, "y": 300}},
            {"id": f"{workflow_id}-aggregate", "type": "process", "data": {"label": "Aggregate", "status": "idle"}, "position": {"x": 500, "y": 200}},
            {"id": f"{workflow_id}-load", "type": "sink", "data": {"label": "Load to DB", "status": "idle"}, "position": {"x": 700, "y": 200}},
        ]
        edges = [
            {"id": f"e-{workflow_id}-1", "source": f"{workflow_id}-extract", "target": f"{workflow_id}-validate", "animated": False},
            {"id": f"e-{workflow_id}-2", "source": f"{workflow_id}-extract", "target": f"{workflow_id}-transform", "animated": False},
            {"id": f"e-{workflow_id}-3", "source": f"{workflow_id}-validate", "target": f"{workflow_id}-aggregate", "animated": False},
            {"id": f"e-{workflow_id}-4", "source": f"{workflow_id}-transform", "target": f"{workflow_id}-aggregate", "animated": False},
            {"id": f"e-{workflow_id}-5", "source": f"{workflow_id}-aggregate", "target": f"{workflow_id}-load", "animated": False},
        ]
        return nodes, edges
    
    def _create_microservice_workflow(self, workflow_id: str) -> tuple:
        """Create microservice orchestration workflow"""
        nodes = [
            {"id": f"{workflow_id}-gateway", "type": "source", "data": {"label": "API Gateway", "status": "idle"}, "position": {"x": 100, "y": 200}},
            {"id": f"{workflow_id}-auth", "type": "process", "data": {"label": "Auth Service", "status": "idle"}, "position": {"x": 300, "y": 100}},
            {"id": f"{workflow_id}-user", "type": "process", "data": {"label": "User Service", "status": "idle"}, "position": {"x": 300, "y": 200}},
            {"id": f"{workflow_id}-order", "type": "process", "data": {"label": "Order Service", "status": "idle"}, "position": {"x": 300, "y": 300}},
            {"id": f"{workflow_id}-payment", "type": "process", "data": {"label": "Payment Service", "status": "idle"}, "position": {"x": 500, "y": 150}},
            {"id": f"{workflow_id}-notification", "type": "process", "data": {"label": "Notification", "status": "idle"}, "position": {"x": 500, "y": 300}},
            {"id": f"{workflow_id}-response", "type": "sink", "data": {"label": "Response", "status": "idle"}, "position": {"x": 700, "y": 200}},
        ]
        edges = [
            {"id": f"e-{workflow_id}-1", "source": f"{workflow_id}-gateway", "target": f"{workflow_id}-auth", "animated": False},
            {"id": f"e-{workflow_id}-2", "source": f"{workflow_id}-auth", "target": f"{workflow_id}-user", "animated": False},
            {"id": f"e-{workflow_id}-3", "source": f"{workflow_id}-auth", "target": f"{workflow_id}-order", "animated": False},
            {"id": f"e-{workflow_id}-4", "source": f"{workflow_id}-order", "target": f"{workflow_id}-payment", "animated": False},
            {"id": f"e-{workflow_id}-5", "source": f"{workflow_id}-order", "target": f"{workflow_id}-notification", "animated": False},
            {"id": f"e-{workflow_id}-6", "source": f"{workflow_id}-payment", "target": f"{workflow_id}-response", "animated": False},
            {"id": f"e-{workflow_id}-7", "source": f"{workflow_id}-notification", "target": f"{workflow_id}-response", "animated": False},
        ]
        return nodes, edges
    
    def _create_batch_workflow(self, workflow_id: str) -> tuple:
        """Create batch processing workflow"""
        nodes = [
            {"id": f"{workflow_id}-scheduler", "type": "source", "data": {"label": "Scheduler", "status": "idle"}, "position": {"x": 100, "y": 200}},
            {"id": f"{workflow_id}-worker1", "type": "process", "data": {"label": "Worker 1", "status": "idle"}, "position": {"x": 300, "y": 100}},
            {"id": f"{workflow_id}-worker2", "type": "process", "data": {"label": "Worker 2", "status": "idle"}, "position": {"x": 300, "y": 200}},
            {"id": f"{workflow_id}-worker3", "type": "process", "data": {"label": "Worker 3", "status": "idle"}, "position": {"x": 300, "y": 300}},
            {"id": f"{workflow_id}-collector", "type": "process", "data": {"label": "Result Collector", "status": "idle"}, "position": {"x": 500, "y": 200}},
            {"id": f"{workflow_id}-output", "type": "sink", "data": {"label": "Output Store", "status": "idle"}, "position": {"x": 700, "y": 200}},
        ]
        edges = [
            {"id": f"e-{workflow_id}-1", "source": f"{workflow_id}-scheduler", "target": f"{workflow_id}-worker1", "animated": False},
            {"id": f"e-{workflow_id}-2", "source": f"{workflow_id}-scheduler", "target": f"{workflow_id}-worker2", "animated": False},
            {"id": f"e-{workflow_id}-3", "source": f"{workflow_id}-scheduler", "target": f"{workflow_id}-worker3", "animated": False},
            {"id": f"e-{workflow_id}-4", "source": f"{workflow_id}-worker1", "target": f"{workflow_id}-collector", "animated": False},
            {"id": f"e-{workflow_id}-5", "source": f"{workflow_id}-worker2", "target": f"{workflow_id}-collector", "animated": False},
            {"id": f"e-{workflow_id}-6", "source": f"{workflow_id}-worker3", "target": f"{workflow_id}-collector", "animated": False},
            {"id": f"e-{workflow_id}-7", "source": f"{workflow_id}-collector", "target": f"{workflow_id}-output", "animated": False},
        ]
        return nodes, edges
    
    async def execute_workflow(self, workflow_id: str):
        """Execute a workflow with simulated processing"""
        self.running_workflows[workflow_id] = True
        
        workflow = await self.db.workflows.find_one({"id": workflow_id})
        if not workflow:
            return
        
        nodes = workflow["nodes"]
        edges = workflow["edges"]
        
        await self.db.workflows.update_one({"id": workflow_id}, {"$set": {"status": "running"}})
        await self._broadcast_workflow_update(workflow_id, "running", nodes, edges)
        
        # Execute nodes in order
        for i, node in enumerate(nodes):
            if not self.running_workflows.get(workflow_id):
                break
            
            node_id = node["id"]
            
            # Update node to running
            node["data"]["status"] = "running"
            await self._broadcast_workflow_update(workflow_id, "running", nodes, edges)
            await self._add_log("INFO", f"Node {node['data']['label']} started", node_id)
            
            # Simulate processing time
            processing_time = random.uniform(1.5, 4.0)
            await asyncio.sleep(processing_time)
            
            # Simulate occasional failures
            if random.random() < 0.1:  # 10% failure rate
                node["data"]["status"] = "error"
                await self._broadcast_workflow_update(workflow_id, "running", nodes, edges)
                await self._add_log("ERROR", f"Node {node['data']['label']} failed: Timeout exceeded", node_id)
                await self._create_alert("critical", f"Node failure in workflow {workflow_id}", node_id)
                
                # Trigger auto-healing
                await self._trigger_auto_healing(workflow_id, node_id, "timeout")
                
                # Retry the node
                await asyncio.sleep(2)
                node["data"]["status"] = "running"
                await self._broadcast_workflow_update(workflow_id, "running", nodes, edges)
                await self._add_log("INFO", f"Auto-healing: Retrying node {node['data']['label']}", node_id)
                await asyncio.sleep(processing_time)
            
            # Mark node as completed
            node["data"]["status"] = "completed"
            await self._broadcast_workflow_update(workflow_id, "running", nodes, edges)
            await self._add_log("INFO", f"Node {node['data']['label']} completed", node_id)
        
        # Complete workflow
        final_status = "completed" if self.running_workflows.get(workflow_id) else "stopped"
        await self.db.workflows.update_one(
            {"id": workflow_id},
            {"$set": {"status": final_status, "nodes": nodes}}
        )
        await self._broadcast_workflow_update(workflow_id, final_status, nodes, edges)
        await self._add_log("INFO", f"Workflow {workflow_id} {final_status}", workflow_id)
        
        self.running_workflows.pop(workflow_id, None)
    
    def stop_workflow(self, workflow_id: str):
        """Stop a running workflow"""
        self.running_workflows[workflow_id] = False
    
    async def _broadcast_workflow_update(self, workflow_id: str, status: str, nodes: List, edges: List):
        """Broadcast workflow update via WebSocket"""
        await self.ws_manager.broadcast({
            "type": "workflow_update",
            "data": {
                "id": workflow_id,
                "status": status,
                "nodes": nodes,
                "edges": edges,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        })
    
    async def _add_log(self, level: str, message: str, component: str):
        """Add a log entry"""
        log = {
            "id": str(uuid.uuid4()),
            "level": level,
            "message": message,
            "component": component,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await self.db.logs.insert_one(log)
        log.pop("_id", None)
        await self.ws_manager.broadcast({"type": "log", "data": log})
    
    async def _create_alert(self, severity: str, message: str, source: str):
        """Create an alert"""
        alert = {
            "id": str(uuid.uuid4()),
            "severity": severity,
            "message": message,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "acknowledged": False
        }
        await self.db.alerts.insert_one(alert)
        alert.pop("_id", None)
        await self.ws_manager.broadcast({"type": "alert", "data": alert})
    
    async def _trigger_auto_healing(self, workflow_id: str, node_id: str, failure_type: str):
        """Trigger auto-healing action"""
        action = {
            "id": str(uuid.uuid4()),
            "type": "retry",
            "workflow_id": workflow_id,
            "node_id": node_id,
            "failure_type": failure_type,
            "status": "executed",
            "result": "Node retry initiated",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await self.db.healing_actions.insert_one(action)
        action.pop("_id", None)
        await self.ws_manager.broadcast({"type": "healing_action", "data": action})
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        return self.current_metrics.copy()
    
    async def start_simulation(self):
        """Start background simulation of metrics and logs"""
        self.simulation_running = True
        asyncio.create_task(self._run_metrics_simulation())
        asyncio.create_task(self._run_log_simulation())
        asyncio.create_task(self._run_prediction_simulation())
    
    def stop_simulation(self):
        """Stop background simulation"""
        self.simulation_running = False
    
    async def _run_metrics_simulation(self):
        """Simulate changing metrics"""
        while self.simulation_running:
            # Update metrics with some randomness
            self.current_metrics["cpu"] = max(10, min(95, self.current_metrics["cpu"] + random.uniform(-8, 8)))
            self.current_metrics["memory"] = max(20, min(95, self.current_metrics["memory"] + random.uniform(-5, 5)))
            self.current_metrics["latency"] = max(50, min(1200, self.current_metrics["latency"] + random.uniform(-50, 50)))
            self.current_metrics["throughput"] = max(500, min(3000, self.current_metrics["throughput"] + random.uniform(-100, 100)))
            self.current_metrics["error_rate"] = max(0, min(10, self.current_metrics["error_rate"] + random.uniform(-0.5, 0.5)))
            self.current_metrics["active_workers"] = random.randint(4, 12)
            self.current_metrics["queue_depth"] = random.randint(5, 100)
            
            metrics_with_time = {
                **self.current_metrics,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Store metrics
            await self.db.metrics.insert_one(metrics_with_time)
            metrics_with_time.pop("_id", None)
            
            # Broadcast metrics
            await self.ws_manager.broadcast({
                "type": "metrics",
                "data": metrics_with_time
            })
            
            # Check for anomalies
            anomalies = self.ai_brain.detect_anomalies(self.current_metrics)
            for anomaly in anomalies:
                await self._create_alert(anomaly["severity"], anomaly["message"], "metrics")
            
            await asyncio.sleep(2)
    
    async def _run_log_simulation(self):
        """Simulate log generation"""
        log_messages = {
            "INFO": [
                "Request processed successfully",
                "Worker heartbeat received",
                "Cache hit for query",
                "Connection pool healthy",
                "Task completed in {}ms",
                "New worker joined cluster",
                "Checkpoint saved",
                "Data sync completed"
            ],
            "WARNING": [
                "High memory usage detected",
                "Slow query detected: {}ms",
                "Connection retry attempt",
                "Rate limit approaching threshold",
                "Disk usage above 70%"
            ],
            "ERROR": [
                "Connection timeout after {}ms",
                "Failed to process request",
                "Database connection lost",
                "Memory allocation failed",
                "Worker node unresponsive"
            ]
        }
        
        components = ["api-gateway", "worker-1", "worker-2", "worker-3", "scheduler", "db-connector", "cache", "load-balancer"]
        
        while self.simulation_running:
            # Generate random log
            level = random.choices(["INFO", "WARNING", "ERROR"], weights=[85, 12, 3])[0]
            message = random.choice(log_messages[level])
            if "{}" in message:
                message = message.format(random.randint(50, 2000))
            
            component = random.choice(components)
            await self._add_log(level, message, component)
            
            await asyncio.sleep(random.uniform(0.5, 3))
    
    async def _run_prediction_simulation(self):
        """Periodically generate AI predictions"""
        while self.simulation_running:
            # Get recent metrics
            metrics = await self.db.metrics.find({}, {"_id": 0}).sort("timestamp", -1).to_list(20)
            
            # Generate prediction
            prediction = await self.ai_brain.predict_failure(metrics)
            prediction["id"] = str(uuid.uuid4())
            prediction["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            await self.db.predictions.insert_one(prediction)
            prediction.pop("_id", None)
            
            await self.ws_manager.broadcast({
                "type": "prediction",
                "data": prediction
            })
            
            await asyncio.sleep(10)
