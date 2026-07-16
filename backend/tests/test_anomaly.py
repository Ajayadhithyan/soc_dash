"""
Tests for the Anomaly Detection engine.
"""

import pytest
from backend.ml.anomaly import AnomalyDetector


class TestAnomalyDetector:
    def test_extract_features(self, sample_event):
        detector = AnomalyDetector()
        features = detector._extract_features(sample_event)
        assert len(features) == 7
        assert features[0] == 12  # hour
        assert features[1] == 0   # SSH_BRUTE_FORCE -> 0
        assert features[2] == 2   # HIGH -> 2

    def test_score_untrained(self, sample_event):
        detector = AnomalyDetector()
        score = detector.score(sample_event)
        assert 0.0 <= score <= 1.0

    def test_train_insufficient_data(self):
        detector = AnomalyDetector()
        detector.train([])
        assert detector.is_trained is False

    def test_event_type_map_has_impossible_travel(self):
        assert "IMPOSSIBLE_TRAVEL" in AnomalyDetector.EVENT_TYPE_MAP
        assert AnomalyDetector.EVENT_TYPE_MAP["IMPOSSIBLE_TRAVEL"] == 5
