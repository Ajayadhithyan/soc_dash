"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AlertEvent(BaseModel):
    timestamp: str = ""
    src_ip: str = ""
    dest_ip: str = ""
    event_type: str = ""
    severity: str = ""
    user: str = ""
    raw_log: str = ""
    ai_summary: str = ""
    risk_score: float = 0.0
    risk_label: str = "Low"
    anomaly_score: float = 0.0
    cvss_base: float = 0.0
    asset_criticality: float = 0.0
    asset_type: str = "default"
    mitre: Dict[str, Any] = Field(default_factory=dict)
    auto_response: Optional[Dict[str, Any]] = None
    id: str = ""


class AlertListResponse(BaseModel):
    alerts: List[Dict[str, Any]] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 50


class StatsOverview(BaseModel):
    total_alerts: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    avg_risk_score: float = 0.0
    active_threats: int = 0
    alerts_last_hour: int = 0


class SeverityDistribution(BaseModel):
    severity: str
    count: int


class TimelinePoint(BaseModel):
    time: str
    count: int


class TopSource(BaseModel):
    ip: str
    count: int
    last_seen: str = ""
    primary_attack: str = ""


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    response: str
    context_alerts_used: int = 0


class AutoResponseRequest(BaseModel):
    action: str = Field(..., pattern="^(block_ip|quarantine_host|create_ticket)$")
    alert_id: str = ""


class AutoResponseResult(BaseModel):
    success: bool
    action: str
    message: str
    timestamp: str = ""
    details: dict = {}


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserDetails(BaseModel):
    username: str
    role: str = "analyst"
