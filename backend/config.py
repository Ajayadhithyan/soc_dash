"""
Configuration module for SOC AI Dashboard backend.
Loads settings from environment variables / .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "soc_ai_dashboard")
OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY", "sk-3Ev6Mvwe8hzVJ5q7u9w5WKtu0KHrE7H4vw2z0ia5GObw5XVHpidDSDI3O6jdS9A1")
EVENT_GENERATION_INTERVAL = int(os.getenv("EVENT_INTERVAL", "4"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

WEIGHT_CVSS = 0.40
WEIGHT_ANOMALY = 0.35
WEIGHT_ASSET_CRITICALITY = 0.25

MAX_ANALYST_BLOCKED_IPS = 1000
