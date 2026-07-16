"""
Dependency Injection container.
Centralizes creation and wiring of all services, ML models, and DB handles.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends, FastAPI
from typing import Optional

from backend import config
from backend.ml.anomaly import AnomalyDetector
from backend.ml.chat_assistant import ChatAssistant
from backend.ml.llm_summarizer import AlertSummarizer
from backend.ml.mitre_mapper import MitreMapper
from backend.ml.threat_scorer import RiskScorer
from backend.ml.feedback_classifier import FeedbackClassifier
from backend.ml.correlation_engine import CorrelationEngine
from backend.ml.sigma_engine import SigmaEngine
from backend.services.websocket_manager import ConnectionManager
from backend.services.threat_intel import ThreatIntelService
from backend.services.playbook_engine import PlaybookEngine
from backend.services.auth import AuthService


class AppContainer:
    def __init__(self):
        self._mongo_client: Optional[AsyncIOMotorClient] = None
        self._db = None
        self._websocket_manager: Optional[ConnectionManager] = None
        self._anomaly_detector: Optional[AnomalyDetector] = None
        self._mitre_mapper: Optional[MitreMapper] = None
        self._summarizer: Optional[AlertSummarizer] = None
        self._risk_scorer: Optional[RiskScorer] = None
        self._feedback_classifier: Optional[FeedbackClassifier] = None
        self._correlation_engine: Optional[CorrelationEngine] = None
        self._sigma_engine: Optional[SigmaEngine] = None
        self._threat_intel: Optional[ThreatIntelService] = None
        self._playbook_engine: Optional[PlaybookEngine] = None
        self._chat_assistant: Optional[ChatAssistant] = None
        self._auth_service: Optional[AuthService] = None

    async def start(self):
        self._mongo_client = AsyncIOMotorClient(config.MONGODB_URI)
        self._db = self._mongo_client[config.DB_NAME]

        self._websocket_manager = ConnectionManager()
        self._anomaly_detector = AnomalyDetector()
        self._mitre_mapper = MitreMapper(config.GEMINI_API_KEY)
        self._summarizer = AlertSummarizer(config.GEMINI_API_KEY)
        self._risk_scorer = RiskScorer(
            weight_cvss=config.WEIGHT_CVSS,
            weight_anomaly=config.WEIGHT_ANOMALY,
            weight_asset=config.WEIGHT_ASSET_CRITICALITY,
        )
        self._feedback_classifier = FeedbackClassifier()
        self._correlation_engine = CorrelationEngine()
        self._sigma_engine = SigmaEngine()
        self._threat_intel = ThreatIntelService()
        self._playbook_engine = PlaybookEngine()
        self._chat_assistant = ChatAssistant(self._db, config.GEMINI_API_KEY)
        self._auth_service = AuthService(self._db)

    async def shutdown(self):
        if self._mongo_client:
            self._mongo_client.close()

    @property
    def db(self):
        return self._db

    @property
    def websocket_manager(self) -> ConnectionManager:
        return self._websocket_manager

    @property
    def anomaly_detector(self) -> AnomalyDetector:
        return self._anomaly_detector

    @property
    def mitre_mapper(self) -> MitreMapper:
        return self._mitre_mapper

    @property
    def summarizer(self) -> AlertSummarizer:
        return self._summarizer

    @property
    def risk_scorer(self) -> RiskScorer:
        return self._risk_scorer

    @property
    def feedback_classifier(self) -> FeedbackClassifier:
        return self._feedback_classifier

    @property
    def correlation_engine(self) -> CorrelationEngine:
        return self._correlation_engine

    @property
    def sigma_engine(self) -> SigmaEngine:
        return self._sigma_engine

    @property
    def threat_intel(self) -> ThreatIntelService:
        return self._threat_intel

    @property
    def playbook_engine(self) -> PlaybookEngine:
        return self._playbook_engine

    @property
    def chat_assistant(self) -> ChatAssistant:
        return self._chat_assistant

    @property
    def auth_service(self) -> AuthService:
        return self._auth_service


container = AppContainer()


async def get_container() -> AppContainer:
    return container


def get_db(container: AppContainer = Depends(get_container)):
    return container.db


def get_ws_manager(container: AppContainer = Depends(get_container)):
    return container.websocket_manager


def get_anomaly_detector(container: AppContainer = Depends(get_container)):
    return container.anomaly_detector


def get_chat_assistant(container: AppContainer = Depends(get_container)):
    return container.chat_assistant


def get_auth_service(container: AppContainer = Depends(get_container)):
    return container.auth_service
