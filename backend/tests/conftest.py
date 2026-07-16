"""
Pytest fixtures for backend testing.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_db():
    """Create a mock MongoDB database."""
    mock = MagicMock()
    mock["security_events"] = AsyncMock()
    mock["audit_logs"] = AsyncMock()
    return mock


@pytest.fixture
def sample_event():
    """Return a sample security event for testing."""
    return {
        "timestamp": "2025-01-01 12:00:00",
        "src_ip": "185.220.100.42",
        "dest_ip": "10.0.0.5",
        "event_type": "SSH_BRUTE_FORCE",
        "severity": "HIGH",
        "user": "root",
        "raw_log": "SSH brute-force detected: 50 failed login attempts from 185.220.100.42 targeting 10.0.0.5 for user 'root'",
        "asset_type": "server",
        "geo": {"country": "Russia", "lat": 55.75, "lng": 37.62},
    }
