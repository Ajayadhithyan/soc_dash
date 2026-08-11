"""
Main entrypoint for the FastAPI backend server.
Coordinates WebSocket broadcasts, ML pipelines, API routing, and synthetic event generation.
"""

import asyncio
import logging
import json
import sys
import uuid
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

# Add project root to sys.path to allow running from any directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend import config
from backend.services.container import container
from backend.services.rate_limiter import RateLimitMiddleware
from backend.routes import alerts, chat, stats, audit, auth, ingest, agent
from backend.services.auth import get_current_user, verify_jwt
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
        await db["security_events"].create_index("id", unique=True, sparse=True)
        await db["audit_logs"].create_index("timestamp")
        await db["agent_tokens"].create_index("token_id", unique=True)
        await db["agent_tokens"].create_index("agent_id")
        await db["endpoints"].create_index("agent_id", unique=True)
        await db["endpoints"].create_index("last_seen")
        logger.info("[Database] MongoDB indexes created successfully.")
    except Exception as e:
        logger.error(f"[Database] Failed to create indexes: {e}")


async def run_data_generator():
    """Background task that generates synthetic events, runs the pipeline, saves to DB, and broadcasts."""
    logger.info("Starting background security event generator...")
    try:
        await asyncio.sleep(2)
        db = container.db

        from backend.services.event_pipeline import process_and_persist

        async def _process_and_broadcast(raw_event):
            return await process_and_persist(container, raw_event)

        if config.ENABLE_SYNTHETIC_GENERATOR:
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
            await asyncio.sleep(config.EVENT_GENERATION_INTERVAL)
            if not config.ENABLE_SYNTHETIC_GENERATOR:
                continue

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

    except asyncio.CancelledError:
        logger.info("Background security event generator stopped.")
    except Exception as e:
        logger.error(f"Unexpected error in background generator: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global bg_generator_task

    config.validate_runtime_config()

    # 1. Start DI container
    await container.start()
    db = container.db

    # 1.5. Initialize experiment management system
    try:
        # Check if experiment mode is enabled via environment variable
        if os.getenv("ENABLE_EXPERIMENT_MODE", "false").lower() in ("true", "1", "yes"):
            exp_manager = container.experiment_manager

            # Try to load and start a default experiment
            experiment_id = os.getenv("EXPERIMENT_ID", "default_research")
            experiment = exp_manager.get_experiment(experiment_id)

            if experiment:
                # Get seed from environment if specified
                seed_str = os.getenv("EXPERIMENT_SEED")
                seed = int(seed_str) if seed_str and seed_str.isdigit() else None

                if exp_manager.start_experiment(experiment_id, seed):
                    logger.info(f"[Experiment] Started experiment: {experiment_id}")
                    if seed is not None:
                        logger.info(f"[Experiment] Using seed for reproducibility: {seed}")
                else:
                    logger.warning(f"[Experiment] Failed to start experiment: {experiment_id}")
            else:
                logger.warning(f"[Experiment] Experiment not found: {experiment_id}")
                logger.info("[Experiment] Available experiments: " +
                           ", ".join(exp_manager.list_experiments()))
        else:
            logger.info("[Experiment] Experiment mode disabled. Set ENABLE_EXPERIMENT_MODE=true to enable.")
    except Exception as e:
        logger.error(f"[Experiment] Failed to initialize experiment management: {e}")

    # 2. Create indexes
    await create_indexes(db)

    # 2.5. Ensure an agent token exists for endpoint agents
    try:
        await container.agent_auth.ensure_bootstrap_token()
    except Exception as e:
        logger.error(f"[Agent] Failed to bootstrap agent token: {e}")

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

    # 6. Start background synthetic event generator task.
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

app.add_middleware(RateLimitMiddleware, max_requests=10000, window_seconds=60)

app.include_router(alerts.router)
app.include_router(stats.router)
app.include_router(chat.router)
app.include_router(audit.router)
app.include_router(auth.router)
app.include_router(ingest.router)
app.include_router(agent.router)


@app.get("/")
@app.get("/api/health")
def read_root():
    ad = container.anomaly_detector
    return {
        "status": "online",
        "service": "SOC AI Dashboard API",
        "database": "connected" if container.db is not None else "disconnected",
        "gemini_api": "configured" if bool(config.OPENCODE_API_KEY) else "fallback_mode",
        "opencode_api": "configured" if bool(config.OPENCODE_API_KEY) else "fallback_mode",
        "anomaly_detector": "trained" if ad and ad.is_trained else "untrained",
        "demo_mode": config.DEMO_MODE,
        "synthetic_generator": "enabled" if config.ENABLE_SYNTHETIC_GENERATOR else "disabled",
    }


@app.post("/api/model/train")
async def train_model(current_user: dict = Depends(get_current_user)):
    user_role = current_user.get("role", "analyst")
    if user_role == "viewer":
        return {"success": False, "message": "Insufficient permissions: Viewers cannot train models."}
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
async def train_feedback_model(current_user: dict = Depends(get_current_user)):
    user_role = current_user.get("role", "analyst")
    if user_role == "viewer":
        return {"success": False, "message": "Insufficient permissions: Viewers cannot train models."}
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
    # Extract token from query params or headers
    token = None
    # Try query param
    query_params = dict(query_params) if (query_params := websocket.query_params) else {}
    token = query_params.get("token")
    if not token:
        # Try Authorization header
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        await websocket.close(code=4001, reason="Authentication token missing")
        return
    # Verify token
    payload = verify_jwt(token)
    if payload is None:
        await websocket.close(code=4002, reason="Invalid or expired token")
        return
    # Optionally
    # Attach user info to websocket for possible use
    websocket.scope["user"] = payload
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
