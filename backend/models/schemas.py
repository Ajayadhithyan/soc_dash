"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AlertEvent(BaseModel):
    """Schema for a security alert event."""
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
    mitre: dict = {}
    auto_response: Optional[dict] = None
    id: str = ""


class AlertListResponse(BaseModel):
    """Paginated list of alerts."""
    alerts: List[dict] = []
    total: int = 0
    page: int = 1
    per_page: int = 50


class StatsOverview(BaseModel):
    """KPI overview metrics."""
    total_alerts: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    avg_risk_score: float = 0.0
    active_threats: int = 0
    alerts_last_hour: int = 0


class SeverityDistribution(BaseModel):
    """Severity breakdown for charts."""
    severity: str
    count: int


class TimelinePoint(BaseModel):
    """Single point in timeline chart."""
    time: str
    count: int


class TopSource(BaseModel):
    """Top attacking source IP."""
    ip: str
    count: int
    last_seen: str = ""
    primary_attack: str = ""


class ChatRequest(BaseModel):
    """Chat message from analyst."""
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    """Chat response from AI assistant."""
    response: str
    context_alerts_used: int = 0


class AutoResponseRequest(BaseModel):
    """Auto-response action request."""
    action: str = Field(..., pattern="^(block_ip|quarantine_host|create_ticket)$")
    alert_id: str = ""


class AutoResponseResult(BaseModel):
    """Result of an auto-response action."""
    success: bool
    action: str
    message: str
    timestamp: str = ""
    details: dict = {}
