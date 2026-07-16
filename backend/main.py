"""
Main entrypoint for the FastAPI backend server.
Coordinates WebSocket broadcasts, ML pipelines, API routing, and synthetic event generation.
"""

import asyncio
import logging
import json
import sys
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend import config
from backend.services.container import container
from backend.services.rate_limiter import RateLimitMiddleware
from backend.routes import alerts, chat, stats, audit, auth
from backend.services.alert_processor import generate_event, process_event

# Structured JSON logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "exc_info") and record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger("soc_backend")

bg_generator_task = None


async def create_indexes(db):
    """Create MongoDB indexes for performance."""
    try:
        await db["security_events"].create_index("timestamp")
        await db["security_events"].create_index("severity")
        await db["security_events"].create_index("event_type")
        await db["security_events"].create_index("src_ip")
        await db["security_events"].create_index("risk_score")
        await db["audit_logs"].create_index("timestamp")
        logger.info("[Database] MongoDB indexes created successfully.")
    except Exception as e:
        logger.error(f"[Database] Failed to create indexes: {e}")


async def run_data_generator():
    """Background task that generates synthetic events, runs the pipeline, saves to DB, and broadcasts."""
    logger.info("Starting background security event generator...")
    try:
        await asyncio.sleep(2)
        db = container.db
        ws_mgr = container.websocket_manager

        async def _process_and_broadcast(raw_event):
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
            await db["security_events"].insert_one(enriched)

            copy = dict(enriched)
            if "_id" in copy:
                copy["_id"] = str(copy["_id"])
            if "id" not in copy:
                copy["id"] = f"{copy.get('timestamp')}_{copy.get('src_ip')}"

            await ws_mgr.broadcast({"type": "NEW_ALERT", "data": copy})
            return copy

        logger.info("Pre-populating 5 fresh security alerts...")
        for i in range(5):
            try:
                result = await _process_and_broadcast(generate_event())
                logger.info(f"Pre-populated startup alert {i+1}/5: {result.get('event_type')}")
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Error pre-populating startup event: {e}")

        new_events_count = 0
        while True:
            try:
                result = await _process_and_broadcast(generate_event())
                logger.info(f"Processed and broadcast alert: {result.get('event_type')} (Risk: {result.get('risk_score')})")

                new_events_count += 1
                if new_events_count >= 20:
                    logger.info("Auto-retraining Isolation Forest anomaly model...")
                    try:
                        past_events = []
                        cursor = db["security_events"].find({}).sort("timestamp", -1).limit(500)
                        async for doc in cursor:
                            past_events.append(doc)
                        if len(past_events) >= 10:
                            container.anomaly_detector.train(past_events)
                            new_events_count = 0
                    except Exception as train_err:
                        logger.error(f"Auto-train error: {train_err}")

            except Exception as e:
                logger.error(f"Error in data generator iteration: {e}", exc_info=True)

            await asyncio.sleep(config.EVENT_GENERATION_INTERVAL)

    except asyncio.CancelledError:
        logger.info("Background security event generator stopped.")
    except Exception as e:
        logger.error(f"Unexpected error in background generator: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global bg_generator_task

    # 1. Start DI container
    await container.start()
    db = container.db

    # 2. Create indexes
    await create_indexes(db)

    # 3. Bootstrap ML training
    logger.info("Retrieving past security events to train Isolation Forest baseline...")
    try:
        past_events = []
        cursor = db["security_events"].find({}).sort("timestamp", -1).limit(500)
        async for doc in cursor:
            past_events.append(doc)
        if len(past_events) >= 10:
            container.anomaly_detector.train(past_events)
        else:
            logger.info("Insufficient historical events. Model will auto-train as events stream in.")
    except Exception as e:
        logger.error(f"Failed to bootstrap train ML anomaly engine: {e}")

    # 4. Bootstrap feedback classifier
    try:
        labeled_events = []
        cursor = db["security_events"].find({"analyst_verification": {"$exists": True}}).limit(500)
        async for doc in cursor:
            labeled_events.append(doc)
        if labeled_events:
            container.feedback_classifier.train(labeled_events)
    except Exception as e:
        logger.error(f"Failed to bootstrap feedback classifier: {e}")

    # 5. Bootstrap correlation engine
    try:
        recent_events = []
        cursor = db["security_events"].find({}).sort("timestamp", -1).limit(100)
        async for doc in cursor:
            recent_events.append(doc)
        recent_events.reverse()
        container.correlation_engine.bootstrap(recent_events)
    except Exception as e:
        logger.error(f"Failed to bootstrap correlation engine: {e}")

    # 6. Start background generator
    bg_generator_task = asyncio.create_task(run_data_generator())

    yield

    # Shutdown
    logger.info("Stopping FastAPI application...")
    if bg_generator_task:
        bg_generator_task.cancel()
        try:
            await bg_generator_task
        except asyncio.CancelledError:
            pass
    await container.shutdown()


app = FastAPI(
    title="AI-Powered SOC Analyst Dashboard Backend",
    description="REST API and WebSocket feed for cybersecurity threat operations.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware, max_requests=120, window_seconds=60)

app.include_router(alerts.router)
app.include_router(stats.router)
app.include_router(chat.router)
app.include_router(audit.router)
app.include_router(auth.router)


@app.get("/")
@app.get("/api/health")
def read_root():
    ad = container.anomaly_detector
    return {
        "status": "online",
        "service": "SOC AI Dashboard API",
        "database": "connected" if container.db is not None else "disconnected",
        "gemini_api": "configured" if bool(config.GEMINI_API_KEY) else "fallback_mode",
        "anomaly_detector": "trained" if ad and ad.is_trained else "untrained",
    }


@app.post("/api/model/train")
async def train_model():
    logger.info("Manual training request received for Isolation Forest...")
    try:
        db = container.db
        events = []
        cursor = db["security_events"].find({}).sort("timestamp", -1).limit(500)
        async for doc in cursor:
            events.append(doc)

        if len(events) >= 10:
            container.anomaly_detector.train(events)
            return {"success": True, "message": f"Successfully trained model on {len(events)} events.", "anomaly_detector": "trained"}
        else:
            return {"success": False, "message": "Need at least 10 events to train.", "anomaly_detector": "untrained"}
    except Exception as e:
        logger.error(f"Failed to manually train ML anomaly engine: {e}")
        return {"success": False, "message": f"Failed to train ML engine: {str(e)}", "anomaly_detector": "trained" if container.anomaly_detector.is_trained else "untrained"}


@app.post("/api/model/train-feedback")
async def train_feedback_model():
    logger.info("Manual feedback classifier training requested...")
    try:
        db = container.db
        labeled_events = []
        cursor = db["security_events"].find({"analyst_verification": {"$exists": True}}).limit(500)
        async for doc in cursor:
            labeled_events.append(doc)

        if len(labeled_events) >= container.feedback_classifier.min_samples:
            container.feedback_classifier.train(labeled_events)
            return {"success": True, "message": f"Feedback classifier trained on {len(labeled_events)} events.", "classifier_trained": True}
        else:
            return {"success": False, "message": f"Need at least {container.feedback_classifier.min_samples} labeled events.", "classifier_trained": False}
    except Exception as e:
        logger.error(f"Failed to train feedback classifier: {e}")
        return {"success": False, "message": f"Training error: {str(e)}", "classifier_trained": container.feedback_classifier.is_trained}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    ws_mgr = container.websocket_manager
    await ws_mgr.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        ws_mgr.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket communication error: {e}")
        ws_mgr.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
