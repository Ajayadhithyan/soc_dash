"""
Ingest API endpoint for receiving real-time security events from external sources.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime, timezone

from backend.services.alert_processor import process_event
from backend.services.container import get_container, AppContainer
from backend.models.schemas import AlertEvent  # for type hint only

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


class IngestPayload(BaseModel):
    """
    Minimal set of fields that the sender must provide.
    Other fields will be filled by defaults or enrichment steps.
    """
    timestamp: Optional[str] = Field(None, description="ISO 8601 timestamp; if omitted, server time is used")
    src_ip: Optional[str] = Field(None, description="Source IP address")
    dest_ip: Optional[str] = Field(None, description="Destination IP address")
    event_type: Optional[str] = Field(None, description="Event type (e.g., PORT_SCAN, MALWARE_DETECTION)")
    severity: Optional[str] = Field(None, description="Severity level (LOW, MEDIUM, HIGH, CRITICAL)")
    user: Optional[str] = Field(None, description="Username associated with the event")
    raw_log: Optional[str] = Field(None, description="Original log line or raw message")
    # Optional enrichment fields
    asset_type: Optional[str] = Field(None, description="Type of asset (server, workstation, etc.)")
    asset_criticality: Optional[float] = Field(None, description="Criticality score of the asset")
    cvss_base: Optional[float] = Field(None, description="Base CVSS score if applicable")


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def ingest_event(
    payload: IngestPayload,
    container: AppContainer = Depends(get_container),
):
    """
    Accept a security event, run it through the full processing pipeline,
    store it in MongoDB, and broadcast it via WebSocket.
    """
    # Convert Pydantic model to dict, dropping None values
    raw_event = payload.dict(exclude_none=True)

    # Ensure we have a timestamp; if missing, use current UTC time in ISO format
    if not raw_event.get("timestamp"):
        raw_event["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Run the event through the same pipeline as the synthetic generator
    try:
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
    except Exception as e:
        # Log the error (in real code, use logger)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Event processing failed: {str(e)}",
        )

    # Ensure we have a unique ID for the event
    enriched.setdefault("id", str(uuid.uuid4()))

    # Persist to MongoDB
    await container.db["security_events"].insert_one(enriched)

    # Prepare a copy for WebSocket broadcast (ensure _id is string)
    ws_copy = dict(enriched)
    if "_id" in ws_copy:
        ws_copy["_id"] = str(ws_copy["_id"])

    # Broadcast to all connected WebSocket clients
    await container.websocket_manager.broadcast({"type": "NEW_ALERT", "data": ws_copy})

    return {"status": "queued", "event_id": enriched["id"]}