# AlertIQ AI: Autonomous Multi-Agent Network Intrusion Detection System
### Second-Year Engineering Hackathon Project | Fast, Reliable, & Fully Functional

AlertIQ AI is an end-to-end, machine learning-powered Autonomous Multi-Agent Cybersecurity System built with **Python (FastAPI, Scikit-learn, Pandas, NumPy, SQLite)** and a modern **React + Vite + Tailwind CSS** frontend.

It integrates a genuine **78-feature Random Forest ML pipeline** trained on the canonical **CIC-IDS2017** network intrusion dataset to detect cyber threats, coordinate multi-agent containment workflows, enforce **Human-in-the-Loop (HITL)** approvals, and track operational telemetry (latency, token usage, and costs).

---

## 1. System Architecture

```
AlertIQ-AI/
├── backend/
│   ├── main.py                  # FastAPI server, REST routes, CORS, SPA static serving
│   ├── database.py              # SQLite persistence (agents, executions, logs, approvals, alerts, predictions)
│   ├── agent_engine.py          # Multi-agent orchestration, execution engine, fault injection, HITL
│   ├── sample_data.py           # Generates 20-flow realistic CIC-IDS2017 sample CSVs & templates
│   ├── test_backend.py          # Automated verification for ML inference & traffic analysis (14 tests)
│   └── test_agent_system.py     # Automated verification for the 9-step Agent AI User Journey
├── frontend/                    # React 18 + Vite 5 + Tailwind CSS + Lucide Icons + Recharts
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── App.jsx              # Unified navigation shell and reactive polling
│       ├── api.js               # Centralized REST client for all backend endpoints
│       ├── components/
│       │   ├── Sidebar.jsx      # Navigation, status indicators, pending approval & alert badges
│       │   ├── Header.jsx       # Quick Demo Seed, Reset DB, Refresh controls
│       │   ├── StatusBadge.jsx  # Status indicators (Agent, Execution, Severity, Alert)
│       │   ├── StatCard.jsx     # Telemetry summary metric cards
│       │   ├── FeatureModal.jsx # 78-feature network flow inspector with instant search
│       │   ├── ExecutionLogModal.jsx # Step-by-step audit log console with token & cost telemetry
│       │   ├── CreateAgentModal.jsx  # Form to register new autonomous agents
│       │   ├── RunTaskModal.jsx      # Form to execute custom tasks on any agent
│       │   └── ApprovalDecisionModal.jsx # Human-in-the-loop authorization dialog
│       └── pages/
│           ├── Dashboard.jsx        # SOC summary metrics, traffic donut chart, active incident stream
│           ├── AgentManagement.jsx  # Multi-agent visualizer, agent cards, start/stop, fault injection
│           ├── AgentMonitoring.jsx  # Token & cost telemetry, execution history stream, logs viewer
│           ├── ApprovalsCenter.jsx  # Pending Human-in-the-loop authorization center
│           ├── TrafficAnalysis.jsx  # CSV upload, 78-feature validation, real-time ML inference
│           ├── Alerts.jsx           # Incident queue with Acknowledge and Resolve actions
│           ├── History.jsx          # Full historical prediction ledger with class filtering
│           ├── Analytics.jsx        # Attack distribution, severity breakdown, top ports charts
│           └── ModelInfo.jsx        # Random Forest specs and 78-feature registry
├── machine_learning/
│   ├── ai_engine.py             # Model loader & inference wrapper (predict_alert, predict_batch)
│   └── models/
│       └── alertiq_model.joblib # Serialized Scikit-learn Pipeline (SimpleImputer + RandomForestClassifier)
├── data/
│   ├── samples/
│   │   ├── sample_traffic.csv   # 20 real CIC-IDS2017 flows (10 Benign, 10 Attack) for testing
│   │   └── sample_template.csv  # Blank CSV with 78 required column headers
│   └── processed/
│       └── alertiq_training.csv # Cleaned training dataset
├── backup/                      # Original ML files safety backup
├── requirements.txt             # Python backend dependencies
└── .env.example                 # Environment configuration template
```

---

## 2. Multi-Agent Pipeline & Roles

AlertIQ AI features four autonomous agents that coordinate during an incident:

1. **Traffic Ingestion Agent (`agent-ingest`):**  
   Ingests raw packet streams, strips whitespace, replaces non-numeric artifacts, and vectors flows into the standardized 78-dimensional CIC-IDS2017 schema.
2. **ML Intrusion Triage Agent (`agent-ml-triage`):**  
   Executes the trained Scikit-learn Random Forest pipeline (`alertiq_model.joblib`) to calculate confidence scores and classify flows into **BENIGN** or **ATTACK**.
3. **SOC Automated Response Agent (`agent-mitigate`):**  
   Evaluates attack severity. If high or critical, formulates containment rules (e.g. blocking the destination port) and halts execution to trigger a **Human-in-the-Loop Approval Request**.
4. **Audit & Compliance Agent (`agent-audit`):**  
   Maintains non-repudiable audit logs, tracks telemetry (tokens, duration, cost), and ensures NIST SP 800-61 / SOC-2 compliance.

---

## 3. Quick Start Guide (Windows)

### Prerequisites
- Python 3.10+ (tested with Python 3.14 on Windows)
- Node.js 18+ and npm

---

### Step 1: Backend Setup & Launch

Open a PowerShell terminal in the project root (`d:\AlertIQ-AI`):

```powershell
# 1. Activate the virtual environment
.\venv\Scripts\Activate.ps1

# 2. (Optional) Install dependencies if running on a new machine
pip install -r requirements.txt

# 3. Start the FastAPI backend server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be available at: **http://127.0.0.1:8000**  
Interactive API Documentation (Swagger): **http://127.0.0.1:8000/docs**

---

### Step 2: Frontend Launch

Open a second PowerShell terminal in `d:\AlertIQ-AI\frontend`:

```powershell
# 1. Navigate to frontend directory
cd frontend

# 2. Start the Vite development server
npm run dev
```

The frontend will be available at: **http://localhost:5173**  
*(Note: API requests are automatically proxied from `http://localhost:5173/api` to `http://127.0.0.1:8000`)*

> **Tip for Single-Command Demos:**  
> The backend automatically serves the pre-built React frontend at `http://127.0.0.1:8000/` without needing `npm run dev`!

---

## 4. Demonstrating the 9-Step User Journey to Hackathon Judges

Follow this workflow during your presentation:

1. **Open Dashboard (`/`):**  
   Point out real-time database metrics: Total Traffic, Benign Flows, Detected Attacks, and Active Alerts. Click **"Quick Demo Seed"** to immediately populate the database with 20 realistic flows.
2. **Select or Register an Agent:**  
   Navigate to **Agent Management**. Show the 4 seeded agents. Click **"Register New Agent"** to create a custom agent (e.g., "Zero-Day Hunter").
3. **Execute an Agent Task:**  
   Click **"Execute Task"** on any agent. Enter a task name and run it. Show the execution status badge turn to `SUCCESS`.
4. **View Step-by-Step Execution Logs:**  
   Navigate to **Agent Monitoring & Logs**. Click **"View Logs"** on any execution. Inspect the live duration ($ms$), token consumption ($Prompt + Completion$), estimated cost, and timestamped audit logs.
5. **Trigger a Failure Scenario:**  
   On **Agent Management**, click **"Fault Injection Test"**. Explain that this simulates an abnormal execution scenario (e.g. sensor tensor corruption). Show the execution fail with status `FAILED` and log the `ValidationError`.
6. **Show Generated Security Alert:**  
   Show how the failure automatically created a `CRITICAL` severity alert in the **Security Alerts** page (`Agent Execution Failure: agent-ml-triage`).
7. **Submit a Human Approval Request:**  
   Click **"Run Multi-Agent Pipeline"**. Watch the workflow execute steps 1 and 2. Because an attack was classified, the Response Agent halts and creates a pending approval (`WAITING_HUMAN_APPROVAL`).
8. **Review and Decide (Approve / Reject):**  
   Navigate to **Human-In-The-Loop**. Notice the amber notification badge. Click **"Review & Authorize Action"**. Review the target port and threat justification, type an analyst note, and click **"Authorize Action"**.
9. **Verify Workflow Updated:**  
   Show the approval move to the **Decision Log**, and show the underlying execution record update to `SUCCESS` with the analyst's approval notes.

---

## 5. Automated Acceptance Test Commands

Run the test suites directly in PowerShell to prove 100% functionality:

```powershell
# Run the 14 Traffic Analysis & ML Model verification tests
.\venv\Scripts\python.exe -u backend/test_backend.py

# Run the 9-Step Agent AI User Journey verification tests
.\venv\Scripts\python.exe -u backend/test_agent_system.py
```

Both test suites execute in $<5$ seconds and pass with 100% success.

---

## 6. Known Limitations & Design Choices
- **Token Cost Mode (`ESTIMATED_TELEMETRY`):** Because the project uses on-device Scikit-learn pipelines rather than paid proprietary third-party APIs (avoiding unexpected API key failures during live demonstrations), token counts and costs are calculated from telemetry models ($1.50 / 1M prompt tokens, $2.00 / 1M completion tokens) and clearly labeled as estimated.
- **CSV Ingestion:** Traffic analysis accepts CSV captures adhering to the 78 CIC-IDS2017 features. Downloadable sample files and templates are provided directly in the UI.
