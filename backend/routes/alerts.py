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

    return result


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
    }
    return playbooks.get(event_type, {
        "name": "General Response",
        "steps": ["1. Investigate the alert.", "2. Escalate if necessary."],
        "severity": "MEDIUM",
        "estimated_time": "15 minutes",
    })
