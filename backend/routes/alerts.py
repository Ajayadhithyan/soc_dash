"""
Alert API routes.
Provides endpoints for listing, filtering, and responding to security alerts.
"""

import random
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Union, Dict, Any

from backend import config
from backend.models.schemas import AutoResponseResult
from backend.services.auth import get_current_user
from backend.services.container import get_db, get_container, AppContainer
from backend.services.log_parser import parse_raw_log
from backend.services.alert_processor import process_event

logger = logging.getLogger("soc_backend")
router = APIRouter(prefix="/api/alerts", tags=["alerts"])


def _public_alert(doc: dict) -> dict:
    doc = dict(doc)
    if "_id" in doc:
        doc.setdefault("id", str(doc["_id"]))
        doc.pop("_id", None)
    doc.setdefault("id", str(uuid.uuid4()))
    return doc


async def _find_alert(db, alert_id: str, projection: dict | None = None):
    doc = await db["security_events"].find_one({"id": alert_id}, projection)
    if doc:
        return doc
    try:
        from bson import ObjectId

        doc = await db["security_events"].find_one({"_id": ObjectId(alert_id)}, projection)
        if doc:
            return doc
    except Exception:
        pass
    return await db["security_events"].find_one({"timestamp": alert_id}, projection)


@router.get("")
async def get_alerts(
    db=Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    severity: str = Query(None),
    event_type: str = Query(None),
    sort_by: str = Query("timestamp"),
    sort_order: str = Query("desc"),
    current_user: dict = Depends(get_current_user),
):
    query = {}
    if severity:
        query["severity"] = severity.upper()
    if event_type:
        query["event_type"] = event_type.upper()

    sort_direction = -1 if sort_order == "desc" else 1
    allowed_sort_fields = {"timestamp", "severity", "event_type", "src_ip", "risk_score"}
    if sort_by not in allowed_sort_fields:
        sort_by = "timestamp"
    skip = (page - 1) * per_page

    total = await db["security_events"].count_documents(query)
    cursor = db["security_events"].find(query).sort(sort_by, sort_direction).skip(skip).limit(per_page)

    alerts = []
    async for doc in cursor:
        alerts.append(_public_alert(doc))

    return {"alerts": alerts, "total": total, "page": page, "per_page": per_page}


@router.get("/recent")
async def get_recent_alerts(
    db=Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    cursor = db["security_events"].find({}).sort("timestamp", -1).limit(limit)
    alerts = []
    async for doc in cursor:
        alerts.append(_public_alert(doc))
    return {"alerts": alerts, "count": len(alerts)}


@router.get("/{alert_id}")
async def get_alert_detail(
    alert_id: str,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    doc = await _find_alert(db, alert_id)
    if not doc:
        return {"error": "Alert not found"}

    doc = _public_alert(doc)
    doc["playbook"] = _get_playbook(doc.get("event_type", ""))
    return doc


@router.post("/{alert_id}/respond")
async def auto_respond(
    alert_id: str,
    action: str = Query(...),
    db=Depends(get_db),
    container: AppContainer = Depends(get_container),
    current_user: dict = Depends(get_current_user),
):
    # Role-based access control for destructive actions
    if action in ["block_ip", "quarantine_host"]:
        user_role = current_user.get("role", "analyst")
        if user_role not in ["admin", "senior_analyst"]:
            return {"success": False, "message": f"Insufficient permissions to perform action: {action}"}

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_doc = await _find_alert(db, alert_id)
    src_ip = alert_doc.get("src_ip", "unknown") if alert_doc else "unknown"

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
            "message": "Host isolation initiated. Network segment quarantined.",
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
            "message": "Incident ticket created and assigned to SOC Tier-2 team.",
            "timestamp": now,
            "details": {
                "ticket_id": f"INC-{random.randint(100000, 999999)}",
                "priority": "P1 - Critical",
                "assigned_to": "SOC Tier-2 Team",
                "sla_response": "15 minutes",
            },
        },
        "escalate_to_siem": {
            "success": True,
            "action": "escalate_to_siem",
            "message": "Alert escalated to enterprise SIEM (Splunk/Sentinel) with full correlation context.",
            "timestamp": now,
            "details": {
                "siem_event_id": f"SIEM-{random.randint(100000, 999999)}",
                "forwarded_to": "Splunk ES / Azure Sentinel",
                "correlation_enriched": True,
                "priority": "Critical",
            },
        },
        "notify_slack": {
            "success": True,
            "action": "notify_slack",
            "message": "Slack notification dispatched to #soc-critical-alerts channel.",
            "timestamp": now,
            "details": {
                "channel": "#soc-critical-alerts",
                "webhook_status": "delivered",
                "notification_id": f"SLK-{random.randint(10000, 99999)}",
                "mentioned_groups": ["@soc-team", "@incident-response"],
            },
        },
    }

    result = responses.get(action)
    if not result:
        return {"success": False, "message": f"Unknown action: {action}"}

    if alert_doc:
        await db["security_events"].update_one({"_id": alert_doc["_id"]}, {"$set": {"auto_response": result}})

    analyst_user = current_user.get("sub", "analyst") if current_user else "anonymous"
    audit_entry = {
        "timestamp": now,
        "alert_id": alert_id,
        "action": action,
        "analyst_user": analyst_user,
        "success": True,
        "details": result.get("details", {}),
    }
    await db["audit_logs"].insert_one(audit_entry)

    if action == "block_ip" and src_ip != "unknown":
        container.threat_intel.add_blocked_ip(src_ip)

    return result


@router.post("/{alert_id}/verify")
async def verify_alert(
    alert_id: str,
    status: str = Query(...),
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if status.upper() not in ["TRUE_POSITIVE", "FALSE_POSITIVE"]:
        return {"success": False, "message": f"Invalid verification status: {status}"}

    alert_doc = await _find_alert(db, alert_id)
    if alert_doc:
        res = await db["security_events"].update_one(
            {"_id": alert_doc["_id"]},
            {"$set": {"analyst_verification": status.upper()}},
        )
        if res.matched_count > 0:
            return {"success": True, "message": f"Alert marked as {status.upper()}."}

    return {"success": False, "message": "Alert not found."}


def _get_playbook(event_type):
    playbooks = {
        "SSH_BRUTE_FORCE": {
            "name": "SSH Brute Force Response",
            "steps": [
                "1. Verify if the targeted account has been compromised by checking successful logins.",
                "2. Block the source IP at the perimeter firewall.",
                "3. Enforce account lockout policy (5 failed attempts to 30 min lock).",
                "4. Enable MFA on the targeted account if not already active.",
                "5. Review SSH server configuration: disable root login, use key-based auth.",
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
                "6. If internal source: investigate for compromised host or insider threat.",
            ],
            "severity": "MEDIUM",
            "estimated_time": "10-20 minutes",
        },
        "FAILED_LOGIN": {
            "name": "Authentication Failure Review",
            "steps": [
                "1. Check if this is an isolated event or part of a pattern.",
                "2. Verify the user account is valid and not a service account.",
                "3. If repeated: implement temporary IP-based rate limiting.",
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
                "5. Block the C2 server IP/DNS at firewall level.",
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
                "4. Check if the source host is compromised: run EDR scan.",
                "5. Notify data governance/legal team if PII/sensitive data involved.",
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
                "7. Check for lateral movement or data exfiltration from either session.",
            ],
            "severity": "CRITICAL",
            "estimated_time": "30-45 minutes",
        },
    }
    return playbooks.get(
        event_type,
        {
            "name": "General Response",
            "steps": ["1. Investigate the alert.", "2. Escalate if necessary."],
            "severity": "MEDIUM",
            "estimated_time": "15 minutes",
        },
    )


@router.get("/config/synthetic")
async def get_synthetic_config(current_user: dict = Depends(get_current_user)):
    return {"enabled": config.ENABLE_SYNTHETIC_GENERATOR}


@router.post("/config/synthetic")
async def toggle_synthetic_config(enabled: bool, current_user: dict = Depends(get_current_user)):
    config.ENABLE_SYNTHETIC_GENERATOR = enabled
    logger.info(f"Synthetic generator status set to {enabled} by user {current_user.get('sub')}")
    return {"success": True, "enabled": config.ENABLE_SYNTHETIC_GENERATOR}


class IngestPayload(BaseModel):
    logs: List[Union[str, Dict[str, Any]]]


@router.post("/ingest")
async def ingest_logs(
    payload: IngestPayload,
    db = Depends(get_db),
    container: AppContainer = Depends(get_container),
    current_user: dict = Depends(get_current_user),
):
    ingested_count = 0
    for item in payload.logs:
        if isinstance(item, str):
            raw_event = parse_raw_log(item)
        elif isinstance(item, dict):
            raw_log = item.get("raw_log", "")
            base_parsed = parse_raw_log(raw_log) if raw_log else {}
            raw_event = {**base_parsed, **item}
            raw_event.setdefault("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            raw_event.setdefault("src_ip", "127.0.0.1")
            raw_event.setdefault("dest_ip", "10.0.0.5")
            raw_event.setdefault("event_type", "UNKNOWN")
            raw_event.setdefault("severity", "LOW")
            raw_event.setdefault("user", "unknown")
            raw_event.setdefault("raw_log", "JSON ingest payload")
            raw_event.setdefault("asset_type", "server")
            if "geo" not in raw_event:
                from backend.services.log_parser import resolve_geoip
                raw_event["geo"] = resolve_geoip(raw_event["src_ip"])
        else:
            continue

        enriched = await process_event(
            raw_event,
            container.anomaly_detector,
            container.mitre_mapper,
            container.summarizer,
            container.risk_scorer,
            feedback_classifier=container.feedback_classifier,
            correlation_engine=container.correlation_engine,
            sigma_engine=container.sigma_engine,
            threat_intel=container.threat_intel,
            playbook_engine=container.playbook_engine,
        )

        import uuid
        enriched.setdefault("id", str(uuid.uuid4()))
        await db["security_events"].insert_one(enriched)

        copy_evt = dict(enriched)
        if "_id" in copy_evt:
            copy_evt["_id"] = str(copy_evt["_id"])
        await container.websocket_manager.broadcast({"type": "NEW_ALERT", "data": copy_evt})
        ingested_count += 1

    return {"success": True, "count": ingested_count}
