"""
Ingest API endpoint for receiving real-time security events from external sources.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

from backend.services.container import get_container, AppContainer
from backend.services.event_pipeline import process_and_persist

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

    # Run the event through the same pipeline as the synthetic generator
    try:
        enriched = await process_and_persist(container, raw_event)
    except Exception as e:
        # Log the error (in real code, use logger)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Event processing failed: {str(e)}",
        )

    return {"status": "queued", "event_id": enriched["id"]}