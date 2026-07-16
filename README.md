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
