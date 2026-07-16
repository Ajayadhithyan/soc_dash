"""
Supervised Feedback Classifier.
Learns from analyst TRUE_POSITIVE / FALSE_POSITIVE verifications
to predict alert confidence and recommend suppression of likely false positives.
"""

import os
import json
import logging
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime

from backend.ml.anomaly import _NumpyEncoder

logger = logging.getLogger("soc_backend")


class FeedbackClassifier:
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

    def __init__(self, min_samples=20, suppression_threshold=0.25, model_dir=None):
        if model_dir is None:
            model_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "saved_models"
            )
        self.model_dir = model_dir
        self.model_path = os.path.join(self.model_dir, "feedback_classifier.json")

        self.model = LogisticRegression(max_iter=500, random_state=42, class_weight="balanced")
        self.scaler = StandardScaler()
        self.is_trained = False
        self.min_samples = min_samples
        self.suppression_threshold = suppression_threshold
        self.training_count = 0
        self.load()

    def save(self):
        try:
            os.makedirs(self.model_dir, exist_ok=True)
            data = {
                "model_params": {
                    "max_iter": self.model.max_iter,
                    "random_state": self.model.random_state,
                    "class_weight": self.model.class_weight,
                },
                "scaler_params": {},
                "is_trained": self.is_trained,
                "training_count": self.training_count,
            }
            if hasattr(self.scaler, "mean_"):
                data["scaler_params"]["mean_"] = self.scaler.mean_.tolist()
                data["scaler_params"]["scale_"] = self.scaler.scale_.tolist()
                data["scaler_params"]["var_"] = self.scaler.var_.tolist()
            if hasattr(self.scaler, "n_features_in_"):
                data["scaler_params"]["n_features_in_"] = self.scaler.n_features_in_
            if hasattr(self.model, "coef_"):
                data["model_params"]["coef_"] = self.model.coef_.tolist()
                data["model_params"]["intercept_"] = self.model.intercept_.tolist()

            with open(self.model_path, "w", encoding="utf-8") as f:
                json.dump(data, f, cls=_NumpyEncoder)
            logger.info(f"[Feedback] Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"[Feedback] Failed to save model: {e}")

    def load(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.is_trained = data.get("is_trained", False)
                self.training_count = data.get("training_count", 0)
                logger.info(f"[Feedback] Model metadata loaded from {self.model_path}")
            except Exception as e:
                logger.error(f"[Feedback] Failed to load model: {e}")

    def _extract_features(self, event):
        event_type = event.get("event_type", "FAILED_LOGIN")
        event_code = self.EVENT_TYPE_MAP.get(event_type, 2)
        severity = event.get("severity", "LOW")
        severity_code = self.SEVERITY_MAP.get(severity, 0)
        anomaly_score = event.get("anomaly_score", 0.5)
        risk_score = event.get("risk_score", 50.0) / 100.0
        privileged_users = {"root", "admin", "kali"}
        user = event.get("user", "")
        is_privileged = 1 if user in privileged_users else 0

        ts = event.get("timestamp", "")
        if isinstance(ts, str) and ts:
            try:
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dt = datetime.now()
        else:
            dt = datetime.now()
        hour = dt.hour

        return [event_code, severity_code, anomaly_score, risk_score, is_privileged, hour]

    def train(self, labeled_events):
        valid = [
            e for e in labeled_events
            if e.get("analyst_verification") in ("TRUE_POSITIVE", "FALSE_POSITIVE")
        ]

        if len(valid) < self.min_samples:
            logger.info(f"[Feedback] Insufficient labeled data ({len(valid)}/{self.min_samples}).")
            self.is_trained = False
            return

        features = [self._extract_features(e) for e in valid]
        labels = [1 if e["analyst_verification"] == "TRUE_POSITIVE" else 0 for e in valid]

        X = np.array(features, dtype=np.float64)
        y = np.array(labels, dtype=np.int32)

        if len(set(y)) < 2:
            logger.info("[Feedback] Need both TRUE_POSITIVE and FALSE_POSITIVE labels to train.")
            self.is_trained = False
            return

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        self.training_count = len(valid)
        logger.info(f"[Feedback] Classifier trained on {len(valid)} labeled events.")
        self.save()

    def predict(self, event):
        if not self.is_trained:
            return {"feedback_confidence": 0.5, "suppress_recommendation": False, "classifier_trained": False}

        features = np.array([self._extract_features(event)], dtype=np.float64)
        features_scaled = self.scaler.transform(features)
        proba = self.model.predict_proba(features_scaled)[0][1]
        suppress = proba < self.suppression_threshold

        return {
            "feedback_confidence": round(float(proba), 4),
            "suppress_recommendation": suppress,
            "classifier_trained": True,
        }
