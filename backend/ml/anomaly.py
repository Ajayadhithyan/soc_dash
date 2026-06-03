"""
Anomaly Detection Engine using Isolation Forest.
Scores incoming security events for statistical anomalies.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime


class AnomalyDetector:
    """
    Unsupervised anomaly detector using Isolation Forest.
    Extracts numerical features from security events and scores
    each event on a 0.0–1.0 scale (higher = more anomalous).
    """

    # Encode event types as numeric features
    EVENT_TYPE_MAP = {
        "SSH_BRUTE_FORCE": 0,
        "PORT_SCAN": 1,
        "FAILED_LOGIN": 2,
        "MALWARE_DETECTION": 3,
        "DATA_EXFILTRATION": 4,
    }

    SEVERITY_MAP = {
        "LOW": 0,
        "MEDIUM": 1,
        "HIGH": 2,
        "CRITICAL": 3,
    }

    def __init__(self, contamination=0.15, n_estimators=100):
        """
        Args:
            contamination: Expected proportion of anomalies in data.
            n_estimators: Number of trees in the Isolation Forest.
        """
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=42,
            n_jobs=-1,
        )
        self.is_trained = False

    def _extract_features(self, event):
        """
        Extract numerical features from a single security event.

        Features:
            1. hour_of_day (0-23)
            2. event_type_encoded (0-4)
            3. severity_encoded (0-3)
            4. src_ip_last_octet (0-255) — proxy for IP diversity
            5. dest_ip_last_octet (0-255)
            6. is_privileged_user (0 or 1)
            7. day_of_week (0-6)
        """
        # Parse timestamp
        ts = event.get("timestamp", "")
        if isinstance(ts, str) and ts:
            try:
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dt = datetime.now()
        elif isinstance(ts, datetime):
            dt = ts
        else:
            dt = datetime.now()

        hour = dt.hour
        day_of_week = dt.weekday()

        # Event type encoding
        event_type = event.get("event_type", "FAILED_LOGIN")
        event_code = self.EVENT_TYPE_MAP.get(event_type, 2)

        # Severity encoding
        severity = event.get("severity", "LOW")
        severity_code = self.SEVERITY_MAP.get(severity, 0)

        # IP features — extract last octet as a numeric proxy
        src_ip = event.get("src_ip", "0.0.0.0")
        dest_ip = event.get("dest_ip", "0.0.0.0")
        try:
            src_last_octet = int(src_ip.split(".")[-1])
        except (ValueError, IndexError):
            src_last_octet = 0
        try:
            dest_last_octet = int(dest_ip.split(".")[-1])
        except (ValueError, IndexError):
            dest_last_octet = 0

        # Privileged user check
        privileged_users = {"root", "admin", "kali"}
        user = event.get("user", "")
        is_privileged = 1 if user in privileged_users else 0

        return [
            hour,
            event_code,
            severity_code,
            src_last_octet,
            dest_last_octet,
            is_privileged,
            day_of_week,
        ]

    def train(self, events):
        """
        Train the Isolation Forest on a list of historical events.

        Args:
            events: List of event dicts from MongoDB.
        """
        if not events or len(events) < 10:
            print("[Anomaly] Not enough data to train (need >= 10 events). Using default scoring.")
            self.is_trained = False
            return

        features = []
        for event in events:
            features.append(self._extract_features(event))

        X = np.array(features, dtype=np.float64)
        self.model.fit(X)
        self.is_trained = True
        print(f"[Anomaly] Model trained on {len(events)} events.")

    def score(self, event):
        """
        Score a single event for anomaly.

        Returns:
            float: Anomaly score between 0.0 (normal) and 1.0 (highly anomalous).
        """
        features = np.array([self._extract_features(event)], dtype=np.float64)

        if not self.is_trained:
            # Fallback: heuristic scoring based on severity and time
            severity = event.get("severity", "LOW")
            severity_score = self.SEVERITY_MAP.get(severity, 0) / 3.0

            ts = event.get("timestamp", "")
            if isinstance(ts, str) and ts:
                try:
                    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    dt = datetime.now()
            else:
                dt = datetime.now()

            # Off-hours (22:00-06:00) are more suspicious
            hour = dt.hour
            time_factor = 0.3 if (hour >= 22 or hour <= 6) else 0.0

            raw = min(1.0, severity_score * 0.7 + time_factor + np.random.uniform(0, 0.15))
            return round(raw, 4)

        # Isolation Forest: decision_function returns negative for anomalies
        raw_score = self.model.decision_function(features)[0]

        # Normalize: decision_function ranges roughly from -0.5 to 0.5
        # Map to 0.0–1.0 where higher = more anomalous
        normalized = 1.0 - (raw_score + 0.5)
        clamped = max(0.0, min(1.0, normalized))
        return round(clamped, 4)
