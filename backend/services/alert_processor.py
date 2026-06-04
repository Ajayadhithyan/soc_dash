"""
Alert Processing Pipeline.
Generates events, runs them through ML models, and saves enriched alerts to MongoDB.
"""

import random
import logging
from datetime import datetime
from faker import Faker

fake = Faker()
logger = logging.getLogger("soc_backend")

# -----------------------------------
# EVENT CONFIGURATION
# -----------------------------------

EVENT_TYPES = [
    "SSH_BRUTE_FORCE",
    "PORT_SCAN",
    "FAILED_LOGIN",
    "MALWARE_DETECTION",
    "DATA_EXFILTRATION",
]

EVENT_WEIGHTS = [0.20, 0.25, 0.25, 0.15, 0.15]

SEVERITY_LEVELS = {
    "SSH_BRUTE_FORCE": "HIGH",
    "PORT_SCAN": "MEDIUM",
    "FAILED_LOGIN": "LOW",
    "MALWARE_DETECTION": "CRITICAL",
    "DATA_EXFILTRATION": "CRITICAL",
}

USERS = ["root", "admin", "guest", "ubuntu", "kali", "test", "sysadmin", "devops"]

MALWARE_NAMES = [
    "Trojan.Win32", "LockBit.Ransomware", "Spyware.Keylogger",
    "Worm.AutoRun", "Backdoor.DarkComet", "Emotet.Loader",
    "Cobalt.Strike.Beacon", "Mimikatz.Dump",
]

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 139, 443, 445, 3306, 3389, 8080, 8443]

ASSET_TYPES = ["server", "workstation", "iot_device", "database", "firewall"]

# Geographic source data for threat map
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


def generate_raw_log(event_type, src_ip, dest_ip, user):
    """Generate a realistic raw log string for the event type."""
    if event_type == "SSH_BRUTE_FORCE":
        attempts = random.randint(10, 100)
        return (
            f"SSH brute-force detected: {attempts} failed login attempts "
            f"from {src_ip} targeting {dest_ip} for user '{user}'"
        )
    elif event_type == "PORT_SCAN":
        ports = random.sample(COMMON_PORTS, min(4, len(COMMON_PORTS)))
        return (
            f"Port scan detected from {src_ip} against {dest_ip} "
            f"targeting ports {ports}"
        )
    elif event_type == "FAILED_LOGIN":
        return f"Authentication failure for user '{user}' from IP {src_ip}"
    elif event_type == "MALWARE_DETECTION":
        malware = random.choice(MALWARE_NAMES)
        return (
            f"Malware detected: {malware} identified on endpoint {dest_ip} "
            f"originating from {src_ip}"
        )
    elif event_type == "DATA_EXFILTRATION":
        size_mb = round(random.uniform(50, 2000), 1)
        return (
            f"Anomalous data transfer: {size_mb} MB sent from {dest_ip} "
            f"to external host {src_ip} via encrypted channel"
        )
    return "Unknown security event"


def generate_event():
    """Generate a single synthetic security event."""
    event_type = random.choices(EVENT_TYPES, weights=EVENT_WEIGHTS, k=1)[0]
    src_ip = fake.ipv4_public()
    dest_ip = fake.ipv4_private()
    user = random.choice(USERS)
    asset_type = random.choice(ASSET_TYPES)
    geo = random.choice(GEO_SOURCES)

    event = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "src_ip": src_ip,
        "dest_ip": dest_ip,
        "event_type": event_type,
        "severity": SEVERITY_LEVELS[event_type],
        "user": user,
        "raw_log": generate_raw_log(event_type, src_ip, dest_ip, user),
        "asset_type": asset_type,
        "geo": geo,
    }
    return event


# Map to track login history of users: { username: { country, timestamp_str, lat, lng } }
last_login_locations = {}

def check_impossible_travel(event):
    """
    Check if a user logs in from two different countries in a timeframe
    physically impossible to travel, overriding to IMPOSSIBLE_TRAVEL if so.
    """
    global last_login_locations
    user = event.get("user")
    event_type = event.get("event_type")
    geo = event.get("geo")
    
    if not user or not geo or user in ["SYSTEM", "unknown"]:
        return event

    # Check for login related event types
    if event_type in ["FAILED_LOGIN", "SSH_BRUTE_FORCE"]:
        now_str = event.get("timestamp")
        try:
            now_dt = datetime.strptime(now_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            now_dt = datetime.now()
            
        last_login = last_login_locations.get(user)
        if last_login:
            last_country = last_login["country"]
            last_time_str = last_login["timestamp"]
            try:
                last_dt = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                last_dt = now_dt
                
            time_diff = (now_dt - last_dt).total_seconds()
            
            # If country is different and time diff is extremely short (e.g. less than 200 seconds)
            if last_country != geo["country"] and 0 < time_diff < 200:
                # Trigger IMPOSSIBLE_TRAVEL alert
                event["event_type"] = "IMPOSSIBLE_TRAVEL"
                event["severity"] = "CRITICAL"
                event["raw_log"] = (
                    f"Impossible travel detected: User '{user}' authenticated "
                    f"from {geo['country']} at {now_str} after logging in "
                    f"from {last_country} at {last_time_str} ({int(time_diff)}s ago)."
                )
                logger.warning(f"Impossible travel flagged for user '{user}': {last_country} -> {geo['country']}")
        
        # Update last login location
        last_login_locations[user] = {
            "country": geo["country"],
            "timestamp": now_str,
            "lat": geo.get("lat"),
            "lng": geo.get("lng")
        }
    return event


def dispatch_webhook(event):
    """
    Simulates sending a Slack webhook notification for CRITICAL severity alerts.
    """
    severity = event.get("severity", "LOW")
    if severity == "CRITICAL":
        event_type = event.get("event_type")
        risk = event.get("risk_score")
        user = event.get("user")
        src_ip = event.get("src_ip")

        slack_payload = {
            "text": f"🚨 *CRITICAL ALERT DETECTED* 🚨\n"
                    f"*Type:* `{event_type}`\n"
                    f"*Risk Score:* `{risk}`/100\n"
                    f"*Source IP:* `{src_ip}`\n"
                    f"*Target User:* `{user}`\n"
                    f"*Raw Log:* `{event.get('raw_log')}`"
        }
        logger.info(f"[Slack Webhook Sim] Dispatching notification payload:\n{slack_payload['text']}")


async def process_event(event, anomaly_detector, mitre_mapper, summarizer, risk_scorer):
    """
    Run a single event through the full ML pipeline.

    Pipeline: event → anomaly score → MITRE map → LLM summary → risk score

    Returns the enriched event dict ready for MongoDB insertion.
    """
    # Run Impossible Travel rule check
    event = check_impossible_travel(event)

    # 1. Anomaly Detection
    anomaly_score = anomaly_detector.score(event)
    event["anomaly_score"] = anomaly_score

    # 2. MITRE ATT&CK Mapping
    mitre = mitre_mapper.map_event(event)
    event["mitre"] = mitre

    # 3. AI Summary
    summary = summarizer.summarize(event)
    event["ai_summary"] = summary

    # 4. Risk Scoring
    risk = risk_scorer.score(event, anomaly_score)
    event["risk_score"] = risk["risk_score"]
    event["risk_label"] = risk["risk_label"]
    event["cvss_base"] = risk["cvss_base"]
    event["asset_criticality"] = risk["asset_criticality"]

    # Dispatch simulated Slack Webhook for Critical alerts
    dispatch_webhook(event)

    return event
