import csv
import random
import time
import argparse

from faker import Faker
from datetime import datetime
from pymongo import MongoClient

import os

# -----------------------------------
# INITIAL SETUP
# -----------------------------------

fake = Faker()

# MongoDB Connection
mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
db_name = os.getenv("DB_NAME", "soc_ai_dashboard")

client = MongoClient(mongodb_uri)

# Database
db = client[db_name]

# Collection
collection = db["security_events"]

# CSV FILE
CSV_FILE = "security_logs.csv"

# -----------------------------------
# EVENT CONFIGURATION
# -----------------------------------

EVENT_TYPES = [
    "SSH_BRUTE_FORCE",
    "PORT_SCAN",
    "FAILED_LOGIN",
    "MALWARE_DETECTION",
    "DATA_EXFILTRATION"
]

SEVERITY_LEVELS = {
    "SSH_BRUTE_FORCE": "HIGH",
    "PORT_SCAN": "MEDIUM",
    "FAILED_LOGIN": "LOW",
    "MALWARE_DETECTION": "CRITICAL",
    "DATA_EXFILTRATION": "CRITICAL"
}

USERS = [
    "root",
    "admin",
    "guest",
    "ubuntu",
    "kali",
    "test"
]

MALWARE_NAMES = [
    "Trojan.Win32",
    "LockBit.Ransomware",
    "Spyware.Keylogger",
    "Worm.AutoRun",
    "Backdoor.DarkComet"
]

COMMON_PORTS = [
    21, 22, 23, 25, 53,
    80, 110, 139, 443,
    445, 3306, 3389, 8080
]

# -----------------------------------
# CSV SETUP
# -----------------------------------

def setup_csv():

    try:

        with open(CSV_FILE, "x", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                "timestamp",
                "src_ip",
                "dest_ip",
                "event_type",
                "severity",
                "user",
                "raw_log"
            ])

        print("[+] CSV file created")

    except FileExistsError:

        print("[+] CSV file already exists")


# -----------------------------------
# GENERATE RAW LOG
# -----------------------------------

def generate_raw_log(
    event_type,
    src_ip,
    dest_ip,
    user
):

    # SSH BRUTE FORCE
    if event_type == "SSH_BRUTE_FORCE":

        attempts = random.randint(10, 100)

        return (
            f"SSH brute-force detected: "
            f"{attempts} failed login attempts "
            f"from {src_ip} targeting {dest_ip} "
            f"for user '{user}'"
        )

    # PORT SCAN
    elif event_type == "PORT_SCAN":

        ports = random.sample(
            COMMON_PORTS,
            4
        )

        return (
            f"Port scan detected from {src_ip} "
            f"against {dest_ip} "
            f"targeting ports {ports}"
        )

    # FAILED LOGIN
    elif event_type == "FAILED_LOGIN":

        return (
            f"Authentication failure for "
            f"user '{user}' from IP {src_ip}"
        )

    # MALWARE DETECTION
    elif event_type == "MALWARE_DETECTION":

        malware = random.choice(
            MALWARE_NAMES
        )

        return (
            f"Malware detected: {malware} "
            f"identified on endpoint {dest_ip} "
            f"originating from {src_ip}"
        )

    # DATA EXFILTRATION
    elif event_type == "DATA_EXFILTRATION":
        
        size_mb = round(random.uniform(50, 2000), 1)
        
        return (
            f"Anomalous data transfer: {size_mb} MB sent from {dest_ip} "
            f"to external host {src_ip} via encrypted channel"
        )

    return "Unknown security event"


# -----------------------------------
# GENERATE EVENT
# -----------------------------------

def generate_event():

    event_type = random.choice(
        EVENT_TYPES
    )

    src_ip = fake.ipv4_public()

    dest_ip = fake.ipv4_private()

    user = random.choice(
        USERS
    )

    event = {

        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "src_ip": src_ip,

        "dest_ip": dest_ip,

        "event_type": event_type,

        "severity": SEVERITY_LEVELS[
            event_type
        ],

        "user": user,

        "raw_log": generate_raw_log(
            event_type,
            src_ip,
            dest_ip,
            user
        )
    }

    return event


# -----------------------------------
# SAVE TO CSV
# -----------------------------------

def save_to_csv(event):

    with open(
        CSV_FILE,
        "a",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            event["timestamp"],
            event["src_ip"],
            event["dest_ip"],
            event["event_type"],
            event["severity"],
            event["user"],
            event["raw_log"]
        ])


# -----------------------------------
# SAVE TO MONGODB
# -----------------------------------

def save_to_mongodb(event):

    collection.insert_one(event)


# -----------------------------------
# DISPLAY EVENT
# -----------------------------------

def display_event(event):

    print("\n==============================")
    print(f"Timestamp   : {event['timestamp']}")
    print(f"Source IP   : {event['src_ip']}")
    print(f"Destination : {event['dest_ip']}")
    print(f"Event Type  : {event['event_type']}")
    print(f"Severity    : {event['severity']}")
    print(f"User        : {event['user']}")
    print(f"Raw Log     : {event['raw_log']}")
    print("==============================\n")


# -----------------------------------
# MAIN FUNCTION
# -----------------------------------

def main(
    stream=False,
    count=10
):

    setup_csv()

    # STREAMING MODE
    if stream:

        print(
            "[+] Live streaming enabled..."
        )

        while True:

            event = generate_event()

            save_to_csv(event)

            save_to_mongodb(event)

            display_event(event)

            # NEW EVENT EVERY 2 SECONDS
            time.sleep(2)

    # NORMAL MODE
    else:

        print(
            f"[+] Generating {count} events..."
        )

        for _ in range(count):

            event = generate_event()

            save_to_csv(event)

            save_to_mongodb(event)

            display_event(event)

        print(
            "[+] Log generation completed"
        )


# -----------------------------------
# ARGUMENT PARSER
# -----------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="SOC AI Log Generator"
    )

    parser.add_argument(
        "--stream",
        action="store_true",
        help="Enable live streaming"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of logs to generate"
    )

    args = parser.parse_args()

    main(
        stream=args.stream,
        count=args.count
    )