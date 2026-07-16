"""
CLI script to clear MongoDB collections.
Uses config module for connection settings.
"""

import sys
from pymongo import MongoClient

sys.path.insert(0, ".")
from backend import config


def main():
    mongodb_uri = config.MONGODB_URI
    db_name = config.DB_NAME

    print(f"Connecting to MongoDB at {mongodb_uri}...")
    client = MongoClient(mongodb_uri)
    db = client[db_name]

    collections_to_clear = ["security_events", "audit_logs"]
    for col_name in collections_to_clear:
        count = db[col_name].count_documents({})
        print(f"Found {count} documents in collection '{col_name}'. Wiping them...")
        db[col_name].delete_many({})
        print(f"Collection '{col_name}' cleared. Document count now: {db[col_name].count_documents({})}")

    client.close()
    print("Done database wipe!")


if __name__ == "__main__":
    main()
