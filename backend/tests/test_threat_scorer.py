"""
Tests for the Risk Scoring engine.
"""

import pytest
from backend.ml.threat_scorer import RiskScorer


class TestRiskScorer:
    def setup_method(self):
        self.scorer = RiskScorer()

    def test_score_ssh_brute_force(self, sample_event):
        result = self.scorer.score(sample_event, anomaly_score=0.7)
        assert 0 <= result["risk_score"] <= 100
        assert result["risk_label"] in ("Low", "Medium", "High", "Critical")
        assert "cvss_base" in result
        assert "asset_criticality" in result

    def test_score_low_anomaly(self, sample_event):
        result = self.scorer.score(sample_event, anomaly_score=0.1)
        risk = result["risk_score"]
        assert risk >= 0

    def test_score_high_anomaly(self, sample_event):
        result = self.scorer.score(sample_event, anomaly_score=0.95)
        high_risk = result["risk_score"]
        low_result = self.scorer.score(sample_event, anomaly_score=0.1)
        assert high_risk >= low_result["risk_score"]
