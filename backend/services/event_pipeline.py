"""
Shared event pipeline.

Runs a raw event through the full ML enrichment pipeline, persists the result
to MongoDB, and broadcasts it to connected WebSocket clients. Used by every
ingest surface (single-event ingest, batch ingest, and endpoint agents) so the
processing path stays identical regardless of the event's origin.
"""

import logging
import uuid
from datetime import datetime, timezone

from backend.services.alert_processor import process_event

logger = logging.getLogger("soc_backend")


async def process_and_persist(container, raw_event: dict) -> dict:
    """
    Run `raw_event` through enrichment, save to `security_events`, and
    broadcast a NEW_ALERT message. Returns the enriched event dict.
    """
    if not raw_event.get("timestamp"):
        raw_event["timestamp"] = datetime.now(timezone.utc).isoformat()

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
        logger.error("Event processing failed: %s", e, exc_info=True)
        raise

    enriched.setdefault("id", str(uuid.uuid4()))
    await container.db["security_events"].insert_one(enriched)

    ws_copy = dict(enriched)
    if "_id" in ws_copy:
        ws_copy["_id"] = str(ws_copy["_id"])

    await container.websocket_manager.broadcast({"type": "NEW_ALERT", "data": ws_copy})
    return enriched