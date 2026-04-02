
<img width="1893" height="860" alt="Screenshot 2026-04-02 123254" src="https://github.com/user-attachments/assets/0ac5f2da-39d3-4010-8a2a-0f58ee22a588" />
---
<img width="1900" height="857" alt="Screenshot 2026-04-02 123344" src="https://github.com/user-attachments/assets/8760c71b-1a23-4f69-bd73-0ea51c080d94" />
<img width="1910" height="902" alt="Screenshot 2026-04-02 123425" src="https://github.com/user-attachments/assets/6636b12c-b109-48da-9a9c-9e6a5821a698" />

## ✦ AI Brain

The intelligence layer powers system awareness and decision-making:

• Anomaly Detection  
Detects abnormal system behavior using statistical and ML models  

• Failure Prediction  
Predicts workflow failures before they occur using time-series modeling  

• Log Intelligence (NLP)  
Understands logs semantically using LLMs to identify root causes  

• Decision Engine  
Suggests and executes corrective actions automatically  

---

## ✦ Tech Stack

Backend  
- FastAPI  
- Python (AsyncIO)  
- MongoDB  

AI / ML  
- OpenAI GPT (log intelligence)  
- Time-series models (LSTM / statistical)  
- Anomaly detection models  

Frontend  
- React  
- React Flow (workflow graphs)  
- Recharts (metrics)  
- Framer Motion (animations)  

DevOps Ready  
- WebSockets (real-time updates)  
- Docker / Kubernetes (scalable deployment)  

---

## ✦ Key Features

• JWT-based authentication system  
• Visual workflow builder (node-edge graphs)  
• Live event stream and system logs  
• AI-generated alerts and explanations  
• Failure simulation and recovery testing  
• Auto-retry and healing mechanisms  

---

## ✦ Example Use Cases

• Monitoring distributed microservices  
• Managing ETL and data pipelines  
• Detecting failures in real-time systems  
• Automating DevOps incident response  

---

## ✦ Project Structure


nexus-ai-orchestrator/
├── backend/
├── frontend/
├── models/
├── services/
├── requirements.txt
└── README.md


---

## ✦ Setup

Clone repository:

git clone https://github.com/jiten54/nexus-ai-orchestrator.git  
cd nexus-ai-orchestrator  

Run backend:

cd backend  
pip install -r ../requirements.txt  
uvicorn main:app --reload  

Run frontend:

cd frontend  
npm install  
npm start  
