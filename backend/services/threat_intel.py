"""
Threat Intelligence Service.
Checks source IPs against a local blocklist of known malicious ranges
and a dynamic cache of analyst-blocked IPs.
"""

import logging
from ipaddress import ip_address, ip_network

logger = logging.getLogger("soc_backend")


# Simulated local threat intelligence blocklist
# These represent known malicious CIDR ranges from threat feeds
KNOWN_MALICIOUS_RANGES = [
    # APT groups and botnets (simulated)
    {"cidr": "185.220.100.0/24", "source": "TOR Exit Nodes", "category": "anonymization"},
    {"cidr": "45.155.205.0/24", "source": "Cobalt Strike C2", "category": "c2_infrastructure"},
    {"cidr": "194.26.29.0/24", "source": "Known Botnet C2", "category": "botnet"},
    {"cidr": "91.219.236.0/24", "source": "RU APT Infrastructure", "category": "apt"},
    {"cidr": "103.75.201.0/24", "source": "CN Threat Actor", "category": "apt"},
    {"cidr": "5.188.86.0/24", "source": "Brute Force Farm", "category": "credential_attack"},
    {"cidr": "141.98.10.0/24", "source": "Scanning Infrastructure", "category": "reconnaissance"},
    {"cidr": "45.129.56.0/24", "source": "DarkNet Proxy", "category": "anonymization"},
    {"cidr": "23.128.248.0/24", "source": "TOR Exit Nodes", "category": "anonymization"},
    {"cidr": "171.25.193.0/24", "source": "TOR Exit Nodes", "category": "anonymization"},
    {"cidr": "209.141.32.0/24", "source": "Bulletproof Hosting", "category": "malware_hosting"},
    {"cidr": "198.98.48.0/24", "source": "Bulletproof Hosting", "category": "malware_hosting"},
    {"cidr": "77.247.181.0/24", "source": "Ransomware C2", "category": "ransomware"},
    {"cidr": "46.166.139.0/24", "source": "Phishing Infrastructure", "category": "phishing"},
    {"cidr": "185.100.87.0/24", "source": "TOR Exit Nodes", "category": "anonymization"},
]

# Threat category risk multipliers
CATEGORY_RISK = {
    "c2_infrastructure": 1.0,
    "apt": 0.95,
    "ransomware": 0.95,
    "botnet": 0.85,
    "malware_hosting": 0.8,
    "phishing": 0.75,
    "credential_attack": 0.7,
    "anonymization": 0.6,
    "reconnaissance": 0.5,
}


class ThreatIntelService:
    """
    Local threat intelligence service.
    Checks IPs against bundled blocklists and dynamic analyst block cache.
    """

    def __init__(self):
        # Pre-parse CIDR networks for fast lookup
        self.blocklist = []
        for entry in KNOWN_MALICIOUS_RANGES:
            try:
                network = ip_network(entry["cidr"], strict=False)
                self.blocklist.append({
                    "network": network,
                    "source": entry["source"],
                    "category": entry["category"],
                })
            except ValueError as e:
                logger.warning(f"[ThreatIntel] Invalid CIDR: {entry['cidr']}: {e}")

        # Dynamic cache of analyst-blocked IPs (populated from SOAR actions)
        self.analyst_blocked_ips = set()

        logger.info(f"[ThreatIntel] Loaded {len(self.blocklist)} malicious CIDR ranges.")

    def add_blocked_ip(self, ip_str):
        """Add an IP to the analyst-blocked cache (from BLOCK_IP SOAR actions)."""
        self.analyst_blocked_ips.add(ip_str)
        logger.info(f"[ThreatIntel] Added analyst-blocked IP: {ip_str}")

    def check_ip(self, ip_str):
        """
        Check if an IP is in known malicious ranges or analyst-blocked list.

        Args:
            ip_str: IP address string (e.g., "185.220.100.42").

        Returns:
            dict: Threat intelligence result.
        """
        result = {
            "is_known_malicious": False,
            "blocklist_source": None,
            "threat_category": None,
            "risk_multiplier": 0.0,
            "analyst_blocked": False,
        }

        if not ip_str:
            return result

        # Check analyst-blocked cache
        if ip_str in self.analyst_blocked_ips:
            result["analyst_blocked"] = True
            result["is_known_malicious"] = True
            result["blocklist_source"] = "Analyst Block Action"
            result["threat_category"] = "analyst_flagged"
            result["risk_multiplier"] = 0.8
            return result

        # Check against threat feed blocklists
        try:
            ip_obj = ip_address(ip_str)
            for entry in self.blocklist:
                if ip_obj in entry["network"]:
                    result["is_known_malicious"] = True
                    result["blocklist_source"] = entry["source"]
                    result["threat_category"] = entry["category"]
                    result["risk_multiplier"] = CATEGORY_RISK.get(entry["category"], 0.5)
                    logger.info(
                        f"[ThreatIntel] MATCH: {ip_str} found in {entry['source']} "
                        f"({entry['category']})"
                    )
                    return result
        except ValueError:
            # Invalid IP format
            pass

        return result

    def enrich_event(self, event):
        """
        Enrich a security event with threat intelligence data.

        Args:
            event: Security event dict with 'src_ip' field.

        Returns:
            dict: Threat intelligence enrichment data.
        """
        src_ip = event.get("src_ip", "")
        return self.check_ip(src_ip)
