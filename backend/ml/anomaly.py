"""
Anomaly Detection Engine using Isolation Forest.
Scores incoming security events for statistical anomalies.
"""

import os
import json
import logging
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime

logger = logging.getLogger("soc_backend")


class AnomalyDetector:
    EVENT_TYPE_MAP = {
        "SSH_BRUTE_FORCE": 0,
        "PORT_SCAN": 1,
        "FAILED_LOGIN": 2,
        "MALWARE_DETECTION": 3,
        "DATA_EXFILTRATION": 4,
        "IMPOSSIBLE_TRAVEL": 5,
    }

    SEVERITY_MAP = {
        "LOW": 0,
        "MEDIUM": 1,
        "HIGH": 2,
        "CRITICAL": 3,
    }

    def __init__(self, contamination=0.15, n_estimators=100, model_dir=None):
        if model_dir is None:
            model_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "saved_models"
            )
        self.model_dir = model_dir
        self.model_path = os.path.join(self.model_dir, "anomaly_detector.json")

        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=42,
            n_jobs=-1,
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.load()

    def save(self):
        try:
            os.makedirs(self.model_dir, exist_ok=True)
            model_params = {
                "contamination": self.model.contamination,
                "n_estimators": self.model.n_estimators,
                "random_state": self.model.random_state,
                "is_trained": self.is_trained,
                "offset_": float(self.model.offset_) if hasattr(self.model, "offset_") else 0.0,
            }
            if hasattr(self.model, "estimators_samples_"):
                model_params["estimators_samples_"] = [
                    s.tolist() for s in self.model.estimators_samples_
                ]
            scaler_params = {}
            if hasattr(self.scaler, "mean_"):
                scaler_params["mean_"] = self.scaler.mean_.tolist()
                scaler_params["scale_"] = self.scaler.scale_.tolist()
                scaler_params["var_"] = self.scaler.var_.tolist()
            if hasattr(self.scaler, "n_features_in_"):
                scaler_params["n_features_in_"] = self.scaler.n_features_in_

            data = {
                "model": model_params,
                "scaler": scaler_params,
                "is_trained": self.is_trained,
            }
            with open(self.model_path, "w", encoding="utf-8") as f:
                json.dump(data, f, cls=_NumpyEncoder)
            logger.info(f"[Anomaly] Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"[Anomaly] Failed to save model: {e}")

    def load(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.is_trained = data.get("is_trained", False)
                logger.info(f"[Anomaly] Model metadata loaded from {self.model_path}")
            except Exception as e:
                logger.error(f"[Anomaly] Failed to load model metadata: {e}")

    def _extract_features(self, event):
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
        event_type = event.get("event_type", "FAILED_LOGIN")
        event_code = self.EVENT_TYPE_MAP.get(event_type, 2)
        severity = event.get("severity", "LOW")
        severity_code = self.SEVERITY_MAP.get(severity, 0)

        geo = event.get("geo") or {}
        lat = 0.0
        lng = 0.0
        if isinstance(geo, dict):
            try:
                lat = float(geo.get("lat", 0.0))
                lng = float(geo.get("lng", 0.0))
            except (ValueError, TypeError):
                pass

        privileged_users = {"root", "admin", "kali"}
        user = event.get("user", "")
        is_privileged = 1 if user in privileged_users else 0

        return [hour, event_code, severity_code, lat, lng, is_privileged, day_of_week]

    def train(self, events):
        if not events or len(events) < 10:
            logger.info("[Anomaly] Not enough data to train (need >= 10 events).")
            self.is_trained = False
            return

        features = [self._extract_features(e) for e in events]
        X = np.array(features, dtype=np.float64)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True
        logger.info(f"[Anomaly] Model trained on {len(events)} events.")
        self.save()

    def score(self, event):
        features_raw = np.array([self._extract_features(event)], dtype=np.float64)

        if not self.is_trained:
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

            hour = dt.hour
            time_factor = 0.3 if (hour >= 22 or hour <= 6) else 0.0
            raw = min(1.0, severity_score * 0.7 + time_factor + np.random.uniform(0, 0.15))
            return round(float(raw), 4)

        features_scaled = self.scaler.transform(features_raw)
        raw_score = self.model.decision_function(features_scaled)[0]
        normalized = 1.0 - (raw_score + 0.5)
        clamped = max(0.0, min(1.0, normalized))
        return round(float(clamped), 4)


class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)
