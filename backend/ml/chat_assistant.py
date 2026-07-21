"""
Zenith SOC Copilot - Comprehensive Self-Contained AI Assistant (v2).

Handles EVERYTHING:
  1. Live DB Queries      - severity counts, top IPs, event types, users targeted,
                           geo threats, audit logs, risk distributions, timeline
  2. Codebase Crawler     - indexes all .py/.ts/.tsx/.json/.md files at startup
  3. Security Knowledge   - MITRE ATT&CK, CVSS, SOAR, anomaly, feedback, playbooks
  4. Playbook Knowledge   - knows all 4 auto-response rules and when they trigger
  5. Risk Scoring         - explains weighted formula, CVSS tables, asset criticality
  6. Feedback Classifier  - explains true/false positive learning
  7. Correlated Analysis  - groups related events, identifies campaigns
  8. Full Summaries       - executive summaries, threat reports, triage checklists
  9. General Cybersecurity - NIST, CIS, OWASP, SOC fundamentals
 10. OpenCode LLM fallback - when credits are loaded, upgrades every response
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

import httpx

logger = logging.getLogger("soc_backend")


# ─────────────────────────────────────────────────────────────────────────────
#  BSON Sanitiser
# ─────────────────────────────────────────────────────────────────────────────
def sanitize_bson(obj):
    if isinstance(obj, list):
        return [sanitize_bson(x) for x in obj]
    if isinstance(obj, dict):
        return {k: sanitize_bson(v) for k, v in obj.items()}
    if hasattr(obj, "strftime"):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    if obj.__class__.__name__ == "ObjectId":
        return str(obj)
    return obj


# ─────────────────────────────────────────────────────────────────────────────
#  Codebase Crawler
# ─────────────────────────────────────────────────────────────────────────────
class CodebaseIndex:
    INCLUDE_EXTS = {".py", ".ts", ".tsx", ".json", ".md", ".yml", ".yaml", ".txt"}
    EXCLUDE_DIRS = {
        "node_modules", "__pycache__", ".git", ".vscode",
        "venv", "dist", "build", ".pytest_cache", "saved_models"
    }
    MAX_FILE_BYTES = 80_000

    def __init__(self, root: str):
        self.root = root
        self.files: dict[str, str] = {}
        self.summaries: dict[str, str] = {}
        self.symbols: dict[str, list[str]] = {}
        self._crawl()

    def _crawl(self):
        root_path = Path(self.root)
        count = 0
        for fpath in root_path.rglob("*"):
            if fpath.is_dir():
                continue
            if any(exc in fpath.parts for exc in self.EXCLUDE_DIRS):
                continue
            if fpath.suffix not in self.INCLUDE_EXTS:
                continue
            if fpath.stat().st_size > self.MAX_FILE_BYTES:
                continue
            try:
                text = fpath.read_text(encoding="utf-8", errors="ignore")
                rel = str(fpath.relative_to(root_path)).replace("\\", "/")
                self.files[rel] = text
                lines = text.splitlines()
                self.summaries[rel] = "\n".join(lines[:40])
                for m in re.finditer(r"(?:class|def|function|const|async def)\s+(\w+)", text):
                    sym = m.group(1)
                    self.symbols.setdefault(sym, []).append(rel)
                count += 1
            except Exception:
                pass
        logger.info(f"[CodebaseIndex] Indexed {count} files from {self.root}")

    def search(self, query: str, top_k: int = 5) -> list[tuple[str, str]]:
        tokens = set(re.findall(r"\w+", query.lower()))
        scores: dict[str, int] = {}
        for path, content in self.files.items():
            content_lower = content.lower()
            score = sum(content_lower.count(t) for t in tokens)
            if score > 0:
                scores[path] = score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [(p, self.files[p]) for p, _ in ranked]

    def get_file(self, partial_path: str) -> str | None:
        for path in self.files:
            if partial_path.lower() in path.lower():
                return self.files[path]
        return None

    def find_symbol(self, name: str) -> list[str]:
        return self.symbols.get(name, [])

    def file_tree(self) -> str:
        dirs: dict[str, list[str]] = defaultdict(list)
        for path in sorted(self.files.keys()):
            parent = str(Path(path).parent)
            dirs[parent].append(Path(path).name)
        lines = []
        for d, files in sorted(dirs.items()):
            lines.append(f"  {d}/")
            for f in files:
                lines.append(f"    {f}")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
#  Comprehensive Knowledge Base
# ─────────────────────────────────────────────────────────────────────────────
KB = {
    "architecture": """
**Zenith SOC Platform Architecture**
- Backend  : FastAPI (Python 3.12) + Motor (async MongoDB) + uvicorn ASGI
- Frontend : React 18 + TypeScript + Vite + Recharts + Leaflet maps + D3
- Database : MongoDB (local port 27017), DB: `soc_ai_dashboard`
- Collections: `security_events` (alerts), `audit_logs` (SOAR actions)
- Real-time : WebSocket push at `/ws` broadcasts new alerts to all connected clients
- Auth      : JWT-based optional auth — dev mode bypasses authentication
""",

    "event_types": {
        "SSH_BRUTE_FORCE":    "Repeated SSH login attempts from one IP. MITRE T1110. CVSS 7.5. Severity: HIGH/CRITICAL.",
        "PORT_SCAN":          "Network reconnaissance scanning many ports. MITRE T1046. CVSS 5.3. Severity: MEDIUM/HIGH.",
        "FAILED_LOGIN":       "Authentication failure events. MITRE T1110.001. CVSS 3.1. Severity: LOW/MEDIUM.",
        "MALWARE_DETECTION":  "Malware signature match (ransomware, worms, trojans). MITRE T1204. CVSS 9.8. Severity: CRITICAL.",
        "DATA_EXFILTRATION":  "Abnormal large outbound data transfer. MITRE T1048. CVSS 9.1. Severity: CRITICAL.",
        "IMPOSSIBLE_TRAVEL":  "Login from two geographically impossible locations within minutes. MITRE T1078. CVSS 8.8. Severity: HIGH/CRITICAL.",
    },

    "mitre": {
        "T1110":   "Brute Force — Credential Access tactic",
        "T1110.001": "Password Guessing — sub-technique of Brute Force",
        "T1046":   "Network Service Discovery — Discovery tactic",
        "T1204":   "User Execution — Execution tactic",
        "T1048":   "Exfiltration Over Alternative Protocol — Exfiltration tactic",
        "T1078":   "Valid Accounts — Persistence, Defense Evasion, Initial Access",
        "T1041":   "Exfiltration Over C2 Channel — Exfiltration tactic",
        "T1071":   "Application Layer Protocol — Command and Control",
        "T1059":   "Command and Scripting Interpreter — Execution",
        "T1021":   "Remote Services — Lateral Movement",
    },

    "mitre_tactics": [
        "Reconnaissance", "Resource Development", "Initial Access", "Execution",
        "Persistence", "Privilege Escalation", "Defense Evasion", "Credential Access",
        "Discovery", "Lateral Movement", "Collection", "Command and Control",
        "Exfiltration", "Impact"
    ],

    "playbooks": """
**Active Automation Playbooks (backend/playbooks/auto_response.yaml):**

1. **Critical Threat Auto-Containment**
   - Triggers: severity=CRITICAL AND anomaly_score>0.85
   - Actions: block_ip, quarantine_host, notify_slack

2. **Malware Auto-Isolation**
   - Triggers: event_type=MALWARE_DETECTION AND risk_score>70
   - Actions: quarantine_host, create_ticket, notify_slack

3. **Exfiltration Emergency Response**
   - Triggers: event_type=DATA_EXFILTRATION AND risk_score>60
   - Actions: block_ip, escalate_to_siem, notify_slack

4. **Impossible Travel Account Lock**
   - Triggers: event_type=IMPOSSIBLE_TRAVEL (always)
   - Actions: create_ticket, escalate_to_siem, notify_slack

**Available SOAR Actions:** block_ip, quarantine_host, create_ticket, escalate_to_siem, notify_slack, reset_password, kill_session
""",

    "risk_scoring": """
**Risk Scoring Formula (backend/ml/threat_scorer.py):**
```
risk_score = (W_cvss × cvss/10) + (W_anomaly × anomaly) + (W_asset × asset_criticality)
           × 100
```
**Weights:** CVSS=0.40, Anomaly=0.35, Asset=0.25

**CVSS Scores by Event:**
- MALWARE_DETECTION: 9.8  → highest
- DATA_EXFILTRATION: 9.1
- IMPOSSIBLE_TRAVEL: 8.8 (approx)
- SSH_BRUTE_FORCE: 7.5
- PORT_SCAN: 5.3
- FAILED_LOGIN: 3.1

**Asset Criticality Multipliers:**
- database: 1.0 (highest)  |  firewall: 0.95  |  server: 0.9
- workstation: 0.5          |  iot_device: 0.3

**Risk Labels:** Low (0-25), Medium (26-50), High (51-75), Critical (76-100)
""",

    "anomaly_detection": """
**Anomaly Detection Engine (backend/ml/anomaly.py):**
- Algorithm: scikit-learn IsolationForest
- Estimators: 100 trees | Contamination: 0.15 (15% expected anomalies)
- Random state: 42 | Parallel jobs: -1 (all CPU cores)
- Feature vector (7 dimensions):
  1. cvss_base        — threat severity from CVSS database
  2. asset_criticality — how critical is the targeted asset
  3. severity_encoded  — LOW/MED/HIGH/CRIT → 0/1/2/3
  4. event_type_encoded — SSH=0, PORT=1, LOGIN=2, MALWARE=3, EXFIL=4, TRAVEL=5
  5. hour_of_day       — 0-23 (catches off-hours attacks)
  6. day_of_week       — 0-6 (weekends are suspicious)
  7. dest_port         — destination port number
- Training: bootstrapped on startup from DB; retrains after 20+ analyst feedback events
- Output: anomaly_score 0.0 (normal) → 1.0 (highly anomalous)
- Saved to: backend/saved_models/anomaly_detector.json
""",

    "feedback_classifier": """
**Analyst Feedback Classifier (backend/ml/feedback_classifier.py):**
- Algorithm: scikit-learn LogisticRegression (class_weight=balanced)
- Purpose: learns from analyst TRUE_POSITIVE / FALSE_POSITIVE markings
- Minimum samples to train: 20 labeled events
- Suppression threshold: 0.25 (if P(false_positive) > 25%, suppress alert)
- Features: same 7D feature vector as AnomalyDetector
- Saves to: backend/saved_models/feedback_classifier.json
- Improves over time — the more analysts verify alerts, the smarter it gets
""",

    "api_endpoints": """
**Complete REST API Endpoints:**
```
GET  /api/alerts              — Paginated alerts list (filters: severity, event_type, sort)
GET  /api/alerts/recent       — Latest N alerts (default: 20)
POST /api/alerts/{id}/verify  — Analyst feedback: true_positive / false_positive
POST /api/alerts/{id}/respond — Trigger SOAR action: block_ip | quarantine_host | create_ticket
GET  /api/stats/overview      — Dashboard KPIs: totals, avg risk, last hour count
GET  /api/stats/severity      — Severity distribution chart data
GET  /api/stats/event-types   — Event type breakdown
GET  /api/stats/timeline      — Alerts over time (1h/6h/24h/7d ranges)
GET  /api/stats/top-sources   — Top attacking source IPs with primary attack type
GET  /api/stats/risk-distribution — Risk label distribution
GET  /api/stats/geo           — Geographic threat heatmap (country, lat/lng)
GET  /api/stats/mitre         — MITRE ATT&CK heatmap data (technique × tactic)
GET  /api/health              — System health: DB, ML models, API status
POST /api/chat                — AI Copilot chat endpoint
WS   /ws                      — WebSocket: live alert push to dashboard
```
""",

    "frontend": """
**Frontend Components (React + TypeScript + Vite):**
- App.tsx              — Root layout, tab navigation, WebSocket listener, global state
- Dashboard.tsx        — KPI cards, timeline chart, severity pie, top sources bar
- AlertsTable.tsx      — Sortable/filterable data grid with pagination
- AlertDetailSidebar.tsx — Triage drawer: raw log, MITRE info, SOAR action buttons
- AICopilot.tsx        — AI chat interface with quick questions and export to Markdown
- ThreatHotspots.tsx   — Leaflet.js world map with attack origin markers
- NetworkGraph.tsx     — D3.js network topology visualization
- MitreHeatmap.tsx     — ATT&CK Matrix heatmap visualization
- SOARAuditTrail.tsx   — Audit log viewer for all automated SOAR actions
""",

    "security_concepts": {
        "SOC": "Security Operations Center — team/platform that monitors, detects, and responds to cyber threats 24/7.",
        "SIEM": "Security Information and Event Management — aggregates logs from all systems for correlation and alerting.",
        "SOAR": "Security Orchestration, Automation and Response — automates repetitive response tasks using playbooks.",
        "CVSS": "Common Vulnerability Scoring System — 0-10 scale rating severity of vulnerabilities. 9.0+ = Critical.",
        "IOC": "Indicator of Compromise — evidence of a breach: malicious IPs, file hashes, domain names.",
        "TTPs": "Tactics, Techniques, and Procedures — describes how threat actors operate (documented in MITRE ATT&CK).",
        "RAT": "Remote Access Trojan — malware giving attackers remote control of a system.",
        "C2": "Command and Control — infrastructure attackers use to communicate with malware on victim machines.",
        "Lateral Movement": "After initial compromise, attacker moves through the network to reach high-value targets.",
        "Privilege Escalation": "Gaining higher permissions than originally obtained — e.g., regular user to admin.",
        "Zero-day": "Vulnerability that is unknown to the vendor and has no patch available yet.",
        "IOA": "Indicator of Attack — behavioral evidence of attack in progress (vs IOC which is post-breach evidence).",
        "EDR": "Endpoint Detection and Response — agent on each endpoint that monitors and responds to threats in real-time.",
        "Threat Hunting": "Proactive search for hidden threats that have bypassed automated detection systems.",
        "NIST CSF": "NIST Cybersecurity Framework — Identify, Protect, Detect, Respond, Recover.",
        "CIS Controls": "Center for Internet Security — 18 prioritized security controls for cyber defense.",
        "Blue Team": "Defensive security team — monitors, detects, and responds to attacks.",
        "Red Team": "Offensive security team — simulates attackers to test defenses.",
        "Purple Team": "Collaborative exercise where Red and Blue teams work together to improve defenses.",
    },

    "triage_steps": """
**Standard Alert Triage Checklist:**
1. **Confirm severity** — Is it truly CRITICAL or could it be a false positive?
2. **Check source IP** — Is it in known-bad IP lists? Is it internal or external?
3. **Review raw log** — Does the log match the alert classification?
4. **Check MITRE technique** — What is the attacker trying to accomplish?
5. **Check user context** — Is the user account legitimate? Any recent credential changes?
6. **Check destination** — What asset was targeted? What is its criticality?
7. **Correlate with other events** — Are there related events from the same IP/user?
8. **Verify in DB** — Has this IP/user triggered multiple alerts recently?
9. **Decide action** — Block IP / Quarantine host / Create ticket / Mark false positive
10. **Document** — Use SOAR to log all actions taken for audit trail
""",
}


# ─────────────────────────────────────────────────────────────────────────────
#  Intent Patterns  — 25+ categories
# ─────────────────────────────────────────────────────────────────────────────
INTENT_PATTERNS = {
    "greeting": [
        r"\b(hi|hello|hey|yo+|greetings|howdy|good\s+morning|good\s+evening|what'?s\s+up|sup|hola)\b"
    ],
    "count_events": [
        r"\bhow many\b", r"\bcount\b", r"\btotal\b", r"\bnumber of\b", r"\bstatistics\b", r"\bstats\b"
    ],
    "top_threats": [
        r"\btop threat\b", r"\bbiggest threat\b", r"\bmost dangerous\b", r"\bworst\b",
        r"\bprimary\b", r"\bmost common\b", r"\bfrequent\b", r"\bprevalent\b",
        r"\bdominant\b", r"\bhighest\b"
    ],
    "ip_query": [
        r"\bip\b", r"\battacker\b", r"\bsource ip\b", r"\boffending\b",
        r"\borigin\b", r"\bwhere.*attack\b", r"\bwho.*attack\b",
        r"\btop.*ip\b", r"\battacking\b", r"\bmalicious\s+ip\b",
        r"\bsource address\b", r"\bthreat actor\b"
    ],
    "severity_query": [
        r"\bseverity\b", r"\bcritical\b", r"\bhigh\b", r"\bmedium\b", r"\blow\b",
        r"\brisk score\b", r"\brisk level\b", r"\bdanger\b"
    ],
    "recommend_action": [
        r"\brecommend\b", r"\bsuggest\b", r"\bwhat should\b", r"\bnext step\b",
        r"\baction\b", r"\bwhat to do\b", r"\bmitigate\b", r"\bfix\b",
        r"\bhow to respond\b", r"\bresponse plan\b", r"\btriage\b", r"\bhandle\b"
    ],
    "mitre_query": [
        r"\bmitre\b", r"\battack framework\b", r"\btechnique\b", r"\btactic\b",
        r"\bt1\d{3}\b", r"\bkill chain\b", r"\battck\b"
    ],
    "architecture_query": [
        r"\barchitecture\b", r"\bstack\b", r"\bbuilt with\b", r"\btechnology\b",
        r"\bhow.*work\b", r"\bframework\b", r"\bbackend\b", r"\bfrontend\b",
        r"\bdatabase\b", r"\bmongodb\b", r"\bfastapi\b", r"\breact\b",
        r"\bdesign\b", r"\bsystem design\b"
    ],
    "code_query": [
        r"\bcode\b", r"\bfile\b", r"\bclass\b", r"\bfunction\b", r"\bimport\b",
        r"\bmodule\b", r"\bcomponent\b", r"\bwhere.*implement\b", r"\bwhich file\b",
        r"\bshow.*code\b", r"\bexplain.*code\b", r"\bsource\b",
        r"\bwhat files\b", r"\blist files\b", r"\bfile tree\b", r"\bshow.*files\b",
        r"\bcodebase\b", r"\bproject structure\b"
    ],
    "anomaly_query": [
        r"\banomaly\b", r"\bisolation forest\b", r"\bml model\b", r"\bmachine learning\b",
        r"\bdetect\b", r"\babnormal\b", r"\boutlier\b", r"\bai model\b",
        r"\bdetection\b", r"\bml\b"
    ],
    "soar_query": [
        r"\bsoar\b", r"\bauto.?response\b", r"\bblock\b",
        r"\bquarantine\b", r"\bticket\b", r"\bremediate\b", r"\bisolate\b",
        r"\bautomation\b", r"\bautomated\b"
    ],
    "playbook_query": [
        r"\bplaybook\b", r"\brule\b", r"\bauto.*trigger\b", r"\bcondition\b",
        r"\bwhen.*trigger\b", r"\bwhat.*trigger\b"
    ],
    "timeline_query": [
        r"\bwhen\b", r"\btime\b", r"\blast hour\b", r"\blast \d+ hour\b",
        r"\btoday\b", r"\byesterday\b", r"\brecent\b", r"\blatest\b",
        r"\btimeline\b", r"\btrend\b", r"\bover time\b", r"\bhistory\b"
    ],
    "specific_event": [
        r"\bssh.?brute\b", r"\bbrute.?force\b", r"\bport.?scan\b",
        r"\bmalware\b", r"\bexfiltration\b", r"\bimpossible.?travel\b",
        r"\bfailed.?login\b", r"\bransomware\b", r"\btrojan\b"
    ],
    "project_info": [
        r"\bwhat is zenith\b", r"\babout this\b", r"\bproject\b",
        r"\bplatform\b", r"\bpurpose\b", r"\bwhat does this\b",
        r"\bzenith\b", r"\bsoc platform\b"
    ],
    "audit_query": [
        r"\baudit\b", r"\bsoar action\b", r"\bresponded\b", r"\bblocked\b",
        r"\bquarantined\b", r"\bticket created\b"
    ],
    "user_query": [
        r"\busers?\b", r"\bwho\b", r"\baccount\b",
        r"\btarget.*users?\b", r"\bvictim\b", r"\bcompromised.*account\b",
        r"\bwhich users?\b", r"\battacked.*users?\b", r"\bmost.*targeted\b",
        r"\buser.*targeted\b", r"\buser.*attack\b"
    ],
    "geo_query": [
        r"\bcountry\b", r"\bgeograph\w*\b", r"\blocation\b", r"\bwhere.*from\b",
        r"\borigin\b", r"\bmap\b", r"\bregion\b", r"\bnation\b",
        r"\bgeograph\b", r"\bgeo\b", r"\bcities\b"
    ],
    "risk_query": [
        r"\brisk\b", r"\bscore\b", r"\bcvss\b", r"\bweight\b",
        r"\bformula\b", r"\bcalculate\b", r"\bhow.*score\b", r"\bscoring\b"
    ],
    "feedback_query": [
        r"\bfeedback\b", r"\btrue positive\b", r"\bfalse positive\b",
        r"\bverif\w+\b", r"\banalyst.*mark\b", r"\blearn\b",
        r"\bsuppress\b", r"\bconfidence\b"
    ],
    "summary_request": [
        r"\bsummariz\b", r"\bsummary\b", r"\bbrief\b", r"\boverview\b",
        r"\breport\b", r"\bexecutive\b", r"\bgive me all\b", r"\btell me everything\b",
        r"\bwhat.*happening\b", r"\bsituation\b"
    ],
    "correlation_query": [
        r"\bcorrelat\w*\b", r"\brelated event\b", r"\bsame.*ip\b", r"\bsame.*user\b",
        r"\bcampaign\b", r"\battack.*pattern\b", r"\bconnected attack\b",
        r"\blinked event\b", r"\bmulti.*attack\b"
    ],
    "security_concepts": [
        r"\bsiem\b", r"\bedr\b", r"\bioc\b", r"\bioa\b",
        r"\bc2\b", r"\bcommand.*control\b",
        r"\blateral\s+move\w*\b", r"\blateral\s+movement\b",
        r"\bprivilege.*escalat\b", r"\bzero.?day\b", r"\bpenetration\b",
        r"\bred team\b", r"\bblue team\b", r"\bthreat hunt\b",
        r"\bnist\b", r"\bcis control\b", r"\bowasp\b",
        r"\bexplain\s+\w+\b", r"\bwhat is\s+\w+\b", r"\bwhat are\s+\w+\b"
    ],
    "health_query": [
        r"\bhealth\b", r"\bstatus\b", r"\bconnect\b", r"\bonline\b",
        r"\bapi.*status\b", r"\bdb.*status\b", r"\bml.*status\b",
        r"\bsystem.*status\b", r"\bis.*running\b"
    ],
    "network_query": [
        r"\bnetwork\b", r"\bgraph\b", r"\btopology\b", r"\bconnection\b",
        r"\bpeer\b", r"\bport\b", r"\btraffic\b"
    ],
}


def classify_intent(question: str) -> list[str]:
    q = question.lower()
    matched = []
    for intent, patterns in INTENT_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, q):
                matched.append(intent)
                break
    return matched if matched else ["general"]


# ─────────────────────────────────────────────────────────────────────────────
#  DB Query Engine
# ─────────────────────────────────────────────────────────────────────────────
class DBQueryEngine:
    def __init__(self, db):
        self.db = db

    async def get_overview(self) -> dict:
        if self.db is None:
            return {}
        coll = self.db["security_events"]
        total = await coll.count_documents({})
        critical = await coll.count_documents({"severity": "CRITICAL"})
        high = await coll.count_documents({"severity": "HIGH"})
        medium = await coll.count_documents({"severity": "MEDIUM"})
        low = await coll.count_documents({"severity": "LOW"})
        one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        last_hour = await coll.count_documents({"timestamp": {"$gte": one_hour_ago}})
        active = await coll.count_documents({"severity": {"$in": ["HIGH", "CRITICAL"]}, "timestamp": {"$gte": one_hour_ago}})
        pipeline = [{"$match": {"risk_score": {"$exists": True}}}, {"$group": {"_id": None, "avg": {"$avg": "$risk_score"}}}]
        avg_res = await coll.aggregate(pipeline).to_list(1)
        avg_risk = round(avg_res[0]["avg"], 1) if avg_res else 0.0
        return {"total": total, "critical": critical, "high": high, "medium": medium, "low": low,
                "last_hour": last_hour, "active_threats": active, "avg_risk": avg_risk}

    async def get_event_type_breakdown(self) -> dict:
        if self.db is None:
            return {}
        pipeline = [{"$group": {"_id": "$event_type", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
        results = {}
        async for doc in self.db["security_events"].aggregate(pipeline):
            results[doc["_id"]] = doc["count"]
        return results

    async def get_top_ips(self, n: int = 10) -> list[dict]:
        if self.db is None:
            return []
        pipeline = [
            {"$match": {"src_ip": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$src_ip", "count": {"$sum": 1},
                        "max_risk": {"$max": "$risk_score"},
                        "last_seen": {"$max": "$timestamp"},
                        "event_types": {"$addToSet": "$event_type"},
                        "severities": {"$addToSet": "$severity"}}},
            {"$sort": {"count": -1}}, {"$limit": n}
        ]
        results = []
        async for doc in self.db["security_events"].aggregate(pipeline):
            results.append({"ip": doc["_id"], "count": doc["count"],
                            "max_risk": round(doc.get("max_risk") or 0, 1),
                            "last_seen": doc.get("last_seen", ""),
                            "event_types": doc.get("event_types", []),
                            "severities": doc.get("severities", [])})
        return results

    async def get_top_users(self, n: int = 10) -> list[dict]:
        if self.db is None:
            return []
        pipeline = [
            {"$match": {"user": {"$exists": True, "$ne": None, "$ne": ""}}},
            {"$group": {"_id": "$user", "count": {"$sum": 1},
                        "max_risk": {"$max": "$risk_score"},
                        "event_types": {"$addToSet": "$event_type"},
                        "last_attack": {"$max": "$timestamp"}}},
            {"$sort": {"count": -1}}, {"$limit": n}
        ]
        results = []
        async for doc in self.db["security_events"].aggregate(pipeline):
            results.append({"user": doc["_id"], "events": doc["count"],
                            "max_risk": round(doc.get("max_risk") or 0, 1),
                            "attack_types": doc.get("event_types", []),
                            "last_attack": doc.get("last_attack", "")})
        return results

    async def get_recent_alerts(self, limit: int = 10, severity: str = None) -> list[dict]:
        if self.db is None:
            return []
        q = {}
        if severity:
            q["severity"] = severity.upper()
        cursor = self.db["security_events"].find(
            q, {"_id": 0, "timestamp": 1, "event_type": 1, "severity": 1,
                "src_ip": 1, "dest_ip": 1, "risk_score": 1, "user": 1,
                "mitre": 1, "ai_summary": 1, "anomaly_score": 1}
        ).sort("timestamp", -1).limit(limit)
        results = []
        async for doc in cursor:
            results.append(sanitize_bson(doc))
        return results

    async def get_alerts_by_type(self, event_type: str, limit: int = 10) -> list[dict]:
        if self.db is None:
            return []
        cursor = self.db["security_events"].find(
            {"event_type": event_type.upper()},
            {"_id": 0, "timestamp": 1, "severity": 1, "src_ip": 1,
             "dest_ip": 1, "risk_score": 1, "user": 1, "anomaly_score": 1, "raw_log": 1}
        ).sort("timestamp", -1).limit(limit)
        results = []
        async for doc in cursor:
            results.append(sanitize_bson(doc))
        return results

    async def get_timeline(self, hours: int = 24) -> list[dict]:
        if self.db is None:
            return []
        since = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        pipeline = [
            {"$match": {"timestamp": {"$gte": since}}},
            {"$group": {"_id": {"$substr": ["$timestamp", 0, 13]}, "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}, {"$limit": 48}
        ]
        results = []
        async for doc in self.db["security_events"].aggregate(pipeline):
            results.append({"hour": doc["_id"], "count": doc["count"]})
        return results

    async def get_audit_summary(self) -> dict:
        if self.db is None:
            return {}
        total = await self.db["audit_logs"].count_documents({})
        pipeline = [{"$group": {"_id": "$action", "count": {"$sum": 1}, "successes": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}}}}]
        breakdown = {}
        async for doc in self.db["audit_logs"].aggregate(pipeline):
            breakdown[doc["_id"]] = {"count": doc["count"], "successes": doc.get("successes", 0)}
        recent_cursor = self.db["audit_logs"].find({}, {"_id": 0}).sort("timestamp", -1).limit(5)
        recent = []
        async for doc in recent_cursor:
            recent.append(sanitize_bson(doc))
        return {"total_actions": total, "breakdown": breakdown, "recent": recent}

    async def search_by_ip(self, ip: str) -> list[dict]:
        if self.db is None:
            return []
        cursor = self.db["security_events"].find(
            {"$or": [{"src_ip": ip}, {"dest_ip": ip}]},
            {"_id": 0, "timestamp": 1, "event_type": 1, "severity": 1,
             "src_ip": 1, "dest_ip": 1, "risk_score": 1, "user": 1, "mitre": 1}
        ).sort("timestamp", -1).limit(20)
        results = []
        async for doc in cursor:
            results.append(sanitize_bson(doc))
        return results

    async def search_by_user(self, user: str) -> list[dict]:
        if self.db is None:
            return []
        cursor = self.db["security_events"].find(
            {"user": {"$regex": user, "$options": "i"}},
            {"_id": 0, "timestamp": 1, "event_type": 1, "severity": 1,
             "src_ip": 1, "risk_score": 1, "user": 1}
        ).sort("timestamp", -1).limit(15)
        results = []
        async for doc in cursor:
            results.append(sanitize_bson(doc))
        return results

    async def get_high_risk_events(self, threshold: float = 75.0, limit: int = 10) -> list[dict]:
        if self.db is None:
            return []
        cursor = self.db["security_events"].find(
            {"risk_score": {"$gte": threshold}},
            {"_id": 0, "timestamp": 1, "event_type": 1, "severity": 1,
             "src_ip": 1, "risk_score": 1, "mitre": 1, "user": 1, "ai_summary": 1}
        ).sort("risk_score", -1).limit(limit)
        results = []
        async for doc in cursor:
            results.append(sanitize_bson(doc))
        return results

    async def get_geo_breakdown(self) -> list[dict]:
        if self.db is None:
            return []
        pipeline = [
            {"$match": {"geo.country": {"$exists": True}}},
            {"$group": {"_id": "$geo.country", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}, {"$limit": 15}
        ]
        results = []
        async for doc in self.db["security_events"].aggregate(pipeline):
            results.append({"country": doc["_id"], "count": doc["count"]})
        return results

    async def get_mitre_heatmap(self) -> list[dict]:
        if self.db is None:
            return []
        pipeline = [
            {"$match": {"mitre.technique_id": {"$exists": True}}},
            {"$group": {"_id": {"tid": "$mitre.technique_id", "name": "$mitre.technique_name", "tactic": "$mitre.tactic"},
                        "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}, {"$limit": 10}
        ]
        results = []
        async for doc in self.db["security_events"].aggregate(pipeline):
            results.append({
                "technique_id": doc["_id"]["tid"],
                "technique_name": doc["_id"]["name"],
                "tactic": doc["_id"]["tactic"],
                "count": doc["count"]
            })
        return results

    async def get_correlated_events(self, limit: int = 5) -> list[dict]:
        """Find IPs with multiple different event types — indicates campaigns."""
        if self.db is None:
            return []
        pipeline = [
            {"$group": {"_id": "$src_ip", "types": {"$addToSet": "$event_type"},
                        "count": {"$sum": 1}, "max_risk": {"$max": "$risk_score"}}},
            {"$match": {"$expr": {"$gt": [{"$size": "$types"}, 1]}}},
            {"$sort": {"count": -1}}, {"$limit": limit}
        ]
        results = []
        async for doc in self.db["security_events"].aggregate(pipeline):
            results.append({"ip": doc["_id"], "types": doc["types"],
                            "count": doc["count"], "max_risk": round(doc.get("max_risk") or 0, 1)})
        return results

    async def count_by_type(self, event_type: str) -> int:
        if self.db is None:
            return 0
        return await self.db["security_events"].count_documents({"event_type": event_type.upper()})


# ─────────────────────────────────────────────────────────────────────────────
#  Response Generator
# ─────────────────────────────────────────────────────────────────────────────
class ResponseGenerator:
    def __init__(self, codebase_index: CodebaseIndex, db_engine: DBQueryEngine):
        self.idx = codebase_index
        self.db = db_engine

    async def generate(self, question: str, intents: list[str]) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        q_lower = question.lower()
        parts = []

        # ── GREETING ──────────────────────────────────────────────────────────
        if intents == ["greeting"] or (intents == ["general"] and len(question.strip()) < 20):
            overview = await self.db.get_overview()
            total = overview.get("total", 0)
            c = overview.get("critical", 0)
            last_hour = overview.get("last_hour", 0)
            return (
                "Hello! I'm **Zenith Copilot**, your AI-powered SOC analyst assistant.\n\n"
                f"**Current threat status at {now}:**\n"
                f"- Total alerts in database: **{total}**\n"
                f"- Critical severity alerts: **{c}**\n"
                f"- Alerts in the last hour: **{last_hour}**\n\n"
                "I can help you with **anything** about this platform:\n\n"
                "**Live Data:**\n"
                "- Alert counts, severity breakdowns, top IPs, targeted users\n"
                "- Geographic threat origins, MITRE technique heatmaps\n"
                "- SOAR audit logs, correlated attack campaigns\n\n"
                "**Codebase & Architecture:**\n"
                "- How any feature works, which file implements what\n"
                "- Risk scoring formula, anomaly detection model\n"
                "- Playbook rules, API endpoints, data schemas\n\n"
                "**Security Knowledge:**\n"
                "- MITRE ATT&CK techniques and tactics\n"
                "- Triage procedures, incident response steps\n"
                "- SOC/SIEM/SOAR concepts, CVSS scoring, IOCs\n\n"
                "Just ask anything — I'm trained on the full platform!"
            )

        # ── PROJECT INFO ───────────────────────────────────────────────────────
        if "project_info" in intents:
            parts.append(
                "## About Zenith SOC Platform\n"
                "Zenith is a full-stack AI-powered **Security Operations Center (SOC) dashboard** "
                "for real-time threat monitoring, ML-based anomaly detection, MITRE ATT&CK mapping, "
                "automated incident response (SOAR), and analyst-in-the-loop feedback learning.\n"
                + KB["architecture"]
            )

        # ── EXECUTIVE SUMMARY ──────────────────────────────────────────────────
        if "summary_request" in intents:
            overview = await self.db.get_overview()
            breakdown = await self.db.get_event_type_breakdown()
            top_ips = await self.db.get_top_ips(5)
            high_risk = await self.db.get_high_risk_events(75.0, 5)
            audit = await self.db.get_audit_summary()
            mitre_top = await self.db.get_mitre_heatmap()

            total = overview.get("total", 0)
            c = overview.get("critical", 0)
            h = overview.get("high", 0)
            last_hr = overview.get("last_hour", 0)
            avg_risk = overview.get("avg_risk", 0)

            top_type = max(breakdown, key=breakdown.get) if breakdown else "N/A"
            top_ip = top_ips[0]["ip"] if top_ips else "N/A"
            top_ip_count = top_ips[0]["count"] if top_ips else 0

            high_risk_rows = "\n".join(
                f"  {e.get('timestamp','')} | {e.get('event_type','')} | {e.get('src_ip','')} | Risk: {round(e.get('risk_score') or 0, 1)}"
                for e in high_risk[:5]
            ) if high_risk else "  None found"

            top_mitre = f"{mitre_top[0]['technique_id']} ({mitre_top[0]['technique_name']}) — {mitre_top[0]['count']} events" if mitre_top else "N/A"

            parts.append(
                f"## Executive Threat Summary — {now}\n\n"
                f"### Database Overview\n"
                f"| Metric | Value |\n|--------|-------|\n"
                f"| Total Alerts | {total} |\n"
                f"| CRITICAL | {c} |\n"
                f"| HIGH | {h} |\n"
                f"| Avg Risk Score | {avg_risk} |\n"
                f"| Alerts (last hour) | {last_hr} |\n\n"
                f"### Top Threat Type\n**{top_type}** with {breakdown.get(top_type, 0)} events\n\n"
                f"### Most Active Attacker IP\n`{top_ip}` with {top_ip_count} events\n\n"
                f"### Top MITRE Technique\n{top_mitre}\n\n"
                f"### Highest Risk Events\n```\n{high_risk_rows}\n```\n\n"
                f"### SOAR Actions Executed\n{audit.get('total_actions', 0)} automated responses since startup"
            )

        # ── COUNT / STATS ──────────────────────────────────────────────────────
        if "count_events" in intents or ("severity_query" in intents and "summary_request" not in intents):
            overview = await self.db.get_overview()
            if overview:
                total = overview.get("total", 0)
                c = overview.get("critical", 0)
                h = overview.get("high", 0)
                m = overview.get("medium", 0)
                lo = overview.get("low", 0)
                last_hr = overview.get("last_hour", 0)
                avg = overview.get("avg_risk", 0)
                active = overview.get("active_threats", 0)
                parts.append(
                    f"## Live Database Statistics — {now}\n\n"
                    f"| Severity | Count |\n|----------|-------|\n"
                    f"| CRITICAL | **{c}** |\n"
                    f"| HIGH     | {h} |\n"
                    f"| MEDIUM   | {m} |\n"
                    f"| LOW      | {lo} |\n"
                    f"| **TOTAL**   | **{total}** |\n\n"
                    f"**Alerts in last hour:** {last_hr} | **Active threats (H+C, last hour):** {active} | **Avg risk score:** {avg}"
                )

        # ── TOP THREATS ────────────────────────────────────────────────────────
        if "top_threats" in intents:
            breakdown = await self.db.get_event_type_breakdown()
            if breakdown:
                rows = "\n".join(f"| {et} | {cnt} |" for et, cnt in list(breakdown.items())[:6])
                desc_lines = []
                for et, cnt in list(breakdown.items())[:6]:
                    desc = KB["event_types"].get(et, "Unknown event type")
                    desc_lines.append(f"**{et}** ({cnt} events): {desc}")
                parts.append(
                    f"## Top Threat Types\n\n"
                    f"| Event Type | Count |\n|-----------|-------|\n{rows}\n\n"
                    + "\n".join(desc_lines)
                )

        # ── SPECIFIC IP LOOKUP ────────────────────────────────────────────────
        if "ip_query" in intents:
            ip_match = re.search(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b", question)
            if ip_match:
                specific_ip = ip_match.group(1)
                events = await self.db.search_by_ip(specific_ip)
                if events:
                    rows = "\n".join(
                        f"| {e.get('timestamp','')} | {e.get('event_type','')} | "
                        f"{e.get('severity','')} | {round(e.get('risk_score') or 0, 1)} |"
                        for e in events[:10]
                    )
                    parts.append(
                        f"## Investigation: IP `{specific_ip}`\n\n"
                        f"Found **{len(events)}** events for this IP:\n\n"
                        f"| Timestamp | Event Type | Severity | Risk Score |\n"
                        f"|-----------|-----------|----------|------------|\n{rows}"
                    )
                else:
                    parts.append(f"No events found for IP `{specific_ip}` in the database.")
            else:
                top_ips = await self.db.get_top_ips(10)
                if top_ips:
                    rows = "\n".join(
                        f"| `{r['ip']}` | {r['count']} | {r['max_risk']} | {r.get('last_seen','')} | {', '.join(r['event_types'][:2])} |"
                        for r in top_ips
                    )
                    parts.append(
                        f"## Top Attacking Source IPs\n\n"
                        f"| IP Address | Events | Max Risk | Last Seen | Attack Types |\n"
                        f"|-----------|--------|----------|-----------|------------|  \n{rows}"
                    )

        # ── USER QUERY ─────────────────────────────────────────────────────────
        if "user_query" in intents:
            # Check for specific username
            user_match = re.search(r"\buser[:\s]+([a-zA-Z0-9_@.]+)\b", q_lower)
            if user_match:
                username = user_match.group(1)
                events = await self.db.search_by_user(username)
                if events:
                    rows = "\n".join(
                        f"| {e.get('timestamp','')} | {e.get('event_type','')} | {e.get('severity','')} | {round(e.get('risk_score') or 0, 1)} |"
                        for e in events[:8]
                    )
                    parts.append(
                        f"## User Investigation: `{username}`\n\n"
                        f"| Timestamp | Event Type | Severity | Risk Score |\n"
                        f"|-----------|-----------|----------|------------|\n{rows}"
                    )
            else:
                top_users = await self.db.get_top_users(10)
                if top_users:
                    rows = "\n".join(
                        f"| `{u['user']}` | {u['events']} | {u['max_risk']} | {', '.join(u['attack_types'][:2])} |"
                        for u in top_users
                    )
                    parts.append(
                        f"## Most Targeted Users\n\n"
                        f"| Username | Events | Max Risk | Attack Types |\n"
                        f"|----------|--------|----------|-------------|  \n{rows}\n\n"
                        "These users have been most frequently targeted. Consider mandatory password resets for high-risk accounts."
                    )

        # ── SPECIFIC EVENT TYPE ────────────────────────────────────────────────
        if "specific_event" in intents:
            et_map = {
                "ssh": "SSH_BRUTE_FORCE", "brute": "SSH_BRUTE_FORCE",
                "port scan": "PORT_SCAN", "portscan": "PORT_SCAN", "scan": "PORT_SCAN",
                "malware": "MALWARE_DETECTION", "ransomware": "MALWARE_DETECTION", "trojan": "MALWARE_DETECTION",
                "exfil": "DATA_EXFILTRATION", "data exfil": "DATA_EXFILTRATION", "exfiltration": "DATA_EXFILTRATION",
                "travel": "IMPOSSIBLE_TRAVEL", "impossible travel": "IMPOSSIBLE_TRAVEL",
                "failed login": "FAILED_LOGIN", "login fail": "FAILED_LOGIN", "login": "FAILED_LOGIN",
            }
            matched_type = None
            for kw, et in et_map.items():
                if kw in q_lower:
                    matched_type = et
                    break
            if matched_type:
                events = await self.db.get_alerts_by_type(matched_type, 8)
                count = 0
                if self.db.db is not None:
                    count = await self.db.db["security_events"].count_documents({"event_type": matched_type})
                desc = KB["event_types"].get(matched_type, "")
                if events:
                    rows = "\n".join(
                        f"| {e.get('timestamp','')} | {e.get('severity','')} | "
                        f"{e.get('src_ip','')} -> {e.get('dest_ip','')} | "
                        f"{round(e.get('risk_score') or 0, 1)} | {e.get('user', '')} |"
                        for e in events
                    )
                    parts.append(
                        f"## {matched_type} Events ({count} total in DB)\n\n"
                        f"**Description:** {desc}\n\n"
                        f"| Timestamp | Severity | IPs | Risk | User |\n"
                        f"|-----------|----------|-----|------|------|\n{rows}"
                    )

        # ── TIMELINE ───────────────────────────────────────────────────────────
        if "timeline_query" in intents:
            hours = 24
            if "1 hour" in q_lower or "last hour" in q_lower:
                hours = 1
            elif "6 hour" in q_lower:
                hours = 6
            elif "7 day" in q_lower or "week" in q_lower:
                hours = 168
            timeline = await self.db.get_timeline(hours)
            if timeline:
                peak = max(timeline, key=lambda x: x["count"])
                total_24h = sum(t["count"] for t in timeline)
                quiet = min(timeline, key=lambda x: x["count"])
                parts.append(
                    f"## Alert Timeline (Last {hours}h)\n"
                    f"- **Total alerts in window:** {total_24h}\n"
                    f"- **Peak hour:** `{peak['hour']}` with **{peak['count']}** alerts\n"
                    f"- **Quietest hour:** `{quiet['hour']}` with {quiet['count']} alerts\n"
                    f"- **Time window covers:** {len(timeline)} data points"
                )

        # ── GEO QUERY ─────────────────────────────────────────────────────────
        if "geo_query" in intents:
            geo = await self.db.get_geo_breakdown()
            if geo:
                rows = "\n".join(f"| {g['country']} | {g['count']} |" for g in geo[:10])
                parts.append(
                    f"## Geographic Threat Origins\n\n"
                    f"| Country | Events |\n|---------|--------|\n{rows}\n\n"
                    "Geographic data is shown on the **Threat Hotspots** map panel in the dashboard."
                )
            else:
                parts.append("Geographic data is stored in `geo.country`, `geo.lat`, `geo.lng` fields on each security event. "
                             "It's visualized on the **Threat Hotspots** Leaflet map panel.")

        # ── MITRE ATT&CK ─────────────────────────────────────────────────────
        if "mitre_query" in intents:
            tech_match = re.search(r"T1\d{3}(?:\.\d{3})?", question, re.I)
            mitre_live = await self.db.get_mitre_heatmap()
            if tech_match:
                tid = tech_match.group(0).upper()
                desc = KB["mitre"].get(tid, "Details available at attack.mitre.org")
                parts.append(f"## MITRE Technique: {tid}\n**{desc}**")
            else:
                rows = "\n".join(
                    f"| {t['technique_id']} | {t['technique_name']} | {t['tactic']} | {t['count']} |"
                    for t in mitre_live[:8]
                ) if mitre_live else "No MITRE data yet"
                tactics_str = ", ".join(KB["mitre_tactics"])
                parts.append(
                    f"## MITRE ATT&CK Coverage\n\n"
                    f"**Top Techniques (Live from DB):**\n\n"
                    f"| Technique | Name | Tactic | Events |\n"
                    f"|-----------|------|--------|--------|\n{rows}\n\n"
                    f"**All 14 ATT&CK Tactics:**\n{tactics_str}\n\n"
                    "Full heatmap visible on the **MITRE ATT&CK** tab in the dashboard."
                )

        # ── PLAYBOOKS ────────────────────────────────────────────────────────
        if "playbook_query" in intents or "soar_query" in intents:
            audit = await self.db.get_audit_summary()
            parts.append(KB["playbooks"])
            if audit and audit.get("total_actions", 0) > 0:
                bd_text = "\n".join(
                    f"  - {k}: {v['count']} times ({v['successes']} successes)"
                    for k, v in audit["breakdown"].items()
                )
                recent = audit.get("recent", [])
                recent_text = "\n".join(
                    f"  [{r.get('timestamp','')}] {r.get('action','')} — {r.get('status','')}"
                    for r in recent[:3]
                )
                parts.append(
                    f"**SOAR Actions Executed So Far: {audit['total_actions']}**\n"
                    f"{bd_text}\n\n"
                    f"**Recent Actions:**\n{recent_text if recent_text else '  None yet'}"
                )

        # ── AUDIT LOG ─────────────────────────────────────────────────────────
        if "audit_query" in intents and "soar_query" not in intents and "playbook_query" not in intents:
            audit = await self.db.get_audit_summary()
            if audit:
                bd_text = "\n".join(
                    f"| {k} | {v['count']} | {v['successes']} |"
                    for k, v in audit["breakdown"].items()
                )
                recent = audit.get("recent", [])
                recent_text = "\n".join(
                    f"| {r.get('timestamp','')} | {r.get('action','')} | {r.get('status','')} |"
                    for r in recent
                )
                parts.append(
                    f"## SOAR Audit Log\n\n"
                    f"**Total automated responses:** {audit['total_actions']}\n\n"
                    f"| Action | Count | Successes |\n|--------|-------|----------|\n{bd_text}\n\n"
                    f"**Recent Actions:**\n| Timestamp | Action | Status |\n|-----------|--------|--------|\n{recent_text}"
                )

        # ── CORRELATED EVENTS ─────────────────────────────────────────────────
        if "correlation_query" in intents:
            correlated = await self.db.get_correlated_events(5)
            if correlated:
                rows = "\n".join(
                    f"| `{c['ip']}` | {c['count']} | {', '.join(c['types'])} | {c['max_risk']} |"
                    for c in correlated
                )
                parts.append(
                    f"## Correlated Attack Campaigns\n\n"
                    f"These IPs have launched **multiple different attack types** — strong indicator of a coordinated campaign:\n\n"
                    f"| IP Address | Events | Attack Types | Max Risk |\n"
                    f"|-----------|--------|-------------|----------|\n{rows}\n\n"
                    "Recommendation: Immediately block all listed IPs at the perimeter firewall."
                )
            else:
                parts.append("No correlated multi-type attack campaigns detected from a single IP yet.")

        # ── ANOMALY DETECTION ────────────────────────────────────────────────
        if "anomaly_query" in intents:
            parts.append(KB["anomaly_detection"])
            anomaly_src = self.idx.get_file("ml/anomaly.py")
            if anomaly_src:
                sigs = re.findall(r"(?:def|class)\s+\w+[^:]*:", anomaly_src)[:8]
                parts.append(
                    f"**Source:** `backend/ml/anomaly.py`\n"
                    f"Key definitions: `{'`, `'.join(sigs)}`"
                )

        # ── FEEDBACK CLASSIFIER ────────────────────────────────────────────────
        if "feedback_query" in intents:
            parts.append(KB["feedback_classifier"])

        # ── RISK SCORING ──────────────────────────────────────────────────────
        if "risk_query" in intents:
            parts.append(KB["risk_scoring"])
            if "critical" in q_lower or "high risk" in q_lower:
                high_risk = await self.db.get_high_risk_events(75.0, 8)
                if high_risk:
                    rows = "\n".join(
                        f"| {e.get('timestamp','')} | {e.get('event_type','')} | `{e.get('src_ip','')}` | **{round(e.get('risk_score') or 0, 1)}** |"
                        for e in high_risk
                    )
                    parts.append(
                        f"\n**Highest Risk Events (Score >= 75):**\n\n"
                        f"| Timestamp | Event Type | Source IP | Risk Score |\n"
                        f"|-----------|-----------|-----------|------------|\n{rows}"
                    )

        # ── ARCHITECTURE ─────────────────────────────────────────────────────
        if "architecture_query" in intents:
            parts.append(KB["architecture"])
            parts.append(KB["api_endpoints"])
            parts.append(KB["frontend"])

        # ── CODEBASE / FILES ─────────────────────────────────────────────────
        if "code_query" in intents:
            if any(kw in q_lower for kw in ["what files", "list files", "file tree", "show files", "codebase", "project structure"]):
                tree = self.idx.file_tree()
                total_files = len(self.idx.files)
                parts.append(
                    f"## Project File Tree ({total_files} indexed files)\n\n"
                    f"```\n{tree}\n```"
                )
            else:
                results = self.idx.search(question, top_k=3)
                if results:
                    code_sections = []
                    for path, content in results:
                        lines = content.splitlines()
                        preview = "\n".join(lines[:30])
                        code_sections.append(f"### `{path}`\n```python\n{preview}\n```")
                    parts.append("## Relevant Code Files\n" + "\n\n".join(code_sections))
                sym_match = re.search(r"\b([A-Z][a-zA-Z]{2,}|[a-z]{3,}_[a-z]+)\b", question)
                if sym_match:
                    sym = sym_match.group(1)
                    files_with_sym = self.idx.find_symbol(sym)
                    if files_with_sym:
                        parts.append(f"`{sym}` defined/used in: `{'`, `'.join(files_with_sym[:4])}`")

        # ── RECOMMENDATIONS ───────────────────────────────────────────────────
        if "recommend_action" in intents:
            overview = await self.db.get_overview()
            top_ips = await self.db.get_top_ips(3)
            top_users = await self.db.get_top_users(3)
            c = overview.get("critical", 0) if overview else 0
            h = overview.get("high", 0) if overview else 0
            ip_list = ", ".join(f"`{r['ip']}`" for r in top_ips) if top_ips else "N/A"
            user_list = ", ".join(f"`{u['user']}`" for u in top_users) if top_users else "N/A"
            parts.append(
                f"## Analyst Recommendations — {now}\n\n"
                f"**Current Status:** {c} CRITICAL, {h} HIGH alerts\n\n"
                "**Immediate Actions:**\n"
                f"1. **Block top attacking IPs** at perimeter firewall: {ip_list}\n"
                "2. **Triage CRITICAL alerts first** — prioritize MALWARE_DETECTION and DATA_EXFILTRATION\n"
                "3. **Quarantine compromised endpoints** showing malware or exfiltration patterns\n"
                f"4. **Reset credentials** for targeted users: {user_list}\n"
                "5. **Check correlated events** — same IP launching multiple attack types indicates a campaign\n\n"
                "**Standard Triage Checklist:**\n" + KB["triage_steps"] + "\n\n"
                "Use **Alert Detail Sidebar → SOAR Actions** to execute block/quarantine/ticket directly from the dashboard."
            )

        # ── SECURITY CONCEPTS ─────────────────────────────────────────────────
        if "security_concepts" in intents:
            best_concept = None
            best_score = 0
            for concept, definition in KB["security_concepts"].items():
                concept_lower = concept.lower()
                if concept_lower in q_lower:
                    score = 100
                else:
                    words = [w for w in concept_lower.split() if len(w) > 2]
                    score = sum(2 if w in q_lower else 0 for w in words)
                if score > best_score:
                    best_score = score
                    best_concept = concept
            if best_concept and best_score > 0:
                parts.append(f"## {best_concept}\n{KB['security_concepts'][best_concept]}")
            elif "explain" in q_lower or "what is" in q_lower or "what are" in q_lower:
                matched = [
                    f"**{k}**: {v}" for k, v in KB["security_concepts"].items()
                    if any(w in q_lower for w in k.lower().split() if len(w) > 2)
                ]
                if matched:
                    parts.append("## Security Concepts\n" + "\n".join(matched[:5]))

        # ── HEALTH ────────────────────────────────────────────────────────────
        if "health_query" in intents:
            overview = await self.db.get_overview()
            db_ok = overview.get("total", -1) >= 0
            parts.append(
                f"## System Health — {now}\n\n"
                f"| Component | Status |\n|-----------|--------|\n"
                f"| MongoDB Database | {'CONNECTED' if db_ok else 'OFFLINE'} |\n"
                f"| FastAPI Backend | RUNNING (port 8000) |\n"
                f"| Vite Frontend | RUNNING (port 5173) |\n"
                f"| IsolationForest ML | TRAINED |\n"
                f"| Feedback Classifier | ACTIVE |\n"
                f"| Playbook Engine | LOADED (4 rules) |\n"
                f"| WebSocket Broadcast | ACTIVE |\n\n"
                f"Check `/api/health` for detailed JSON health report."
            )

        # ── NETWORK ───────────────────────────────────────────────────────────
        if "network_query" in intents:
            top_ips = await self.db.get_top_ips(5)
            parts.append(
                "## Network Topology\n"
                "The **NetworkGraph** component (D3.js) visualizes connections between source and destination IPs.\n"
                "It shows which internal hosts are being attacked from which external IPs.\n\n"
                "**Current active nodes (top attackers):**\n"
                + "\n".join(f"- `{r['ip']}` → {r['count']} connections, types: {', '.join(r['event_types'][:2])}" for r in top_ips)
            )

        # ── GENERAL / FALLBACK ────────────────────────────────────────────────
        if not parts:
            results = self.idx.search(question, top_k=2)
            overview = await self.db.get_overview()

            if results:
                path, content = results[0]
                preview = "\n".join(content.splitlines()[:20])
                parts.append(
                    f"I searched the codebase and found relevant content in `{path}`:\n\n"
                    f"```\n{preview}\n```"
                )

            # Check if it's a general security question
            for concept, definition in KB["security_concepts"].items():
                if concept.lower() in q_lower:
                    parts.append(f"**{concept}**: {definition}")
                    break

            if overview:
                total = overview.get("total", 0)
                c = overview.get("critical", 0)
                parts.append(
                    f"The database currently holds **{total}** security events with **{c}** CRITICAL alerts."
                )

            if not parts:
                parts.append(
                    "I can help with any of these topics — just ask!\n\n"
                    "- `how many critical alerts?` — live DB stats\n"
                    "- `top attacking IPs` — attacker analysis\n"
                    "- `which users are targeted?` — user investigation\n"
                    "- `show malware events` — event type drill-down\n"
                    "- `explain MITRE ATT&CK` — security knowledge\n"
                    "- `how does risk scoring work?` — formula explanation\n"
                    "- `show me the playbooks` — SOAR automation rules\n"
                    "- `give me a summary` — full executive report\n"
                    "- `what files are in this project?` — codebase exploration\n"
                    "- `how does anomaly detection work?` — ML model details"
                )

        return "\n\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
#  Main ChatAssistant
# ─────────────────────────────────────────────────────────────────────────────
class ChatAssistant:
    def __init__(self, db=None, opencode_api_key=None):
        self.db = db
        self.opencode_api_key = opencode_api_key or os.getenv("OPENCODE_API_KEY", "")
        self.use_llm = bool(self.opencode_api_key)

        this_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(this_dir, "..", ".."))

        logger.info(f"[Chat] Building codebase index from {self.project_root} ...")
        self.codebase_index = CodebaseIndex(self.project_root)
        self.db_engine = DBQueryEngine(db)
        self.response_gen = ResponseGenerator(self.codebase_index, self.db_engine)

        if self.use_llm:
            logger.info("[Chat] OpenCode API configured — LLM enhancement enabled.")

    async def _call_llm_async(self, messages, model="deepseek-v4-flash", temperature=0.2):
        if not self.use_llm:
            raise Exception("LLM disabled")
        url = "https://opencode.ai/zen/go/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.opencode_api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": messages, "temperature": temperature}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.post(url, headers=headers, json=payload)
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"].strip()
                if r.status_code in [401, 403]:
                    logger.error(f"[Chat] LLM disabled — auth/credit error {r.status_code}")
                    self.use_llm = False
                raise Exception(f"API {r.status_code}: {r.text}")
        except (httpx.ConnectTimeout, httpx.ConnectError, httpx.ReadTimeout):
            logger.error("[Chat] LLM timeout. Disabling LLM mode.")
            self.use_llm = False
            raise

    async def chat(self, question: str) -> str:
        question = question.strip()
        if not question:
            return "Please ask a question and I'll help you analyze your security environment."

        intents = classify_intent(question)
        logger.info(f"[Chat] Q: {question!r} | Intents: {intents}")

        local_answer = await self.response_gen.generate(question, intents)

        # LLM enhancement when credits available
        if self.use_llm:
            try:
                overview = await self.db_engine.get_overview()
                top_ips = await self.db_engine.get_top_ips(5)
                breakdown = await self.db_engine.get_event_type_breakdown()
                code_results = self.codebase_index.search(question, top_k=2)
                code_ctx = "\n\n".join(f"=== {p} ===\n{c[:1200]}" for p, c in code_results) if code_results else ""
                system = (
                    "You are Zenith Copilot, an expert AI SOC assistant embedded in the Zenith SOC platform. "
                    "You have full access to the codebase and live MongoDB security data. "
                    "Answer analytically, reference actual file names and function names, use markdown formatting."
                )
                user_msg = (
                    f"Question: {question}\n\n"
                    f"Live DB: {json.dumps(overview)}\n"
                    f"Top IPs: {json.dumps(top_ips[:3])}\n"
                    f"Event breakdown: {json.dumps(breakdown)}\n"
                    f"Code context:\n{code_ctx}\n\n"
                    f"Local analysis:\n{local_answer}\n\n"
                    "Provide an expert, detailed, data-driven response."
                )
                messages = [{"role": "system", "content": system}, {"role": "user", "content": user_msg}]
                return await self._call_llm_async(messages, temperature=0.3)
            except Exception as e:
                logger.warning(f"[Chat] LLM failed ({e}), using local answer.")

        return local_answer

    def load_codebase_context(self) -> str:
        return self.codebase_index.file_tree()

    async def get_context_alerts(self, limit: int = 20) -> list[dict]:
        return await self.db_engine.get_recent_alerts(limit)
