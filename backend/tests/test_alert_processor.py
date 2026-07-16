"""
Tests for the Alert Processing pipeline.
"""

import sys
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from backend.services.alert_processor import generate_event, check_impossible_travel, EVENT_TYPES


class TestAlertProcessor:
    def test_generate_event(self):
        event = generate_event()
        assert "timestamp" in event
        assert "src_ip" in event
        assert "dest_ip" in event
        assert event["event_type"] in EVENT_TYPES
        assert event["severity"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        assert "geo" in event
        assert "asset_type" in event

    def test_check_impossible_travel_no_change(self, sample_event):
        result = check_impossible_travel(dict(sample_event))
        assert result["event_type"] == "SSH_BRUTE_FORCE"

    def test_check_impossible_travel_none_user(self, sample_event):
        event = dict(sample_event)
        event["user"] = "SYSTEM"
        result = check_impossible_travel(event)
        assert result["event_type"] == "SSH_BRUTE_FORCE"

    def test_generate_event_has_raw_log(self):
        event = generate_event()
        assert len(event["raw_log"]) > 10

    def test_generate_event_consistent_severity(self):
        severity_map = {
            "SSH_BRUTE_FORCE": "HIGH",
            "PORT_SCAN": "MEDIUM",
            "FAILED_LOGIN": "LOW",
            "MALWARE_DETECTION": "CRITICAL",
            "DATA_EXFILTRATION": "CRITICAL",
        }
        for event_type, expected_sev in severity_map.items():
            from backend.services.alert_processor import SEVERITY_LEVELS
            assert SEVERITY_LEVELS[event_type] == expected_sev
