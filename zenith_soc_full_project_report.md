# 🛡️ Zenith SOC Platform — Full Project Documentation Report

**Document Generated On:** 2026-07-02 12:09:22

## 📖 Executive Summary
This report compiles 100% of the architectural overview, directory structures, and complete source code files for the **Zenith SOC Platform**. Zenith SOC is a cyber operations command center that incorporates real-time WebSocket telemetry, unsupervised machine learning anomaly detection (Isolation Forest), and Generative AI (Gemini) RAG capabilities to automate threat triage and execution of playbooks for security analysts.

## 📁 Directory Structure & File Hierarchy
```
soc/
├── .gitignore
├── README.md
├── pyrightconfig.json
├── backend/
│   ├── .env
│   ├── .env.example
│   ├── __init__.py
│   ├── clear_db.py
│   ├── config.py
│   ├── main.py
│   ├── pyrightconfig.json
│   ├── requirements.txt
│   ├── data_generator/
│   │   ├── __init__.py
│   │   ├── generator.py
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── anomaly.py
│   │   ├── chat_assistant.py
│   │   ├── llm_summarizer.py
│   │   ├── mitre_mapper.py
│   │   ├── threat_scorer.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── alerts.py
│   │   ├── audit.py
│   │   ├── chat.py
│   │   ├── stats.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── alert_processor.py
│   │   ├── websocket_manager.py
├── frontend/
│   ├── .gitignore
│   ├── README.md
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── public/
│   │   ├── favicon.svg
│   │   ├── icons.svg
│   ├── src/
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── main.jsx
│   │   ├── assets/
│   │   │   ├── react.svg
│   │   │   ├── vite.svg
│   │   ├── components/
│   │   │   ├── AICopilot.jsx
│   │   │   ├── AlertDetailSidebar.jsx
│   │   │   ├── AlertsTable.jsx
│   │   │   ├── AnalyticsCharts.jsx
│   │   │   ├── DashboardHeader.jsx
│   │   │   ├── OverviewCards.jsx
│   │   │   ├── SOARAuditLogs.jsx
│   │   │   ├── ThreatHotspots.jsx
│   │   ├── utils/
│   │   │   ├── api.js
```

## 📋 Project File Catalog
| File Path | Description | Size (Bytes) |
| :--- | :--- | :--- |
| `.gitignore` | Source code/configuration resource. | 474 |
| `README.md` | Source code/configuration resource. | 21,458 |
| `backend/.env` | Source code/configuration resource. | 341 |
| `backend/.env.example` | Template setting environment variables for local development. | 404 |
| `backend/__init__.py` | Source code/configuration resource. | 18 |
| `backend/clear_db.py` | Utility script to clear all security events and audit log documents from MongoDB collections. | 744 |
| `backend/config.py` | Configuration module loading database, AI, application parameters from environment variables. | 969 |
| `backend/data_generator/__init__.py` | Source code/configuration resource. | 25 |
| `backend/data_generator/generator.py` | Mock event generator simulating live network threat logs (brute-force, port scan, data exfiltration). | 7,108 |
| `backend/main.py` | Main entrypoint for the FastAPI backend server. Coordinates WebSocket broadcasts, ML pipelines, API routing, and synthetic event generation. | 11,502 |
| `backend/ml/__init__.py` | Source code/configuration resource. | 13 |
| `backend/ml/anomaly.py` | Machine learning anomaly detection engine using Isolation Forest from scikit-learn. | 5,358 |
| `backend/ml/chat_assistant.py` | Core RAG assistant parsing database context and codebase context to answer analyst questions. | 12,625 |
| `backend/ml/llm_summarizer.py` | Gemini LLM generator producing plain-English alert summaries (with structured fallback templates). | 6,132 |
| `backend/ml/mitre_mapper.py` | Maps alerts to MITRE ATT&CK techniques using deterministic and zero-shot LLM classification. | 6,927 |
| `backend/ml/threat_scorer.py` | Mathematical scoring engine compiling CVSS base severity, anomaly score, and asset criticality into a 0-100 risk score. | 2,556 |
| `backend/models/__init__.py` | Source code/configuration resource. | 17 |
| `backend/models/schemas.py` | Pydantic validation schemas for API requests and response payloads. | 2,204 |
| `backend/pyrightconfig.json` | Pyright Linter config settings for backend. | 357 |
| `backend/requirements.txt` | Core Python package dependencies required to run the backend engine. | 185 |
| `backend/routes/__init__.py` | Source code/configuration resource. | 17 |
| `backend/routes/alerts.py` | API endpoints handling security alerts, playbooks, analyst verification, and SOAR response actions. | 10,663 |
| `backend/routes/audit.py` | API endpoints for retrieving SOAR playbook audit trails. | 708 |
| `backend/routes/chat.py` | API endpoint for the RAG-powered Zenith AI Copilot chat routing. | 1,256 |
| `backend/routes/stats.py` | API endpoints aggregating KPI stats, timeline history, and geographical threat map data. | 6,105 |
| `backend/services/__init__.py` | Source code/configuration resource. | 19 |
| `backend/services/alert_processor.py` | Pipeline orchestrator scoring events for anomalies, mapping MITRE ATT&CK vectors, summarizing logs, and calculating final risk scores. | 8,019 |
| `backend/services/websocket_manager.py` | Active connection tracking manager for real-time alert broadcasts. | 1,702 |
| `frontend/.gitignore` | Source code/configuration resource. | 253 |
| `frontend/README.md` | Source code/configuration resource. | 1,027 |
| `frontend/eslint.config.js` | Linter settings for React codebase. | 568 |
| `frontend/index.html` | Main entry point page loading stylesheet headers and React root elements. | 1,217 |
| `frontend/package.json` | Source code/configuration resource. | 750 |
| `frontend/public/favicon.svg` | Source code/configuration resource. | 9,522 |
| `frontend/public/icons.svg` | Source code/configuration resource. | 5,031 |
| `frontend/src/App.css` | Custom layout overrides. | 47 |
| `frontend/src/App.jsx` | Primary frontend orchestrator handling tabs, real-time WebSockets, and state sync. | 18,920 |
| `frontend/src/assets/react.svg` | Source code/configuration resource. | 4,126 |
| `frontend/src/assets/vite.svg` | Source code/configuration resource. | 8,709 |
| `frontend/src/components/AICopilot.jsx` | Interactive terminal-style AI Copilot widget with formatting logic. | 12,031 |
| `frontend/src/components/AlertDetailSidebar.jsx` | Incident triage side investigator drawer with playbook controls. | 20,246 |
| `frontend/src/components/AlertsTable.jsx` | Live security alert feed table with searching and sorting parameters. | 8,629 |
| `frontend/src/components/AnalyticsCharts.jsx` | Recharts visualizer for incident timelines, severities, and top source IPs. | 8,885 |
| `frontend/src/components/DashboardHeader.jsx` | System health and status bar containing manual retraining controls. | 5,590 |
| `frontend/src/components/OverviewCards.jsx` | Aggregate dashboard KPI metrics boxes. | 3,052 |
| `frontend/src/components/SOARAuditLogs.jsx` | Chronological SOAR automation compliance ledgers table. | 17,988 |
| `frontend/src/components/ThreatHotspots.jsx` | SVG interactive geospatial coordinate map plotting threat origins. | 10,448 |
| `frontend/src/index.css` | Core styling, Tailwind themes, custom animations, and glassmorphism definitions. | 5,542 |
| `frontend/src/main.jsx` | React mounting index bootloader. | 229 |
| `frontend/src/utils/api.js` | Centralized Axios client instance and API helpers for frontend-backend interaction. | 2,038 |
| `frontend/vite.config.js` | Vite server port configuration and local backend API proxy mapping. | 430 |
| `pyrightconfig.json` | Pyright configuration for root directory. | 357 |

## 💻 Comprehensive Source Code Registry
Below lies the complete source code for each configuration, route, utility, helper, and frontend component of the Zenith SOC project.

---

### 📄 File: `.gitignore`
**Purpose:** Source code/configuration resource.  
**Size:** 474 bytes

```python
# Virtual environments
venv/
.venv/
env/
ENV/

# Python compiled cache
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/

# Sensitive environment variables & API keys
.env
.env.local
.env.*.local
backend/.env
backend/.env.example

# Local generated CSV security logs
*.csv
security_logs.csv

# Frontend dependencies & production builds
frontend/node_modules/
frontend/dist/

# IDE & OS files
.vscode/
.idea/
*.suo
*.ntvs*
*.njsproj
*.sln
*.swp
Thumbs.db
ehthumbs.db
Desktop.ini

```


---

### 📄 File: `README.md`
**Purpose:** Source code/configuration resource.  
**Size:** 21,458 bytes

```markdown
# 🛡️ Zenith SOC Dashboard — Command Center

> **Real-Time Cybersecurity Threat Telemetry, Machine Learning Anomaly Detection & AI Playbook Orchestrator**

Zenith SOC is a production-inspired Security Operations Center (SOC) analyst dashboard designed to aggregate, analyze, prioritize, and respond to security events in real-time. By combining **scikit-learn unsupervised machine learning**, **Google Gemini AI reasoning**, and **real-time WebSocket streaming**, Zenith SOC automates the initial triage stages of a security incident, giving analysts high-context data, threat intelligence mapping, and automated playbooks at their fingertips.

---

## 📖 Table of Contents
1. [Key Features](#-key-features)
2. [Technical Architecture](#-technical-architecture)
3. [Deep Dive: AI & ML Engine](#-deep-dive-ai--ml-engine)
   - [Isolation Forest Anomaly Detection](#1-isolation-forest-anomaly-detection)
   - [Manual & Auto Model Training](#2-manual--auto-model-training)
   - [Retrieval-Augmented Generation (RAG) Copilot](#3-retrieval-augmented-generation-rag-copilot)
   - [MITRE ATT&CK Mapping Engine](#4-mitre-attck-mapping-engine)
   - [Algorithmic Risk Scoring](#5-algorithmic-risk-scoring)
4. [Project Structure](#-project-structure)
5. [Step-by-Step Setup & Installation](#-step-by-step-setup--installation)
6. [API Endpoints Reference](#-api-endpoints-reference)
7. [Incident Response Playbooks](#-incident-response-playbooks)
8. [License & Context](#-license--context)

---

## 📸 Key Features

| Core Capability | Technical Implementation | Analyst Value |
|:---|:---|:---|
| 📡 **Real-Time Threat Stream** | Native HTML5 WebSockets broadcast server in FastAPI | New alerts flash onto the dashboard instantly with a visual neon blue glow. |
| 🧠 **ML Anomaly Detection** | Unsupervised `IsolationForest` (scikit-learn) | Fits a model to multi-dimensional event vectors, scoring outliers between `0.0` and `1.0`. |
| 🎛️ **On-Demand Model Training** | Header HUD button + `/api/model/train` API | Allows analysts to manually train the anomaly engine on historical DB events dynamically. |
| 🤖 **Generative Alert Summaries** | LLM API integration with `gemini-2.5-flash` | Explains complex, raw JSON firewall/system logs into readable, 2-sentence summaries. |
| 🎯 **MITRE ATT&CK Mapping** | Zero-shot LLM prompts & deterministic mapping | Automatically flags the exact Tactic, Technique ID, and Sub-techniques for every event. |
| 💬 **AI SOC Copilot (RAG)** | Retrieval-Augmented Generation context injector | Injects the 20 most recent high-criticality threats into the LLM chat window context. |
| 🌍 **Threat Hotspots Map** | Geospatial IP grouping & mapping | Plots attack vectors globally, highlighting country-level threat source densities. |
| ⚡ **Simulated SOAR Playbooks** | State-driven response logic | Simulates firewall blocking, endpoint quarantine, and incident ticket creation. |

---

## 🏗️ Technical Architecture

Zenith SOC uses a distributed, full-stack architecture optimized for high-throughput stream processing and low-latency rendering:

```
                  ┌─────────────────────────────────────────────────────────────┐
                  │                      REACT FRONTEND                         │
                  │   ┌───────────────┬─────────────────┬──────────────────┐    │
                  │   │  Triage Feed  │  Charts Panel   │  AI Copilot Lab  │    │
                  │   ├───────────────┼─────────────────┼──────────────────┤    │
                  │   │ KPI HUD Cards │ Playbook SOAR   │ Geolocation Map  │    │
                  │   └───────────────┴─────────────────┴──────────────────┘    │
                  │                     ↕ Axios / WebSocket                     │
                  └─────────────────────────────────────────────────────────────┘
                                                │
                                      ┌─────────┴─────────┐
                                      │   VITE DEV PROXY  │
                                      │  /api  → :8000    │
                                      │  /ws   → ws/:8000 │
                                      └─────────┬─────────┘
                                                │
                  ┌─────────────────────────────┴───────────────────────────────┐
                  │                       FASTAPI BACKEND                       │
                  │                                                             │
                  │   ┌─────────────────────┐             ┌─────────────────┐   │
                  │   │   REST API Routes   │             │   WebSockets    │   │
                  │   │ - /api/alerts (GET) │             │ - /ws (Stream)  │   │
                  │   │ - /api/stats (GET)  │             └────────┬────────┘   │
                  │   │ - /api/chat (POST)  │                      │            │
                  │   └──────────┬──────────┘                      │            │
                  │              │                                 │            │
                  │  ┌───────────▼─────────────────────────────────▼─────────┐  │
                  │  │                  ML & AI PIPELINE                     │  │
                  │  │  ┌─────────────────────────┐ ┌─────────────────────┐  │  │
                  │  │  │ scikit-learn            │ │ Google Gemini SDK   │  │  │
                  │  │  │ - IsolationForest Engine│ │ - gemini-2.5-flash  │  │  │
                  │  │  └─────────────────────────┘ └─────────────────────┘  │  │
                  │  └───────────────────────┬───────────────────────────────┘  │
                  └──────────────────────────┼──────────────────────────────────┘
                                             │
                                   ┌─────────┴─────────┐
                                   │     MongoDB       │
                                   │  (security_events)│
                                   └───────────────────┘
```

1. **Vite + React (Frontend)**: Standard single-page application styled using a customized Tailwind theme containing cybernetic grid animations, glow effects, and modern card designs. Uses `Recharts` for charting and `lucide-react` for system status icons.
2. **FastAPI (Backend)**: Async-first python server executing concurrent database tasks using `motor` (asynchronous MongoDB driver). Configures WebSocket connections to broadcast events as they are generated.
3. **Background Data Generator**: Generates synthetic threat vectors (Faker logs representing SSH attacks, data exfiltration, port scans, etc.) every `EVENT_GENERATION_INTERVAL` seconds to simulate a live corporate network feed.

---

## 🧠 Deep Dive: AI & ML Engine

### 1. Isolation Forest Anomaly Detection
The anomaly detection engine resides in `backend/ml/anomaly.py`. It uses the **Isolation Forest** algorithm—an unsupervised learning approach that isolates anomalies by randomly partitioning feature spaces. Because anomalies require fewer splits to isolate, they appear closer to the root of trees.

For each security log, the engine constructs a **7-dimensional numerical feature vector**:
1. **Hour of Day** `[0-23]`: Attacks occurring during off-hours are mathematically distinct.
2. **Event Type Code** `[0-4]`: Ordinal mapping: `SSH_BRUTE_FORCE: 0`, `PORT_SCAN: 1`, `FAILED_LOGIN: 2`, `MALWARE_DETECTION: 3`, `DATA_EXFILTRATION: 4`.
3. **Severity Code** `[0-3]`: Severity ranking: `LOW: 0`, `MEDIUM: 1`, `HIGH: 2`, `CRITICAL: 3`.
4. **Source IP Octet** `[0-255]`: Uses the last octet of the source IP address to model network subnet patterns.
5. **Destination IP Octet** `[0-255]`: Uses the last octet of the target host IP address to detect targeted server anomalies.
6. **Privileged User Flag** `[0 or 1]`: Checked against high-risk accounts (`root`, `admin`, `kali`).
7. **Day of Week** `[0-6]`: Modeled to identify weekend vs. weekday baseline shifts.

```python
# Isolation Forest Scoring Logic:
raw_score = self.model.decision_function(features)[0]
# Normalizes decision function (typically [-0.5, 0.5]) into a [0.0, 1.0] scale
normalized_anomaly_score = 1.0 - (raw_score + 0.5)
```

### 2. Manual & Auto Model Training
- **Bootstrap Phase**: During backend startup, the Lifespan handler attempts to load up to 500 recent events from MongoDB. If at least 10 logs exist, it automatically trains the Isolation Forest.
- **Untrained Fallback**: If the database is empty or contains less than 10 logs, the engine falls back to a deterministic heuristic scoring engine combining event severity, off-hour checks (suspicious between 22:00 and 06:00), and minor random jitter.
- **On-Demand Training UI**: A button labeled `Train Model` in the top right dashboard header enables analysts to trigger manual retraining. Clicking this issues a POST request to `/api/model/train` which fits a new Isolation Forest to current database records, instantly updating the HUD status label from `untrained` (gray) to `trained` (purple).

### 3. Retrieval-Augmented Generation (RAG) Copilot
The **AI Copilot Lab** tab integrates RAG capabilities. Instead of relying purely on pre-trained LLM parameters, the system fetches active state context directly from the security environment:
- When a prompt is submitted, the backend fetches the **20 most recent high-severity (HIGH or CRITICAL) alerts** from MongoDB.
- These events are serialized and injected into a structured system prompt.
- The compiled prompt is sent to `gemini-2.5-flash` to formulate an analytical, contextual response.
- **Fallback Rule**: If the Gemini API key is missing or quota is exhausted, the system redirects the request to a local **Regex Keyword and Rule Engine** that aggregates alert counts, flags recurring source IPs, and suggests relevant mitigation advice.
- **Greeting Detection**: Recognizes simple hellos/greetings without sending expensive API requests, responding with a static assistant greeting to preserve API quota.

### 4. MITRE ATT&CK Mapping Engine
A hybrid mapping logic categorizes every security alert:
- **Known Events**: Detections matching preset signatures (e.g. `SSH_BRUTE_FORCE` or `PORT_SCAN`) are deterministically mapped to MITRE IDs (e.g. `T1110` for Brute Force, `T1046` for Network Service Discovery) to conserve processing time.
- **Unknown/Uncategorized Events**: Enters the Gemini inference pipeline, using zero-shot classification to map the incident to a relevant Technique ID, Name, Tactic, and list of Sub-techniques.

### 5. Algorithmic Risk Scoring
Rather than relying on raw severity flags, Zenith SOC evaluates a weighted index formula:

$$\text{Risk Score} = (0.40 \times \text{CVSS Normalized}) + (0.35 \times \text{Anomaly Score} \times 10) + (0.25 \times \text{Asset Criticality})$$

Where:
- **CVSS Normalized**: Raw base vulnerability score mapped to a 0–10 indicator.
- **Anomaly Score**: The scikit-learn Isolation Forest output `[0.0 - 1.0]`.
- **Asset Criticality**: Evaluates target value based on server tagging (e.g. Database servers = `10`, workstations = `3`).

The score maps to four risk bands:
- `0 - 25`: 🟢 **Low**
- `26 - 50`: 🟡 **Medium**
- `51 - 75`: 🟠 **High**
- `76 - 100`: 🔴 **Critical**

---

## 📋 Project Structure

```
soc/
├── backend/
│   ├── main.py                  # FastAPI server, lifespan, websockets, data loops
│   ├── config.py                # Environment configs & parsing defaults
│   ├── requirements.txt         # Core backend python dependencies
│   ├── .env                     # Local environment keys (ignored by git)
│   ├── .env.example             # Environment template for new setups
│   ├── __init__.py
│   ├── data_generator/
│   │   ├── __init__.py
│   │   └── generator.py         # Generates mock telemetry events
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── anomaly.py           # Isolation Forest model and feature extraction
│   │   ├── llm_summarizer.py    # LLM logs parser (Gemini API adapter)
│   │   ├── mitre_mapper.py      # MITRE ATT&CK zero-shot mapper
│   │   ├── threat_scorer.py     # Multi-metric Risk Score calculator
│   │   └── chat_assistant.py    # RAG assistant logic with greeting checks
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic validation objects
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── alerts.py            # Alert database queries & response playbooks
│   │   ├── stats.py             # Analytical aggregates (geo, timeline, severity)
│   │   └── chat.py              # Copilot post route
│   └── services/
│       ├── __init__.py
│       ├── alert_processor.py   # Orchestrator sending raw events through ML/AI
│       └── websocket_manager.py # Broadcast list client tracking
├── frontend/
│   ├── index.html               # Main template & custom Google fonts
│   ├── package.json             # NPM dependencies & build scripts
│   ├── vite.config.js           # Server port binding and backend /api proxying
│   ├── eslint.config.js         # Frontend linting definitions
│   └── src/
│       ├── main.jsx             # React entry mounting
│       ├── App.jsx              # App layout, WebSocket handlers, sync logic
│       ├── App.css              # Custom styling overrides
│       ├── index.css            # Styling core, Tailwind themes, animations
│       ├── components/
│       │   ├── DashboardHeader.jsx    # System state, health indicators, training triggers
│       │   ├── OverviewCards.jsx      # High-level statistics boxes
│       │   ├── AnalyticsCharts.jsx    # Severity charts, incident volume line timeline
│       │   ├── ThreatHotspots.jsx     # Geographic coordinate threat mapping
│       │   ├── AlertsTable.jsx        # Data list containing severity sorting & search
│       │   ├── AlertDetailSidebar.jsx # Slide-out inspector, MITRE tabs, SOAR buttons
│       │   └── AICopilot.jsx          # Interactive AI chat assistant box
│       └── utils/
│           └── api.js           # Centralized Axios fetch configuration
└── README.md                    # Detailed project overview
```

---

## 🚀 Step-by-Step Setup & Installation

### Prerequisites
- **Python 3.11+** installed on the system path.
- **Node.js 18+** with npm package manager.
- **MongoDB** running locally on port `27017` (or access to an online MongoDB Atlas cluster).

### Step 1: Clone the Repository
```bash
git clone https://github.com/Ajayadhithyan/soc_dash.git
cd soc
```

### Step 2: Configure Environment Variables
Inside the `backend/` directory, create a `.env` file from the example:
```bash
cd backend
cp .env.example .env
```
Open `backend/.env` and edit the values:
```env
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=soc_ai_dashboard
GEMINI_API_KEY=your_gemini_api_key_here
EVENT_GENERATION_INTERVAL=90
```
> **Note**: Zenith SOC will run perfectly in fallback mode if `GEMINI_API_KEY` is left blank, substituting local rule engines for RAG chat and structured templates for alert summaries.

### Step 3: Set up Python Backend
Create a virtual environment, activate it, and install dependencies:
```bash
# From the project root directory
python -m venv venv

# Activate on Windows:
venv\Scripts\activate
# Activate on macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Step 4: Install Frontend Dependencies
Configure Vite React packages:
```bash
# Navigate to the frontend directory
cd frontend
npm install
```

### Step 5: Start the Application

#### Running the Backend
From the virtual environment, start the FastAPI server:
```bash
# Ensure venv is active and run from project root:
venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Running the Frontend
In a new terminal window, boot the Vite local development server:
```bash
cd frontend
npm run dev
```

Open your browser and navigate to **http://localhost:5173**. The application will automatically query the backend, spin up a live WebSockets listener, and pre-populate the database with 5 startup events before periodically streaming new attacks.

---

## 📡 API Endpoints Reference

### System Health
- `GET /` & `GET /api/health`: Evaluates system connectivity, database response, Gemini config state, and whether the Isolation Forest is fully trained.

### Security Alerts
- `GET /api/alerts`: Fetches paginated list of alerts. Supports filtering via URL queries:
  - `page`: Page index (default: `1`)
  - `per_page`: Records per page (default: `10`)
  - `severity`: Filter by `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.
  - `event_type`: Filter by attack signatures (e.g. `DATA_EXFILTRATION`).
- `GET /api/alerts/{id}`: Returns the complete detailed log of a specific alert, including mapped MITRE ATT&CK schema structures and auto-response SOAR action logs.
- `POST /api/alerts/{id}/respond?action=`: Executes a simulated SOAR action. Supported query parameters for `action`:
  - `BLOCK_IP`: Blocks source IP at the network edge.
  - `QUARANTINE_HOST`: Isolates target machine from subnet.
  - `CREATE_TICKET`: Integrates incident details into an external ticketing system (e.g. Jira).

### Statistics & Metrics
- `GET /api/stats/overview`: Computes critical HUD highlights: total alert count, active threat count, and average environment risk score.
- `GET /api/stats/severity`: Returns counts grouped by severity labels for rendering pie/doughnut distributions.
- `GET /api/stats/timeline`: Groups alerts by temporal hourly buckets for trend graphs.
- `GET /api/stats/top-sources`: Identifies recurring source IPs targeting assets.
- `GET /api/stats/geo`: Aggregates attack coordinates to map global geographic threats.

### Machine Learning & AI Chat
- `POST /api/model/train`: Fits a new `IsolationForest` model to recent events from MongoDB. Returns execution status messages.
- `POST /api/chat`: Routes natural language questions to the AI Copilot. Evaluates recent security alerts in RAG context.

---

## ⚡ Incident Response Playbooks

When an alert is inspected, the **Playbook** view is populated with step-by-step containment instructions. In addition to manual steps, analysts can trigger one-click automated actions:

1. **IP Blocking (`BLOCK_IP`)**:
   - *Threat Target*: Command and Control (C2) servers, brute-force hosts, port scanners.
   - *Action*: Simulates push of ACL rules to perimeter firewalls. Returns a success log with firewall confirmation.
2. **Host Quarantine (`QUARANTINE_HOST`)**:
   - *Threat Target*: Malware infections, active command execution, compromised servers.
   - *Action*: Signals simulated endpoint response (EDR) agent to revoke NIC network access except to the SOC management segment.
3. **Ticket Creation (`CREATE_TICKET`)**:
   - *Threat Target*: High-severity alerts needing escalation.
   - *Action*: Submits incident metadata to ITSM tools, generating a simulated tracking reference.

---

## 📄 License & Context

This project is developed for educational and operational demonstration purposes. All simulated log streams, geo-origins, and attacks are synthetic and designed to illustrate the efficiency of combining unsupervised machine learning anomaly modeling with large language models inside SOC pipelines.

```


---

### 📄 File: `backend/.env`
**Purpose:** Source code/configuration resource.  
**Size:** 341 bytes

```python
# MongoDB Connection (local default or Atlas URI)
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=soc_ai_dashboard

GEMINI_API_KEY=your_gemini_api_key_here

# Event generation interval in seconds
EVENT_INTERVAL=17

# CORS allowed origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

```


---

### 📄 File: `backend/.env.example`
**Purpose:** Template setting environment variables for local development.  
**Size:** 404 bytes

```python
# MongoDB Connection (local default or Atlas URI)
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=soc_ai_dashboard

# Google Gemini API Key (free from https://aistudio.google.com/apikey)
# Leave empty to use rule-based fallback mode
GEMINI_API_KEY=

# Event generation interval in seconds
EVENT_INTERVAL=4

# CORS allowed origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

```


---

### 📄 File: `backend/__init__.py`
**Purpose:** Source code/configuration resource.  
**Size:** 18 bytes

```python
# backend package

```


---

### 📄 File: `backend/clear_db.py`
**Purpose:** Utility script to clear all security events and audit log documents from MongoDB collections.  
**Size:** 744 bytes

```python
import os
from pymongo import MongoClient

def main():
    mongodb_uri = "mongodb://localhost:27017/"
    db_name = "soc_ai_dashboard"
    
    print(f"Connecting to MongoDB at {mongodb_uri}...")
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    
    collections_to_clear = ["security_events", "audit_logs"]
    for col_name in collections_to_clear:
        count = db[col_name].count_documents({})
        print(f"Found {count} documents in collection '{col_name}'. Wiping them...")
        db[col_name].delete_many({})
        print(f"Collection '{col_name}' cleared. Document count now: {db[col_name].count_documents({})}")
        
    client.close()
    print("Done database wipe!")

if __name__ == "__main__":
    main()

```


---

### 📄 File: `backend/config.py`
**Purpose:** Configuration module loading database, AI, application parameters from environment variables.  
**Size:** 969 bytes

```python
"""
Configuration module for SOC AI Dashboard backend.
Loads settings from environment variables / .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

# -----------------------------------
# DATABASE
# -----------------------------------
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "soc_ai_dashboard")

# -----------------------------------
# AI / LLM
# -----------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# -----------------------------------
# APPLICATION
# -----------------------------------
EVENT_GENERATION_INTERVAL = int(os.getenv("EVENT_INTERVAL", "4"))  # seconds
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

# -----------------------------------
# RISK SCORING WEIGHTS
# -----------------------------------
WEIGHT_CVSS = 0.40
WEIGHT_ANOMALY = 0.35
WEIGHT_ASSET_CRITICALITY = 0.25

```


---

### 📄 File: `backend/data_generator/__init__.py`
**Purpose:** Source code/configuration resource.  
**Size:** 25 bytes

```python
# data_generator package

```


---

### 📄 File: `backend/data_generator/generator.py`
**Purpose:** Mock event generator simulating live network threat logs (brute-force, port scan, data exfiltration).  
**Size:** 7,108 bytes

```python
import csv
import random
import time
import argparse

from faker import Faker
from datetime import datetime
from pymongo import MongoClient

import os

# -----------------------------------
# INITIAL SETUP
# -----------------------------------

fake = Faker()

# MongoDB Connection
mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
db_name = os.getenv("DB_NAME", "soc_ai_dashboard")

client = MongoClient(mongodb_uri)

# Database
db = client[db_name]

# Collection
collection = db["security_events"]

# CSV FILE
CSV_FILE = "security_logs.csv"

# -----------------------------------
# EVENT CONFIGURATION
# -----------------------------------

EVENT_TYPES = [
    "SSH_BRUTE_FORCE",
    "PORT_SCAN",
    "FAILED_LOGIN",
    "MALWARE_DETECTION",
    "DATA_EXFILTRATION"
]

SEVERITY_LEVELS = {
    "SSH_BRUTE_FORCE": "HIGH",
    "PORT_SCAN": "MEDIUM",
    "FAILED_LOGIN": "LOW",
    "MALWARE_DETECTION": "CRITICAL",
    "DATA_EXFILTRATION": "CRITICAL"
}

USERS = [
    "root",
    "admin",
    "guest",
    "ubuntu",
    "kali",
    "test"
]

MALWARE_NAMES = [
    "Trojan.Win32",
    "LockBit.Ransomware",
    "Spyware.Keylogger",
    "Worm.AutoRun",
    "Backdoor.DarkComet"
]

COMMON_PORTS = [
    21, 22, 23, 25, 53,
    80, 110, 139, 443,
    445, 3306, 3389, 8080
]

# -----------------------------------
# CSV SETUP
# -----------------------------------

def setup_csv():

    try:

        with open(CSV_FILE, "x", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                "timestamp",
                "src_ip",
                "dest_ip",
                "event_type",
                "severity",
                "user",
                "raw_log"
            ])

        print("[+] CSV file created")

    except FileExistsError:

        print("[+] CSV file already exists")


# -----------------------------------
# GENERATE RAW LOG
# -----------------------------------

def generate_raw_log(
    event_type,
    src_ip,
    dest_ip,
    user
):

    # SSH BRUTE FORCE
    if event_type == "SSH_BRUTE_FORCE":

        attempts = random.randint(10, 100)

        return (
            f"SSH brute-force detected: "
            f"{attempts} failed login attempts "
            f"from {src_ip} targeting {dest_ip} "
            f"for user '{user}'"
        )

    # PORT SCAN
    elif event_type == "PORT_SCAN":

        ports = random.sample(
            COMMON_PORTS,
            4
        )

        return (
            f"Port scan detected from {src_ip} "
            f"against {dest_ip} "
            f"targeting ports {ports}"
        )

    # FAILED LOGIN
    elif event_type == "FAILED_LOGIN":

        return (
            f"Authentication failure for "
            f"user '{user}' from IP {src_ip}"
        )

    # MALWARE DETECTION
    elif event_type == "MALWARE_DETECTION":

        malware = random.choice(
            MALWARE_NAMES
        )

        return (
            f"Malware detected: {malware} "
            f"identified on endpoint {dest_ip} "
            f"originating from {src_ip}"
        )

    # DATA EXFILTRATION
    elif event_type == "DATA_EXFILTRATION":
        
        size_mb = round(random.uniform(50, 2000), 1)
        
        return (
            f"Anomalous data transfer: {size_mb} MB sent from {dest_ip} "
            f"to external host {src_ip} via encrypted channel"
        )

    return "Unknown security event"


# -----------------------------------
# GENERATE EVENT
# -----------------------------------

def generate_event():

    event_type = random.choice(
        EVENT_TYPES
    )

    src_ip = fake.ipv4_public()

    dest_ip = fake.ipv4_private()

    user = random.choice(
        USERS
    )

    event = {

        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "src_ip": src_ip,

        "dest_ip": dest_ip,

        "event_type": event_type,

        "severity": SEVERITY_LEVELS[
            event_type
        ],

        "user": user,

        "raw_log": generate_raw_log(
            event_type,
            src_ip,
            dest_ip,
            user
        )
    }

    return event


# -----------------------------------
# SAVE TO CSV
# -----------------------------------

def save_to_csv(event):

    with open(
        CSV_FILE,
        "a",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            event["timestamp"],
            event["src_ip"],
            event["dest_ip"],
            event["event_type"],
            event["severity"],
            event["user"],
            event["raw_log"]
        ])


# -----------------------------------
# SAVE TO MONGODB
# -----------------------------------

def save_to_mongodb(event):

    collection.insert_one(event)


# -----------------------------------
# DISPLAY EVENT
# -----------------------------------

def display_event(event):

    print("\n==============================")
    print(f"Timestamp   : {event['timestamp']}")
    print(f"Source IP   : {event['src_ip']}")
    print(f"Destination : {event['dest_ip']}")
    print(f"Event Type  : {event['event_type']}")
    print(f"Severity    : {event['severity']}")
    print(f"User        : {event['user']}")
    print(f"Raw Log     : {event['raw_log']}")
    print("==============================\n")


# -----------------------------------
# MAIN FUNCTION
# -----------------------------------

def main(
    stream=False,
    count=10
):

    setup_csv()

    # STREAMING MODE
    if stream:

        print(
            "[+] Live streaming enabled..."
        )

        while True:

            event = generate_event()

            save_to_csv(event)

            save_to_mongodb(event)

            display_event(event)

            # NEW EVENT EVERY 2 SECONDS
            time.sleep(2)

    # NORMAL MODE
    else:

        print(
            f"[+] Generating {count} events..."
        )

        for _ in range(count):

            event = generate_event()

            save_to_csv(event)

            save_to_mongodb(event)

            display_event(event)

        print(
            "[+] Log generation completed"
        )


# -----------------------------------
# ARGUMENT PARSER
# -----------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="SOC AI Log Generator"
    )

    parser.add_argument(
        "--stream",
        action="store_true",
        help="Enable live streaming"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of logs to generate"
    )

    args = parser.parse_args()

    main(
        stream=args.stream,
        count=args.count
    )
```


---

### 📄 File: `backend/main.py`
**Purpose:** Main entrypoint for the FastAPI backend server. Coordinates WebSocket broadcasts, ML pipelines, API routing, and synthetic event generation.  
**Size:** 11,502 bytes

```python
"""
Main entrypoint for the FastAPI backend server.
Coordinates WebSocket broadcasts, ML pipelines, API routing, and synthetic event generation.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from backend import config
from backend.ml.anomaly import AnomalyDetector
from backend.ml.chat_assistant import ChatAssistant
from backend.ml.llm_summarizer import AlertSummarizer
from backend.ml.mitre_mapper import MitreMapper
from backend.ml.threat_scorer import RiskScorer
from backend.routes import alerts, chat, stats, audit
from backend.services.alert_processor import generate_event, process_event
from backend.services.websocket_manager import ConnectionManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("soc_backend")

# Initialize shared components
websocket_manager = ConnectionManager()
anomaly_detector = AnomalyDetector()
mitre_mapper = MitreMapper(config.GEMINI_API_KEY)
summarizer = AlertSummarizer(config.GEMINI_API_KEY)
risk_scorer = RiskScorer(
    weight_cvss=config.WEIGHT_CVSS,
    weight_anomaly=config.WEIGHT_ANOMALY,
    weight_asset=config.WEIGHT_ASSET_CRITICALITY
)

# Async MongoDB Clients
mongo_client = None
db = None
chat_assistant = None
bg_generator_task = None


async def run_data_generator():
    """Background task that generates synthetic events, runs the pipeline, saves to DB, and broadcasts."""
    logger.info("Starting background security event generator...")
    try:
        # Wait a few seconds for initialization and initial ML training to settle
        await asyncio.sleep(4)
        
        # Pre-populate 5 fresh alerts immediately on startup so the analyst has fresh data instantly
        logger.info("Pre-populating 5 fresh security alerts...")
        for i in range(5):
            try:
                raw_event = generate_event()
                enriched_event = await process_event(
                    raw_event,
                    anomaly_detector,
                    mitre_mapper,
                    summarizer,
                    risk_scorer
                )
                await db["security_events"].insert_one(enriched_event)
                
                enriched_event_copy = dict(enriched_event)
                if "_id" in enriched_event_copy:
                    enriched_event_copy["_id"] = str(enriched_event_copy["_id"])
                
                if "id" not in enriched_event_copy:
                    enriched_event_copy["id"] = f"{enriched_event_copy.get('timestamp')}_{enriched_event_copy.get('src_ip')}"
                
                await websocket_manager.broadcast({
                    "type": "NEW_ALERT",
                    "data": enriched_event_copy
                })
                logger.info(f"Pre-populated startup alert {i+1}/5: {enriched_event_copy.get('event_type')}")
                
                # Tiny sleep to ensure separate timestamps/IDs
                await asyncio.sleep(1.2)
            except Exception as e:
                logger.error(f"Error pre-populating startup event: {e}")
        
        new_events_count = 0
        while True:
            try:
                # 1. Generate synthetic security event
                raw_event = generate_event()
                
                # 2. Process event through ML / AI pipeline
                enriched_event = await process_event(
                    raw_event,
                    anomaly_detector,
                    mitre_mapper,
                    summarizer,
                    risk_scorer
                )
                
                # 3. Save to MongoDB
                await db["security_events"].insert_one(enriched_event)
                
                # Clean MongoDB _id to allow serialization
                enriched_event_copy = dict(enriched_event)
                if "_id" in enriched_event_copy:
                    enriched_event_copy["_id"] = str(enriched_event_copy["_id"])
                
                # Add a synthetic id for the frontend if not already present
                if "id" not in enriched_event_copy:
                    enriched_event_copy["id"] = f"{enriched_event_copy.get('timestamp')}_{enriched_event_copy.get('src_ip')}"
                
                # 4. Broadcast via WebSocket
                await websocket_manager.broadcast({
                    "type": "NEW_ALERT",
                    "data": enriched_event_copy
                })
                
                logger.info(f"Processed and broadcast alert: {enriched_event_copy.get('event_type')} (Risk: {enriched_event_copy.get('risk_score')})")
                
                # Increment counter and retrain if threshold reached
                new_events_count += 1
                if new_events_count >= 20:
                    logger.info("Continuous ML Training: Auto-retraining Isolation Forest anomaly model on recent logs...")
                    try:
                        past_events_cursor = db["security_events"].find({}).sort("timestamp", -1).limit(500)
                        past_events = []
                        async for doc in past_events_cursor:
                            past_events.append(doc)
                        if len(past_events) >= 10:
                            anomaly_detector.train(past_events)
                            new_events_count = 0
                    except Exception as train_err:
                        logger.error(f"Failed to auto-train model in background: {train_err}")
                
            except Exception as e:
                logger.error(f"Error in data generator iteration: {e}", exc_info=True)
                
            # Interval between event generations (now 90 seconds)
            await asyncio.sleep(config.EVENT_GENERATION_INTERVAL)
            
    except asyncio.CancelledError:
        logger.info("Background security event generator stopped.")
    except Exception as e:
        logger.error(f"Unexpected error in background generator: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI Lifespan events handler (startup & shutdown)."""
    global mongo_client, db, chat_assistant, bg_generator_task
    
    # 1. Connect to MongoDB
    logger.info(f"Connecting to MongoDB at {config.MONGODB_URI} ...")
    mongo_client = AsyncIOMotorClient(config.MONGODB_URI)
    db = mongo_client[config.DB_NAME]
    
    # 2. Inject DB dependencies to routes
    alerts.set_db(db)
    stats.set_db(db)
    audit.set_db(db)
    
    # 3. Initialize & Inject Chat Assistant
    chat_assistant = ChatAssistant(db, config.GEMINI_API_KEY)
    chat.set_assistant(chat_assistant)
    
    # 4. ML Model Bootstrap Training
    # Get recent historical logs from DB to fit anomaly model
    logger.info("Retrieving past security events to train Isolation Forest baseline...")
    try:
        past_events_cursor = db["security_events"].find({}).sort("timestamp", -1).limit(500)
        past_events = []
        async for doc in past_events_cursor:
            past_events.append(doc)
            
        if len(past_events) >= 10:
            logger.info(f"Training anomaly detection model on {len(past_events)} historic events...")
            anomaly_detector.train(past_events)
        else:
            logger.info("Insufficient historical events found in database to train Isolation Forest. Model will use fallback scoring and auto-train as events stream in.")
    except Exception as e:
        logger.error(f"Failed to bootstrap train ML anomaly engine: {e}")
        
    # 5. Start background data generator task
    bg_generator_task = asyncio.create_task(run_data_generator())
    
    yield
    
    # SHUTDOWN PROCESS
    logger.info("Stopping FastAPI application...")
    if bg_generator_task:
        bg_generator_task.cancel()
        try:
            await bg_generator_task
        except asyncio.CancelledError:
            pass
            
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed.")


# Create FastAPI App instance
app = FastAPI(
    title="AI-Powered SOC Analyst Dashboard Backend",
    description="REST API and WebSocket feed for cybersecurity threat operations.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(alerts.router)
app.include_router(stats.router)
app.include_router(chat.router)
app.include_router(audit.router)


@app.get("/")
@app.get("/api/health")
def read_root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "SOC AI Dashboard API",
        "database": "connected" if db is not None else "disconnected",
        "gemini_api": "configured" if bool(config.GEMINI_API_KEY) else "fallback_mode",
        "anomaly_detector": "trained" if anomaly_detector.is_trained else "untrained"
    }


@app.post("/api/model/train")
async def train_model():
    """Manually trigger ML model training on historic security events."""
    logger.info("Manual training request received for Isolation Forest...")
    try:
        past_events_cursor = db["security_events"].find({}).sort("timestamp", -1).limit(500)
        past_events = []
        async for doc in past_events_cursor:
            past_events.append(doc)
            
        if len(past_events) >= 10:
            logger.info(f"Training anomaly detection model on {len(past_events)} historic events...")
            anomaly_detector.train(past_events)
            return {
                "success": True,
                "message": f"Successfully trained model on {len(past_events)} events.",
                "anomaly_detector": "trained"
            }
        else:
            return {
                "success": False,
                "message": "Insufficient historical events in database. Need at least 10 events to train.",
                "anomaly_detector": "untrained"
            }
    except Exception as e:
        logger.error(f"Failed to manually train ML anomaly engine: {e}")
        return {
            "success": False,
            "message": f"Failed to train ML engine: {str(e)}",
            "anomaly_detector": "trained" if anomaly_detector.is_trained else "untrained"
        }



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time threat stream."""
    await websocket_manager.connect(websocket)
    try:
        # Keep connection open and listen for any client messages (ping/pong, etc.)
        while True:
            # Receive data (discard or handle in-dashboard requests)
            data = await websocket.receive_text()
            # Simple Echo or confirmation
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket communication error: {e}")
        websocket_manager.disconnect(websocket)


if __name__ == "__main__":
    # Start the server
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

```


---

### 📄 File: `backend/ml/__init__.py`
**Purpose:** Source code/configuration resource.  
**Size:** 13 bytes

```python
# ml package

```


---

### 📄 File: `backend/ml/anomaly.py`
**Purpose:** Machine learning anomaly detection engine using Isolation Forest from scikit-learn.  
**Size:** 5,358 bytes

```python
"""
Anomaly Detection Engine using Isolation Forest.
Scores incoming security events for statistical anomalies.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime


class AnomalyDetector:
    """
    Unsupervised anomaly detector using Isolation Forest.
    Extracts numerical features from security events and scores
    each event on a 0.0–1.0 scale (higher = more anomalous).
    """

    # Encode event types as numeric features
    EVENT_TYPE_MAP = {
        "SSH_BRUTE_FORCE": 0,
        "PORT_SCAN": 1,
        "FAILED_LOGIN": 2,
        "MALWARE_DETECTION": 3,
        "DATA_EXFILTRATION": 4,
    }

    SEVERITY_MAP = {
        "LOW": 0,
        "MEDIUM": 1,
        "HIGH": 2,
        "CRITICAL": 3,
    }

    def __init__(self, contamination=0.15, n_estimators=100):
        """
        Args:
            contamination: Expected proportion of anomalies in data.
            n_estimators: Number of trees in the Isolation Forest.
        """
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=42,
            n_jobs=-1,
        )
        self.is_trained = False

    def _extract_features(self, event):
        """
        Extract numerical features from a single security event.

        Features:
            1. hour_of_day (0-23)
            2. event_type_encoded (0-4)
            3. severity_encoded (0-3)
            4. src_ip_last_octet (0-255) — proxy for IP diversity
            5. dest_ip_last_octet (0-255)
            6. is_privileged_user (0 or 1)
            7. day_of_week (0-6)
        """
        # Parse timestamp
        ts = event.get("timestamp", "")
        if isinstance(ts, str) and ts:
            try:
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dt = datetime.now()
        elif isinstance(ts, datetime):
            dt = ts
        else:
            dt = datetime.now()

        hour = dt.hour
        day_of_week = dt.weekday()

        # Event type encoding
        event_type = event.get("event_type", "FAILED_LOGIN")
        event_code = self.EVENT_TYPE_MAP.get(event_type, 2)

        # Severity encoding
        severity = event.get("severity", "LOW")
        severity_code = self.SEVERITY_MAP.get(severity, 0)

        # IP features — extract last octet as a numeric proxy
        src_ip = event.get("src_ip", "0.0.0.0")
        dest_ip = event.get("dest_ip", "0.0.0.0")
        try:
            src_last_octet = int(src_ip.split(".")[-1])
        except (ValueError, IndexError):
            src_last_octet = 0
        try:
            dest_last_octet = int(dest_ip.split(".")[-1])
        except (ValueError, IndexError):
            dest_last_octet = 0

        # Privileged user check
        privileged_users = {"root", "admin", "kali"}
        user = event.get("user", "")
        is_privileged = 1 if user in privileged_users else 0

        return [
            hour,
            event_code,
            severity_code,
            src_last_octet,
            dest_last_octet,
            is_privileged,
            day_of_week,
        ]

    def train(self, events):
        """
        Train the Isolation Forest on a list of historical events.

        Args:
            events: List of event dicts from MongoDB.
        """
        if not events or len(events) < 10:
            print("[Anomaly] Not enough data to train (need >= 10 events). Using default scoring.")
            self.is_trained = False
            return

        features = []
        for event in events:
            features.append(self._extract_features(event))

        X = np.array(features, dtype=np.float64)
        self.model.fit(X)
        self.is_trained = True
        print(f"[Anomaly] Model trained on {len(events)} events.")

    def score(self, event):
        """
        Score a single event for anomaly.

        Returns:
            float: Anomaly score between 0.0 (normal) and 1.0 (highly anomalous).
        """
        features = np.array([self._extract_features(event)], dtype=np.float64)

        if not self.is_trained:
            # Fallback: heuristic scoring based on severity and time
            severity = event.get("severity", "LOW")
            severity_score = self.SEVERITY_MAP.get(severity, 0) / 3.0

            ts = event.get("timestamp", "")
            if isinstance(ts, str) and ts:
                try:
                    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    dt = datetime.now()
            else:
                dt = datetime.now()

            # Off-hours (22:00-06:00) are more suspicious
            hour = dt.hour
            time_factor = 0.3 if (hour >= 22 or hour <= 6) else 0.0

            raw = min(1.0, severity_score * 0.7 + time_factor + np.random.uniform(0, 0.15))
            return round(raw, 4)

        # Isolation Forest: decision_function returns negative for anomalies
        raw_score = self.model.decision_function(features)[0]

        # Normalize: decision_function ranges roughly from -0.5 to 0.5
        # Map to 0.0–1.0 where higher = more anomalous
        normalized = 1.0 - (raw_score + 0.5)
        clamped = max(0.0, min(1.0, normalized))
        return round(clamped, 4)

```


---

### 📄 File: `backend/ml/chat_assistant.py`
**Purpose:** Core RAG assistant parsing database context and codebase context to answer analyst questions.  
**Size:** 12,625 bytes

```python
"""
RAG Chat Assistant.
Retrieves recent high-severity alerts from MongoDB, injects them
as context into a Gemini prompt, and answers analyst questions.
Falls back to keyword-based aggregation without an API key.
"""

import os
from datetime import datetime


class ChatAssistant:
    """
    AI chat assistant for SOC analysts.
    Uses RAG (Retrieval-Augmented Generation) with recent alerts as context.
    """

    def __init__(self, db=None, gemini_api_key=None):
        """
        Args:
            db: MongoDB database instance (motor async db).
            gemini_api_key: Optional Gemini API key.
        """
        self.db = db
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.use_llm = bool(self.gemini_api_key)
        self._gemini_model = None

        # Technical files map for full codebase context injection
        self.codebase_files = {
            "backend/main.py": "FastAPI Server setup, lifespan events, websockets, and generator loops",
            "backend/config.py": "Environment settings and threat risk calculation weights",
            "backend/ml/anomaly.py": "scikit-learn Isolation Forest model and 7D feature encoding",
            "backend/ml/threat_scorer.py": "Multi-criteria risk scoring formula logic",
            "backend/ml/llm_summarizer.py": "LLM Generative alert text summarizer engine",
            "backend/ml/mitre_mapper.py": "MITRE ATT&CK zero-shot classification mapping",
            "backend/models/schemas.py": "Pydantic v2 validation models",
            "backend/routes/alerts.py": "Alert routes, playbooks, analyst verification and SOAR actions",
            "backend/routes/stats.py": "Analytics aggregation and charting data logic",
            "frontend/src/App.jsx": "React layout navigation, WS listeners, and state synchronization",
            "frontend/src/components/AICopilot.jsx": "Copilot Chat UI component",
            "frontend/src/components/AlertDetailSidebar.jsx": "Triage details inspector drawer & SOAR trigger controls",
            "frontend/src/components/ThreatHotspots.jsx": "Geographic coordinate threat mapping component"
        }

        if self.use_llm:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self._gemini_model = genai.GenerativeModel("gemini-2.5-flash")
                print("[Chat] Gemini API configured for RAG chat assistant.")
            except Exception as e:
                print(f"[Chat] Gemini init failed: {e}. Using fallback mode.")
                self.use_llm = False

    def load_codebase_context(self):
        """Read and format actual files from the project codebase for high-context technical queries."""
        context_parts = []
        for filepath, description in self.codebase_files.items():
            try:
                resolved_path = os.path.abspath(filepath)
                if os.path.exists(resolved_path):
                    with open(resolved_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Extract up to 250 lines to stay inside token budgets while preserving full context
                    lines = content.splitlines()
                    if len(lines) > 250:
                        trimmed = "\n".join(lines[:250]) + "\n... [truncated for prompt length limit]"
                    else:
                        trimmed = content
                    
                    context_parts.append(
                        f"=== FILE: {filepath} ===\n"
                        f"Scope: {description}\n"
                        f"```code\n{trimmed}\n```\n"
                    )
            except Exception as e:
                context_parts.append(f"=== FILE: {filepath} ===\nLoad Error: {e}\n")
        return "\n".join(context_parts)

    async def get_context_alerts(self, limit=20):
        """Retrieve recent high-severity alerts from MongoDB as context."""
        if self.db is None:
            return []

        cursor = self.db["security_events"].find(
            {"severity": {"$in": ["HIGH", "CRITICAL"]}},
            {"_id": 0, "timestamp": 1, "event_type": 1, "severity": 1,
             "src_ip": 1, "dest_ip": 1, "raw_log": 1, "risk_score": 1,
             "ai_summary": 1, "mitre": 1}
        ).sort("timestamp", -1).limit(limit)

        alerts = []
        async for doc in cursor:
            alerts.append(doc)
        return alerts

    async def chat(self, question):
        """
        Answer an analyst's question using RAG.

        Args:
            question: Natural language question string.

        Returns:
            str: AI-generated answer.
        """
        context_alerts = await self.get_context_alerts()

        if self.use_llm and self._gemini_model:
            return await self._llm_chat(question, context_alerts)
        return self._fallback_chat(question, context_alerts)

    async def _llm_chat(self, question, context_alerts):
        """Use Gemini with RAG context to answer the question."""
        try:
            # Format alerts as context
            context_lines = []
            for i, alert in enumerate(context_alerts, 1):
                mitre_id = ""
                if isinstance(alert.get("mitre"), dict):
                    mitre_id = alert["mitre"].get("technique_id", "")
                context_lines.append(
                    f"{i}. [{alert.get('timestamp', 'N/A')}] "
                    f"{alert.get('event_type', 'N/A')} ({alert.get('severity', 'N/A')}) "
                    f"from {alert.get('src_ip', 'N/A')} → {alert.get('dest_ip', 'N/A')} "
                    f"| Risk: {alert.get('risk_score', 'N/A')} "
                    f"| MITRE: {mitre_id}"
                )

            context_str = "\n".join(context_lines) if context_lines else "No recent alerts available."

            # Load actual codebase files to answer technical questions precisely
            codebase_context = self.load_codebase_context()

            prompt = f"""You are Zenith Copilot, an expert AI Security Operations Center (SOC) assistant built into the Zenith SOC Platform. You have real-time access to the system's actual code repositories, application layouts, playbooks, routes, and live telemetry data.

Answer the analyst's question. Be highly specific, technical, and refer to lines of code, function names, classes, or database operations where relevant. Do NOT give generic or hand-waving responses.

=== ACTUAL CODEBASE SOURCE FILES ===
{codebase_context}

=== LIVE ENVIRONMENT CONTEXT (RECENT ALERTS) ===
{context_str}

=== ANALYST QUESTION ===
{question}

=== YOUR RESPONSE ===
"""

            response = self._gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[Chat] LLM error: {e}")
            return self._fallback_chat(question, context_alerts)

    def _fallback_chat(self, question, context_alerts):
        """Keyword-based answer engine when no LLM is available."""
        question_lower = question.lower()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not context_alerts:
            # Check for greetings even if no database context is ready
            greetings = {"hi", "hello", "hey", "yoo", "yo", "greetings", "good morning", "good afternoon", "good evening", "sup", "howdy", "hi there"}
            cleaned_question = question_lower.strip().rstrip("!?.,")
            if cleaned_question in greetings or any(cleaned_question.startswith(g + " ") for g in greetings):
                return (
                    "Hello! I am the Zenith SOC Copilot, your virtual SOC assistant. "
                    "I am ready to help you analyze security alerts, investigate threat actors, "
                    "or recommend response playbooks. How can I assist you today?"
                )
            return (
                f"As of {now}, I don't have enough alert data to answer your question. "
                "The system is still collecting events. Please check back shortly."
            )

        total = len(context_alerts)
        critical_count = sum(1 for a in context_alerts if a.get("severity") == "CRITICAL")
        high_count = sum(1 for a in context_alerts if a.get("severity") == "HIGH")

        # Count event types
        type_counts = {}
        for a in context_alerts:
            t = a.get("event_type", "UNKNOWN")
            type_counts[t] = type_counts.get(t, 0) + 1

        # Collect unique source IPs
        src_ips = list(set(a.get("src_ip", "") for a in context_alerts if a.get("src_ip")))

        # Check for simple greetings
        greetings = {"hi", "hello", "hey", "yoo", "yo", "greetings", "good morning", "good afternoon", "good evening", "sup", "howdy", "hi there"}
        cleaned_question = question_lower.strip().rstrip("!?.,")
        if cleaned_question in greetings or any(cleaned_question.startswith(g + " ") for g in greetings):
            has_other_keywords = any(
                any(kw in question_lower for kw in kw_list)
                for kw_list in [
                    ["top threat", "biggest threat", "main threat", "worst", "most dangerous"],
                    ["how many", "count", "total", "number"],
                    ["ip", "source", "attacker", "origin"],
                    ["recommend", "suggest", "action", "what should", "next step"]
                ]
            )
            if not has_other_keywords:
                return (
                    "Hello! I am the Zenith SOC Copilot, your virtual SOC assistant. "
                    "I can help you analyze security alerts, investigate threat actors, "
                    "or recommend response playbooks. How can I assist you today?"
                )

        # Top threats / summary
        if any(kw in question_lower for kw in ["top threat", "biggest threat", "main threat", "worst", "most dangerous"]):
            top_type = max(type_counts, key=type_counts.get)
            return (
                f"Based on the last {total} high-severity alerts, the most frequent threat type is "
                f"**{top_type}** ({type_counts[top_type]} occurrences). "
                f"There are {critical_count} CRITICAL and {high_count} HIGH severity alerts. "
                f"Top attacking IPs include: {', '.join(src_ips[:5])}. "
                "I recommend focusing on the CRITICAL alerts first and checking for any correlated attack patterns."
            )

        if any(kw in question_lower for kw in ["how many", "count", "total", "number"]):
            type_summary = ", ".join(f"{k}: {v}" for k, v in type_counts.items())
            return (
                f"In the recent alert window, there are **{total}** high-severity alerts: "
                f"{critical_count} CRITICAL, {high_count} HIGH. "
                f"Breakdown by type: {type_summary}."
            )

        if any(kw in question_lower for kw in ["ip", "source", "attacker", "origin"]):
            return (
                f"The following source IPs have been flagged in recent alerts: "
                f"{', '.join(src_ips[:10])}. "
                f"Total unique attacking IPs: {len(src_ips)}. "
                "Consider blocking repeat offenders at the perimeter firewall."
            )

        if any(kw in question_lower for kw in ["recommend", "suggest", "action", "what should", "next step"]):
            return (
                f"Based on {total} recent high-severity alerts ({critical_count} CRITICAL), I recommend:\n"
                "1. **Triage CRITICAL alerts first** — focus on malware detections and data exfiltration events.\n"
                "2. **Block repeat source IPs** at the firewall for IPs with multiple attack attempts.\n"
                "3. **Isolate affected endpoints** that show malware detection or brute-force compromise.\n"
                "4. **Review user accounts** targeted in brute-force attacks for credential reset.\n"
                "5. **Correlate events** to identify coordinated attack campaigns."
            )

        # Default summary
        type_summary = ", ".join(f"{k}: {v}" for k, v in type_counts.items())
        return (
            f"Here's what I see in the recent alert data: {total} high-severity alerts "
            f"({critical_count} CRITICAL, {high_count} HIGH). "
            f"Event breakdown: {type_summary}. "
            f"Unique source IPs: {len(src_ips)}. "
            "Ask me about specific threats, top attackers, or recommended actions for more detail."
        )

```


---

### 📄 File: `backend/ml/llm_summarizer.py`
**Purpose:** Gemini LLM generator producing plain-English alert summaries (with structured fallback templates).  
**Size:** 6,132 bytes

```python
"""
LLM Alert Summarizer.
Generates plain-English summaries of raw security alerts using
Google Gemini API or a smart rule-based fallback.
"""

import os
import random


# -----------------------------------
# FALLBACK TEMPLATES
# -----------------------------------

SUMMARY_TEMPLATES = {
    "SSH_BRUTE_FORCE": [
        "A brute-force SSH attack was detected from {src_ip} targeting {dest_ip}, with multiple failed login attempts against the '{user}' account. Immediate investigation is recommended to determine if any credentials were compromised.",
        "Repeated SSH login failures from {src_ip} indicate a credential-stuffing or brute-force attack against host {dest_ip}. The targeted account '{user}' should be temporarily locked and the source IP blocked at the firewall.",
        "An external host {src_ip} is aggressively attempting SSH authentication against {dest_ip} using the '{user}' account. This pattern is consistent with automated brute-force tooling and warrants immediate containment.",
    ],
    "PORT_SCAN": [
        "Network reconnaissance activity detected from {src_ip} scanning multiple ports on {dest_ip}. This is typically a precursor to exploitation and the source should be monitored for follow-up attacks.",
        "A systematic port scan from {src_ip} against {dest_ip} was identified, probing for exposed services. Verify that all non-essential ports are firewalled and assess if this IP has conducted prior scanning activity.",
        "Host {src_ip} is performing active network enumeration against {dest_ip}, testing multiple service ports. This reconnaissance behavior often precedes targeted exploitation attempts.",
    ],
    "FAILED_LOGIN": [
        "A failed authentication attempt was recorded for user '{user}' from IP {src_ip}. While isolated failures are common, a pattern of failures from this source should trigger account lockout policies.",
        "User '{user}' failed to authenticate from {src_ip}. Monitor for additional failures from this source — repeated attempts may indicate credential compromise or unauthorized access attempts.",
    ],
    "MALWARE_DETECTION": [
        "Malware was detected on endpoint {dest_ip} with traffic originating from {src_ip}. The affected host should be immediately isolated from the network, and a full forensic scan should be initiated.",
        "A malicious payload was identified on {dest_ip}, likely delivered from external source {src_ip}. Quarantine the endpoint immediately, collect forensic artifacts, and check for lateral movement indicators.",
        "Critical malware detection on {dest_ip} traced to {src_ip}. Immediate host isolation and incident response procedures are required to prevent potential lateral spread across the network.",
    ],
    "DATA_EXFILTRATION": [
        "Anomalous outbound data transfer detected from {dest_ip} to external host {src_ip}, transferring an unusually large volume of data. This may indicate active data exfiltration requiring immediate investigation.",
        "A potential data exfiltration event was identified with {dest_ip} sending significant data to {src_ip}. Verify whether this transfer was authorized and check for signs of compromised credentials or insider threat.",
    ],
}


class AlertSummarizer:
    """
    Generates analyst-friendly summaries for security alerts.
    Uses Google Gemini API when available, otherwise falls back
    to contextual template-based summaries.
    """

    def __init__(self, gemini_api_key=None):
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.use_llm = bool(self.gemini_api_key)
        self._gemini_model = None

        if self.use_llm:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self._gemini_model = genai.GenerativeModel("gemini-2.5-flash")
                print("[Summarizer] Gemini API configured for alert summarization.")
            except Exception as e:
                print(f"[Summarizer] Gemini init failed: {e}. Using fallback templates.")
                self.use_llm = False

    def summarize(self, event):
        """
        Generate a 2-sentence analyst-friendly summary.

        Args:
            event: dict with event_type, raw_log, src_ip, dest_ip, user, severity.

        Returns:
            str: Plain-English summary.
        """
        if self.use_llm and self._gemini_model:
            return self._llm_summarize(event)
        return self._fallback_summarize(event)

    def _llm_summarize(self, event):
        """Use Gemini to generate a natural-language summary."""
        try:
            prompt = f"""You are a senior SOC analyst. Summarize this security alert in exactly 2 concise sentences for an analyst dashboard. Be specific about the threat and recommended action.

Event Type: {event.get('event_type', 'Unknown')}
Severity: {event.get('severity', 'Unknown')}
Source IP: {event.get('src_ip', 'Unknown')}
Destination IP: {event.get('dest_ip', 'Unknown')}
User: {event.get('user', 'Unknown')}
Raw Log: {event.get('raw_log', 'No log available')}

Summary:"""

            response = self._gemini_model.generate_content(prompt)
            summary = response.text.strip()

            # Truncate if too long (keep it concise)
            sentences = summary.split(". ")
            if len(sentences) > 3:
                summary = ". ".join(sentences[:2]) + "."

            return summary
        except Exception as e:
            print(f"[Summarizer] LLM error: {e}. Using fallback.")
            return self._fallback_summarize(event)

    def _fallback_summarize(self, event):
        """Generate a summary using contextual templates."""
        event_type = event.get("event_type", "FAILED_LOGIN")
        templates = SUMMARY_TEMPLATES.get(event_type, SUMMARY_TEMPLATES["FAILED_LOGIN"])

        template = random.choice(templates)
        return template.format(
            src_ip=event.get("src_ip", "unknown"),
            dest_ip=event.get("dest_ip", "unknown"),
            user=event.get("user", "unknown"),
        )

```


---

### 📄 File: `backend/ml/mitre_mapper.py`
**Purpose:** Maps alerts to MITRE ATT&CK techniques using deterministic and zero-shot LLM classification.  
**Size:** 6,927 bytes

```python
"""
MITRE ATT&CK Mapper.
Maps security events to ATT&CK technique IDs using either
Google Gemini (zero-shot classification) or a deterministic fallback table.
"""

import os

# -----------------------------------
# DETERMINISTIC MAPPING TABLE
# -----------------------------------

MITRE_MAPPINGS = {
    "SSH_BRUTE_FORCE": {
        "technique_id": "T1110",
        "technique_name": "Brute Force",
        "tactic": "Credential Access",
        "description": "Adversary uses brute-force methods to attempt login by systematically trying passwords.",
        "sub_techniques": ["T1110.001 - Password Guessing", "T1110.003 - Password Spraying"],
        "severity_boost": 0.1,
    },
    "PORT_SCAN": {
        "technique_id": "T1046",
        "technique_name": "Network Service Discovery",
        "tactic": "Discovery",
        "description": "Adversary scans for open ports and services to identify attack surfaces.",
        "sub_techniques": ["T1046 - Network Service Scanning"],
        "severity_boost": 0.0,
    },
    "FAILED_LOGIN": {
        "technique_id": "T1078",
        "technique_name": "Valid Accounts",
        "tactic": "Defense Evasion, Persistence",
        "description": "Adversary may attempt to use valid account credentials to gain access.",
        "sub_techniques": ["T1078.001 - Default Accounts", "T1078.003 - Local Accounts"],
        "severity_boost": 0.0,
    },
    "MALWARE_DETECTION": {
        "technique_id": "T1204",
        "technique_name": "User Execution",
        "tactic": "Execution",
        "description": "Malicious code executed on the endpoint, possibly via user interaction or exploit.",
        "sub_techniques": ["T1204.002 - Malicious File", "T1059 - Command and Scripting Interpreter"],
        "severity_boost": 0.15,
    },
    "DATA_EXFILTRATION": {
        "technique_id": "T1041",
        "technique_name": "Exfiltration Over C2 Channel",
        "tactic": "Exfiltration",
        "description": "Adversary exfiltrates data from the network through the command-and-control channel.",
        "sub_techniques": ["T1041 - Exfiltration Over C2", "T1048 - Exfiltration Over Alternative Protocol"],
        "severity_boost": 0.2,
    },
}


class MitreMapper:
    """
    Maps security events to MITRE ATT&CK techniques.
    Uses Gemini API for zero-shot classification when available,
    otherwise falls back to deterministic table.
    """

    def __init__(self, gemini_api_key=None):
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.use_llm = bool(self.gemini_api_key)
        self._gemini_model = None

        if self.use_llm:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self._gemini_model = genai.GenerativeModel("gemini-2.5-flash")
                print("[MITRE] Gemini API configured for zero-shot classification.")
            except Exception as e:
                print(f"[MITRE] Gemini init failed: {e}. Using fallback mapping.")
                self.use_llm = False

    def map_event(self, event):
        """
        Map a security event to MITRE ATT&CK technique.

        Args:
            event: dict with event_type, raw_log, etc.

        Returns:
            dict with technique_id, technique_name, tactic, description, sub_techniques.
        """
        event_type = event.get("event_type", "")

        # Always use deterministic mapping for speed and reliability
        # LLM is used only for enrichment / unknown event types
        if event_type in MITRE_MAPPINGS:
            mapping = MITRE_MAPPINGS[event_type].copy()

            # If LLM is available, try to get additional context
            if self.use_llm and self._gemini_model:
                try:
                    enrichment = self._llm_enrich(event)
                    if enrichment:
                        mapping["llm_analysis"] = enrichment
                except Exception:
                    pass

            return mapping

        # Unknown event type — try LLM or return generic
        if self.use_llm and self._gemini_model:
            return self._llm_classify(event)

        return {
            "technique_id": "T1059",
            "technique_name": "Command and Scripting Interpreter",
            "tactic": "Execution",
            "description": "Unknown event type — generic classification applied.",
            "sub_techniques": [],
            "severity_boost": 0.0,
        }

    def _llm_classify(self, event):
        """Use Gemini for zero-shot MITRE ATT&CK classification."""
        try:
            prompt = f"""You are a cybersecurity analyst. Classify this security event into the most likely MITRE ATT&CK technique.

Event Type: {event.get('event_type', 'Unknown')}
Raw Log: {event.get('raw_log', 'No log available')}
Severity: {event.get('severity', 'Unknown')}

Respond in exactly this format:
Technique ID: T[XXXX]
Technique Name: [name]
Tactic: [tactic name]
Description: [one sentence description]"""

            response = self._gemini_model.generate_content(prompt)
            text = response.text.strip()

            # Parse response
            lines = text.split("\n")
            result = {
                "technique_id": "T1059",
                "technique_name": "Unknown",
                "tactic": "Unknown",
                "description": text,
                "sub_techniques": [],
                "severity_boost": 0.0,
            }

            for line in lines:
                if "Technique ID:" in line:
                    result["technique_id"] = line.split(":", 1)[1].strip()
                elif "Technique Name:" in line:
                    result["technique_name"] = line.split(":", 1)[1].strip()
                elif "Tactic:" in line:
                    result["tactic"] = line.split(":", 1)[1].strip()
                elif "Description:" in line:
                    result["description"] = line.split(":", 1)[1].strip()

            return result
        except Exception as e:
            print(f"[MITRE] LLM classify error: {e}")
            return {
                "technique_id": "T1059",
                "technique_name": "Command and Scripting Interpreter",
                "tactic": "Execution",
                "description": "LLM classification failed — fallback applied.",
                "sub_techniques": [],
                "severity_boost": 0.0,
            }

    def _llm_enrich(self, event):
        """Use Gemini to add extra analyst context to the mapping."""
        try:
            prompt = f"""In one sentence, explain the tactical significance of this security event for a SOC analyst:

Event: {event.get('event_type', '')}
Log: {event.get('raw_log', '')}"""

            response = self._gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return None

```


---

### 📄 File: `backend/ml/threat_scorer.py`
**Purpose:** Mathematical scoring engine compiling CVSS base severity, anomaly score, and asset criticality into a 0-100 risk score.  
**Size:** 2,556 bytes

```python
"""
Risk Scoring Engine.
Combines CVSS severity, ML anomaly score, and asset criticality
into a unified 0–100 risk index.
"""


# CVSS base scores per event type (approximate)
CVSS_SCORES = {
    "SSH_BRUTE_FORCE": 7.5,
    "PORT_SCAN": 5.3,
    "FAILED_LOGIN": 3.1,
    "MALWARE_DETECTION": 9.8,
    "DATA_EXFILTRATION": 9.1,
}

# Asset criticality tiers
ASSET_CRITICALITY = {
    "server": 0.9,
    "workstation": 0.5,
    "iot_device": 0.3,
    "database": 1.0,
    "firewall": 0.95,
    "default": 0.6,
}

# Risk labels
RISK_LABELS = {
    (0, 25): "Low",
    (26, 50): "Medium",
    (51, 75): "High",
    (76, 100): "Critical",
}


class RiskScorer:
    """
    Weighted risk scoring engine.

    Formula:
        risk = (W_cvss × CVSS_norm) + (W_anomaly × anomaly) + (W_asset × criticality)
    Scaled to 0–100.
    """

    def __init__(
        self,
        weight_cvss=0.40,
        weight_anomaly=0.35,
        weight_asset=0.25,
    ):
        self.weight_cvss = weight_cvss
        self.weight_anomaly = weight_anomaly
        self.weight_asset = weight_asset

    def score(self, event, anomaly_score=0.5):
        """
        Compute a risk score for an event.

        Args:
            event: dict with event_type, severity, etc.
            anomaly_score: float 0.0–1.0 from AnomalyDetector.

        Returns:
            dict with risk_score (0–100) and risk_label.
        """
        # 1. CVSS normalized (0-10 → 0-1)
        event_type = event.get("event_type", "FAILED_LOGIN")
        cvss = CVSS_SCORES.get(event_type, 5.0)
        cvss_normalized = cvss / 10.0

        # 2. Anomaly score (already 0-1)
        anomaly = max(0.0, min(1.0, anomaly_score))

        # 3. Asset criticality
        asset_type = event.get("asset_type", "default")
        criticality = ASSET_CRITICALITY.get(asset_type, 0.6)

        # Weighted sum → 0-1 → scale to 0-100
        raw = (
            self.weight_cvss * cvss_normalized
            + self.weight_anomaly * anomaly
            + self.weight_asset * criticality
        )
        risk_score = round(min(100.0, max(0.0, raw * 100)), 1)

        # Determine label
        risk_label = "Low"
        for (low, high), label in RISK_LABELS.items():
            if low <= risk_score <= high:
                risk_label = label
                break

        return {
            "risk_score": risk_score,
            "risk_label": risk_label,
            "cvss_base": cvss,
            "anomaly_score": round(anomaly, 4),
            "asset_criticality": criticality,
        }

```


---

### 📄 File: `backend/models/__init__.py`
**Purpose:** Source code/configuration resource.  
**Size:** 17 bytes

```python
# models package

```


---

### 📄 File: `backend/models/schemas.py`
**Purpose:** Pydantic validation schemas for API requests and response payloads.  
**Size:** 2,204 bytes

```python
"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AlertEvent(BaseModel):
    """Schema for a security alert event."""
    timestamp: str = ""
    src_ip: str = ""
    dest_ip: str = ""
    event_type: str = ""
    severity: str = ""
    user: str = ""
    raw_log: str = ""
    ai_summary: str = ""
    risk_score: float = 0.0
    risk_label: str = "Low"
    anomaly_score: float = 0.0
    cvss_base: float = 0.0
    asset_criticality: float = 0.0
    asset_type: str = "default"
    mitre: Dict[str, Any] = Field(default_factory=dict)
    auto_response: Optional[Dict[str, Any]] = None
    id: str = ""


class AlertListResponse(BaseModel):
    """Paginated list of alerts."""
    alerts: List[Dict[str, Any]] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 50


class StatsOverview(BaseModel):
    """KPI overview metrics."""
    total_alerts: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    avg_risk_score: float = 0.0
    active_threats: int = 0
    alerts_last_hour: int = 0


class SeverityDistribution(BaseModel):
    """Severity breakdown for charts."""
    severity: str
    count: int


class TimelinePoint(BaseModel):
    """Single point in timeline chart."""
    time: str
    count: int


class TopSource(BaseModel):
    """Top attacking source IP."""
    ip: str
    count: int
    last_seen: str = ""
    primary_attack: str = ""


class ChatRequest(BaseModel):
    """Chat message from analyst."""
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    """Chat response from AI assistant."""
    response: str
    context_alerts_used: int = 0


class AutoResponseRequest(BaseModel):
    """Auto-response action request."""
    action: str = Field(..., pattern="^(block_ip|quarantine_host|create_ticket)$")
    alert_id: str = ""


class AutoResponseResult(BaseModel):
    """Result of an auto-response action."""
    success: bool
    action: str
    message: str
    timestamp: str = ""
    details: dict = {}

```


---

### 📄 File: `backend/pyrightconfig.json`
**Purpose:** Pyright Linter config settings for backend.  
**Size:** 357 bytes

```json
{
  "venvPath": "C:\\Users\\V.AJAY ADHITHYAN\\Desktop\\soc",
  "venv": "venv",
  "pythonVersion": "3.12",
  "pythonPlatform": "Windows",
  "extraPaths": [
    "C:\\Users\\V.AJAY ADHITHYAN\\Desktop\\soc",
    "C:\\Users\\V.AJAY ADHITHYAN\\Desktop\\soc\\venv\\Lib\\site-packages"
  ],
  "reportMissingImports": "none",
  "reportMissingModuleSource": "none"
}

```


---

### 📄 File: `backend/requirements.txt`
**Purpose:** Core Python package dependencies required to run the backend engine.  
**Size:** 185 bytes

```text
fastapi==0.115.6
uvicorn[standard]==0.32.1
motor==3.6.0
pymongo>=4.9,<4.10
python-dotenv==1.0.1
scikit-learn==1.5.2
pandas==2.2.3
numpy==1.26.4
faker==33.3.1
google-generativeai==0.8.4

```


---

### 📄 File: `backend/routes/__init__.py`
**Purpose:** Source code/configuration resource.  
**Size:** 17 bytes

```python
# routes package

```


---

### 📄 File: `backend/routes/alerts.py`
**Purpose:** API endpoints handling security alerts, playbooks, analyst verification, and SOAR response actions.  
**Size:** 10,663 bytes

```python
"""
Alert API routes.
Provides endpoints for listing, filtering, and responding to security alerts.
"""

from fastapi import APIRouter, Query
from datetime import datetime
import random

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# Will be set from main.py
db = None


def set_db(database):
    global db
    db = database


@router.get("")
async def get_alerts(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    severity: str = Query(None),
    event_type: str = Query(None),
    sort_by: str = Query("timestamp"),
    sort_order: str = Query("desc"),
):
    """Get paginated list of alerts with optional filters."""
    query = {}

    if severity:
        query["severity"] = severity.upper()
    if event_type:
        query["event_type"] = event_type.upper()

    sort_direction = -1 if sort_order == "desc" else 1
    skip = (page - 1) * per_page

    total = await db["security_events"].count_documents(query)

    cursor = db["security_events"].find(
        query, {"_id": 0}
    ).sort(sort_by, sort_direction).skip(skip).limit(per_page)

    alerts = []
    async for doc in cursor:
        # Add a synthetic ID based on index if not present
        if "id" not in doc:
            doc["id"] = doc.get("timestamp", "") + "_" + doc.get("src_ip", "")
        alerts.append(doc)

    return {
        "alerts": alerts,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/recent")
async def get_recent_alerts(limit: int = Query(20, ge=1, le=100)):
    """Get the most recent alerts."""
    cursor = db["security_events"].find(
        {}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit)

    alerts = []
    async for doc in cursor:
        if "id" not in doc:
            doc["id"] = doc.get("timestamp", "") + "_" + doc.get("src_ip", "")
        alerts.append(doc)

    return {"alerts": alerts, "count": len(alerts)}


@router.get("/{alert_id}")
async def get_alert_detail(alert_id: str):
    """Get a single alert with full details and playbook suggestions."""
    # Parse the synthetic ID
    parts = alert_id.split("_", 1)
    query = {}
    if len(parts) == 2:
        query = {"timestamp": parts[0], "src_ip": parts[1]}
    else:
        query = {"timestamp": alert_id}

    doc = await db["security_events"].find_one(query, {"_id": 0})

    if not doc:
        return {"error": "Alert not found"}

    doc["id"] = alert_id

    # Add playbook suggestions based on event type
    playbooks = _get_playbook(doc.get("event_type", ""))
    doc["playbook"] = playbooks

    return doc


@router.post("/{alert_id}/respond")
async def auto_respond(alert_id: str, action: str = Query(...)):
    """
    Execute a simulated auto-response action.
    Actions: block_ip, quarantine_host, create_ticket
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Parse alert ID to get context
    parts = alert_id.split("_", 1)
    src_ip = parts[1] if len(parts) == 2 else "unknown"

    responses = {
        "block_ip": {
            "success": True,
            "action": "block_ip",
            "message": f"Firewall rule created: BLOCK {src_ip} on all inbound ports.",
            "timestamp": now,
            "details": {
                "rule_id": f"FW-{random.randint(10000, 99999)}",
                "ip_blocked": src_ip,
                "duration": "24 hours",
                "scope": "perimeter_firewall",
            },
        },
        "quarantine_host": {
            "success": True,
            "action": "quarantine_host",
            "message": f"Host isolation initiated. Network segment quarantined.",
            "timestamp": now,
            "details": {
                "ticket_id": f"QR-{random.randint(10000, 99999)}",
                "isolation_type": "network_segment",
                "status": "isolated",
                "duration": "until_manual_release",
            },
        },
        "create_ticket": {
            "success": True,
            "action": "create_ticket",
            "message": f"Incident ticket created and assigned to SOC Tier-2 team.",
            "timestamp": now,
            "details": {
                "ticket_id": f"INC-{random.randint(100000, 999999)}",
                "priority": "P1 - Critical",
                "assigned_to": "SOC Tier-2 Team",
                "sla_response": "15 minutes",
            },
        },
    }

    result = responses.get(action)
    if not result:
        return {"success": False, "message": f"Unknown action: {action}"}

    # Store the response action in the alert
    if len(parts) == 2:
        await db["security_events"].update_one(
            {"timestamp": parts[0], "src_ip": parts[1]},
            {"$set": {"auto_response": result}}
        )

    # Insert into audit_logs
    audit_entry = {
        "timestamp": now,
        "alert_id": alert_id,
        "action": action,
        "analyst_user": "admin_analyst",
        "success": True,
        "details": result.get("details", {})
    }
    await db["audit_logs"].insert_one(audit_entry)

    return result


@router.post("/{alert_id}/verify")
async def verify_alert(alert_id: str, status: str = Query(...)):
    """
    Mark an alert as TRUE_POSITIVE or FALSE_POSITIVE.
    """
    if status.upper() not in ["TRUE_POSITIVE", "FALSE_POSITIVE"]:
        return {"success": False, "message": f"Invalid verification status: {status}"}

    parts = alert_id.split("_", 1)
    if len(parts) == 2:
        res = await db["security_events"].update_one(
            {"timestamp": parts[0], "src_ip": parts[1]},
            {"$set": {"analyst_verification": status.upper()}}
        )
        if res.matched_count > 0:
            return {"success": True, "message": f"Alert marked as {status.upper()}."}

    return {"success": False, "message": "Alert not found."}


def _get_playbook(event_type):
    """Return response playbook suggestions for an event type."""
    playbooks = {
        "SSH_BRUTE_FORCE": {
            "name": "SSH Brute Force Response",
            "steps": [
                "1. Verify if the targeted account has been compromised by checking successful logins.",
                "2. Block the source IP at the perimeter firewall.",
                "3. Enforce account lockout policy (5 failed attempts → 30 min lock).",
                "4. Enable MFA on the targeted account if not already active.",
                "5. Review SSH server configuration — disable root login, use key-based auth.",
                "6. Escalate to Tier-2 if successful login detected from the source IP.",
            ],
            "severity": "HIGH",
            "estimated_time": "15-30 minutes",
        },
        "PORT_SCAN": {
            "name": "Network Reconnaissance Response",
            "steps": [
                "1. Identify all ports that responded to the scan.",
                "2. Verify firewall rules are correctly blocking unused ports.",
                "3. Check if the source IP has conducted prior scanning activity.",
                "4. Add the source IP to the watchlist for 72 hours.",
                "5. Review IDS/IPS signatures for follow-up exploitation attempts.",
                "6. If internal source — investigate for compromised host or insider threat.",
            ],
            "severity": "MEDIUM",
            "estimated_time": "10-20 minutes",
        },
        "FAILED_LOGIN": {
            "name": "Authentication Failure Review",
            "steps": [
                "1. Check if this is an isolated event or part of a pattern.",
                "2. Verify the user account is valid and not a service account.",
                "3. If repeated — implement temporary IP-based rate limiting.",
                "4. Contact the account owner to verify legitimacy.",
                "5. Review authentication logs for the same source IP.",
            ],
            "severity": "LOW",
            "estimated_time": "5-10 minutes",
        },
        "MALWARE_DETECTION": {
            "name": "Malware Incident Response",
            "steps": [
                "1. IMMEDIATELY isolate the affected endpoint from the network.",
                "2. Collect forensic artifacts (memory dump, disk image, logs).",
                "3. Identify the malware family and check for IOCs.",
                "4. Scan all hosts in the same network segment for lateral movement.",
                "5. Block the C2 server IP/domain at DNS and firewall level.",
                "6. Initiate full AV scan across the organization.",
                "7. Restore from last known clean backup if necessary.",
                "8. Escalate to CIRT (Cyber Incident Response Team).",
            ],
            "severity": "CRITICAL",
            "estimated_time": "1-4 hours",
        },
        "DATA_EXFILTRATION": {
            "name": "Data Exfiltration Response",
            "steps": [
                "1. Block the external destination IP immediately.",
                "2. Identify what data was transferred (DLP logs, file access logs).",
                "3. Preserve network capture data for forensic analysis.",
                "4. Check if the source host is compromised — run EDR scan.",
                "5. Notify data governance / legal team if PII/sensitive data involved.",
                "6. Review the user's access permissions and recent activity.",
                "7. Escalate to CIRT and management if confirmed exfiltration.",
            ],
            "severity": "CRITICAL",
            "estimated_time": "2-6 hours",
        },
        "IMPOSSIBLE_TRAVEL": {
            "name": "Impossible Travel Security Playbook",
            "steps": [
                "1. Force terminate all active user sessions for the targeted account.",
                "2. Disable the user account in Active Directory / Identity Provider.",
                "3. Contact the user via secondary channel (phone) to verify active location.",
                "4. Check for anomalous successful authentication logs from both flagged locations.",
                "5. Inspect EDR/endpoint logs on devices used at both locations.",
                "6. Enforce immediate credential reset and MFA token re-registration.",
                "7. Check for lateral movement or data exfiltration from either session."
            ],
            "severity": "CRITICAL",
            "estimated_time": "30-45 minutes",
        },
    }
    return playbooks.get(event_type, {
        "name": "General Response",
        "steps": ["1. Investigate the alert.", "2. Escalate if necessary."],
        "severity": "MEDIUM",
        "estimated_time": "15 minutes",
    })

```


---

### 📄 File: `backend/routes/audit.py`
**Purpose:** API endpoints for retrieving SOAR playbook audit trails.  
**Size:** 708 bytes

```python
"""
Audit Log API routes.
Provides endpoints for retrieving action logs executed on the platform.
"""

from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/audit", tags=["audit"])

# Will be set from main.py
db = None


def set_db(database):
    global db
    db = database


@router.get("")
async def get_audit_logs(limit: int = Query(50, ge=1, le=100)):
    """Get the most recent SOAR audit logs."""
    if db is None:
        return {"audit_logs": [], "count": 0}

    cursor = db["audit_logs"].find(
        {}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit)

    logs = []
    async for doc in cursor:
        logs.append(doc)

    return {"audit_logs": logs, "count": len(logs)}

```


---

### 📄 File: `backend/routes/chat.py`
**Purpose:** API endpoint for the RAG-powered Zenith AI Copilot chat routing.  
**Size:** 1,256 bytes

```python
"""
Chat API route.
RAG-powered chat endpoint for the AI analyst assistant.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Will be set from main.py
chat_assistant = None


def set_assistant(assistant):
    global chat_assistant
    chat_assistant = assistant


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


@router.post("")
async def chat(request: ChatMessage):
    """
    Send a question to the AI SOC analyst assistant.
    Uses RAG with recent alerts as context.
    """
    if chat_assistant is None:
        return {
            "response": "Chat assistant is not initialized. Please check backend configuration.",
            "context_alerts_used": 0,
        }

    try:
        response = await chat_assistant.chat(request.message)
        context_count = len(await chat_assistant.get_context_alerts())
        return {
            "response": response,
            "context_alerts_used": context_count,
        }
    except Exception as e:
        return {
            "response": f"I encountered an error processing your question: {str(e)}. Please try rephrasing.",
            "context_alerts_used": 0,
        }

```


---

### 📄 File: `backend/routes/stats.py`
**Purpose:** API endpoints aggregating KPI stats, timeline history, and geographical threat map data.  
**Size:** 6,105 bytes

```python
"""
Statistics API routes.
Provides endpoints for dashboard KPI metrics, charts, and analytics.
"""

from fastapi import APIRouter
from datetime import datetime, timedelta
from collections import Counter

router = APIRouter(prefix="/api/stats", tags=["stats"])

# Will be set from main.py
db = None


def set_db(database):
    global db
    db = database


@router.get("/overview")
async def get_overview():
    """Get KPI overview metrics for the dashboard."""
    total = await db["security_events"].count_documents({})
    critical = await db["security_events"].count_documents({"severity": "CRITICAL"})
    high = await db["security_events"].count_documents({"severity": "HIGH"})
    medium = await db["security_events"].count_documents({"severity": "MEDIUM"})
    low = await db["security_events"].count_documents({"severity": "LOW"})

    # Average risk score
    pipeline = [
        {"$match": {"risk_score": {"$exists": True}}},
        {"$group": {"_id": None, "avg_risk": {"$avg": "$risk_score"}}},
    ]
    avg_result = await db["security_events"].aggregate(pipeline).to_list(1)
    avg_risk = round(avg_result[0]["avg_risk"], 1) if avg_result else 0.0

    # Active threats (high + critical in last hour)
    one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    active = await db["security_events"].count_documents({
        "severity": {"$in": ["HIGH", "CRITICAL"]},
        "timestamp": {"$gte": one_hour_ago},
    })

    # Alerts in last hour
    alerts_last_hour = await db["security_events"].count_documents({
        "timestamp": {"$gte": one_hour_ago},
    })

    return {
        "total_alerts": total,
        "critical_count": critical,
        "high_count": high,
        "medium_count": medium,
        "low_count": low,
        "avg_risk_score": avg_risk,
        "active_threats": active,
        "alerts_last_hour": alerts_last_hour,
    }


@router.get("/severity")
async def get_severity_distribution():
    """Get severity distribution for bar chart."""
    pipeline = [
        {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    result = await db["security_events"].aggregate(pipeline).to_list(10)

    distribution = []
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    for doc in result:
        distribution.append({
            "severity": doc["_id"] or "UNKNOWN",
            "count": doc["count"],
        })

    distribution.sort(key=lambda x: severity_order.get(x["severity"], 99))
    return {"distribution": distribution}


@router.get("/event-types")
async def get_event_type_distribution():
    """Get event type distribution for charts."""
    pipeline = [
        {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    result = await db["security_events"].aggregate(pipeline).to_list(20)

    return {
        "event_types": [
            {"event_type": doc["_id"] or "UNKNOWN", "count": doc["count"]}
            for doc in result
        ]
    }


@router.get("/timeline")
async def get_timeline():
    """Get alerts over time for line chart (grouped by minute)."""
    # Get last 60 entries grouped by minute
    cursor = db["security_events"].find(
        {}, {"timestamp": 1, "_id": 0}
    ).sort("timestamp", -1).limit(500)

    timestamps = []
    async for doc in cursor:
        timestamps.append(doc.get("timestamp", ""))

    # Group by minute
    minute_counts = Counter()
    for ts in timestamps:
        if ts:
            # Truncate to minute
            minute = ts[:16]  # "YYYY-MM-DD HH:MM"
            minute_counts[minute] += 1

    # Sort and return last 30 minutes
    sorted_minutes = sorted(minute_counts.items())[-30:]

    return {
        "timeline": [
            {"time": m[0], "count": m[1]}
            for m in sorted_minutes
        ]
    }


@router.get("/top-sources")
async def get_top_sources():
    """Get top attacking source IPs."""
    pipeline = [
        {"$group": {
            "_id": "$src_ip",
            "count": {"$sum": 1},
            "last_seen": {"$max": "$timestamp"},
            "events": {"$push": "$event_type"},
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    result = await db["security_events"].aggregate(pipeline).to_list(10)

    sources = []
    for doc in result:
        # Get the most common event type for this IP
        event_counts = Counter(doc.get("events", []))
        primary_attack = event_counts.most_common(1)[0][0] if event_counts else "UNKNOWN"

        sources.append({
            "ip": doc["_id"] or "unknown",
            "count": doc["count"],
            "last_seen": doc.get("last_seen", ""),
            "primary_attack": primary_attack,
        })

    return {"sources": sources}


@router.get("/risk-distribution")
async def get_risk_distribution():
    """Get risk score distribution for analytics."""
    pipeline = [
        {"$match": {"risk_label": {"$exists": True}}},
        {"$group": {"_id": "$risk_label", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    result = await db["security_events"].aggregate(pipeline).to_list(10)

    return {
        "risk_distribution": [
            {"label": doc["_id"] or "Unknown", "count": doc["count"]}
            for doc in result
        ]
    }


@router.get("/geo")
async def get_geo_data():
    """Get geographic threat data for the world map."""
    pipeline = [
        {"$match": {"geo": {"$exists": True}}},
        {"$group": {
            "_id": "$geo.country",
            "count": {"$sum": 1},
            "lat": {"$first": "$geo.lat"},
            "lng": {"$first": "$geo.lng"},
        }},
        {"$sort": {"count": -1}},
    ]
    result = await db["security_events"].aggregate(pipeline).to_list(50)

    return {
        "geo_threats": [
            {
                "country": doc["_id"] or "Unknown",
                "count": doc["count"],
                "lat": doc.get("lat", 0),
                "lng": doc.get("lng", 0),
            }
            for doc in result
        ]
    }

```


---

### 📄 File: `backend/services/__init__.py`
**Purpose:** Source code/configuration resource.  
**Size:** 19 bytes

```python
# services package

```


---

### 📄 File: `backend/services/alert_processor.py`
**Purpose:** Pipeline orchestrator scoring events for anomalies, mapping MITRE ATT&CK vectors, summarizing logs, and calculating final risk scores.  
**Size:** 8,019 bytes

```python
"""
Alert Processing Pipeline.
Generates events, runs them through ML models, and saves enriched alerts to MongoDB.
"""

import random
import logging
from datetime import datetime
from faker import Faker

fake = Faker()
logger = logging.getLogger("soc_backend")

# -----------------------------------
# EVENT CONFIGURATION
# -----------------------------------

EVENT_TYPES = [
    "SSH_BRUTE_FORCE",
    "PORT_SCAN",
    "FAILED_LOGIN",
    "MALWARE_DETECTION",
    "DATA_EXFILTRATION",
]

EVENT_WEIGHTS = [0.20, 0.25, 0.25, 0.15, 0.15]

SEVERITY_LEVELS = {
    "SSH_BRUTE_FORCE": "HIGH",
    "PORT_SCAN": "MEDIUM",
    "FAILED_LOGIN": "LOW",
    "MALWARE_DETECTION": "CRITICAL",
    "DATA_EXFILTRATION": "CRITICAL",
}

USERS = ["root", "admin", "guest", "ubuntu", "kali", "test", "sysadmin", "devops"]

MALWARE_NAMES = [
    "Trojan.Win32", "LockBit.Ransomware", "Spyware.Keylogger",
    "Worm.AutoRun", "Backdoor.DarkComet", "Emotet.Loader",
    "Cobalt.Strike.Beacon", "Mimikatz.Dump",
]

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 139, 443, 445, 3306, 3389, 8080, 8443]

ASSET_TYPES = ["server", "workstation", "iot_device", "database", "firewall"]

# Geographic source data for threat map
GEO_SOURCES = [
    {"country": "Russia", "lat": 55.75, "lng": 37.62},
    {"country": "China", "lat": 39.91, "lng": 116.40},
    {"country": "USA", "lat": 40.71, "lng": -74.01},
    {"country": "Brazil", "lat": -23.55, "lng": -46.63},
    {"country": "India", "lat": 28.61, "lng": 77.21},
    {"country": "Germany", "lat": 52.52, "lng": 13.41},
    {"country": "Iran", "lat": 35.69, "lng": 51.39},
    {"country": "North Korea", "lat": 39.02, "lng": 125.75},
    {"country": "Nigeria", "lat": 6.52, "lng": 3.38},
    {"country": "Romania", "lat": 44.43, "lng": 26.10},
    {"country": "Ukraine", "lat": 50.45, "lng": 30.52},
    {"country": "Turkey", "lat": 41.01, "lng": 28.98},
]


def generate_raw_log(event_type, src_ip, dest_ip, user):
    """Generate a realistic raw log string for the event type."""
    if event_type == "SSH_BRUTE_FORCE":
        attempts = random.randint(10, 100)
        return (
            f"SSH brute-force detected: {attempts} failed login attempts "
            f"from {src_ip} targeting {dest_ip} for user '{user}'"
        )
    elif event_type == "PORT_SCAN":
        ports = random.sample(COMMON_PORTS, min(4, len(COMMON_PORTS)))
        return (
            f"Port scan detected from {src_ip} against {dest_ip} "
            f"targeting ports {ports}"
        )
    elif event_type == "FAILED_LOGIN":
        return f"Authentication failure for user '{user}' from IP {src_ip}"
    elif event_type == "MALWARE_DETECTION":
        malware = random.choice(MALWARE_NAMES)
        return (
            f"Malware detected: {malware} identified on endpoint {dest_ip} "
            f"originating from {src_ip}"
        )
    elif event_type == "DATA_EXFILTRATION":
        size_mb = round(random.uniform(50, 2000), 1)
        return (
            f"Anomalous data transfer: {size_mb} MB sent from {dest_ip} "
            f"to external host {src_ip} via encrypted channel"
        )
    return "Unknown security event"


def generate_event():
    """Generate a single synthetic security event."""
    event_type = random.choices(EVENT_TYPES, weights=EVENT_WEIGHTS, k=1)[0]
    src_ip = fake.ipv4_public()
    dest_ip = fake.ipv4_private()
    user = random.choice(USERS)
    asset_type = random.choice(ASSET_TYPES)
    geo = random.choice(GEO_SOURCES)

    event = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "src_ip": src_ip,
        "dest_ip": dest_ip,
        "event_type": event_type,
        "severity": SEVERITY_LEVELS[event_type],
        "user": user,
        "raw_log": generate_raw_log(event_type, src_ip, dest_ip, user),
        "asset_type": asset_type,
        "geo": geo,
    }
    return event


# Map to track login history of users: { username: { country, timestamp_str, lat, lng } }
last_login_locations = {}

def check_impossible_travel(event):
    """
    Check if a user logs in from two different countries in a timeframe
    physically impossible to travel, overriding to IMPOSSIBLE_TRAVEL if so.
    """
    global last_login_locations
    user = event.get("user")
    event_type = event.get("event_type")
    geo = event.get("geo")
    
    if not user or not geo or user in ["SYSTEM", "unknown"]:
        return event

    # Check for login related event types
    if event_type in ["FAILED_LOGIN", "SSH_BRUTE_FORCE"]:
        now_str = event.get("timestamp")
        try:
            now_dt = datetime.strptime(now_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            now_dt = datetime.now()
            
        last_login = last_login_locations.get(user)
        if last_login:
            last_country = last_login["country"]
            last_time_str = last_login["timestamp"]
            try:
                last_dt = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                last_dt = now_dt
                
            time_diff = (now_dt - last_dt).total_seconds()
            
            # If country is different and time diff is extremely short (e.g. less than 200 seconds)
            if last_country != geo["country"] and 0 < time_diff < 200:
                # Trigger IMPOSSIBLE_TRAVEL alert
                event["event_type"] = "IMPOSSIBLE_TRAVEL"
                event["severity"] = "CRITICAL"
                event["raw_log"] = (
                    f"Impossible travel detected: User '{user}' authenticated "
                    f"from {geo['country']} at {now_str} after logging in "
                    f"from {last_country} at {last_time_str} ({int(time_diff)}s ago)."
                )
                logger.warning(f"Impossible travel flagged for user '{user}': {last_country} -> {geo['country']}")
        
        # Update last login location
        last_login_locations[user] = {
            "country": geo["country"],
            "timestamp": now_str,
            "lat": geo.get("lat"),
            "lng": geo.get("lng")
        }
    return event


def dispatch_webhook(event):
    """
    Simulates sending a Slack webhook notification for CRITICAL severity alerts.
    """
    severity = event.get("severity", "LOW")
    if severity == "CRITICAL":
        event_type = event.get("event_type")
        risk = event.get("risk_score")
        user = event.get("user")
        src_ip = event.get("src_ip")

        slack_payload = {
            "text": f"🚨 *CRITICAL ALERT DETECTED* 🚨\n"
                    f"*Type:* `{event_type}`\n"
                    f"*Risk Score:* `{risk}`/100\n"
                    f"*Source IP:* `{src_ip}`\n"
                    f"*Target User:* `{user}`\n"
                    f"*Raw Log:* `{event.get('raw_log')}`"
        }
        logger.info(f"[Slack Webhook Sim] Dispatching notification payload:\n{slack_payload['text']}")


async def process_event(event, anomaly_detector, mitre_mapper, summarizer, risk_scorer):
    """
    Run a single event through the full ML pipeline.

    Pipeline: event → anomaly score → MITRE map → LLM summary → risk score

    Returns the enriched event dict ready for MongoDB insertion.
    """
    # Run Impossible Travel rule check
    event = check_impossible_travel(event)

    # 1. Anomaly Detection
    anomaly_score = anomaly_detector.score(event)
    event["anomaly_score"] = anomaly_score

    # 2. MITRE ATT&CK Mapping
    mitre = mitre_mapper.map_event(event)
    event["mitre"] = mitre

    # 3. AI Summary
    summary = summarizer.summarize(event)
    event["ai_summary"] = summary

    # 4. Risk Scoring
    risk = risk_scorer.score(event, anomaly_score)
    event["risk_score"] = risk["risk_score"]
    event["risk_label"] = risk["risk_label"]
    event["cvss_base"] = risk["cvss_base"]
    event["asset_criticality"] = risk["asset_criticality"]

    # Dispatch simulated Slack Webhook for Critical alerts
    dispatch_webhook(event)

    return event

```


---

### 📄 File: `backend/services/websocket_manager.py`
**Purpose:** Active connection tracking manager for real-time alert broadcasts.  
**Size:** 1,702 bytes

```python
"""
WebSocket Connection Manager.
Handles multiple client connections and broadcasts new alerts in real time.
"""

from fastapi import WebSocket
import json


class ConnectionManager:
    """Manages WebSocket connections for real-time alert streaming."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected client."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, data: dict):
        """Send data to all connected clients."""
        if not self.active_connections:
            return

        message = json.dumps(data, default=str)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)

        # Clean up broken connections
        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal(self, websocket: WebSocket, data: dict):
        """Send data to a specific client."""
        try:
            message = json.dumps(data, default=str)
            await websocket.send_text(message)
        except Exception:
            self.disconnect(websocket)

```


---

### 📄 File: `frontend/.gitignore`
**Purpose:** Source code/configuration resource.  
**Size:** 253 bytes

```python
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

```


---

### 📄 File: `frontend/README.md`
**Purpose:** Source code/configuration resource.  
**Size:** 1,027 bytes

```markdown
# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

```


---

### 📄 File: `frontend/eslint.config.js`
**Purpose:** Linter settings for React codebase.  
**Size:** 568 bytes

```javascript
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
  },
])

```


---

### 📄 File: `frontend/index.html`
**Purpose:** Main entry point page loading stylesheet headers and React root elements.  
**Size:** 1,217 bytes

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🛡️</text></svg>" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="AI-Powered Cybersecurity Security Operations Center Analyst Dashboard. Real-time threat detection, anomaly scoring, and automated MITRE ATT&CK mapping." />
    <title>Zenith SOC // Analyst Command Center</title>
    <!-- Google Fonts: Inter for UI, Orbitron for futuristic numbers and cyber HUD headers -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Orbitron:wght@400;500;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
  </head>
  <body class="bg-[#030712] text-[#e5e7eb] font-sans antialiased overflow-x-hidden">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>

```


---

### 📄 File: `frontend/package.json`
**Purpose:** Source code/configuration resource.  
**Size:** 750 bytes

```json
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.16.1",
    "lucide-react": "^1.16.0",
    "react": "^19.2.6",
    "react-dom": "^19.2.6",
    "recharts": "^3.8.1",
    "tailwindcss": "^4.3.0"
  },
  "devDependencies": {
    "@eslint/js": "^10.0.1",
    "@tailwindcss/vite": "^4.3.0",
    "@types/react": "^19.2.14",
    "@types/react-dom": "^19.2.3",
    "@vitejs/plugin-react": "^6.0.1",
    "eslint": "^10.3.0",
    "eslint-plugin-react-hooks": "^7.1.1",
    "eslint-plugin-react-refresh": "^0.5.2",
    "globals": "^17.6.0",
    "vite": "^8.0.12"
  }
}

```


---

### 📄 File: `frontend/public/favicon.svg`
**Purpose:** Source code/configuration resource.  
**Size:** 9,522 bytes

```python
<svg xmlns="http://www.w3.org/2000/svg" width="48" height="46" fill="none" viewBox="0 0 48 46"><path fill="#863bff" d="M25.946 44.938c-.664.845-2.021.375-2.021-.698V33.937a2.26 2.26 0 0 0-2.262-2.262H10.287c-.92 0-1.456-1.04-.92-1.788l7.48-10.471c1.07-1.497 0-3.578-1.842-3.578H1.237c-.92 0-1.456-1.04-.92-1.788L10.013.474c.214-.297.556-.474.92-.474h28.894c.92 0 1.456 1.04.92 1.788l-7.48 10.471c-1.07 1.498 0 3.579 1.842 3.579h11.377c.943 0 1.473 1.088.89 1.83L25.947 44.94z" style="fill:#863bff;fill:color(display-p3 .5252 .23 1);fill-opacity:1"/><mask id="a" width="48" height="46" x="0" y="0" maskUnits="userSpaceOnUse" style="mask-type:alpha"><path fill="#000" d="M25.842 44.938c-.664.844-2.021.375-2.021-.698V33.937a2.26 2.26 0 0 0-2.262-2.262H10.183c-.92 0-1.456-1.04-.92-1.788l7.48-10.471c1.07-1.498 0-3.579-1.842-3.579H1.133c-.92 0-1.456-1.04-.92-1.787L9.91.473c.214-.297.556-.474.92-.474h28.894c.92 0 1.456 1.04.92 1.788l-7.48 10.471c-1.07 1.498 0 3.578 1.842 3.578h11.377c.943 0 1.473 1.088.89 1.832L25.843 44.94z" style="fill:#000;fill-opacity:1"/></mask><g mask="url(#a)"><g filter="url(#b)"><ellipse cx="5.508" cy="14.704" fill="#ede6ff" rx="5.508" ry="14.704" style="fill:#ede6ff;fill:color(display-p3 .9275 .9033 1);fill-opacity:1" transform="matrix(.00324 1 1 -.00324 -4.47 31.516)"/></g><g filter="url(#c)"><ellipse cx="10.399" cy="29.851" fill="#ede6ff" rx="10.399" ry="29.851" style="fill:#ede6ff;fill:color(display-p3 .9275 .9033 1);fill-opacity:1" transform="matrix(.00324 1 1 -.00324 -39.328 7.883)"/></g><g filter="url(#d)"><ellipse cx="5.508" cy="30.487" fill="#7e14ff" rx="5.508" ry="30.487" style="fill:#7e14ff;fill:color(display-p3 .4922 .0767 1);fill-opacity:1" transform="rotate(89.814 -25.913 -14.639)scale(1 -1)"/></g><g filter="url(#e)"><ellipse cx="5.508" cy="30.599" fill="#7e14ff" rx="5.508" ry="30.599" style="fill:#7e14ff;fill:color(display-p3 .4922 .0767 1);fill-opacity:1" transform="rotate(89.814 -32.644 -3.334)scale(1 -1)"/></g><g filter="url(#f)"><ellipse cx="5.508" cy="30.599" fill="#7e14ff" rx="5.508" ry="30.599" style="fill:#7e14ff;fill:color(display-p3 .4922 .0767 1);fill-opacity:1" transform="matrix(.00324 1 1 -.00324 -34.34 30.47)"/></g><g filter="url(#g)"><ellipse cx="14.072" cy="22.078" fill="#ede6ff" rx="14.072" ry="22.078" style="fill:#ede6ff;fill:color(display-p3 .9275 .9033 1);fill-opacity:1" transform="rotate(93.35 24.506 48.493)scale(-1 1)"/></g><g filter="url(#h)"><ellipse cx="3.47" cy="21.501" fill="#7e14ff" rx="3.47" ry="21.501" style="fill:#7e14ff;fill:color(display-p3 .4922 .0767 1);fill-opacity:1" transform="rotate(89.009 28.708 47.59)scale(-1 1)"/></g><g filter="url(#i)"><ellipse cx="3.47" cy="21.501" fill="#7e14ff" rx="3.47" ry="21.501" style="fill:#7e14ff;fill:color(display-p3 .4922 .0767 1);fill-opacity:1" transform="rotate(89.009 28.708 47.59)scale(-1 1)"/></g><g filter="url(#j)"><ellipse cx=".387" cy="8.972" fill="#7e14ff" rx="4.407" ry="29.108" style="fill:#7e14ff;fill:color(display-p3 .4922 .0767 1);fill-opacity:1" transform="rotate(39.51 .387 8.972)"/></g><g filter="url(#k)"><ellipse cx="47.523" cy="-6.092" fill="#7e14ff" rx="4.407" ry="29.108" style="fill:#7e14ff;fill:color(display-p3 .4922 .0767 1);fill-opacity:1" transform="rotate(37.892 47.523 -6.092)"/></g><g filter="url(#l)"><ellipse cx="41.412" cy="6.333" fill="#47bfff" rx="5.971" ry="9.665" style="fill:#47bfff;fill:color(display-p3 .2799 .748 1);fill-opacity:1" transform="rotate(37.892 41.412 6.333)"/></g><g filter="url(#m)"><ellipse cx="-1.879" cy="38.332" fill="#7e14ff" rx="4.407" ry="29.108" style="fill:#7e14ff;fill:color(display-p3 .4922 .0767 1);fill-opacity:1" transform="rotate(37.892 -1.88 38.332)"/></g><g filter="url(#n)"><ellipse cx="-1.879" cy="38.332" fill="#7e14ff" rx="4.407" ry="29.108" style="fill:#7e14ff;fill:color(display-p3 .4922 .0767 1);fill-opacity:1" transform="rotate(37.892 -1.88 38.332)"/></g><g filter="url(#o)"><ellipse cx="35.651" cy="29.907" fill="#7e14ff" rx="4.407" ry="29.108" style="fill:#7e14ff;fill:color(display-p3 .4922 .0767 1);fill-opacity:1" transform="rotate(37.892 35.651 29.907)"/></g><g filter="url(#p)"><ellipse cx="38.418" cy="32.4" fill="#47bfff" rx="5.971" ry="15.297" style="fill:#47bfff;fill:color(display-p3 .2799 .748 1);fill-opacity:1" transform="rotate(37.892 38.418 32.4)"/></g></g><defs><filter id="b" width="60.045" height="41.654" x="-19.77" y="16.149" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="7.659"/></filter><filter id="c" width="90.34" height="51.437" x="-54.613" y="-7.533" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="7.659"/></filter><filter id="d" width="79.355" height="29.4" x="-49.64" y="2.03" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/></filter><filter id="e" width="79.579" height="29.4" x="-45.045" y="20.029" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/></filter><filter id="f" width="79.579" height="29.4" x="-43.513" y="21.178" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/></filter><filter id="g" width="74.749" height="58.852" x="15.756" y="-17.901" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="7.659"/></filter><filter id="h" width="61.377" height="25.362" x="23.548" y="2.284" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/></filter><filter id="i" width="61.377" height="25.362" x="23.548" y="2.284" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/></filter><filter id="j" width="56.045" height="63.649" x="-27.636" y="-22.853" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/></filter><filter id="k" width="54.814" height="64.646" x="20.116" y="-38.415" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/></filter><filter id="l" width="33.541" height="35.313" x="24.641" y="-11.323" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/></filter><filter id="m" width="54.814" height="64.646" x="-29.286" y="6.009" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/></filter><filter id="n" width="54.814" height="64.646" x="-29.286" y="6.009" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/></filter><filter id="o" width="54.814" height="64.646" x="8.244" y="-2.416" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/></filter><filter id="p" width="39.409" height="43.623" x="18.713" y="10.588" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/></filter></defs></svg>
```


---

### 📄 File: `frontend/public/icons.svg`
**Purpose:** Source code/configuration resource.  
**Size:** 5,031 bytes

```python
<svg xmlns="http://www.w3.org/2000/svg">
  <symbol id="bluesky-icon" viewBox="0 0 16 17">
    <g clip-path="url(#bluesky-clip)"><path fill="#08060d" d="M7.75 7.735c-.693-1.348-2.58-3.86-4.334-5.097-1.68-1.187-2.32-.981-2.74-.79C.188 2.065.1 2.812.1 3.251s.241 3.602.398 4.13c.52 1.744 2.367 2.333 4.07 2.145-2.495.37-4.71 1.278-1.805 4.512 3.196 3.309 4.38-.71 4.987-2.746.608 2.036 1.307 5.91 4.93 2.746 2.72-2.746.747-4.143-1.747-4.512 1.702.189 3.55-.4 4.07-2.145.156-.528.397-3.691.397-4.13s-.088-1.186-.575-1.406c-.42-.19-1.06-.395-2.741.79-1.755 1.24-3.64 3.752-4.334 5.099"/></g>
    <defs><clipPath id="bluesky-clip"><path fill="#fff" d="M.1.85h15.3v15.3H.1z"/></clipPath></defs>
  </symbol>
  <symbol id="discord-icon" viewBox="0 0 20 19">
    <path fill="#08060d" d="M16.224 3.768a14.5 14.5 0 0 0-3.67-1.153c-.158.286-.343.67-.47.976a13.5 13.5 0 0 0-4.067 0c-.128-.306-.317-.69-.476-.976A14.4 14.4 0 0 0 3.868 3.77C1.546 7.28.916 10.703 1.231 14.077a14.7 14.7 0 0 0 4.5 2.306q.545-.748.965-1.587a9.5 9.5 0 0 1-1.518-.74q.191-.14.372-.293c2.927 1.369 6.107 1.369 8.999 0q.183.152.372.294-.723.437-1.52.74.418.838.963 1.588a14.6 14.6 0 0 0 4.504-2.308c.37-3.911-.63-7.302-2.644-10.309m-9.13 8.234c-.878 0-1.599-.82-1.599-1.82 0-.998.705-1.82 1.6-1.82.894 0 1.614.82 1.599 1.82.001 1-.705 1.82-1.6 1.82m5.91 0c-.878 0-1.599-.82-1.599-1.82 0-.998.705-1.82 1.6-1.82.893 0 1.614.82 1.599 1.82 0 1-.706 1.82-1.6 1.82"/>
  </symbol>
  <symbol id="documentation-icon" viewBox="0 0 21 20">
    <path fill="none" stroke="#aa3bff" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.35" d="m15.5 13.333 1.533 1.322c.645.555.967.833.967 1.178s-.322.623-.967 1.179L15.5 18.333m-3.333-5-1.534 1.322c-.644.555-.966.833-.966 1.178s.322.623.966 1.179l1.534 1.321"/>
    <path fill="none" stroke="#aa3bff" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.35" d="M17.167 10.836v-4.32c0-1.41 0-2.117-.224-2.68-.359-.906-1.118-1.621-2.08-1.96-.599-.21-1.349-.21-2.848-.21-2.623 0-3.935 0-4.983.369-1.684.591-3.013 1.842-3.641 3.428C3 6.449 3 7.684 3 10.154v2.122c0 2.558 0 3.838.706 4.726q.306.383.713.671c.76.536 1.79.64 3.581.66"/>
    <path fill="none" stroke="#aa3bff" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.35" d="M3 10a2.78 2.78 0 0 1 2.778-2.778c.555 0 1.209.097 1.748-.047.48-.129.854-.503.982-.982.145-.54.048-1.194.048-1.749a2.78 2.78 0 0 1 2.777-2.777"/>
  </symbol>
  <symbol id="github-icon" viewBox="0 0 19 19">
    <path fill="#08060d" fill-rule="evenodd" d="M9.356 1.85C5.05 1.85 1.57 5.356 1.57 9.694a7.84 7.84 0 0 0 5.324 7.44c.387.079.528-.168.528-.376 0-.182-.013-.805-.013-1.454-2.165.467-2.616-.935-2.616-.935-.349-.91-.864-1.143-.864-1.143-.71-.48.051-.48.051-.48.787.051 1.2.805 1.2.805.695 1.194 1.817.857 2.268.649.064-.507.27-.857.49-1.052-1.728-.182-3.545-.857-3.545-3.87 0-.857.31-1.558.8-2.104-.078-.195-.349-1 .077-2.078 0 0 .657-.208 2.14.805a7.5 7.5 0 0 1 1.946-.26c.657 0 1.328.092 1.946.26 1.483-1.013 2.14-.805 2.14-.805.426 1.078.155 1.883.078 2.078.502.546.799 1.247.799 2.104 0 3.013-1.818 3.675-3.558 3.87.284.247.528.714.528 1.454 0 1.052-.012 1.896-.012 2.156 0 .208.142.455.528.377a7.84 7.84 0 0 0 5.324-7.441c.013-4.338-3.48-7.844-7.773-7.844" clip-rule="evenodd"/>
  </symbol>
  <symbol id="social-icon" viewBox="0 0 20 20">
    <path fill="none" stroke="#aa3bff" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.35" d="M12.5 6.667a4.167 4.167 0 1 0-8.334 0 4.167 4.167 0 0 0 8.334 0"/>
    <path fill="none" stroke="#aa3bff" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.35" d="M2.5 16.667a5.833 5.833 0 0 1 8.75-5.053m3.837.474.513 1.035c.07.144.257.282.414.309l.93.155c.596.1.736.536.307.965l-.723.73a.64.64 0 0 0-.152.531l.207.903c.164.715-.213.991-.84.618l-.872-.52a.63.63 0 0 0-.577 0l-.872.52c-.624.373-1.003.094-.84-.618l.207-.903a.64.64 0 0 0-.152-.532l-.723-.729c-.426-.43-.289-.864.306-.964l.93-.156a.64.64 0 0 0 .412-.31l.513-1.034c.28-.562.735-.562 1.012 0"/>
  </symbol>
  <symbol id="x-icon" viewBox="0 0 19 19">
    <path fill="#08060d" fill-rule="evenodd" d="M1.893 1.98c.052.072 1.245 1.769 2.653 3.77l2.892 4.114c.183.261.333.48.333.486s-.068.089-.152.183l-.522.593-.765.867-3.597 4.087c-.375.426-.734.834-.798.905a1 1 0 0 0-.118.148c0 .01.236.017.664.017h.663l.729-.83c.4-.457.796-.906.879-.999a692 692 0 0 0 1.794-2.038c.034-.037.301-.34.594-.675l.551-.624.345-.392a7 7 0 0 1 .34-.374c.006 0 .93 1.306 2.052 2.903l2.084 2.965.045.063h2.275c1.87 0 2.273-.003 2.266-.021-.008-.02-1.098-1.572-3.894-5.547-2.013-2.862-2.28-3.246-2.273-3.266.008-.019.282-.332 2.085-2.38l2-2.274 1.567-1.782c.022-.028-.016-.03-.65-.03h-.674l-.3.342a871 871 0 0 1-1.782 2.025c-.067.075-.405.458-.75.852a100 100 0 0 1-.803.91c-.148.172-.299.344-.99 1.127-.304.343-.32.358-.345.327-.015-.019-.904-1.282-1.976-2.808L6.365 1.85H1.8zm1.782.91 8.078 11.294c.772 1.08 1.413 1.973 1.425 1.984.016.017.241.02 1.05.017l1.03-.004-2.694-3.766L7.796 5.75 5.722 2.852l-1.039-.004-1.039-.004z" clip-rule="evenodd"/>
  </symbol>
</svg>

```


---

### 📄 File: `frontend/src/App.css`
**Purpose:** Custom layout overrides.  
**Size:** 47 bytes

```css
/* App-specific custom css overrides if any */

```


---

### 📄 File: `frontend/src/App.jsx`
**Purpose:** Primary frontend orchestrator handling tabs, real-time WebSockets, and state sync.  
**Size:** 18,920 bytes

```javascript
import React, { useState, useEffect, useCallback } from 'react';
import DashboardHeader from './components/DashboardHeader';
import OverviewCards from './components/OverviewCards';
import AnalyticsCharts from './components/AnalyticsCharts';
import ThreatHotspots from './components/ThreatHotspots';
import AlertsTable from './components/AlertsTable';
import AlertDetailSidebar from './components/AlertDetailSidebar';
import AICopilot from './components/AICopilot';
import SOARAuditLogs from './components/SOARAuditLogs';
import {
  getOverview,
  getSeverityDistribution,
  getTimeline,
  getTopSources,
  getGeoData,
  getAlerts,
  getAlertDetail,
  respondToAlert,
  sendChatMessage,
  trainModel,
  verifyAlert,
} from './utils/api';
import { Shield, TrendingUp, Cpu, X, BookOpen, AlertOctagon, Terminal } from 'lucide-react';
import './App.css';

function App() {
  // Navigation active tab
  const [activeTab, setActiveTab] = useState('triage'); // 'triage', 'analytics', 'copilot'

  // Real-time Feed & Pagination States
  const [alerts, setAlerts] = useState([]);
  const [totalAlerts, setTotalAlerts] = useState(0);
  const [page, setPage] = useState(1);
  const [perPage] = useState(15); // Show 15 per page for clean multi-pane layout
  const [filters, setFilters] = useState({
    search: '',
    severity: '',
    eventType: '',
  });

  // Selected Triage Alert & Playbook States
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [isResponding, setIsResponding] = useState(null);
  const [responseLogs, setResponseLogs] = useState({});

  // Analytics & Stats States
  const [stats, setStats] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [severityDist, setSeverityDist] = useState([]);
  const [topSources, setTopSources] = useState([]);
  const [geoData, setGeoData] = useState([]);

  // System status & WebSocket connection
  const [wsStatus, setWsStatus] = useState('disconnected');
  const [systemHealth, setSystemHealth] = useState(null);

  // Chat Copilot States
  const [chatHistory, setChatHistory] = useState([]);
  const [isSendingMessage, setIsSendingMessage] = useState(false);

  // 1. Fetch initial statistics and analytics charts
  const fetchDashboardStats = useCallback(async () => {
    try {
      const [overviewData, sevData, timeData, srcData, mapData] = await Promise.all([
        getOverview(),
        getSeverityDistribution(),
        getTimeline(),
        getTopSources(),
        getGeoData(),
      ]);
      setStats(overviewData);
      setSeverityDist(sevData.distribution);
      setTimeline(timeData.timeline);
      setTopSources(srcData.sources);
      setGeoData(mapData.geo_threats);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
    }
  }, []);

  // 2. Fetch paginated alerts list based on page/filters
  const fetchAlertsList = useCallback(async () => {
    try {
      const params = {
        page,
        per_page: perPage,
        severity: filters.severity || undefined,
        event_type: filters.eventType || undefined,
      };
      
      const data = await getAlerts(params);
      
      // Client-side local filtering for search query to make search instantaneous
      let fetchedAlerts = data.alerts;
      if (filters.search) {
        const query = filters.search.toLowerCase();
        fetchedAlerts = fetchedAlerts.filter(
          (alert) =>
            alert.src_ip?.toLowerCase().includes(query) ||
            alert.dest_ip?.toLowerCase().includes(query) ||
            alert.user?.toLowerCase().includes(query) ||
            alert.event_type?.toLowerCase().includes(query) ||
            alert.raw_log?.toLowerCase().includes(query)
        );
      }
      
      setAlerts(fetchedAlerts);
      setTotalAlerts(data.total);
    } catch (err) {
      console.error('Error loading alerts list:', err);
    }
  }, [page, perPage, filters]);

  // Load server status & system config initially
  const fetchSystemHealth = async () => {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        setSystemHealth(data);
      }
    } catch (err) {
      console.error('System health check failed:', err);
      setSystemHealth({ status: 'offline', service: 'SOC API unreachable' });
    }
  };

  // Sync initial render parameters
  useEffect(() => {
    fetchSystemHealth();
    fetchDashboardStats();
  }, [fetchDashboardStats]);

  // Sync alerts when page or filters change
  useEffect(() => {
    fetchAlertsList();
  }, [fetchAlertsList]);

  // 3. Connect to real-time WebSocket threat stream
  useEffect(() => {
    let socket = null;
    let reconnectTimeout = null;

    const connectWS = () => {
      setWsStatus('connecting');
      // Create WebSocket URI relative to hostname
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws`;
      
      socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        console.log('[WebSocket] Connection established.');
        setWsStatus('connected');
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          
          if (payload.type === 'NEW_ALERT') {
            const newAlert = payload.data;
            
            // Append visual glow attribute
            newAlert.isNew = true;

            // Prepend new alert to alerts list (only if it fits current filters / page 1)
            setAlerts((prev) => {
              const filtered = prev.filter((a) => a.id !== newAlert.id);
              const updated = [newAlert, ...filtered.slice(0, perPage - 1)];
              return updated;
            });
            setTotalAlerts((prev) => prev + 1);

            // Re-sync counters and charts automatically to display live changes
            fetchDashboardStats();

            // Clear glow highlight after 4 seconds
            setTimeout(() => {
              setAlerts((prev) =>
                prev.map((a) => (a.id === newAlert.id ? { ...a, isNew: false } : a))
              );
            }, 4000);
          }
        } catch (e) {
          // Ignores text responses like echoes
        }
      };

      socket.onclose = () => {
        console.warn('[WebSocket] Connection dropped. Reconnecting in 3 seconds...');
        setWsStatus('disconnected');
        reconnectTimeout = setTimeout(connectWS, 3000);
      };

      socket.onerror = (err) => {
        console.error('[WebSocket] Error caught:', err);
        socket.close();
      };
    };

    connectWS();

    return () => {
      if (socket) {
        socket.onclose = null;
        socket.onerror = null;
        socket.close();
      }
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, [perPage, fetchDashboardStats]);

  // 4. Alert detail selection handler
  const handleAlertSelect = async (alertSummary) => {
    try {
      const detail = await getAlertDetail(alertSummary.id);
      setSelectedAlert(detail);
    } catch (err) {
      console.error('Error fetching alert details:', err);
      // Fallback to list details if server fails
      setSelectedAlert(alertSummary);
    }
  };

  // 5. Automated incident response action trigger
  const handleRespondAction = async (action) => {
    if (!selectedAlert) return;
    setIsResponding(action);
    try {
      const result = await respondToAlert(selectedAlert.id, action);
      
      // Save result in execution log dictionary
      setResponseLogs((prev) => ({
        ...prev,
        [selectedAlert.id]: result,
      }));
      
      // Reload details to capture updated auto-response fields
      const updatedDetail = await getAlertDetail(selectedAlert.id);
      setSelectedAlert(updatedDetail);
    } catch (err) {
      console.error('Playbook execution failed:', err);
    } finally {
      setIsResponding(null);
    }
  };

  // 6. RAG AI Copilot communication handler
  const handleSendChatMessage = async (msgText) => {
    if (!msgText.trim()) return;
    
    // Push user message to history
    const userMsg = { sender: 'user', text: msgText };
    setChatHistory((prev) => [...prev, userMsg]);
    setIsSendingMessage(true);

    try {
      const res = await sendChatMessage(msgText);
      const botMsg = {
        sender: 'bot',
        text: res.response,
        context_alerts_used: res.context_alerts_used,
      };
      setChatHistory((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error('AI chat copilot error:', err);
      setChatHistory((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: 'I apologize, but I encountered an error communicating with the Zenith AI orchestrator core.',
        },
      ]);
    } finally {
      setIsSendingMessage(false);
    }
  };

  // Handle manual dashboard data refresh
  const handleManualRefresh = () => {
    fetchSystemHealth();
    fetchDashboardStats();
    fetchAlertsList();
  };

  const handleTrainModel = async () => {
    try {
      const data = await trainModel();
      fetchSystemHealth();
      fetchDashboardStats();
      fetchAlertsList();
      return data;
    } catch (err) {
      console.error('Error training model:', err);
      return { success: false, message: 'API error occurred.' };
    }
  };

  const handleVerifyAlert = async (alertId, status) => {
    try {
      const res = await verifyAlert(alertId, status);
      if (res && res.success) {
        setSelectedAlert((prev) => {
          if (prev && prev.id === alertId) {
            return { ...prev, analyst_verification: status };
          }
          return prev;
        });
        setAlerts((prev) =>
          prev.map((a) => (a.id === alertId ? { ...a, analyst_verification: status } : a))
        );
      }
    } catch (err) {
      console.error('Error verifying alert:', err);
    }
  };

  const handlePreCannedPromptClick = (promptText) => {
    handleSendChatMessage(promptText);
  };

  return (
    <div className="min-h-screen bg-cyber-bg cyber-grid-bg text-zinc-200 font-sans flex flex-col antialiased">
      {/* ── HUD Header ── */}
      <DashboardHeader
        wsStatus={wsStatus}
        systemHealth={systemHealth}
        onRefresh={handleManualRefresh}
        onTrainModel={handleTrainModel}
      />

      {/* ── Modern Segmented Navigation Tabs ── */}
      <div className="px-6 py-3 border-b border-zinc-800 bg-zinc-950/80 flex flex-wrap gap-2 text-xs z-10">
        <div className="flex bg-zinc-900/60 p-1 rounded-lg border border-zinc-800/80">
          <button
            onClick={() => setActiveTab('triage')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-md transition-all font-medium cursor-pointer ${
              activeTab === 'triage'
                ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Shield className="w-3.5 h-3.5" />
            Incident Triage
          </button>

          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-md transition-all font-medium cursor-pointer ${
              activeTab === 'analytics'
                ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <TrendingUp className="w-3.5 h-3.5" />
            Analytics & Trends
          </button>

          <button
            onClick={() => setActiveTab('copilot')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-md transition-all font-medium cursor-pointer ${
              activeTab === 'copilot'
                ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Cpu className="w-3.5 h-3.5" />
            AI Copilot Lab
          </button>

          <button
            onClick={() => setActiveTab('audit')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-md transition-all font-medium cursor-pointer ${
              activeTab === 'audit'
                ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            SOAR Audit Trail
          </button>
        </div>
      </div>

      {/* ── Active View Rendering ── */}
      {activeTab === 'triage' && (
        <main className="flex-grow px-6 py-6 grid grid-cols-1 xl:grid-cols-12 gap-6 min-h-0">
          {/* Column 1: Live Alert Feed (Col-span 8) */}
          <div className="xl:col-span-8 flex flex-col min-h-0">
            <AlertsTable
              alerts={alerts}
              total={totalAlerts}
              page={page}
              perPage={perPage}
              filters={filters}
              onFilterChange={(newFilters) => {
                setFilters(newFilters);
                setPage(newFilters.page || 1);
              }}
              onAlertSelect={handleAlertSelect}
              selectedAlertId={selectedAlert?.id}
            />
          </div>

          {/* Column 2: Threat Map OR Incident Playbook Inspector (Col-span 4) */}
          <div className="xl:col-span-4 flex flex-col min-h-0">
            {selectedAlert ? (
              <AlertDetailSidebar
                alert={selectedAlert}
                onRespond={handleRespondAction}
                responseLogs={responseLogs}
                isResponding={isResponding}
                onClose={() => setSelectedAlert(null)}
                onVerifyAlert={handleVerifyAlert}
              />
            ) : (
              <div className="flex flex-col h-full gap-6">
                <ThreatHotspots geoData={geoData} />
                
                <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-6 flex flex-col items-center justify-center text-center gap-3 py-8">
                  <Shield className="w-6 h-6 text-emerald-500/80" />
                  <h3 className="text-sm font-semibold text-zinc-200 tracking-wide">Zenith Telemetry Active</h3>
                  <p className="text-xs text-zinc-400 max-w-[280px] leading-relaxed">
                    Live security incident streaming is running. Click any alert row on the left to analyze payloads, map MITRE ATT&CK vectors, and execute mitigation playbooks.
                  </p>
                </div>
              </div>
            )}
          </div>
        </main>
      )}

      {activeTab === 'analytics' && (
        <main className="flex-grow flex flex-col py-2 min-h-0">
          {/* Overview KPI Cards */}
          <OverviewCards stats={stats} />
          
          {/* Charts visualizations */}
          <div className="px-6 pb-6 flex-grow">
            <AnalyticsCharts
              timeline={timeline}
              severity={severityDist}
              sources={topSources}
            />
          </div>
        </main>
      )}

      {activeTab === 'copilot' && (
        <main className="flex-grow px-6 py-6 grid grid-cols-1 xl:grid-cols-12 gap-6 min-h-0">
          {/* Column 1: Zenith Chat Assistant (Col-span 8) */}
          <div className="xl:col-span-8 flex flex-col min-h-[500px]">
            <AICopilot
              onSendMessage={handleSendChatMessage}
              chatHistory={chatHistory}
              isSendingMessage={isSendingMessage}
            />
          </div>

          {/* Column 2: Zenith AI Guide and Cheatsheet (Col-span 4) */}
          <div className="xl:col-span-4 flex flex-col min-h-0 gap-6">
            <div className="glassmorphism rounded-xl border border-cyber-card-border p-5 flex flex-col h-full">
              <div className="flex items-center gap-2 border-b border-cyber-card-border/30 pb-3 mb-4">
                <Terminal className="w-5 h-5 text-cyber-purple animate-pulse" />
                <h2 className="text-sm font-bold font-cyber tracking-wider text-slate-200 uppercase">
                  Zenith AI Copilot Lab
                </h2>
              </div>

              <p className="text-[11px] text-slate-400 font-mono mb-4 leading-relaxed">
                The Zenith AI Copilot leverages large language model (LLM) intelligence to inspect your entire security logs catalog, explain attack methodologies, and design remediation actions.
              </p>

              <div className="flex-1 flex flex-col gap-3 font-mono text-[10px] overflow-y-auto">
                <div className="text-slate-500 font-bold uppercase tracking-wider flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-cyber-blue" />
                  Suggested Threat Queries
                </div>

                {[
                  {
                    label: "Summarize High-Risk Incidents",
                    prompt: "Summarize all high and critical risk alerts currently stored in our system and tell me the primary threat source."
                  },
                  {
                    label: "Identify Malware Activity",
                    prompt: "Have there been any malware detections? Explain their impact and map them to MITRE ATT&CK techniques."
                  },
                  {
                    label: "Investigate SSH Brute Force",
                    prompt: "Review SSH brute force incidents in the logs and write a custom iptables firewall script to block the source IPs."
                  },
                  {
                    label: "Explain System Risk Scoring",
                    prompt: "How does the risk scorer weigh CVSS base metrics versus real-time anomaly scores? Explain in detail."
                  },
                  {
                    label: "Draft Incident Report Summary",
                    prompt: "Write a high-level executive cybersecurity incident summary report for the SOC team covering today's threat landscape."
                  }
                ].map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => handlePreCannedPromptClick(item.prompt)}
                    className="text-left w-full p-2.5 rounded border border-cyber-card-border hover:border-cyber-purple/50 bg-cyber-card/10 hover:bg-cyber-purple/5 text-slate-300 hover:text-white transition-all duration-200"
                  >
                    <div className="font-bold text-[11px] text-cyber-purple uppercase mb-1">{item.label}</div>
                    <div className="text-[10px] text-slate-400 italic line-clamp-2">"{item.prompt}"</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </main>
      )}

      {activeTab === 'audit' && (
        <SOARAuditLogs />
      )}
    </div>
  );
}

export default App;
```


---

### 📄 File: `frontend/src/assets/react.svg`
**Purpose:** Source code/configuration resource.  
**Size:** 4,126 bytes

```python
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" role="img" class="iconify iconify--logos" width="35.93" height="32" preserveAspectRatio="xMidYMid meet" viewBox="0 0 256 228"><path fill="#00D8FF" d="M210.483 73.824a171.49 171.49 0 0 0-8.24-2.597c.465-1.9.893-3.777 1.273-5.621c6.238-30.281 2.16-54.676-11.769-62.708c-13.355-7.7-35.196.329-57.254 19.526a171.23 171.23 0 0 0-6.375 5.848a155.866 155.866 0 0 0-4.241-3.917C100.759 3.829 77.587-4.822 63.673 3.233C50.33 10.957 46.379 33.89 51.995 62.588a170.974 170.974 0 0 0 1.892 8.48c-3.28.932-6.445 1.924-9.474 2.98C17.309 83.498 0 98.307 0 113.668c0 15.865 18.582 31.778 46.812 41.427a145.52 145.52 0 0 0 6.921 2.165a167.467 167.467 0 0 0-2.01 9.138c-5.354 28.2-1.173 50.591 12.134 58.266c13.744 7.926 36.812-.22 59.273-19.855a145.567 145.567 0 0 0 5.342-4.923a168.064 168.064 0 0 0 6.92 6.314c21.758 18.722 43.246 26.282 56.54 18.586c13.731-7.949 18.194-32.003 12.4-61.268a145.016 145.016 0 0 0-1.535-6.842c1.62-.48 3.21-.974 4.76-1.488c29.348-9.723 48.443-25.443 48.443-41.52c0-15.417-17.868-30.326-45.517-39.844Zm-6.365 70.984c-1.4.463-2.836.91-4.3 1.345c-3.24-10.257-7.612-21.163-12.963-32.432c5.106-11 9.31-21.767 12.459-31.957c2.619.758 5.16 1.557 7.61 2.4c23.69 8.156 38.14 20.213 38.14 29.504c0 9.896-15.606 22.743-40.946 31.14Zm-10.514 20.834c2.562 12.94 2.927 24.64 1.23 33.787c-1.524 8.219-4.59 13.698-8.382 15.893c-8.067 4.67-25.32-1.4-43.927-17.412a156.726 156.726 0 0 1-6.437-5.87c7.214-7.889 14.423-17.06 21.459-27.246c12.376-1.098 24.068-2.894 34.671-5.345a134.17 134.17 0 0 1 1.386 6.193ZM87.276 214.515c-7.882 2.783-14.16 2.863-17.955.675c-8.075-4.657-11.432-22.636-6.853-46.752a156.923 156.923 0 0 1 1.869-8.499c10.486 2.32 22.093 3.988 34.498 4.994c7.084 9.967 14.501 19.128 21.976 27.15a134.668 134.668 0 0 1-4.877 4.492c-9.933 8.682-19.886 14.842-28.658 17.94ZM50.35 144.747c-12.483-4.267-22.792-9.812-29.858-15.863c-6.35-5.437-9.555-10.836-9.555-15.216c0-9.322 13.897-21.212 37.076-29.293c2.813-.98 5.757-1.905 8.812-2.773c3.204 10.42 7.406 21.315 12.477 32.332c-5.137 11.18-9.399 22.249-12.634 32.792a134.718 134.718 0 0 1-6.318-1.979Zm12.378-84.26c-4.811-24.587-1.616-43.134 6.425-47.789c8.564-4.958 27.502 2.111 47.463 19.835a144.318 144.318 0 0 1 3.841 3.545c-7.438 7.987-14.787 17.08-21.808 26.988c-12.04 1.116-23.565 2.908-34.161 5.309a160.342 160.342 0 0 1-1.76-7.887Zm110.427 27.268a347.8 347.8 0 0 0-7.785-12.803c8.168 1.033 15.994 2.404 23.343 4.08c-2.206 7.072-4.956 14.465-8.193 22.045a381.151 381.151 0 0 0-7.365-13.322Zm-45.032-43.861c5.044 5.465 10.096 11.566 15.065 18.186a322.04 322.04 0 0 0-30.257-.006c4.974-6.559 10.069-12.652 15.192-18.18ZM82.802 87.83a323.167 323.167 0 0 0-7.227 13.238c-3.184-7.553-5.909-14.98-8.134-22.152c7.304-1.634 15.093-2.97 23.209-3.984a321.524 321.524 0 0 0-7.848 12.897Zm8.081 65.352c-8.385-.936-16.291-2.203-23.593-3.793c2.26-7.3 5.045-14.885 8.298-22.6a321.187 321.187 0 0 0 7.257 13.246c2.594 4.48 5.28 8.868 8.038 13.147Zm37.542 31.03c-5.184-5.592-10.354-11.779-15.403-18.433c4.902.192 9.899.29 14.978.29c5.218 0 10.376-.117 15.453-.343c-4.985 6.774-10.018 12.97-15.028 18.486Zm52.198-57.817c3.422 7.8 6.306 15.345 8.596 22.52c-7.422 1.694-15.436 3.058-23.88 4.071a382.417 382.417 0 0 0 7.859-13.026a347.403 347.403 0 0 0 7.425-13.565Zm-16.898 8.101a358.557 358.557 0 0 1-12.281 19.815a329.4 329.4 0 0 1-23.444.823c-7.967 0-15.716-.248-23.178-.732a310.202 310.202 0 0 1-12.513-19.846h.001a307.41 307.41 0 0 1-10.923-20.627a310.278 310.278 0 0 1 10.89-20.637l-.001.001a307.318 307.318 0 0 1 12.413-19.761c7.613-.576 15.42-.876 23.31-.876H128c7.926 0 15.743.303 23.354.883a329.357 329.357 0 0 1 12.335 19.695a358.489 358.489 0 0 1 11.036 20.54a329.472 329.472 0 0 1-11 20.722Zm22.56-122.124c8.572 4.944 11.906 24.881 6.52 51.026c-.344 1.668-.73 3.367-1.15 5.09c-10.622-2.452-22.155-4.275-34.23-5.408c-7.034-10.017-14.323-19.124-21.64-27.008a160.789 160.789 0 0 1 5.888-5.4c18.9-16.447 36.564-22.941 44.612-18.3ZM128 90.808c12.625 0 22.86 10.235 22.86 22.86s-10.235 22.86-22.86 22.86s-22.86-10.235-22.86-22.86s10.235-22.86 22.86-22.86Z"></path></svg>
```


---

### 📄 File: `frontend/src/assets/vite.svg`
**Purpose:** Source code/configuration resource.  
**Size:** 8,709 bytes

```python
<svg xmlns="http://www.w3.org/2000/svg" width="77" height="47" fill="none" aria-labelledby="vite-logo-title" viewBox="0 0 77 47"><title id="vite-logo-title">Vite</title><style>.parenthesis{fill:#000}@media (prefers-color-scheme:dark){.parenthesis{fill:#fff}}</style><path fill="#9135ff" d="M40.151 45.71c-.663.844-2.02.374-2.02-.699V34.708a2.26 2.26 0 0 0-2.262-2.262H24.493c-.92 0-1.457-1.04-.92-1.788l7.479-10.471c1.07-1.498 0-3.578-1.842-3.578H15.443c-.92 0-1.456-1.04-.92-1.788l9.696-13.576c.213-.297.556-.474.92-.474h28.894c.92 0 1.456 1.04.92 1.788l-7.48 10.472c-1.07 1.497 0 3.578 1.842 3.578h11.376c.944 0 1.474 1.087.89 1.83L40.153 45.712z"/><mask id="a" width="48" height="47" x="14" y="0" maskUnits="userSpaceOnUse" style="mask-type:alpha"><path fill="#000" d="M40.047 45.71c-.663.843-2.02.374-2.02-.699V34.708a2.26 2.26 0 0 0-2.262-2.262H24.389c-.92 0-1.457-1.04-.92-1.788l7.479-10.472c1.07-1.497 0-3.578-1.842-3.578H15.34c-.92 0-1.456-1.04-.92-1.788l9.696-13.575c.213-.297.556-.474.92-.474H53.93c.92 0 1.456 1.04.92 1.788L47.37 13.03c-1.07 1.498 0 3.578 1.842 3.578h11.376c.944 0 1.474 1.088.89 1.831L40.049 45.712z"/></mask><g mask="url(#a)"><g filter="url(#b)"><ellipse cx="5.508" cy="14.704" fill="#eee6ff" rx="5.508" ry="14.704" transform="rotate(269.814 20.96 11.29)scale(-1 1)"/></g><g filter="url(#c)"><ellipse cx="10.399" cy="29.851" fill="#eee6ff" rx="10.399" ry="29.851" transform="rotate(89.814 -16.902 -8.275)scale(1 -1)"/></g><g filter="url(#d)"><ellipse cx="5.508" cy="30.487" fill="#8900ff" rx="5.508" ry="30.487" transform="rotate(89.814 -19.197 -7.127)scale(1 -1)"/></g><g filter="url(#e)"><ellipse cx="5.508" cy="30.599" fill="#8900ff" rx="5.508" ry="30.599" transform="rotate(89.814 -25.928 4.177)scale(1 -1)"/></g><g filter="url(#f)"><ellipse cx="5.508" cy="30.599" fill="#8900ff" rx="5.508" ry="30.599" transform="rotate(89.814 -25.738 5.52)scale(1 -1)"/></g><g filter="url(#g)"><ellipse cx="14.072" cy="22.078" fill="#eee6ff" rx="14.072" ry="22.078" transform="rotate(93.35 31.245 55.578)scale(-1 1)"/></g><g filter="url(#h)"><ellipse cx="3.47" cy="21.501" fill="#8900ff" rx="3.47" ry="21.501" transform="rotate(89.009 35.419 55.202)scale(-1 1)"/></g><g filter="url(#i)"><ellipse cx="3.47" cy="21.501" fill="#8900ff" rx="3.47" ry="21.501" transform="rotate(89.009 35.419 55.202)scale(-1 1)"/></g><g filter="url(#j)"><ellipse cx="14.592" cy="9.743" fill="#8900ff" rx="4.407" ry="29.108" transform="rotate(39.51 14.592 9.743)"/></g><g filter="url(#k)"><ellipse cx="61.728" cy="-5.321" fill="#8900ff" rx="4.407" ry="29.108" transform="rotate(37.892 61.728 -5.32)"/></g><g filter="url(#l)"><ellipse cx="55.618" cy="7.104" fill="#00c2ff" rx="5.971" ry="9.665" transform="rotate(37.892 55.618 7.104)"/></g><g filter="url(#m)"><ellipse cx="12.326" cy="39.103" fill="#8900ff" rx="4.407" ry="29.108" transform="rotate(37.892 12.326 39.103)"/></g><g filter="url(#n)"><ellipse cx="12.326" cy="39.103" fill="#8900ff" rx="4.407" ry="29.108" transform="rotate(37.892 12.326 39.103)"/></g><g filter="url(#o)"><ellipse cx="49.857" cy="30.678" fill="#8900ff" rx="4.407" ry="29.108" transform="rotate(37.892 49.857 30.678)"/></g><g filter="url(#p)"><ellipse cx="52.623" cy="33.171" fill="#00c2ff" rx="5.971" ry="15.297" transform="rotate(37.892 52.623 33.17)"/></g></g><path d="M6.919 0c-9.198 13.166-9.252 33.575 0 46.789h6.215c-9.25-13.214-9.196-33.623 0-46.789zm62.424 0h-6.215c9.198 13.166 9.252 33.575 0 46.789h6.215c9.25-13.214 9.196-33.623 0-46.789" class="parenthesis"/><defs><filter id="b" width="60.045" height="41.654" x="-5.564" y="16.92" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="7.659"/></filter><filter id="c" width="90.34" height="51.437" x="-40.407" y="-6.762" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="7.659"/></filter><filter id="d" width="79.355" height="29.4" x="-35.435" y="2.801" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="4.596"/></filter><filter id="e" width="79.579" height="29.4" x="-30.84" y="20.8" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="4.596"/></filter><filter id="f" width="79.579" height="29.4" x="-29.307" y="21.949" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="4.596"/></filter><filter id="g" width="74.749" height="58.852" x="29.961" y="-17.13" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="7.659"/></filter><filter id="h" width="61.377" height="25.362" x="37.754" y="3.055" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="4.596"/></filter><filter id="i" width="61.377" height="25.362" x="37.754" y="3.055" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="4.596"/></filter><filter id="j" width="56.045" height="63.649" x="-13.43" y="-22.082" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="4.596"/></filter><filter id="k" width="54.814" height="64.646" x="34.321" y="-37.644" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="4.596"/></filter><filter id="l" width="33.541" height="35.313" x="38.847" y="-10.552" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="4.596"/></filter><filter id="m" width="54.814" height="64.646" x="-15.081" y="6.78" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="4.596"/></filter><filter id="n" width="54.814" height="64.646" x="-15.081" y="6.78" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="4.596"/></filter><filter id="o" width="54.814" height="64.646" x="22.45" y="-1.645" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="4.596"/></filter><filter id="p" width="39.409" height="43.623" x="32.919" y="11.36" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse"><feFlood flood-opacity="0" result="BackgroundImageFix"/><feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/><feGaussianBlur result="effect1_foregroundBlur_2002_17286" stdDeviation="4.596"/></filter></defs></svg>

```


---

### 📄 File: `frontend/src/components/AICopilot.jsx`
**Purpose:** Interactive terminal-style AI Copilot widget with formatting logic.  
**Size:** 12,031 bytes

```javascript
import React, { useState, useRef, useEffect } from 'react';
import { Send, Cpu, Terminal, MessageSquare, FileText } from 'lucide-react';

function AICopilot({ onSendMessage, chatHistory, isSendingMessage }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const quickQuestions = [
    'Recommend triage next steps',
    'What is the top threat type?',
    'Any critical alerts in the system?',
    'List all unique attacking IPs',
  ];

  const handleSend = (e) => {
    if (e) e.preventDefault();
    if (!input.trim() || isSendingMessage) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleQuickQuestionClick = (q) => {
    if (isSendingMessage) return;
    onSendMessage(q);
  };

  // Compile history to a markdown report file and download
  const handleExportTranscript = () => {
    if (chatHistory.length === 0) return;

    let mdContent = `# 🛡️ Zenith AI SOC Threat Assessment Report\n`;
    mdContent += `Generated: ${new Date().toLocaleString()}\n`;
    mdContent += `=========================================\n\n`;

    chatHistory.forEach((msg) => {
      const isUser = msg.sender === 'user';
      mdContent += `### 👤 [${isUser ? 'ANALYST QUESTION' : 'ZENITH COPILOT RESPONSE'}]\n`;
      if (!isUser && msg.context_alerts_used > 0) {
        mdContent += `*RAG Security Context Alerts Referenced: ${msg.context_alerts_used}*\n\n`;
      }
      mdContent += `${msg.text}\n\n`;
      mdContent += `---\n\n`;
    });

    const blob = new Blob([mdContent], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `zenith_soc_report_${new Date().toISOString().slice(0, 10)}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Custom Inline Markdown Parser for bolding and inline code
  const parseInlineMarkdown = (inlineText) => {
    // Splits by bold (**text**) and code chips (`code`)
    const regex = /(\*\*.*?\*\*|`.*?`)/g;
    const parts = inlineText.split(regex);

    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={index} className="font-semibold text-zinc-100">
            {part.slice(2, -2)}
          </strong>
        );
      } else if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code
            key={index}
            className="bg-zinc-950 border border-zinc-800 text-purple-400 font-mono text-[10px] px-1 py-0.5 rounded"
          >
            {part.slice(1, -1)}
          </code>
        );
      }
      return part;
    });
  };

  // Custom block-level Markdown formatter
  const renderParsedText = (text) => {
    if (!text) return null;

    // Split text by triple-backtick code blocks
    const parts = text.split(/(```[\s\S]*?```)/g);

    return parts.map((part, index) => {
      if (part.startsWith('```') && part.endsWith('```')) {
        // Find code language and block body
        const match = part.match(/```(\w*)\n([\s\S]*?)```/);
        const lang = match ? match[1] : '';
        const code = match ? match[2] : part.slice(3, -3);

        return (
          <div
            key={index}
            className="my-3 border border-zinc-800 bg-zinc-950/90 rounded-lg p-3 font-mono text-[10px] relative group overflow-x-auto"
          >
            <div className="flex justify-between items-center text-[9px] text-zinc-500 uppercase border-b border-zinc-900 pb-1 mb-2">
              <span>{lang || 'code segment'}</span>
              <button
                onClick={() => navigator.clipboard.writeText(code.trim())}
                className="hover:text-zinc-300 transition-colors cursor-pointer"
                title="Copy code to clipboard"
              >
                Copy Code
              </button>
            </div>
            <pre className="text-emerald-400 whitespace-pre leading-relaxed">{code.trim()}</pre>
          </div>
        );
      } else {
        // Plain paragraphs, list items, and headers
        const lines = part.split('\n');
        return (
          <div key={index} className="space-y-1.5 text-zinc-300 font-sans text-xs">
            {lines.map((line, lineIdx) => {
              const trimmed = line.trim();

              // 1. Level 3 Headers
              if (trimmed.startsWith('###')) {
                return (
                  <h4
                    key={lineIdx}
                    className="text-zinc-100 font-semibold text-[11px] mt-3 mb-1.5 font-sans border-l-2 border-emerald-500 pl-2 uppercase tracking-wide"
                  >
                    {parseInlineMarkdown(trimmed.replace(/^###\s*/, ''))}
                  </h4>
                );
              }

              // 2. Level 2 Headers
              if (trimmed.startsWith('##')) {
                return (
                  <h3
                    key={lineIdx}
                    className="text-white font-bold text-xs mt-4 mb-2 font-sans border-l-2 border-purple-500 pl-2 uppercase tracking-wider"
                  >
                    {parseInlineMarkdown(trimmed.replace(/^##\s*/, ''))}
                  </h3>
                );
              }

              // 3. Bullet list items
              if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
                return (
                  <li key={lineIdx} className="list-disc ml-4 pl-1 text-zinc-300 leading-relaxed">
                    {parseInlineMarkdown(trimmed.replace(/^[-*]\s*/, ''))}
                  </li>
                );
              }

              // 4. Blank lines
              if (trimmed === '') {
                return <div key={lineIdx} className="h-1.5" />;
              }

              // 5. Normal text paragraphs
              return (
                <p key={lineIdx} className="leading-relaxed">
                  {parseInlineMarkdown(line)}
                </p>
              );
            })}
          </div>
        );
      }
    });
  };

  // Scroll chat window to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isSendingMessage]);

  return (
    <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 h-[350px] flex flex-col relative overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-emerald-500" />
          <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">
            Zenith AI Copilot
          </h3>
        </div>
        <div className="flex items-center gap-3">
          {chatHistory.length > 0 && (
            <button
              onClick={handleExportTranscript}
              className="text-[9px] text-zinc-400 hover:text-white border border-zinc-850 hover:border-zinc-700 bg-zinc-950/40 px-2 py-0.5 rounded flex items-center gap-1 cursor-pointer transition-colors"
              title="Download Incident Report"
            >
              <FileText className="w-3 h-3 text-purple-400" />
              Export Report
            </button>
          )}
          <div className="font-mono text-[9px] text-zinc-500">
            Model: Gemini 2.5
          </div>
        </div>
      </div>

      {/* Terminal Message Stream */}
      <div className="flex-1 overflow-y-auto space-y-3 font-mono text-[11px] pr-1 mb-3">
        {chatHistory.length > 0 ? (
          chatHistory.map((msg, index) => {
            const isUser = msg.sender === 'user';
            return (
              <div
                key={index}
                className={`flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}
              >
                <div className="flex items-center gap-1 text-[9px] text-zinc-500 uppercase">
                  <span>{isUser ? 'Analyst' : 'Zenith Copilot'}</span>
                  {!isUser && msg.context_alerts_used > 0 && (
                    <span className="bg-purple-500/10 text-purple-400 border border-purple-500/20 px-1.5 py-0.5 rounded text-[8px]">
                      RAG Context: {msg.context_alerts_used}
                    </span>
                  )}
                </div>
                <div
                  className={`p-2.5 rounded-lg border max-w-[85%] leading-relaxed ${
                    isUser
                      ? 'bg-blue-500/10 border-blue-500/25 text-zinc-200'
                      : 'bg-zinc-900/60 border-zinc-800 text-zinc-300'
                  }`}
                >
                  {isUser ? (
                    msg.text
                  ) : (
                    <div className="whitespace-normal">{renderParsedText(msg.text)}</div>
                  )}
                </div>
              </div>
            );
          })
        ) : (
          <div className="h-full flex flex-col justify-center items-center gap-2 text-zinc-500 text-center font-sans">
            <MessageSquare className="w-5 h-5 text-zinc-600" />
            <div>
              AI Copilot Assistant
              <p className="text-[9px] text-zinc-500 uppercase mt-1">
                Ask about current threat trends, attackers, or playbook suggestions
              </p>
            </div>
          </div>
        )}

        {/* Loading Indicator */}
        {isSendingMessage && (
          <div className="flex flex-col gap-1 items-start">
            <div className="text-[9px] text-zinc-500 uppercase animate-pulse">
              Zenith Copilot typing...
            </div>
            <div className="bg-zinc-900/60 border border-zinc-800 p-2.5 rounded-lg flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce"></span>
              <span
                className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce"
                style={{ animationDelay: '0.2s' }}
              ></span>
              <span
                className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce"
                style={{ animationDelay: '0.4s' }}
              ></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Questions Chips */}
      {chatHistory.length === 0 && !isSendingMessage && (
        <div className="flex flex-wrap gap-1.5 mb-3 font-sans text-[10px] z-10">
          {quickQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleQuickQuestionClick(q)}
              className="bg-zinc-900/60 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 rounded-lg px-2.5 py-1 text-zinc-400 hover:text-white transition-colors cursor-pointer"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Text Input Footer Form */}
      <form onSubmit={handleSend} className="flex gap-2 items-center border-t border-zinc-800/80 pt-3 z-10">
        <span className="text-zinc-500 pl-1">
          <Terminal className="w-4 h-4" />
        </span>
        <input
          type="text"
          placeholder="Ask copilot a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isSendingMessage}
          className="bg-zinc-950/60 border border-zinc-800 text-zinc-300 font-sans text-xs rounded-lg px-3 py-1.5 flex-1 focus:outline-none focus:border-zinc-700 disabled:opacity-40 transition-colors"
        />
        <button
          type="submit"
          disabled={!input.trim() || isSendingMessage}
          className="bg-emerald-600 hover:bg-emerald-500 text-white p-1.5 rounded-lg transition-colors disabled:opacity-30 cursor-pointer"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}

export default AICopilot;

```


---

### 📄 File: `frontend/src/components/AlertDetailSidebar.jsx`
**Purpose:** Incident triage side investigator drawer with playbook controls.  
**Size:** 20,246 bytes

```javascript
import React, { useState } from 'react';
import {
  ShieldAlert,
  Terminal,
  Activity,
  GitPullRequest,
  Clock,
  Play,
  RotateCw,
  X,
  AlertOctagon
} from 'lucide-react';

function AlertDetailSidebar({ alert, onRespond, responseLogs, isResponding, onClose, onVerifyAlert }) {
  const [activeTab, setActiveTab] = useState('triage');
  const [isVerifying, setIsVerifying] = useState(null);

  // Helper to color code severity
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return 'text-rose-400 border-rose-500/20 bg-rose-500/5';
      case 'HIGH':
        return 'text-amber-400 border-amber-500/20 bg-amber-500/5';
      case 'MEDIUM':
        return 'text-blue-400 border-blue-500/20 bg-blue-500/5';
      case 'LOW':
        return 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5';
      default:
        return 'text-zinc-400 border-zinc-700 bg-zinc-800/10';
    }
  };

  const getRiskColor = (score) => {
    if (score > 75) return 'text-rose-400';
    if (score > 50) return 'text-amber-400';
    return 'text-emerald-400';
  };

  return (
    <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-5 flex flex-col h-full">
      {/* 1. Header Details Title */}
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-500/80" />
          <h2 className="text-xs font-semibold tracking-wider text-zinc-100 uppercase">
            Incident Investigator
          </h2>
        </div>
        <div className="flex items-center gap-3">
          <div className="font-mono text-[9px] text-zinc-500">
            ID: {alert ? alert.id?.substring(0, 15) + '...' : 'N/A'}
          </div>
          {alert && onClose && (
            <button
              onClick={onClose}
              className="text-zinc-400 hover:text-rose-400 transition-colors p-1 rounded-lg hover:bg-zinc-800 cursor-pointer"
              title="Close Panel"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {alert ? (
        <div className="flex-1 flex flex-col min-h-0">
          {/* 2. Top Summary Widget */}
          <div className="bg-zinc-900 border border-zinc-800/80 rounded-xl p-4 flex justify-between items-center gap-4 mb-3">
            <div>
              <div className="font-semibold text-zinc-100 text-xs tracking-wide uppercase">
                {alert.event_type}
              </div>
              <div className="text-[10px] text-zinc-400 font-mono mt-1">
                Target Asset: <span className="text-zinc-200 font-semibold">{alert.dest_ip} ({alert.asset_type})</span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-[9px] text-zinc-500 font-mono">RISK SCORE</div>
              <div className={`text-2xl font-bold leading-none tracking-tight ${getRiskColor(alert.risk_score)}`}>
                {alert.risk_score}
              </div>
            </div>
          </div>

          {/* 3. Triage Tabs Navigation */}
          <div className="flex border-b border-zinc-800 mb-3 text-[11px]">
            <button
              onClick={() => setActiveTab('triage')}
              className={`flex-1 py-2 text-center border-b-2 font-medium transition-colors cursor-pointer ${activeTab === 'triage' ? 'border-emerald-500 text-zinc-200 font-semibold' : 'border-transparent text-zinc-500 hover:text-zinc-300'}`}
            >
              Triage
            </button>
            <button
              onClick={() => setActiveTab('mitre')}
              className={`flex-1 py-2 text-center border-b-2 font-medium transition-colors cursor-pointer ${activeTab === 'mitre' ? 'border-emerald-500 text-zinc-200 font-semibold' : 'border-transparent text-zinc-500 hover:text-zinc-300'}`}
            >
              MITRE ATT&CK
            </button>
            <button
              onClick={() => setActiveTab('playbook')}
              className={`flex-1 py-2 text-center border-b-2 font-medium transition-colors cursor-pointer ${activeTab === 'playbook' ? 'border-emerald-500 text-zinc-200 font-semibold' : 'border-transparent text-zinc-500 hover:text-zinc-300'}`}
            >
              Playbook & Actions
            </button>
          </div>

          {/* 4. Tab Contents */}
          <div className="flex-1 overflow-y-auto min-h-0 font-mono text-[11px] pr-1">
            {activeTab === 'triage' && (
              <div className="flex flex-col gap-3">
                {/* AI Summary Card */}
                {alert.ai_summary && (
                  <div className="bg-emerald-950/20 border border-emerald-900/40 rounded-xl p-3">
                    <div className="text-[10px] text-emerald-400 font-semibold mb-1.5 flex items-center gap-1.5">
                      <Activity className="w-3.5 h-3.5" />
                      AI Analysis Summary
                    </div>
                    <p className="text-zinc-300 text-[11px] leading-relaxed font-sans font-normal">
                      {alert.ai_summary}
                    </p>
                  </div>
                )}

                {/* Incident Classification feedback loop */}
                <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3 flex flex-col gap-2">
                  <div className="text-[10px] text-zinc-400 font-semibold uppercase tracking-wide">
                    Incident Classification
                  </div>
                  {alert.analyst_verification ? (
                    <div className={`text-center py-1.5 px-3 rounded-lg border text-[10px] font-semibold tracking-wide ${
                      alert.analyst_verification === 'TRUE_POSITIVE'
                        ? 'bg-emerald-950/30 border-emerald-500/50 text-emerald-400'
                        : 'bg-rose-950/30 border-rose-500/50 text-rose-400'
                    }`}>
                      VERIFIED: {alert.analyst_verification.replace('_', ' ')}
                    </div>
                  ) : (
                    <div className="flex gap-2">
                      <button
                        onClick={async () => {
                          if (onVerifyAlert) {
                            setIsVerifying('TRUE_POSITIVE');
                            await onVerifyAlert(alert.id, 'TRUE_POSITIVE');
                            setIsVerifying(null);
                          }
                        }}
                        disabled={isVerifying !== null}
                        className="flex-1 bg-emerald-950/20 hover:bg-emerald-900/30 border border-emerald-900/30 hover:border-emerald-700/80 text-emerald-300 font-semibold py-1.5 rounded-lg text-[10px] transition-colors disabled:opacity-40 cursor-pointer text-center"
                      >
                        {isVerifying === 'TRUE_POSITIVE' ? 'Saving...' : 'True Positive'}
                      </button>
                      <button
                        onClick={async () => {
                          if (onVerifyAlert) {
                            setIsVerifying('FALSE_POSITIVE');
                            await onVerifyAlert(alert.id, 'FALSE_POSITIVE');
                            setIsVerifying(null);
                          }
                        }}
                        disabled={isVerifying !== null}
                        className="flex-1 bg-rose-950/20 hover:bg-rose-900/30 border border-rose-900/30 hover:border-rose-700/80 text-rose-300 font-semibold py-1.5 rounded-lg text-[10px] transition-colors disabled:opacity-40 cursor-pointer text-center"
                      >
                        {isVerifying === 'FALSE_POSITIVE' ? 'Saving...' : 'False Positive'}
                      </button>
                    </div>
                  )}
                </div>

                {/* Score Breakdown telemetry */}
                <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                  <div className="text-[10px] text-zinc-400 font-semibold mb-2.5 uppercase tracking-wide">
                    Risk Assessment Matrix
                  </div>
                  <div className="flex flex-col gap-1.5 text-[10px]">
                    <div className="flex justify-between items-center border-b border-zinc-800/50 pb-1.5">
                      <span className="text-zinc-500">CVSS Base Severity:</span>
                      <span className="text-zinc-200 font-semibold">{alert.cvss_base ?? 'N/A'} / 10</span>
                    </div>
                    <div className="flex justify-between items-center border-b border-zinc-800/50 pb-1.5">
                      <span className="text-zinc-500">Anomaly Engine Score:</span>
                      <span className="text-zinc-200 font-semibold">{(alert.anomaly_score * 100)?.toFixed(1) ?? 'N/A'}%</span>
                    </div>
                    <div className="flex justify-between items-center border-b border-zinc-800/50 pb-1.5">
                      <span className="text-zinc-500">Asset Criticality Factor:</span>
                      <span className="text-zinc-200 font-semibold">{(alert.asset_criticality * 100)?.toFixed(0) ?? 'N/A'}%</span>
                    </div>
                    <div className="flex justify-between items-center pt-0.5">
                      <span className="text-zinc-500">Target IP Host:</span>
                      <span className="text-blue-400 font-semibold">{alert.dest_ip}</span>
                    </div>
                  </div>
                </div>

                {/* Raw security log logs */}
                <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                  <div className="text-[10px] text-zinc-400 font-semibold mb-2.5 flex items-center gap-1">
                    <Terminal className="w-3 h-3 text-zinc-500" />
                    RAW SYSLOG TELEMETRY
                  </div>
                  <pre className="text-[10px] text-zinc-300 whitespace-pre-wrap font-mono leading-relaxed bg-zinc-950/60 p-2 rounded-lg border border-zinc-800/80 max-h-[100px] overflow-y-auto">
                    {alert.raw_log}
                  </pre>
                </div>

                {/* Alert Metadata */}
                <div className="flex justify-between items-center text-[10px] text-zinc-500 px-1">
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Time: {alert.timestamp}</span>
                  </div>
                  <span>User: {alert.user || 'SYSTEM'}</span>
                </div>
              </div>
            )}

            {activeTab === 'mitre' && (
              <div className="flex flex-col gap-3">
                {/* MITRE technique main display */}
                <div className="bg-blue-950/15 border border-blue-900/30 rounded-xl p-4">
                  <div className="flex justify-between items-center border-b border-blue-900/20 pb-2 mb-3">
                    <span className="text-blue-400 font-semibold text-xs flex items-center gap-1.5">
                      <GitPullRequest className="w-3.5 h-3.5" />
                      MITRE ATT&CK Classification
                    </span>
                    <span className="bg-blue-500/10 border border-blue-500/20 text-blue-400 font-semibold text-[10px] px-2 py-0.5 rounded">
                      {alert.mitre?.technique_id || 'N/A'}
                    </span>
                  </div>
                  <div className="flex flex-col gap-3">
                    <div>
                      <div className="text-zinc-500 text-[10px] uppercase font-semibold">Technique Name</div>
                      <div className="text-zinc-200 text-xs font-semibold mt-0.5">
                        {alert.mitre?.technique_name || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-zinc-500 text-[10px] uppercase font-semibold">Attack Tactic</div>
                      <div className="text-amber-400 font-semibold text-xs mt-0.5">
                        {alert.mitre?.tactic || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-zinc-500 text-[10px] uppercase font-semibold">Tactic Description</div>
                      <p className="text-zinc-300 text-xs font-sans mt-1 leading-relaxed">
                        {alert.mitre?.description || 'No mapping description available.'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* MITRE Sub-techniques */}
                {alert.mitre?.sub_techniques && alert.mitre.sub_techniques.length > 0 && (
                  <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                    <div className="text-[10px] text-zinc-400 font-semibold mb-2 uppercase tracking-wide">
                      Targeted Sub-Techniques
                    </div>
                    <div className="flex flex-col gap-1.5">
                      {alert.mitre.sub_techniques.map((sub, idx) => (
                        <div key={idx} className="bg-zinc-950/40 border border-zinc-800/60 rounded-lg p-2 text-[10px] text-zinc-300">
                          {sub}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* LLM ATT&CK Enrichment Description */}
                {alert.mitre?.llm_analysis && (
                  <div className="bg-purple-950/15 border border-purple-900/30 rounded-xl p-3">
                    <div className="text-[10px] text-purple-400 font-semibold mb-1 uppercase">
                      Tactical Analyst Enrichment
                    </div>
                    <p className="text-zinc-300 text-xs italic leading-relaxed font-sans">
                      {alert.mitre.llm_analysis}
                    </p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'playbook' && (
              <div className="flex flex-col gap-3">
                {/* Playbook recommendations */}
                {alert.playbook && (
                  <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                    <div className="flex justify-between items-center border-b border-zinc-800/50 pb-2 mb-2">
                      <span className="font-semibold text-zinc-200 text-xs uppercase">
                        {alert.playbook.name}
                      </span>
                      <span className="text-[9px] text-zinc-500 font-semibold">
                        EST. TIME: {alert.playbook.estimated_time}
                      </span>
                    </div>
                    <div className="flex flex-col gap-2 text-[11px] text-zinc-300 max-h-[140px] overflow-y-auto">
                      {alert.playbook.steps?.map((step, idx) => (
                        <div key={idx} className="leading-relaxed border-b border-zinc-800/40 pb-1.5">
                          {step}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Automated response trigger buttons */}
                <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                  <div className="text-[10px] text-zinc-400 font-semibold mb-3 uppercase tracking-wide">
                    Orchestrated Response Actions
                  </div>
                  <div className="flex flex-col gap-2">
                    <button
                      onClick={() => onRespond('block_ip')}
                      disabled={isResponding}
                      className="bg-rose-950/20 hover:bg-rose-900/30 border border-rose-900/30 hover:border-rose-700/80 text-rose-300 font-semibold py-2 px-3 rounded-lg flex items-center justify-between text-[11px] transition-colors disabled:opacity-40 cursor-pointer"
                    >
                      <span className="flex items-center gap-2">
                        <Play className="w-3.5 h-3.5" />
                        Firewall: Block Attacker IP
                      </span>
                      {isResponding === 'block_ip' && <RotateCw className="w-3.5 h-3.5 animate-spin" />}
                    </button>

                    <button
                      onClick={() => onRespond('quarantine_host')}
                      disabled={isResponding}
                      className="bg-amber-950/20 hover:bg-amber-900/30 border border-amber-900/30 hover:border-amber-700/80 text-amber-300 font-semibold py-2 px-3 rounded-lg flex items-center justify-between text-[11px] transition-colors disabled:opacity-40 cursor-pointer"
                    >
                      <span className="flex items-center gap-2">
                        <Play className="w-3.5 h-3.5" />
                        EDR: Quarantine Host Segment
                      </span>
                      {isResponding === 'quarantine_host' && <RotateCw className="w-3.5 h-3.5 animate-spin" />}
                    </button>

                    <button
                      onClick={() => onRespond('create_ticket')}
                      disabled={isResponding}
                      className="bg-blue-950/20 hover:bg-blue-900/30 border border-blue-900/30 hover:border-blue-700/80 text-blue-300 font-semibold py-2 px-3 rounded-lg flex items-center justify-between text-[11px] transition-colors disabled:opacity-40 cursor-pointer"
                    >
                      <span className="flex items-center gap-2">
                        <Play className="w-3.5 h-3.5" />
                        Jira: Dispatch Ticket (Tier-2)
                      </span>
                      {isResponding === 'create_ticket' && <RotateCw className="w-3.5 h-3.5 animate-spin" />}
                    </button>
                  </div>
                </div>

                {/* Monospace Action Console Output Logs */}
                {responseLogs[alert.id] && (
                  <div className="bg-zinc-950 border border-zinc-800/80 rounded-xl p-3">
                    <div className="text-[10px] text-emerald-400 font-semibold mb-2 flex items-center gap-1.5">
                      <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                      Playbook Execution Log
                    </div>
                    <div className="font-mono text-[9px] leading-relaxed text-zinc-300 max-h-[120px] overflow-y-auto bg-zinc-950/40 p-2 rounded-lg border border-zinc-800/50">
                      <div className="text-emerald-400 font-semibold">
                        &gt; Status: {responseLogs[alert.id].success ? 'SUCCESSFUL' : 'FAILED'}
                      </div>
                      <div className="text-zinc-400 mt-1">&gt; Action: {responseLogs[alert.id].action}</div>
                      <div className="text-zinc-200 mt-1">&gt; Message: {responseLogs[alert.id].message}</div>
                      {responseLogs[alert.id].details && (
                        <div className="text-zinc-500 mt-1 whitespace-pre-wrap">
                          &gt; Details: {JSON.stringify(responseLogs[alert.id].details, null, 2)}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="flex-grow flex flex-col justify-center items-center gap-3 text-zinc-500 font-sans text-xs text-center p-6 border border-dashed border-zinc-800 rounded-xl">
          <AlertOctagon className="w-7 h-7 text-zinc-600 animate-pulse" />
          <div>
            No alert selected for triage
            <p className="text-[10px] text-zinc-500 mt-1.5 uppercase tracking-wide">
              Click an alert row in the feed to investigate details
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default AlertDetailSidebar;

```


---

### 📄 File: `frontend/src/components/AlertsTable.jsx`
**Purpose:** Live security alert feed table with searching and sorting parameters.  
**Size:** 8,629 bytes

```javascript
import React from 'react';
import { Search, Shield, ChevronLeft, ChevronRight, Filter } from 'lucide-react';

function AlertsTable({
  alerts,
  total,
  page,
  perPage,
  filters,
  onFilterChange,
  onAlertSelect,
  selectedAlertId,
}) {
  const severities = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
  const eventTypes = [
    { label: 'ALL EVENTS', value: 'ALL' },
    { label: 'MALWARE', value: 'MALWARE_DETECTION' },
    { label: 'BRUTE FORCE', value: 'SSH_BRUTE_FORCE' },
    { label: 'EXFILTRATION', value: 'DATA_EXFILTRATION' },
    { label: 'PORT SCAN', value: 'PORT_SCAN' },
    { label: 'FAILED LOGIN', value: 'FAILED_LOGIN' },
  ];

  // Helper to color code severity badges with professional muted colors
  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-rose-500/10 border border-rose-500/20 text-rose-400';
      case 'HIGH':
        return 'bg-amber-500/10 border border-amber-500/20 text-amber-400';
      case 'MEDIUM':
        return 'bg-blue-500/10 border border-blue-500/20 text-blue-400';
      case 'LOW':
        return 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400';
      default:
        return 'bg-zinc-800 border border-zinc-700 text-zinc-400';
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / perPage));

  return (
    <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-5 flex flex-col h-full min-h-[480px]">
      {/* 1. Header Filters Section */}
      <div className="flex flex-col md:flex-row gap-3 justify-between items-start md:items-center border-b border-zinc-800/80 pb-4 mb-4">
        {/* Title & Count */}
        <div className="flex items-center gap-2.5">
          <Shield className="w-5 h-5 text-emerald-500/80" />
          <div>
            <h2 className="text-sm font-semibold tracking-wide text-zinc-100">
              Security Alert Feed
            </h2>
            <p className="text-[11px] text-zinc-500 font-mono">
              Total system events: <span className="text-zinc-300 font-semibold">{total}</span>
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Search bar */}
          <div className="relative flex-1 md:flex-none">
            <span className="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-zinc-500">
              <Search className="w-3.5 h-3.5" />
            </span>
            <input
              type="text"
              placeholder="Search IP, host, user..."
              value={filters.search}
              onChange={(e) => onFilterChange({ ...filters, search: e.target.value })}
              className="bg-zinc-950/60 border border-zinc-800 text-zinc-300 font-mono text-xs rounded-lg pl-8 pr-3 py-1.5 w-full md:w-56 focus:outline-none focus:border-zinc-700 transition-colors"
            />
          </div>

          {/* Severity selector */}
          <div className="flex items-center gap-1.5 font-sans text-xs">
            <Filter className="w-3.5 h-3.5 text-zinc-500" />
            <select
              value={filters.severity}
              onChange={(e) => onFilterChange({ ...filters, severity: e.target.value })}
              className="bg-zinc-950/60 border border-zinc-800 text-zinc-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-zinc-700 transition-colors text-xs"
            >
              {severities.map((sev) => (
                <option key={sev} value={sev === 'ALL' ? '' : sev} className="bg-zinc-950 text-zinc-300">
                  {sev}
                </option>
              ))}
            </select>
          </div>

          {/* Event type selector */}
          <div className="flex items-center gap-1.5 font-sans text-xs">
            <select
              value={filters.eventType}
              onChange={(e) => onFilterChange({ ...filters, eventType: e.target.value })}
              className="bg-zinc-950/60 border border-zinc-800 text-zinc-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-zinc-700 transition-colors text-xs"
            >
              {eventTypes.map((et) => (
                <option key={et.value} value={et.value === 'ALL' ? '' : et.value} className="bg-zinc-950 text-zinc-300">
                  {et.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 2. Grid Table Body */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-left font-mono text-[11px] border-collapse">
          <thead>
            <tr className="text-zinc-500 border-b border-zinc-800/60 pb-2 uppercase text-[10px] tracking-wider font-semibold">
              <th className="py-2.5 px-3">Timestamp</th>
              <th className="py-2.5 px-3">Severity</th>
              <th className="py-2.5 px-3">Threat Type</th>
              <th className="py-2.5 px-3">Source IP</th>
              <th className="py-2.5 px-3">Destination IP</th>
              <th className="py-2.5 px-3 text-right">Risk Score</th>
            </tr>
          </thead>
          <tbody>
            {alerts && alerts.length > 0 ? (
              alerts.slice(0, perPage).map((alert) => {
                const isSelected = selectedAlertId === alert.id;
                const isRecent = alert.isNew;
                return (
                  <tr
                    key={alert.id}
                    onClick={() => onAlertSelect(alert)}
                    className={`cursor-pointer border-b border-zinc-800/40 transition-all hover:bg-zinc-800/20 ${isSelected ? 'bg-zinc-800/40 border-l-2 border-l-emerald-500 text-white font-medium' : 'text-zinc-300'}`}
                  >
                    <td className="py-3 px-3 text-zinc-400 flex items-center gap-1.5">
                      {isRecent && <span className="w-1.5 h-1.5 rounded-full bg-blue-500 inline-block animate-pulse" title="New Alert" />}
                      {alert.timestamp}
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[9px] font-semibold uppercase tracking-wider ${getSeverityBadge(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-semibold text-zinc-200">{alert.event_type}</td>
                    <td className="py-3 px-3 text-blue-400 font-semibold">{alert.src_ip}</td>
                    <td className="py-3 px-3 text-zinc-400">{alert.dest_ip}</td>
                    <td className="py-3 px-3 text-right font-bold">
                      <span className={alert.risk_score > 75 ? 'text-rose-400' : alert.risk_score > 50 ? 'text-amber-400' : 'text-emerald-400'}>
                        {alert.risk_score}
                      </span>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="6" className="py-12 text-center text-zinc-500 text-xs">
                  No security alerts matching search query.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* 3. Footer Pagination */}
      <div className="border-t border-zinc-800/80 pt-3 mt-3 flex justify-between items-center font-mono text-[10px] text-zinc-500">
        <div>
          Showing {alerts?.length ?? 0} of {total} events
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onFilterChange({ ...filters, page: Math.max(1, page - 1) })}
            disabled={page === 1}
            className="p-1 rounded-lg border border-zinc-800 bg-zinc-900 text-zinc-400 hover:text-white disabled:opacity-30 disabled:hover:text-zinc-400 transition-colors cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span>
            Page <span className="text-zinc-200 font-semibold">{page}</span> of {totalPages}
          </span>
          <button
            onClick={() => onFilterChange({ ...filters, page: Math.min(totalPages, page + 1) })}
            disabled={page === totalPages}
            className="p-1 rounded-lg border border-zinc-800 bg-zinc-900 text-zinc-400 hover:text-white disabled:opacity-30 disabled:hover:text-zinc-400 transition-colors cursor-pointer"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default AlertsTable;

```


---

### 📄 File: `frontend/src/components/AnalyticsCharts.jsx`
**Purpose:** Recharts visualizer for incident timelines, severities, and top source IPs.  
**Size:** 8,885 bytes

```javascript
import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { Shield, Flame, Activity } from 'lucide-react';

function AnalyticsCharts({ timeline, severity, sources }) {
  // 1. Process Timeline data
  const chartTimeline = timeline?.map((p) => ({
    time: p.time.split(' ')[1] || p.time, // extract time part
    count: p.count,
  })) || [];

  // 2. Process Severity distribution
  const chartSeverity = severity?.map((s) => ({
    name: s.severity,
    value: s.count,
  })) || [];

  // Define colors for severities
  const COLORS = {
    CRITICAL: '#ef4444', // Red
    HIGH: '#f59e0b',     // Amber/Orange
    MEDIUM: '#3b82f6',   // Blue
    LOW: '#10b981',      // Green
  };

  // Custom tooltips for clean slate look
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-zinc-950 border border-zinc-800 p-2.5 rounded-lg font-mono text-[11px] shadow-lg">
          <p className="text-zinc-400 font-semibold">{label}</p>
          <p className="text-emerald-400 mt-0.5">
            Events: <span className="font-bold text-zinc-100">{payload[0].value}</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 px-6 pb-4">
      {/* 1. Real-Time Threat Volume Timeline */}
      <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 flex flex-col h-[260px]">
        <div className="flex items-center gap-2 mb-3">
          <Activity className="w-4 h-4 text-emerald-500" />
          <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">
            Threat Volume Timeline (30m)
          </h3>
        </div>
        <div className="flex-1 w-full text-slate-300">
          {chartTimeline.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartTimeline} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(63, 63, 70, 0.1)" vertical={false} />
                <XAxis
                  dataKey="time"
                  stroke="#52525b"
                  fontSize={9}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  stroke="#52525b"
                  fontSize={9}
                  tickLine={false}
                  axisLine={false}
                  allowDecimals={false}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#10b981"
                  strokeWidth={1.5}
                  fillOpacity={1}
                  fill="url(#colorCount)"
                  dot={false}
                  activeDot={{ r: 3, fill: '#10b981', stroke: '#09090b', strokeWidth: 1.5 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-zinc-500 font-sans text-xs">
              <div className="text-center">
                <Activity className="w-6 h-6 mx-auto mb-2 opacity-30" />
                Awaiting telemetry signals...
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 2. Threats by Severity Breakdown */}
      <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 flex flex-col h-[260px]">
        <div className="flex items-center gap-2 mb-3">
          <Flame className="w-4 h-4 text-amber-500" />
          <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">
            Incidents by Severity
          </h3>
        </div>
        <div className="flex-1 flex flex-col sm:flex-row items-center justify-center gap-4 text-slate-300">
          {chartSeverity.length > 0 ? (
            <>
              {/* Pie Chart display */}
              <div className="w-[130px] h-[130px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartSeverity}
                      cx="50%"
                      cy="50%"
                      innerRadius={42}
                      outerRadius={56}
                      paddingAngle={3}
                      dataKey="value"
                      strokeWidth={0}
                    >
                      {chartSeverity.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#71717a'} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#09090b',
                        border: '1px solid rgba(63, 63, 70, 0.4)',
                        borderRadius: '8px',
                        fontSize: '11px',
                        fontFamily: 'JetBrains Mono, monospace',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Legends with detail counts */}
              <div className="flex flex-col gap-1.5 font-mono text-xs flex-1 w-full justify-center">
                {chartSeverity.map((item, idx) => (
                  <div key={idx} className="flex justify-between items-center border-b border-zinc-800/60 pb-1">
                    <span className="flex items-center gap-1.5 text-zinc-400 text-[11px] font-sans">
                      <span
                        className="w-2 h-2 rounded-full inline-block"
                        style={{ backgroundColor: COLORS[item.name] || '#71717a' }}
                      ></span>
                      {item.name}
                    </span>
                    <span className="font-semibold text-zinc-200 text-[11px]">{item.value}</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="h-full flex items-center justify-center text-zinc-500 font-sans text-xs">
              <div className="text-center">
                <Flame className="w-6 h-6 mx-auto mb-2 opacity-30" />
                No incident data received.
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 3. Top Attacking Source IPs */}
      <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 flex flex-col h-[260px]">
        <div className="flex items-center gap-2 mb-3">
          <Shield className="w-4 h-4 text-blue-500" />
          <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">
            Top Aggressors (Sources)
          </h3>
        </div>
        <div className="flex-1 overflow-y-auto pr-1">
          {sources && sources.length > 0 ? (
            <div className="flex flex-col gap-2 font-mono">
              {sources.slice(0, 5).map((src, index) => (
                <div
                  key={index}
                  className="bg-zinc-950/40 border border-zinc-800/60 rounded-lg p-2.5 flex flex-col gap-1 text-[11px] hover:border-blue-900/20 transition-colors"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-blue-400 font-semibold tracking-wider">{src.ip}</span>
                    <span className="bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[9px] px-1.5 py-0.5 rounded font-bold">
                      {src.count} Alerts
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-[10px] text-zinc-500 font-sans">
                    <span>Type: {src.primary_attack}</span>
                    <span className="text-[9px] font-mono">Last seen: {src.last_seen?.split(' ')[1] || src.last_seen}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-zinc-500 font-sans text-xs">
              <div className="text-center">
                <Shield className="w-6 h-6 mx-auto mb-2 opacity-30" />
                No host reconnaissance detected.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AnalyticsCharts;

```


---

### 📄 File: `frontend/src/components/DashboardHeader.jsx`
**Purpose:** System health and status bar containing manual retraining controls.  
**Size:** 5,590 bytes

```javascript
import React, { useState, useEffect } from 'react';
import { Shield, Radio, Activity, RefreshCw, Cpu } from 'lucide-react';

function DashboardHeader({ wsStatus, systemHealth, onRefresh, onTrainModel }) {
  const [time, setTime] = useState(new Date());
  const [isTraining, setIsTraining] = useState(false);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { hour12: false });
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handleTrainClick = async () => {
    if (isTraining || !onTrainModel) return;
    setIsTraining(true);
    setFeedback(null);
    try {
      const res = await onTrainModel();
      if (res && res.success) {
        setFeedback('success');
        setTimeout(() => setFeedback(null), 3000);
      } else {
        setFeedback('error');
        setTimeout(() => setFeedback(null), 3000);
      }
    } catch (err) {
      setFeedback('error');
      setTimeout(() => setFeedback(null), 3000);
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <header className="bg-zinc-950 border-b border-zinc-800 px-6 py-4 flex flex-col md:flex-row justify-between items-center gap-4 relative z-10">
      {/* Brand Logo & Title */}
      <div className="flex items-center gap-3">
        <div className="bg-zinc-900 border border-zinc-800 p-2 rounded-lg text-emerald-500">
          <Shield className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-base font-semibold tracking-tight text-white flex items-center gap-1.5">
            Zenith AI <span className="text-zinc-500 font-normal">|</span> <span className="text-zinc-400 font-normal">SOC Platform</span>
          </h1>
          <p className="text-[11px] text-zinc-500 font-medium">
            Real-time Threat Intelligence & Automated Response
          </p>
        </div>
      </div>

      {/* Health signals */}
      <div className="flex flex-wrap items-center gap-3 text-xs">
        {/* WebSocket Link Status */}
        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-full px-3 py-1 flex items-center gap-2 text-zinc-400">
          <span className={`w-2 h-2 rounded-full ${wsStatus === 'connected' ? 'bg-emerald-500 animate-pulse' : wsStatus === 'connecting' ? 'bg-amber-500' : 'bg-rose-500'}`} />
          <span>Feed: <span className="text-zinc-200 capitalize font-medium">{wsStatus}</span></span>
        </div>

        {/* Database Status */}
        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-full px-3 py-1 flex items-center gap-2 text-zinc-400">
          <span className={`w-2 h-2 rounded-full ${systemHealth?.status === 'online' ? 'bg-emerald-500' : 'bg-rose-500'}`} />
          <span>API: <span className="text-zinc-200 capitalize font-medium">{systemHealth?.status || 'offline'}</span></span>
        </div>

        {/* Anomaly model status */}
        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-full px-3 py-1 flex items-center gap-2 text-zinc-400">
          <span className={`w-2 h-2 rounded-full ${systemHealth?.anomaly_detector === 'trained' ? 'bg-violet-500' : 'bg-zinc-600'}`} />
          <span>ML Model: <span className="text-zinc-200 capitalize font-medium">{systemHealth?.anomaly_detector || 'untrained'}</span></span>
        </div>

        {/* Train Model button */}
        <button
          onClick={handleTrainClick}
          disabled={isTraining || systemHealth?.status !== 'online'}
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs transition-all cursor-pointer font-medium ${
            isTraining
              ? 'bg-zinc-900 border-zinc-800 text-zinc-500 cursor-not-allowed'
              : feedback === 'success'
              ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'
              : feedback === 'error'
              ? 'bg-rose-950/40 border-rose-500/50 text-rose-300'
              : 'bg-violet-950/30 hover:bg-violet-900/40 border-violet-800/50 hover:border-violet-700/60 text-violet-300 hover:text-violet-100 disabled:opacity-50 disabled:cursor-not-allowed'
          }`}
          title="Train Isolation Forest model on latest 500 security events"
        >
          <Cpu className={`w-3.5 h-3.5 ${isTraining ? 'animate-spin' : ''}`} />
          <span>
            {isTraining
              ? 'Training...'
              : feedback === 'success'
              ? 'Trained!'
              : feedback === 'error'
              ? 'Error!'
              : 'Train Model'}
          </span>
        </button>

        {/* Manual Refresh Trigger */}
        <button
          onClick={onRefresh}
          className="bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 transition-colors rounded-lg p-1.5 text-zinc-400 hover:text-zinc-200 cursor-pointer"
          title="Force Sync Stats"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Digital clock HUD */}
      <div className="flex items-center gap-3 text-right">
        <div className="text-xs text-zinc-500">
          {formatDate(time)}
        </div>
        <div className="text-sm font-semibold text-zinc-300 font-mono">
          {formatTime(time)}
        </div>
      </div>
    </header>
  );
}

export default DashboardHeader;

```


---

### 📄 File: `frontend/src/components/OverviewCards.jsx`
**Purpose:** Aggregate dashboard KPI metrics boxes.  
**Size:** 3,052 bytes

```javascript
import React from 'react';
import { AlertTriangle, ShieldAlert, Zap, Award } from 'lucide-react';

function OverviewCards({ stats }) {
  const kpis = [
    {
      title: 'Total Alerts',
      value: stats?.total_alerts ?? 0,
      subtext: `Last hour: ${stats?.alerts_last_hour ?? 0}`,
      icon: AlertTriangle,
      color: 'text-blue-500',
      borderColor: 'border-blue-500/10',
      bgColor: 'bg-blue-500/5',
      indicatorColor: 'bg-blue-500',
    },
    {
      title: 'Active Threats',
      value: stats?.active_threats ?? 0,
      subtext: 'High/critical in last hour',
      icon: ShieldAlert,
      color: 'text-rose-500',
      borderColor: 'border-rose-500/10',
      bgColor: 'bg-rose-500/5',
      indicatorColor: 'bg-rose-500',
    },
    {
      title: 'Average Risk Score',
      value: stats?.avg_risk_score ?? 0,
      subtext: stats?.avg_risk_score > 75 ? 'Status: Critical' : stats?.avg_risk_score > 50 ? 'Status: High' : stats?.avg_risk_score > 25 ? 'Status: Elevated' : 'Status: Normal',
      icon: Zap,
      color: stats?.avg_risk_score > 75 ? 'text-rose-500' : stats?.avg_risk_score > 50 ? 'text-amber-500' : 'text-emerald-500',
      borderColor: stats?.avg_risk_score > 50 ? 'border-amber-500/10' : 'border-emerald-500/10',
      bgColor: stats?.avg_risk_score > 50 ? 'bg-amber-500/5' : 'bg-emerald-500/5',
      indicatorColor: stats?.avg_risk_score > 75 ? 'bg-rose-500' : stats?.avg_risk_score > 50 ? 'bg-amber-500' : 'bg-emerald-500',
    },
    {
      title: 'Severity Ratio',
      value: `${stats?.critical_count ?? 0} / ${stats?.high_count ?? 0}`,
      subtext: 'Critical vs High severity',
      icon: Award,
      color: 'text-violet-500',
      borderColor: 'border-violet-500/10',
      bgColor: 'bg-violet-500/5',
      indicatorColor: 'bg-violet-500',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 px-6 py-4">
      {kpis.map((kpi, idx) => (
        <div
          key={idx}
          className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-5 hover:border-zinc-700 transition-colors flex items-center justify-between gap-4 overflow-hidden relative"
        >
          {/* Left Contents */}
          <div className="flex flex-col">
            <span className="text-[11px] text-zinc-400 font-medium tracking-wide uppercase">
              {kpi.title}
            </span>
            <span className="text-3xl font-bold text-white mt-1 leading-none tracking-tight">
              {kpi.value}
            </span>
            <span className="text-xs text-zinc-400 mt-2 flex items-center gap-1.5">
              <span className={`w-1.5 h-1.5 rounded-full ${kpi.indicatorColor} inline-block`}></span>
              {kpi.subtext}
            </span>
          </div>

          {/* Right Icon Shield */}
          <div className={`p-2.5 rounded-lg border border-zinc-800 bg-zinc-950 text-zinc-400 ${kpi.color}`}>
            <kpi.icon className="w-5 h-5" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default OverviewCards;

```


---

### 📄 File: `frontend/src/components/SOARAuditLogs.jsx`
**Purpose:** Chronological SOAR automation compliance ledgers table.  
**Size:** 17,988 bytes

```javascript
import React, { useState, useEffect, useCallback } from 'react';
import { getAuditLogs } from '../utils/api';
import { ShieldAlert, Terminal, CheckCircle2, Search, RefreshCw, ChevronDown, ChevronUp, Clock, User, Clipboard, Download, Shield, Activity, FileText } from 'lucide-react';

function SOARAuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedRow, setExpandedRow] = useState(null);
  const [filterAction, setFilterAction] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAuditLogs(100); // Fetch top 100 logs
      setLogs(data.audit_logs || []);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
      setError('Failed to retrieve SOAR audit trails from the server.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const toggleRow = (index) => {
    setExpandedRow(expandedRow === index ? null : index);
  };

  const getActionLabel = (action) => {
    switch (action) {
      case 'block_ip':
        return { label: 'BLOCK IP', color: 'bg-rose-500/10 border-rose-500/20 text-rose-400' };
      case 'quarantine_host':
        return { label: 'ISOLATE HOST', color: 'bg-amber-500/10 border-amber-500/20 text-amber-400' };
      case 'create_ticket':
        return { label: 'CREATE TICKET', color: 'bg-blue-500/10 border-blue-500/20 text-blue-400' };
      default:
        return { label: action.toUpperCase(), color: 'bg-zinc-800 border-zinc-700 text-zinc-300' };
    }
  };

  // Filter logs based on filters and search queries
  const filteredLogs = logs.filter((log) => {
    const matchesAction = filterAction === 'all' || log.action === filterAction;
    const matchesSearch = 
      searchTerm === '' ||
      log.alert_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.analyst_user?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      JSON.stringify(log.details || {}).toLowerCase().includes(searchTerm.toLowerCase());
    return matchesAction && matchesSearch;
  });

  // Calculate metrics based on total logs
  const totalActions = logs.length;
  const ipsBlocked = logs.filter(log => log.action === 'block_ip').length;
  const hostsIsolated = logs.filter(log => log.action === 'quarantine_host').length;
  const ticketsCreated = logs.filter(log => log.action === 'create_ticket').length;

  // Export ledger to CSV format
  const handleExportCSV = () => {
    if (logs.length === 0) return;

    let csvContent = "Timestamp,Action,Alert ID Target,Triggered By,Status,Details\n";
    logs.forEach((log) => {
      const timestamp = log.timestamp || "";
      const action = log.action || "";
      const alertId = log.alert_id || "";
      const user = log.analyst_user || "";
      const status = "SUCCESS";
      const details = JSON.stringify(log.details || {}).replace(/"/g, '""');
      csvContent += `"${timestamp}","${action}","${alertId}","${user}","${status}","${details}"\n`;
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `soar_compliance_audit_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex-grow px-6 py-6 flex flex-col min-h-0">
      {/* Page Title & Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h2 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            <Terminal className="w-5 h-5 text-purple-500" />
            SOAR Automation Compliance Audit
          </h2>
          <p className="text-xs text-zinc-400">
            Chronological ledger of executed active containment playbooks and security integrations.
          </p>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          {/* Export Button */}
          <button
            onClick={handleExportCSV}
            disabled={loading || logs.length === 0}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-300 hover:text-white transition-colors cursor-pointer text-xs disabled:opacity-40"
          >
            <Download className="w-3.5 h-3.5 text-purple-400" />
            Export CSV
          </button>

          {/* Refresh Button */}
          <button
            onClick={fetchLogs}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-300 hover:text-white transition-colors cursor-pointer text-xs disabled:opacity-40"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Sync Logs
          </button>
        </div>
      </div>

      {/* ── KPI Metric Cards ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 hover:border-zinc-700 transition-colors flex items-center justify-between gap-4">
          <div className="flex flex-col">
            <span className="text-[10px] text-zinc-500 font-semibold tracking-wide uppercase">Total Mitigations</span>
            <span className="text-2xl font-bold text-white mt-1 leading-none tracking-tight">{totalActions}</span>
            <span className="text-[9px] text-zinc-400 mt-2 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-500 inline-block animate-pulse"></span>
              Ledger coverage active
            </span>
          </div>
          <div className="p-2 rounded-lg border border-zinc-800 bg-zinc-950 text-purple-400">
            <Terminal className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 hover:border-zinc-700 transition-colors flex items-center justify-between gap-4">
          <div className="flex flex-col">
            <span className="text-[10px] text-zinc-500 font-semibold tracking-wide uppercase">IPs Blocked</span>
            <span className="text-2xl font-bold text-white mt-1 leading-none tracking-tight">{ipsBlocked}</span>
            <span className="text-[9px] text-zinc-400 mt-2 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500 inline-block"></span>
              Firewall sync active
            </span>
          </div>
          <div className="p-2 rounded-lg border border-zinc-800 bg-zinc-950 text-rose-400">
            <Shield className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 hover:border-zinc-700 transition-colors flex items-center justify-between gap-4">
          <div className="flex flex-col">
            <span className="text-[10px] text-zinc-500 font-semibold tracking-wide uppercase">Hosts Isolated</span>
            <span className="text-2xl font-bold text-white mt-1 leading-none tracking-tight">{hostsIsolated}</span>
            <span className="text-[9px] text-zinc-400 mt-2 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 inline-block"></span>
              EDR quarantine active
            </span>
          </div>
          <div className="p-2 rounded-lg border border-zinc-800 bg-zinc-950 text-amber-400">
            <Activity className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 hover:border-zinc-700 transition-colors flex items-center justify-between gap-4">
          <div className="flex flex-col">
            <span className="text-[10px] text-zinc-500 font-semibold tracking-wide uppercase">Jira Tickets</span>
            <span className="text-2xl font-bold text-white mt-1 leading-none tracking-tight">{ticketsCreated}</span>
            <span className="text-[9px] text-zinc-400 mt-2 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500 inline-block"></span>
              ITSM escalation active
            </span>
          </div>
          <div className="p-2 rounded-lg border border-zinc-800 bg-zinc-950 text-blue-400">
            <FileText className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Filter HUD Toolbar */}
      <div className="bg-zinc-950/80 border border-zinc-800 rounded-xl p-4 mb-6 flex flex-col md:flex-row gap-4 items-center justify-between">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-zinc-500 pointer-events-none">
            <Search className="w-3.5 h-3.5" />
          </span>
          <input
            type="text"
            placeholder="Search by ID, IP, or parameter..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-zinc-900/40 border border-zinc-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-zinc-300 placeholder-zinc-500 focus:outline-none focus:border-zinc-700 focus:bg-zinc-900 transition-colors"
          />
        </div>

        {/* Action filter tabs */}
        <div className="flex bg-zinc-900/60 p-1 rounded-lg border border-zinc-800/80 text-xs w-full md:w-auto justify-center">
          {[
            { id: 'all', name: 'All Actions' },
            { id: 'block_ip', name: 'IP Block' },
            { id: 'quarantine_host', name: 'Isolations' },
            { id: 'create_ticket', name: 'Jira Tickets' }
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setFilterAction(item.id)}
              className={`px-3 py-1 rounded-md transition-all font-medium cursor-pointer ${
                filterAction === item.id
                  ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              {item.name}
            </button>
          ))}
        </div>
      </div>

      {/* Main Table Panel */}
      <div className="flex-1 bg-zinc-900/25 border border-zinc-800/80 rounded-xl overflow-hidden flex flex-col min-h-0">
        <div className="flex-grow overflow-auto">
          {loading && logs.length === 0 ? (
            <div className="h-60 flex flex-col justify-center items-center gap-3">
              <RefreshCw className="w-6 h-6 text-purple-500 animate-spin" />
              <span className="text-zinc-500 text-xs font-mono">RETRIEVING COMPLIANCE LEDGER...</span>
            </div>
          ) : error ? (
            <div className="h-60 flex flex-col justify-center items-center gap-3 text-center px-4">
              <ShieldAlert className="w-8 h-8 text-rose-500" />
              <span className="text-zinc-300 text-xs font-semibold">{error}</span>
              <button
                onClick={fetchLogs}
                className="mt-2 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs rounded border border-zinc-700 cursor-pointer"
              >
                Retry Request
              </button>
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="h-60 flex flex-col justify-center items-center text-zinc-500 text-xs font-sans">
              <Clipboard className="w-8 h-8 text-zinc-700 mb-2" />
              No audit logs found matching the search criteria.
            </div>
          ) : (
            <table className="w-full text-left border-collapse font-sans text-xs">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-950/60 text-zinc-400 uppercase font-mono text-[10px] tracking-wider">
                  <th className="py-3 px-4 font-semibold">Timestamp</th>
                  <th className="py-3 px-4 font-semibold">Action Triggered</th>
                  <th className="py-3 px-4 font-semibold">Security Alert Target</th>
                  <th className="py-3 px-4 font-semibold">Triggered By</th>
                  <th className="py-3 px-4 font-semibold text-center">Status</th>
                  <th className="py-3 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/40">
                {filteredLogs.map((log, index) => {
                  const actionStyle = getActionLabel(log.action);
                  const isExpanded = expandedRow === index;
                  
                  // Extract target asset parameter from details
                  let targetStr = 'N/A';
                  if (log.action === 'block_ip') {
                    targetStr = `IP: ${log.details?.ip_blocked || 'Unknown'}`;
                  } else if (log.action === 'quarantine_host') {
                    targetStr = `Subnet Isolation`;
                  } else if (log.action === 'create_ticket') {
                    targetStr = `Ticket: ${log.details?.ticket_id || 'INC-ID'}`;
                  }

                  return (
                    <React.Fragment key={index}>
                      <tr className="hover:bg-zinc-800/20 transition-colors">
                        <td className="py-3 px-4 text-zinc-400 font-mono flex items-center gap-1.5">
                          <Clock className="w-3 h-3 text-zinc-600" />
                          {log.timestamp}
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-0.5 rounded border text-[9px] font-mono font-semibold ${actionStyle.color}`}>
                            {actionStyle.label}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-zinc-300 font-mono font-medium">
                          {targetStr}
                        </td>
                        <td className="py-3 px-4 text-zinc-400 font-mono flex items-center gap-1.5">
                          <User className="w-3 h-3 text-zinc-600" />
                          {log.analyst_user}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className="inline-flex items-center gap-1 text-emerald-400 bg-emerald-500/5 px-2 py-0.5 rounded-full border border-emerald-500/10 text-[9px] font-semibold">
                            <CheckCircle2 className="w-3 h-3" />
                            SUCCESS
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button
                            onClick={() => toggleRow(index)}
                            className="text-zinc-500 hover:text-zinc-300 p-1 rounded hover:bg-zinc-800/50 cursor-pointer"
                          >
                            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                          </button>
                        </td>
                      </tr>

                      {/* Expanded Detail Panel */}
                      {isExpanded && (
                        <tr className="bg-zinc-950/40">
                          <td colSpan="6" className="py-4 px-6 border-b border-zinc-800/80">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div className="space-y-2">
                                <div className="text-[10px] text-zinc-500 font-mono uppercase tracking-wider">Audit Metadata</div>
                                <div className="bg-zinc-900/60 border border-zinc-800/60 rounded-lg p-3 space-y-1.5 font-mono text-[10px] text-zinc-400">
                                  <div><span className="text-zinc-600">Event ID Ref:</span> {log.alert_id}</div>
                                  <div><span className="text-zinc-600">Action:</span> {log.action}</div>
                                  <div><span className="text-zinc-600">User Scope:</span> {log.analyst_user} (Tier-1 SOC Admin)</div>
                                  <div><span className="text-zinc-600">Timestamp:</span> {log.timestamp}</div>
                                </div>
                              </div>

                              <div className="space-y-2">
                                <div className="text-[10px] text-zinc-500 font-mono uppercase tracking-wider">SOAR Response Payload</div>
                                <div className="bg-zinc-900/60 border border-zinc-800/60 rounded-lg p-3">
                                  <pre className="text-emerald-500 font-mono text-[10px] whitespace-pre-wrap leading-relaxed">
                                    {JSON.stringify(log.details || {}, null, 2)}
                                  </pre>
                                </div>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
        <div className="bg-zinc-950/60 border-t border-zinc-800 px-4 py-2.5 flex justify-between items-center text-[10px] text-zinc-500 font-mono">
          <div>TOTAL AUDITED ACTIONS: {filteredLogs.length}</div>
          <div>COMPLIANCE STATUS: SECURE</div>
        </div>
      </div>
    </div>
  );
}

export default SOARAuditLogs;

```


---

### 📄 File: `frontend/src/components/ThreatHotspots.jsx`
**Purpose:** SVG interactive geospatial coordinate map plotting threat origins.  
**Size:** 10,448 bytes

```javascript
import React, { useState } from 'react';
import { Target, MapPin, Shield } from 'lucide-react';

function ThreatHotspots({ geoData }) {
  const [hoveredSpot, setHoveredSpot] = useState(null);

  // Sort hotspots by count descending and limit to top 8
  const hotspots = [...(geoData || [])].sort((a, b) => b.count - a.count).slice(0, 8);
  const maxCount = hotspots.length > 0 ? Math.max(...hotspots.map(h => h.count)) : 1;

  // Coordinate projection formulas for SVG viewBox: 0 0 200 100
  const getX = (lng) => {
    // Normalizes longitude [-180, 180] to [0, 200]
    return ((lng + 180) / 360) * 200;
  };

  const getY = (lat) => {
    // Normalizes latitude [-90, 90] to [100, 0] (Mercator projection approximation)
    return ((90 - lat) / 180) * 100;
  };

  // SOC Target Location (Central US for Zenith Hub)
  const socLng = -97.0;
  const socLat = 38.0;
  const socX = getX(socLng);
  const socY = getY(socLat);

  // Stylized Simplified World Continent Outlines (viewBox 0 0 200 100)
  const continentPaths = [
    // North America
    "M 30,12 L 55,10 L 68,12 L 72,25 L 60,35 L 54,46 L 46,43 L 34,38 L 28,24 Z",
    // South America
    "M 54,46 L 63,48 L 70,58 L 65,72 L 58,85 L 56,80 L 53,58 Z",
    // Eurasia (Europe + Asia)
    "M 80,24 L 92,10 L 115,6 L 150,6 L 180,10 L 180,28 L 165,42 L 140,46 L 120,42 L 102,46 L 90,32 Z",
    // Africa
    "M 88,46 L 102,43 L 115,48 L 120,58 L 112,72 L 102,78 L 95,70 L 90,58 Z",
    // Australia
    "M 158,68 L 172,66 L 178,72 L 172,80 L 162,78 Z"
  ];

  return (
    <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-5 flex flex-col h-[320px] relative overflow-hidden">
      {/* Title */}
      <div className="flex items-center gap-2 mb-4 z-10">
        <Target className="w-4 h-4 text-rose-500/95 animate-pulse" />
        <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">
          Tactical Threat Map & Hotspots
        </h3>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 min-h-0 z-10">
        {/* SVG Interactive Map (Col-span 7) */}
        <div className="lg:col-span-7 bg-zinc-950/80 rounded-lg border border-zinc-800/60 p-2 relative flex items-center justify-center min-h-[150px] overflow-hidden">
          {/* Animated Background Scanning Lines */}
          <div className="absolute inset-0 pointer-events-none opacity-[0.02] bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-zinc-200 via-zinc-900 to-black"></div>
          
          <svg
            viewBox="0 0 200 100"
            className="w-full h-full max-h-[170px] select-none"
          >
            {/* World Grid Dotted Grid Overlay */}
            <defs>
              <pattern id="dotPattern" width="4" height="4" patternUnits="userSpaceOnUse">
                <circle cx="1" cy="1" r="0.4" fill="rgba(63, 63, 70, 0.2)" />
              </pattern>
            </defs>
            <rect width="200" height="100" fill="url(#dotPattern)" />

            {/* Continents outlines */}
            {continentPaths.map((path, idx) => (
              <path
                key={idx}
                d={path}
                fill="rgba(24, 24, 27, 0.6)"
                stroke="rgba(82, 82, 91, 0.25)"
                strokeWidth="0.8"
                className="transition-all duration-300"
              />
            ))}

            {/* Attack Vectors - Curved Arcs */}
            {hotspots.map((spot, index) => {
              const x = getX(spot.lng);
              const y = getY(spot.lat);
              
              // Calculate curved path using Quadratic Bezier (Q)
              const midX = (x + socX) / 2;
              const midY = (y + socY) / 2 - 12; // curve height offset
              const pathD = `M ${x} ${y} Q ${midX} ${midY} ${socX} ${socY}`;
              
              const isHovered = hoveredSpot === index;

              return (
                <g key={`arc-${index}`}>
                  {/* Outer glowing trace line */}
                  <path
                    d={pathD}
                    fill="none"
                    stroke={isHovered ? "rgba(244, 63, 94, 0.4)" : "rgba(244, 63, 94, 0.15)"}
                    strokeWidth={isHovered ? "1.5" : "0.8"}
                    strokeDasharray="4, 4"
                    className="transition-all"
                  />
                  {/* Shooting light beam */}
                  <path
                    d={pathD}
                    fill="none"
                    stroke="url(#arcGlow)"
                    strokeWidth="1.2"
                    strokeDasharray="15, 80"
                    style={{
                      animation: `dash 3s linear infinite`,
                      animationDelay: `${index * 0.4}s`
                    }}
                  />
                </g>
              );
            })}

            {/* Linear Gradient for Glowing Shoot Beam */}
            <defs>
              <linearGradient id="arcGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f43f5e" stopOpacity="0" />
                <stop offset="50%" stopColor="#f43f5e" stopOpacity="1" />
                <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0" />
              </linearGradient>
            </defs>

            {/* Pulsing Threat Coordinate Markers */}
            {hotspots.map((spot, index) => {
              const x = getX(spot.lng);
              const y = getY(spot.lat);
              const isHovered = hoveredSpot === index;

              return (
                <g
                  key={`marker-${index}`}
                  onMouseEnter={() => setHoveredSpot(index)}
                  onMouseLeave={() => setHoveredSpot(null)}
                  className="cursor-pointer group"
                >
                  {/* Radar Pulse Circle */}
                  <circle
                    cx={x}
                    cy={y}
                    r="4"
                    fill="none"
                    stroke="#ef4444"
                    strokeWidth="0.5"
                    className="animate-ping"
                    style={{ animationDuration: '2.5s' }}
                  />
                  {/* Threat Target Point */}
                  <circle
                    cx={x}
                    cy={y}
                    r={isHovered ? "2.5" : "1.8"}
                    fill="#ef4444"
                    className="transition-all group-hover:fill-rose-400"
                  />
                </g>
              );
            })}

            {/* Zenith SOC Central Command Hub (Target Center Node) */}
            <g>
              {/* Radar pulse ring */}
              <circle
                cx={socX}
                cy={socY}
                r="7"
                fill="none"
                stroke="#10b981"
                strokeWidth="0.4"
                className="animate-ping"
                style={{ animationDuration: '3s' }}
              />
              {/* Center Dot */}
              <circle
                cx={socX}
                cy={socY}
                r="2.2"
                fill="#10b981"
              />
              {/* Visual Ring */}
              <circle
                cx={socX}
                cy={socY}
                r="3.8"
                fill="none"
                stroke="#10b981"
                strokeWidth="0.7"
              />
            </g>
          </svg>

          {/* Inline styles for custom dash sweep animation */}
          <style>{`
            @keyframes dash {
              to {
                stroke-dashoffset: -95;
              }
            }
          `}</style>
        </div>

        {/* Hotspots Side List (Col-span 5) */}
        <div className="lg:col-span-5 overflow-y-auto pr-1 flex flex-col gap-1.5 font-mono text-[10px]">
          {hotspots.length > 0 ? (
            hotspots.map((spot, index) => {
              const ratio = Math.round((spot.count / maxCount) * 100);
              const isHovered = hoveredSpot === index;
              return (
                <div
                  key={index}
                  onMouseEnter={() => setHoveredSpot(index)}
                  onMouseLeave={() => setHoveredSpot(null)}
                  className={`border rounded-lg p-1.5 flex items-center justify-between gap-3 transition-all ${
                    isHovered
                      ? 'bg-rose-950/15 border-rose-800/40'
                      : 'bg-zinc-950/30 border-zinc-800/40 hover:border-zinc-800'
                  }`}
                >
                  <div className="flex items-center gap-1.5 min-w-0">
                    <MapPin className={`w-3 h-3 flex-shrink-0 ${isHovered ? 'text-rose-400' : 'text-zinc-500'}`} />
                    <span className="font-semibold text-zinc-300 uppercase truncate text-[9px] font-sans">
                      {spot.country}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    {/* Ratio Bar */}
                    <div className="w-12 bg-zinc-800 h-1 rounded-full overflow-hidden border border-zinc-700/20 hidden sm:block">
                      <div
                        className="bg-rose-500/60 h-full rounded-full"
                        style={{ width: `${ratio}%` }}
                      ></div>
                    </div>
                    {/* Counter Label */}
                    <span className="bg-rose-500/10 border border-rose-500/15 text-rose-400 font-semibold px-1.5 py-0.5 rounded text-[8px]">
                      {spot.count} IP
                    </span>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="flex-1 flex items-center justify-center text-zinc-500 font-sans text-xs">
              No geographical signals.
            </div>
          )}
        </div>
      </div>

      {/* Footer locator system metadata */}
      <div className="mt-2 border-t border-zinc-800/80 pt-2 flex justify-between items-center text-[9px] text-zinc-500 font-mono">
        <span className="flex items-center gap-1">
          <Shield className="w-3 h-3 text-emerald-500" />
          SOC CENTRAL NODE: USA HUB
        </span>
        <span className="text-rose-500 font-semibold uppercase animate-pulse-glow">
          TRACKING RADAR ACTIVE
        </span>
      </div>
    </div>
  );
}

export default ThreatHotspots;

```


---

### 📄 File: `frontend/src/index.css`
**Purpose:** Core styling, Tailwind themes, custom animations, and glassmorphism definitions.  
**Size:** 5,542 bytes

```css
@import "tailwindcss";

@theme {
  /* ── Clean Professional Color Tokens ── */
  --color-cyber-bg: #09090b; /* zinc-950 background */
  --color-cyber-card: rgba(20, 20, 23, 0.7); /* sleek dark card background */
  --color-cyber-card-border: rgba(63, 63, 70, 0.3); /* thin zinc-700 border */
  --color-cyber-green: #10b981; /* emerald accent */
  --color-cyber-green-glow: rgba(16, 185, 129, 0.05);
  --color-cyber-blue: #3b82f6; /* blue accent */
  --color-cyber-blue-glow: rgba(59, 130, 246, 0.05);
  --color-cyber-yellow: #f59e0b; /* amber accent */
  --color-cyber-yellow-glow: rgba(245, 158, 11, 0.05);
  --color-cyber-red: #ef4444; /* rose/red accent */
  --color-cyber-red-glow: rgba(239, 68, 68, 0.05);
  --color-cyber-purple: #8b5cf6; /* violet/purple accent */
  --color-cyber-purple-glow: rgba(139, 92, 246, 0.05);

  /* ── Typography (Replacing Orbitron with Inter for professional headers) ── */
  --font-sans: 'Inter', ui-sans-serif, system-ui, sans-serif;
  --font-cyber: 'Inter', ui-sans-serif, sans-serif; /* Fallback font-cyber to Inter */
  --font-mono: 'JetBrains Mono', ui-monospace, 'Cascadia Code', monospace;
}

/* ═══════════════════════════════════════════════
   CUSTOM UTILITIES — Minimal Shadows (Replaces neon glows)
   ═══════════════════════════════════════════════ */
.cyber-glow-green {
  box-shadow: 0 1px 3px rgba(16, 185, 129, 0.05);
}
.cyber-glow-blue {
  box-shadow: 0 1px 3px rgba(59, 130, 246, 0.05);
}
.cyber-glow-yellow {
  box-shadow: 0 1px 3px rgba(245, 158, 11, 0.05);
}
.cyber-glow-red {
  box-shadow: 0 1px 3px rgba(239, 68, 68, 0.05);
}
.cyber-glow-purple {
  box-shadow: 0 1px 3px rgba(139, 92, 246, 0.05);
}

/* ═══════════════════════════════════════════════
   GLASSMORPHISM
   ═══════════════════════════════════════════════ */
.glassmorphism {
  background: rgba(18, 18, 20, 0.65);
  backdrop-filter: blur(12px) saturate(1.1);
  -webkit-backdrop-filter: blur(12px) saturate(1.1);
  border: 1px solid rgba(63, 63, 70, 0.25);
}

/* ═══════════════════════════════════════════════
   CYBER GRID BACKGROUND (Muted grid background)
   ═══════════════════════════════════════════════ */
.cyber-grid-bg {
  background-size: 60px 60px;
  background-image:
    linear-gradient(to right, rgba(63, 63, 70, 0.015) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(63, 63, 70, 0.015) 1px, transparent 1px);
}

/* ═══════════════════════════════════════════════
   ANIMATIONS (Clean, micro-animations)
   ═══════════════════════════════════════════════ */

/* Pulse Glow — simplified status pulse */
@keyframes pulse-glow {
  0%, 100% {
    opacity: 0.8;
  }
  50% {
    opacity: 1;
  }
}
.animate-pulse-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}

/* Scanline — sweep animation (disabled for eye comfort) */
.scanline-effect::after {
  display: none !important;
}

/* Data stream flicker — simplified */
@keyframes data-stream {
  0% { opacity: 0.8; }
  50% { opacity: 1; }
  100% { opacity: 0.8; }
}
.animate-data-stream {
  animation: data-stream 2s ease-in-out infinite;
}

/* Float — subtle floating effect */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-2px); }
}
.animate-float {
  animation: float 5s ease-in-out infinite;
}

/* Glow pulse ring — soft indicator change */
@keyframes glow-ring {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}
.animate-glow-ring {
  animation: glow-ring 2s ease-in-out infinite;
}

/* ═══════════════════════════════════════════════
   SCROLLBAR CUSTOMIZATION
   ═══════════════════════════════════════════════ */
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}
::-webkit-scrollbar-track {
  background: rgba(10, 10, 12, 0.2);
}
::-webkit-scrollbar-thumb {
  background: rgba(63, 63, 70, 0.4);
  border-radius: 9999px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(63, 63, 70, 0.6);
}

/* Firefox scrollbar */
* {
  scrollbar-width: thin;
  scrollbar-color: rgba(63, 63, 70, 0.4) rgba(10, 10, 12, 0.2);
}

/* ═══════════════════════════════════════════════
   GLOBAL STYLES
   ═══════════════════════════════════════════════ */
html {
  background-color: #09090b;
  color-scheme: dark;
}

/* Smooth transitions on interactive elements */
button, a, input, select {
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Selection color */
::selection {
  background: rgba(16, 185, 129, 0.15);
  color: white;
}
```


---

### 📄 File: `frontend/src/main.jsx`
**Purpose:** React mounting index bootloader.  
**Size:** 229 bytes

```javascript
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

```


---

### 📄 File: `frontend/src/utils/api.js`
**Purpose:** Centralized Axios client instance and API helpers for frontend-backend interaction.  
**Size:** 2,038 bytes

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: '', // Proxied via Vite
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getOverview = async () => {
  const response = await api.get('/api/stats/overview');
  return response.data;
};

export const getSeverityDistribution = async () => {
  const response = await api.get('/api/stats/severity');
  return response.data;
};

export const getEventTypes = async () => {
  const response = await api.get('/api/stats/event-types');
  return response.data;
};

export const getTimeline = async () => {
  const response = await api.get('/api/stats/timeline');
  return response.data;
};

export const getTopSources = async () => {
  const response = await api.get('/api/stats/top-sources');
  return response.data;
};

export const getGeoData = async () => {
  const response = await api.get('/api/stats/geo');
  return response.data;
};

export const getAlerts = async (params = {}) => {
  const response = await api.get('/api/alerts', { params });
  return response.data;
};

export const getAlertDetail = async (alertId) => {
  const response = await api.get(`/api/alerts/${alertId}`);
  return response.data;
};

export const respondToAlert = async (alertId, action) => {
  const response = await api.post(`/api/alerts/${alertId}/respond`, null, {
    params: { action },
  });
  return response.data;
};

export const sendChatMessage = async (message) => {
  const response = await api.post('/api/chat', { message });
  return response.data;
};

export const trainModel = async () => {
  const response = await api.post('/api/model/train');
  return response.data;
};

export const verifyAlert = async (alertId, status) => {
  const response = await api.post(`/api/alerts/${alertId}/verify`, null, {
    params: { status },
  });
  return response.data;
};

export const getAuditLogs = async (limit = 50) => {
  const response = await api.get('/api/audit', { params: { limit } });
  return response.data;
};

export default api;

```


---

### 📄 File: `frontend/vite.config.js`
**Purpose:** Vite server port configuration and local backend API proxy mapping.  
**Size:** 430 bytes

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      }
    }
  }
})


```


---

### 📄 File: `pyrightconfig.json`
**Purpose:** Pyright configuration for root directory.  
**Size:** 357 bytes

```json
{
  "venvPath": "C:\\Users\\V.AJAY ADHITHYAN\\Desktop\\soc",
  "venv": "venv",
  "pythonVersion": "3.12",
  "pythonPlatform": "Windows",
  "extraPaths": [
    "C:\\Users\\V.AJAY ADHITHYAN\\Desktop\\soc",
    "C:\\Users\\V.AJAY ADHITHYAN\\Desktop\\soc\\venv\\Lib\\site-packages"
  ],
  "reportMissingImports": "none",
  "reportMissingModuleSource": "none"
}

```
