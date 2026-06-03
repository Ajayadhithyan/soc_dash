"""
Main entrypoint for the FastAPI backend server.
Coordinates WebSocket broadcasts, ML pipelines, API routing, and synthetic event generation.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from backend import config
from backend.ml.anomaly import AnomalyDetector
from backend.ml.chat_assistant import ChatAssistant
from backend.ml.llm_summarizer import AlertSummarizer
from backend.ml.mitre_mapper import MitreMapper
from backend.ml.threat_scorer import RiskScorer
from backend.routes import alerts, chat, stats
from backend.services.alert_processor import generate_event, process_event
from backend.services.websocket_manager import ConnectionManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("soc_backend")

# Initialize shared components
websocket_manager = ConnectionManager()
anomaly_detector = AnomalyDetector()
mitre_mapper = MitreMapper(config.GEMINI_API_KEY)
summarizer = AlertSummarizer(config.GEMINI_API_KEY)
risk_scorer = RiskScorer(
    weight_cvss=config.WEIGHT_CVSS,
    weight_anomaly=config.WEIGHT_ANOMALY,
    weight_asset=config.WEIGHT_ASSET_CRITICALITY
)

# Async MongoDB Clients
mongo_client = None
db = None
chat_assistant = None
bg_generator_task = None


async def run_data_generator():
    """Background task that generates synthetic events, runs the pipeline, saves to DB, and broadcasts."""
    logger.info("Starting background security event generator...")
    try:
        # Wait a few seconds for initialization and initial ML training to settle
        await asyncio.sleep(4)
        
        # Pre-populate 5 fresh alerts immediately on startup so the analyst has fresh data instantly
        logger.info("Pre-populating 5 fresh security alerts...")
        for i in range(5):
            try:
                raw_event = generate_event()
                enriched_event = await process_event(
                    raw_event,
                    anomaly_detector,
                    mitre_mapper,
                    summarizer,
                    risk_scorer
                )
                await db["security_events"].insert_one(enriched_event)
                
                enriched_event_copy = dict(enriched_event)
                if "_id" in enriched_event_copy:
                    enriched_event_copy["_id"] = str(enriched_event_copy["_id"])
                
                if "id" not in enriched_event_copy:
                    enriched_event_copy["id"] = f"{enriched_event_copy.get('timestamp')}_{enriched_event_copy.get('src_ip')}"
                
                await websocket_manager.broadcast({
                    "type": "NEW_ALERT",
                    "data": enriched_event_copy
                })
                logger.info(f"Pre-populated startup alert {i+1}/5: {enriched_event_copy.get('event_type')}")
                
                # Tiny sleep to ensure separate timestamps/IDs
                await asyncio.sleep(1.2)
            except Exception as e:
                logger.error(f"Error pre-populating startup event: {e}")
        
        while True:
            try:
                # 1. Generate synthetic security event
                raw_event = generate_event()
                
                # 2. Process event through ML / AI pipeline
                enriched_event = await process_event(
                    raw_event,
                    anomaly_detector,
                    mitre_mapper,
                    summarizer,
                    risk_scorer
                )
                
                # 3. Save to MongoDB
                await db["security_events"].insert_one(enriched_event)
                
                # Clean MongoDB _id to allow serialization
                enriched_event_copy = dict(enriched_event)
                if "_id" in enriched_event_copy:
                    enriched_event_copy["_id"] = str(enriched_event_copy["_id"])
                
                # Add a synthetic id for the frontend if not already present
                if "id" not in enriched_event_copy:
                    enriched_event_copy["id"] = f"{enriched_event_copy.get('timestamp')}_{enriched_event_copy.get('src_ip')}"
                
                # 4. Broadcast via WebSocket
                await websocket_manager.broadcast({
                    "type": "NEW_ALERT",
                    "data": enriched_event_copy
                })
                
                logger.info(f"Processed and broadcast alert: {enriched_event_copy.get('event_type')} (Risk: {enriched_event_copy.get('risk_score')})")
                
            except Exception as e:
                logger.error(f"Error in data generator iteration: {e}", exc_info=True)
                
            # Interval between event generations (now 90 seconds)
            await asyncio.sleep(config.EVENT_GENERATION_INTERVAL)
            
    except asyncio.CancelledError:
        logger.info("Background security event generator stopped.")
    except Exception as e:
        logger.error(f"Unexpected error in background generator: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI Lifespan events handler (startup & shutdown)."""
    global mongo_client, db, chat_assistant, bg_generator_task
    
    # 1. Connect to MongoDB
    logger.info(f"Connecting to MongoDB at {config.MONGODB_URI} ...")
    mongo_client = AsyncIOMotorClient(config.MONGODB_URI)
    db = mongo_client[config.DB_NAME]
    
    # 2. Inject DB dependencies to routes
    alerts.set_db(db)
    stats.set_db(db)
    
    # 3. Initialize & Inject Chat Assistant
    chat_assistant = ChatAssistant(db, config.GEMINI_API_KEY)
    chat.set_assistant(chat_assistant)
    
    # 4. ML Model Bootstrap Training
    # Get recent historical logs from DB to fit anomaly model
    logger.info("Retrieving past security events to train Isolation Forest baseline...")
    try:
        past_events_cursor = db["security_events"].find({}).sort("timestamp", -1).limit(500)
        past_events = []
        async for doc in past_events_cursor:
            past_events.append(doc)
            
        if len(past_events) >= 10:
            logger.info(f"Training anomaly detection model on {len(past_events)} historic events...")
            anomaly_detector.train(past_events)
        else:
            logger.info("Insufficient historical events found in database to train Isolation Forest. Model will use fallback scoring and auto-train as events stream in.")
    except Exception as e:
        logger.error(f"Failed to bootstrap train ML anomaly engine: {e}")
        
    # 5. Start background data generator task
    bg_generator_task = asyncio.create_task(run_data_generator())
    
    yield
    
    # SHUTDOWN PROCESS
    logger.info("Stopping FastAPI application...")
    if bg_generator_task:
        bg_generator_task.cancel()
        try:
            await bg_generator_task
        except asyncio.CancelledError:
            pass
            
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed.")


# Create FastAPI App instance
app = FastAPI(
    title="AI-Powered SOC Analyst Dashboard Backend",
    description="REST API and WebSocket feed for cybersecurity threat operations.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(alerts.router)
app.include_router(stats.router)
app.include_router(chat.router)


@app.get("/")
@app.get("/api/health")
def read_root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "SOC AI Dashboard API",
        "database": "connected" if db is not None else "disconnected",
        "gemini_api": "configured" if bool(config.GEMINI_API_KEY) else "fallback_mode",
        "anomaly_detector": "trained" if anomaly_detector.is_trained else "untrained"
    }


@app.post("/api/model/train")
async def train_model():
    """Manually trigger ML model training on historic security events."""
    logger.info("Manual training request received for Isolation Forest...")
    try:
        past_events_cursor = db["security_events"].find({}).sort("timestamp", -1).limit(500)
        past_events = []
        async for doc in past_events_cursor:
            past_events.append(doc)
            
        if len(past_events) >= 10:
            logger.info(f"Training anomaly detection model on {len(past_events)} historic events...")
            anomaly_detector.train(past_events)
            return {
                "success": True,
                "message": f"Successfully trained model on {len(past_events)} events.",
                "anomaly_detector": "trained"
            }
        else:
            return {
                "success": False,
                "message": "Insufficient historical events in database. Need at least 10 events to train.",
                "anomaly_detector": "untrained"
            }
    except Exception as e:
        logger.error(f"Failed to manually train ML anomaly engine: {e}")
        return {
            "success": False,
            "message": f"Failed to train ML engine: {str(e)}",
            "anomaly_detector": "trained" if anomaly_detector.is_trained else "untrained"
        }



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time threat stream."""
    await websocket_manager.connect(websocket)
    try:
        # Keep connection open and listen for any client messages (ping/pong, etc.)
        while True:
            # Receive data (discard or handle in-dashboard requests)
            data = await websocket.receive_text()
            # Simple Echo or confirmation
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket communication error: {e}")
        websocket_manager.disconnect(websocket)


if __name__ == "__main__":
    # Start the server
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
