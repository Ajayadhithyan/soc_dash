"""
Configuration module for SOC AI Dashboard backend.
Loads settings from environment variables / .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------
# DATABASE
# -----------------------------------
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "soc_ai_dashboard")

# -----------------------------------
# AI / LLM
# -----------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# -----------------------------------
# APPLICATION
# -----------------------------------
EVENT_GENERATION_INTERVAL = int(os.getenv("EVENT_INTERVAL", "4"))  # seconds
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

# -----------------------------------
# RISK SCORING WEIGHTS
# -----------------------------------
WEIGHT_CVSS = 0.40
WEIGHT_ANOMALY = 0.35
WEIGHT_ASSET_CRITICALITY = 0.25
