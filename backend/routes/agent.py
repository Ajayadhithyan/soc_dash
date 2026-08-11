"""
Agent API endpoints.

Receives telemetry from Endpoint Detection Agents:
    * POST /api/agent/ingest     — batched normalized security events
    * POST /api/agent/heartbeat  — endpoint liveness + resource usage
    * GET  /api/agent/endpoints  — endpoint inventory for the dashboard

Agents authenticate with an API token in the `X-Agent-Token` header. The
agent identity (agent_id) is derived from the verified token, never from the
payload, so agents cannot spoof another endpoint's identity.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

from pydantic import BaseModel, Field

from backend import config
from backend.services.container import AppContainer, get_container
from backend.services.event_pipeline import process_and_persist
from backend.services.auth import get_current_user

logger = logging.getLogger("soc_backend")

router = APIRouter(prefix="/api/agent", tags=["agent"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class AgentEvent(BaseModel):
    """A single normalized telemetry event produced by an endpoint agent."""
    timestamp: Optional[str] = Field(None, description="ISO 8601 timestamp; server time used if omitted")
    src_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    event_type: str = Field("UNKNOWN", description="e.g. PROCESS_STARTED, NETWORK_CONNECTION")
    severity: Optional[str] = Field("LOW", description="LOW, MEDIUM, HIGH, CRITICAL")
    user: Optional[str] = "unknown"
    raw_log: Optional[str] = ""
    category: Optional[str] = Field(None, description="Telemetry source: PROCESS, NETWORK, LOGIN, ...")
    hostname: Optional[str] = None
    os: Optional[str] = None
    metadata: dict = Field(default_factory=dict, description="Monitor-specific details")
    asset_type: Optional[str] = Field(None, description="server, workstation, ...")
    asset_criticality: Optional[float] = None
    cvss_base: Optional[float] = None


class AgentIngestRequest(BaseModel):
    """Batch of events forwarded by one agent."""
    events: List[AgentEvent] = Field(default_factory=list)
    agent_id: Optional[str] = None
    hostname: Optional[str] = None


class HeartbeatPayload(BaseModel):
    """Periodic endpoint health report."""
    hostname: str = ""
    os: str = ""
    os_version: str = ""
    agent_version: str = ""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_percent: float = 0.0
    ip: str = ""


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------

async def verify_agent(
    request: Request,
    container: AppContainer = Depends(get_container),
) -> dict:
    """Validate the X-Agent-Token header; returns the agent identity dict."""
    token = request.headers.get("x-agent-token")
    identity = await container.agent_auth.verify(token)
    if not identity:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing agent token.",
        )
    return identity


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_events(
    payload: AgentIngestRequest,
    identity: dict = Depends(verify_agent),
    container: AppContainer = Depends(get_container),
):
    """
    Accept a batch of agent events, run each through the standard enrichment
    pipeline, persist to MongoDB, and broadcast via WebSocket.
    """
    agent_id = identity["agent_id"]
    accepted = 0
    failed = []
    now = datetime.now(timezone.utc)

    for idx, evt in enumerate(payload.events):
        raw_event = evt.model_dump(exclude_none=True)
        raw_event.setdefault("timestamp", now.isoformat())
        raw_event.setdefault("src_ip", "0.0.0.0")
        raw_event.setdefault("dest_ip", "0.0.0.0")
        raw_event.setdefault("severity", "LOW")
        raw_event.setdefault("user", "unknown")
        raw_event.setdefault("raw_log", "")
        raw_event["agent_id"] = agent_id
        raw_event.setdefault("hostname", identity.get("hostname") or payload.hostname or "")
        try:
            await process_and_persist(container, raw_event)
            accepted += 1
        except Exception as e:
            logger.error("[Agent] Failed to process event %d from %s: %s", idx, agent_id, e)
            failed.append({"index": idx, "error": str(e)})

    return {
        "status": "queued",
        "agent_id": agent_id,
        "total": len(payload.events),
        "accepted": accepted,
        "failed": failed,
    }


@router.post("/heartbeat")
async def heartbeat(
    payload: HeartbeatPayload,
    identity: dict = Depends(verify_agent),
    container: AppContainer = Depends(get_container),
):
    """
    Record endpoint liveness and resource usage. Upserts the `endpoints`
    collection keyed by the verified agent identity.
    """
    agent_id = identity["agent_id"]
    now = datetime.now(timezone.utc)
    last_seen = now.isoformat()

    await container.db["endpoints"].update_one(
        {"agent_id": agent_id},
        {
            "$set": {
                "agent_id": agent_id,
                "hostname": payload.hostname or identity.get("hostname") or agent_id,
                "os": payload.os,
                "os_version": payload.os_version,
                "agent_version": payload.agent_version,
                "cpu_percent": payload.cpu_percent,
                "memory_percent": payload.memory_percent,
                "disk_percent": payload.disk_percent,
                "ip": payload.ip,
                "status": "ONLINE",
                "last_seen": last_seen,
            }
        },
        upsert=True,
    )

    logger.debug("[Agent] Heartbeat received from %s (%s)", agent_id, payload.hostname)
    return {"success": True, "status": "ONLINE", "last_seen": last_seen}


@router.get("/endpoints")
async def list_endpoints(
    container: AppContainer = Depends(get_container),
    current_user: dict = Depends(get_current_user),
):
    """
    Return the endpoint inventory with computed online/offline status.
    Requires a JWT (dashboard users only).
    """
    timeout_seconds = config.AGENT_OFFLINE_TIMEOUT_SECONDS
    now = datetime.now(timezone.utc)

    endpoints = []
    cursor = container.db["endpoints"].find({}).sort("last_seen", -1)
    async for doc in cursor:
        try:
            last_seen_dt = datetime.fromisoformat(doc.get("last_seen", ""))
            is_online = (now - last_seen_dt).total_seconds() <= timeout_seconds
        except (ValueError, TypeError):
            is_online = False

        event_count = 0
        try:
            event_count = await container.db["security_events"].count_documents(
                {"agent_id": doc.get("agent_id")}
            )
        except Exception:
            pass

        endpoints.append(
            {
                "agent_id": doc.get("agent_id"),
                "hostname": doc.get("hostname", ""),
                "os": doc.get("os", ""),
                "os_version": doc.get("os_version", ""),
                "agent_version": doc.get("agent_version", ""),
                "cpu_percent": doc.get("cpu_percent", 0.0),
                "memory_percent": doc.get("memory_percent", 0.0),
                "disk_percent": doc.get("disk_percent", 0.0),
                "ip": doc.get("ip", ""),
                "status": "ONLINE" if is_online else "OFFLINE",
                "is_online": is_online,
                "last_seen": doc.get("last_seen", ""),
                "event_count": event_count,
            }
        )

    return {"endpoints": endpoints, "total": len(endpoints), "offline_timeout_seconds": timeout_seconds}