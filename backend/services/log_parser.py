"""
Log Parser Service.
Parses raw log strings into structured security events and resolves IP geolocation.
"""

import re
import random
import logging
import urllib.request
import json
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger("soc_backend")

# Realistic fallback locations
GEO_SOURCES = [
    {"country": "Russia", "lat": 55.75, "lng": 37.62},
    {"country": "China", "lat": 39.91, "lng": 116.40},
    {"country": "USA", "lat": 40.71, "lng": -74.01},
    {"country": "Brazil", "lat": -23.55, "lng": -46.63},
    {"country": "India", "lat": 28.61, "lng": 77.21},
    {"country": "Germany", "lat": 52.52, "lng": 13.41},
    {"country": "Iran", "lat": 35.69, "lng": 51.39},
    {"country": "North Korea", "lat": 39.02, "lng": 125.75},
    {"country": "Nigeria", "lat": 6.52, "lng": 3.38},
    {"country": "Romania", "lat": 44.43, "lng": 26.10},
    {"country": "Ukraine", "lat": 50.45, "lng": 30.52},
    {"country": "Turkey", "lat": 41.01, "lng": 28.98},
]

SEVERITY_LEVELS = {
    "SSH_BRUTE_FORCE": "HIGH",
    "PORT_SCAN": "MEDIUM",
    "FAILED_LOGIN": "LOW",
    "MALWARE_DETECTION": "CRITICAL",
    "DATA_EXFILTRATION": "CRITICAL",
    "UNKNOWN": "LOW",
}


def is_private_ip(ip: str) -> bool:
    """Check if an IP address is private/local."""
    if not ip:
        return True
    # Basic check for private ranges
    if (
        ip.startswith("10.")
        or ip.startswith("192.168.")
        or ip.startswith("127.")
        or ip.startswith("fe80:")
        or ip.startswith("::1")
    ):
        return True
    # Check for 172.16.0.0 - 172.31.255.255
    match = re.match(r"^172\.(\d+)\.", ip)
    if match:
        second_octet = int(match.group(1))
        return 16 <= second_octet <= 31
    return False


def resolve_geoip(ip: str) -> Dict[str, Any]:
    """Resolve IP geolocation using ip-api.com. Falls back to a realistic location if local or failed."""
    if is_private_ip(ip):
        return random.choice(GEO_SOURCES)

    try:
        url = f"http://ip-api.com/json/{ip}"
        with urllib.request.urlopen(url, timeout=1.5) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "success":
                return {
                    "country": data.get("country", "Unknown"),
                    "lat": float(data.get("lat", 0.0)),
                    "lng": float(data.get("lon", 0.0)),
                }
    except Exception as e:
        logger.warning(f"GeoIP resolution failed for {ip}: {e}")

    return random.choice(GEO_SOURCES)


def parse_raw_log(raw_log: str) -> Dict[str, Any]:
    """
    Parse raw log strings using regex and rules.
    Extracts src_ip, dest_ip, user, event_type, severity, and timestamp.
    """
    # Clean the input log line
    line = raw_log.strip()

    # Extract IP Addresses (IPv4 pattern)
    ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", line)

    src_ip = None
    dest_ip = None

    # Contextual IP search
    src_match = re.search(r"(?:from|originating from|src|source|source ip|src_ip)[ :=]\s*(\b(?:\d{1,3}\.){3}\d{1,3}\b)", line, re.IGNORECASE)
    if src_match:
        src_ip = src_match.group(1)

    dest_match = re.search(r"(?:to|targeting|dest|destination|destination ip|dest_ip|endpoint)[ :=]\s*(\b(?:\d{1,3}\.){3}\d{1,3}\b)", line, re.IGNORECASE)
    if dest_match:
        dest_ip = dest_match.group(1)

    # Fallback to positional IPs if not matched contextually
    if not src_ip:
        src_ip = ips[0] if len(ips) > 0 else "127.0.0.1"
    if not dest_ip:
        remaining_ips = [ip for ip in ips if ip != src_ip]
        dest_ip = remaining_ips[0] if len(remaining_ips) > 0 else "10.0.0.5"

    # Extract User
    user = "unknown"
    user_match = re.search(
        r"(?:user|for user|authenticating user|user=)\s*['\"]?([a-zA-Z0-9_\-\.]+)",
        line,
        re.IGNORECASE,
    )
    if user_match:
        user = user_match.group(1)
    else:
        # Check standard Linux auth log patterns: 'Failed password for invalid user admin'
        invalid_user_match = re.search(r"for\s+(?:invalid\s+user\s+)?(\S+)\s+from", line, re.IGNORECASE)
        if invalid_user_match:
            user = invalid_user_match.group(1)

    # Classify Event Type and Severity
    event_type = "UNKNOWN"

    line_lower = line.lower()
    if "brute" in line_lower or "bruteforce" in line_lower or ("failed password" in line_lower and "ssh" in line_lower):
        event_type = "SSH_BRUTE_FORCE"
    elif "port scan" in line_lower or "portscan" in line_lower or "nmap" in line_lower or "recon" in line_lower:
        event_type = "PORT_SCAN"
    elif "failed password" in line_lower or "auth failure" in line_lower or "failed login" in line_lower or "login failed" in line_lower:
        event_type = "FAILED_LOGIN"
    elif "malware" in line_lower or "virus" in line_lower or "trojan" in line_lower or "ransomware" in line_lower or "infected" in line_lower:
        event_type = "MALWARE_DETECTION"
    elif "exfiltration" in line_lower or "data transfer" in line_lower or "exfil" in line_lower or "leak" in line_lower:
        event_type = "DATA_EXFILTRATION"

    # Extract or set timestamp
    # Attempt to parse Syslog-style timestamps: e.g. "Jul 31 14:22:05" or "2026-07-31T14:22:05Z"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Simple ISO8601 regex check: 2026-07-31T14:22:05 or 2026-07-31 14:22:05
    iso_match = re.search(r"(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})", line)
    if iso_match:
        timestamp = iso_match.group(1).replace("T", " ")
    else:
        # Check syslog month/day/time: Jul 31 14:22:05
        syslog_match = re.search(
            r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2})\b",
            line,
        )
        if syslog_match:
            month_str, day_str, time_str = syslog_match.groups()
            months = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
            current_year = datetime.now().year
            try:
                dt = datetime.strptime(f"{current_year} {months[month_str]} {day_str} {time_str}", "%Y %m %d %H:%M:%S")
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass

    # Resolve GeoIP
    geo = resolve_geoip(src_ip)

    # Asset enrichment defaults
    asset_types = ["server", "workstation", "iot_device", "database", "firewall"]
    asset_type = "server"
    for at in asset_types:
        if at in line_lower:
            asset_type = at
            break

    return {
        "timestamp": timestamp,
        "src_ip": src_ip,
        "dest_ip": dest_ip,
        "event_type": event_type,
        "severity": SEVERITY_LEVELS[event_type],
        "user": user,
        "raw_log": line,
        "asset_type": asset_type,
        "geo": geo,
    }
