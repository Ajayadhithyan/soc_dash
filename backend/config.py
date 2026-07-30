"""
Configuration module for SOC AI Dashboard backend.
Loads settings from environment variables / .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

APP_ENV = os.getenv("APP_ENV", "development").lower()
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in {"1", "true", "yes", "on"}
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "soc_ai_dashboard")
OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY", "")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
EVENT_GENERATION_INTERVAL = int(os.getenv("EVENT_INTERVAL", "4"))
ENABLE_SYNTHETIC_GENERATOR = os.getenv("ENABLE_SYNTHETIC_GENERATOR", "false").lower() in {"1", "true", "yes", "on"}
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

WEIGHT_CVSS = 0.40
WEIGHT_ANOMALY = 0.35
WEIGHT_ASSET_CRITICALITY = 0.25

MAX_ANALYST_BLOCKED_IPS = 1000


def validate_runtime_config() -> None:
    """Fail fast when production starts with unsafe or incomplete configuration."""
    if APP_ENV == "production":
        missing = []
        if not JWT_SECRET_KEY:
            missing.append("JWT_SECRET_KEY")
        if DEMO_MODE:
            missing.append("DEMO_MODE must be false")
        if ENABLE_SYNTHETIC_GENERATOR:
            missing.append("ENABLE_SYNTHETIC_GENERATOR must be false")
        if missing:
            raise RuntimeError(
                "Unsafe production configuration: " + ", ".join(missing)
            )
