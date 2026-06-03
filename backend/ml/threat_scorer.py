"""
Risk Scoring Engine.
Combines CVSS severity, ML anomaly score, and asset criticality
into a unified 0–100 risk index.
"""


# CVSS base scores per event type (approximate)
CVSS_SCORES = {
    "SSH_BRUTE_FORCE": 7.5,
    "PORT_SCAN": 5.3,
    "FAILED_LOGIN": 3.1,
    "MALWARE_DETECTION": 9.8,
    "DATA_EXFILTRATION": 9.1,
}

# Asset criticality tiers
ASSET_CRITICALITY = {
    "server": 0.9,
    "workstation": 0.5,
    "iot_device": 0.3,
    "database": 1.0,
    "firewall": 0.95,
    "default": 0.6,
}

# Risk labels
RISK_LABELS = {
    (0, 25): "Low",
    (26, 50): "Medium",
    (51, 75): "High",
    (76, 100): "Critical",
}


class RiskScorer:
    """
    Weighted risk scoring engine.

    Formula:
        risk = (W_cvss × CVSS_norm) + (W_anomaly × anomaly) + (W_asset × criticality)
    Scaled to 0–100.
    """

    def __init__(
        self,
        weight_cvss=0.40,
        weight_anomaly=0.35,
        weight_asset=0.25,
    ):
        self.weight_cvss = weight_cvss
        self.weight_anomaly = weight_anomaly
        self.weight_asset = weight_asset

    def score(self, event, anomaly_score=0.5):
        """
        Compute a risk score for an event.

        Args:
            event: dict with event_type, severity, etc.
            anomaly_score: float 0.0–1.0 from AnomalyDetector.

        Returns:
            dict with risk_score (0–100) and risk_label.
        """
        # 1. CVSS normalized (0-10 → 0-1)
        event_type = event.get("event_type", "FAILED_LOGIN")
        cvss = CVSS_SCORES.get(event_type, 5.0)
        cvss_normalized = cvss / 10.0

        # 2. Anomaly score (already 0-1)
        anomaly = max(0.0, min(1.0, anomaly_score))

        # 3. Asset criticality
        asset_type = event.get("asset_type", "default")
        criticality = ASSET_CRITICALITY.get(asset_type, 0.6)

        # Weighted sum → 0-1 → scale to 0-100
        raw = (
            self.weight_cvss * cvss_normalized
            + self.weight_anomaly * anomaly
            + self.weight_asset * criticality
        )
        risk_score = round(min(100.0, max(0.0, raw * 100)), 1)

        # Determine label
        risk_label = "Low"
        for (low, high), label in RISK_LABELS.items():
            if low <= risk_score <= high:
                risk_label = label
                break

        return {
            "risk_score": risk_score,
            "risk_label": risk_label,
            "cvss_base": cvss,
            "anomaly_score": round(anomaly, 4),
            "asset_criticality": criticality,
        }
