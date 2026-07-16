"""
Multi-Event Correlation Engine.
Uses sliding time windows to detect attack campaign patterns
by grouping related alerts by source IP, destination IP, and event sequences.
"""

import logging
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

logger = logging.getLogger("soc_backend")


# Kill chain progression patterns (order matters)
KILL_CHAIN_PATTERNS = {
    "recon_to_exploit": {
        "name": "Reconnaissance → Exploitation Chain",
        "sequence": ["PORT_SCAN", "SSH_BRUTE_FORCE"],
        "risk_boost": 15,
    },
    "exploit_to_malware": {
        "name": "Credential Compromise → Malware Deployment",
        "sequence": ["SSH_BRUTE_FORCE", "MALWARE_DETECTION"],
        "risk_boost": 25,
    },
    "full_kill_chain": {
        "name": "Full Kill Chain (Recon → Exploit → Install)",
        "sequence": ["PORT_SCAN", "SSH_BRUTE_FORCE", "MALWARE_DETECTION"],
        "risk_boost": 35,
    },
    "exploit_to_exfil": {
        "name": "Compromise → Data Exfiltration",
        "sequence": ["MALWARE_DETECTION", "DATA_EXFILTRATION"],
        "risk_boost": 30,
    },
    "brute_to_exfil": {
        "name": "Credential Access → Exfiltration",
        "sequence": ["SSH_BRUTE_FORCE", "DATA_EXFILTRATION"],
        "risk_boost": 25,
    },
}


class CorrelationEngine:
    """
    Correlates security events across a sliding time window to detect
    multi-step attack campaigns, lateral movement, and targeted host attacks.
    """

    def __init__(self, window_minutes=5, lateral_threshold=3, targeted_threshold=3):
        """
        Args:
            window_minutes: Size of the sliding correlation window.
            lateral_threshold: Min unique dest_ips from same src_ip to flag lateral movement.
            targeted_threshold: Min unique event types on same dest_ip to flag targeted host.
        """
        self.window_minutes = window_minutes
        self.lateral_threshold = lateral_threshold
        self.targeted_threshold = targeted_threshold

        # In-memory event buffer: stores recent events for correlation
        # Key: timestamp string, Value: event dict
        self.event_buffer = []
        self.max_buffer_size = 500

    def bootstrap(self, events):
        """Bootstrap the sliding window buffer with historical events from MongoDB."""
        self.event_buffer = list(events)
        self._prune_buffer()
        logger.info(f"[Correlation] Bootstrapped sliding window buffer with {len(self.event_buffer)} historical events.")

    def _parse_timestamp(self, ts_str):
        """Parse timestamp string to datetime."""
        if isinstance(ts_str, str) and ts_str:
            try:
                return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return datetime.now()
        return datetime.now()

    def _generate_campaign_id(self, src_ip, pattern_name):
        """Generate a deterministic campaign ID from source IP and pattern."""
        raw = f"{src_ip}_{pattern_name}_{datetime.now().strftime('%Y%m%d%H')}"
        return f"CMP-{hashlib.md5(raw.encode()).hexdigest()[:8].upper()}"

    def _prune_buffer(self):
        """Remove events outside the time window from the buffer."""
        cutoff = datetime.now() - timedelta(minutes=self.window_minutes)
        self.event_buffer = [
            e for e in self.event_buffer
            if self._parse_timestamp(e.get("timestamp", "")) >= cutoff
        ]

        # Hard cap to prevent memory growth
        if len(self.event_buffer) > self.max_buffer_size:
            self.event_buffer = self.event_buffer[-self.max_buffer_size:]

    def _check_kill_chain(self, src_ip):
        """
        Check if events from a source IP match any kill chain pattern.

        Returns:
            dict or None: Matched pattern info with campaign_id.
        """
        src_events = [
            e for e in self.event_buffer
            if e.get("src_ip") == src_ip
        ]

        if not src_events:
            return None

        # Get chronologically ordered event types from this source
        src_events.sort(key=lambda e: e.get("timestamp", ""))
        event_types = [e.get("event_type", "") for e in src_events]

        # Check each kill chain pattern
        best_match = None
        best_boost = 0

        for pattern_id, pattern in KILL_CHAIN_PATTERNS.items():
            sequence = pattern["sequence"]

            # Check if the sequence appears as a subsequence in event_types
            seq_idx = 0
            for et in event_types:
                if seq_idx < len(sequence) and et == sequence[seq_idx]:
                    seq_idx += 1

            if seq_idx == len(sequence) and pattern["risk_boost"] > best_boost:
                best_match = {
                    "pattern_id": pattern_id,
                    "pattern_name": pattern["name"],
                    "risk_boost": pattern["risk_boost"],
                    "campaign_id": self._generate_campaign_id(src_ip, pattern_id),
                    "matched_events_count": len(src_events),
                }
                best_boost = pattern["risk_boost"]

        return best_match

    def _check_lateral_movement(self, src_ip):
        """
        Detect lateral movement: same source IP targeting multiple unique destinations.

        Returns:
            dict or None: Lateral movement info.
        """
        src_events = [
            e for e in self.event_buffer
            if e.get("src_ip") == src_ip
        ]

        unique_dests = set(e.get("dest_ip", "") for e in src_events if e.get("dest_ip"))

        if len(unique_dests) >= self.lateral_threshold:
            return {
                "pattern_name": "Lateral Movement Detected",
                "unique_targets": len(unique_dests),
                "target_ips": list(unique_dests)[:5],
                "campaign_id": self._generate_campaign_id(src_ip, "lateral"),
                "risk_boost": 10,
            }

        return None

    def _check_targeted_host(self, dest_ip):
        """
        Detect targeted host: same destination receiving multiple different attack types.

        Returns:
            dict or None: Targeted host info.
        """
        dest_events = [
            e for e in self.event_buffer
            if e.get("dest_ip") == dest_ip
        ]

        unique_types = set(e.get("event_type", "") for e in dest_events if e.get("event_type"))

        if len(unique_types) >= self.targeted_threshold:
            return {
                "pattern_name": "Targeted Host Under Multi-Vector Attack",
                "unique_attack_types": len(unique_types),
                "attack_types": list(unique_types),
                "campaign_id": self._generate_campaign_id(dest_ip, "targeted"),
                "risk_boost": 15,
            }

        return None

    def correlate(self, event):
        """
        Analyze a new event for correlation patterns.

        Adds the event to the buffer, prunes old entries, and checks
        for kill chains, lateral movement, and targeted host patterns.

        Args:
            event: Enriched event dict.

        Returns:
            dict: Correlation result with pattern matches.
        """
        # Add to buffer
        self.event_buffer.append(event)
        self._prune_buffer()

        src_ip = event.get("src_ip", "")
        dest_ip = event.get("dest_ip", "")

        correlations = []
        total_risk_boost = 0

        # 1. Check kill chain patterns
        kill_chain = self._check_kill_chain(src_ip)
        if kill_chain:
            correlations.append(kill_chain)
            total_risk_boost += kill_chain["risk_boost"]

        # 2. Check lateral movement
        lateral = self._check_lateral_movement(src_ip)
        if lateral:
            correlations.append(lateral)
            total_risk_boost += lateral["risk_boost"]

        # 3. Check targeted host
        targeted = self._check_targeted_host(dest_ip)
        if targeted:
            correlations.append(targeted)
            total_risk_boost += targeted["risk_boost"]

        # Build result
        if correlations:
            primary = correlations[0]
            result = {
                "is_correlated": True,
                "campaign_id": primary["campaign_id"],
                "primary_pattern": primary["pattern_name"],
                "total_risk_boost": min(50, total_risk_boost),
                "related_alert_count": len(self.event_buffer),
                "patterns": correlations,
            }
            logger.info(
                f"[Correlation] Alert correlated: {primary['pattern_name']} "
                f"(src: {src_ip}, boost: +{total_risk_boost})"
            )
            return result

        return {
            "is_correlated": False,
            "campaign_id": None,
            "primary_pattern": None,
            "total_risk_boost": 0,
            "related_alert_count": 0,
            "patterns": [],
        }
