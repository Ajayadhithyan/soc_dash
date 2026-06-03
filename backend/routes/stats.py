"""
Statistics API routes.
Provides endpoints for dashboard KPI metrics, charts, and analytics.
"""

from fastapi import APIRouter
from datetime import datetime, timedelta
from collections import Counter

router = APIRouter(prefix="/api/stats", tags=["stats"])

# Will be set from main.py
db = None


def set_db(database):
    global db
    db = database


@router.get("/overview")
async def get_overview():
    """Get KPI overview metrics for the dashboard."""
    total = await db["security_events"].count_documents({})
    critical = await db["security_events"].count_documents({"severity": "CRITICAL"})
    high = await db["security_events"].count_documents({"severity": "HIGH"})
    medium = await db["security_events"].count_documents({"severity": "MEDIUM"})
    low = await db["security_events"].count_documents({"severity": "LOW"})

    # Average risk score
    pipeline = [
        {"$match": {"risk_score": {"$exists": True}}},
        {"$group": {"_id": None, "avg_risk": {"$avg": "$risk_score"}}},
    ]
    avg_result = await db["security_events"].aggregate(pipeline).to_list(1)
    avg_risk = round(avg_result[0]["avg_risk"], 1) if avg_result else 0.0

    # Active threats (high + critical in last hour)
    one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    active = await db["security_events"].count_documents({
        "severity": {"$in": ["HIGH", "CRITICAL"]},
        "timestamp": {"$gte": one_hour_ago},
    })

    # Alerts in last hour
    alerts_last_hour = await db["security_events"].count_documents({
        "timestamp": {"$gte": one_hour_ago},
    })

    return {
        "total_alerts": total,
        "critical_count": critical,
        "high_count": high,
        "medium_count": medium,
        "low_count": low,
        "avg_risk_score": avg_risk,
        "active_threats": active,
        "alerts_last_hour": alerts_last_hour,
    }


@router.get("/severity")
async def get_severity_distribution():
    """Get severity distribution for bar chart."""
    pipeline = [
        {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    result = await db["security_events"].aggregate(pipeline).to_list(10)

    distribution = []
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    for doc in result:
        distribution.append({
            "severity": doc["_id"] or "UNKNOWN",
            "count": doc["count"],
        })

    distribution.sort(key=lambda x: severity_order.get(x["severity"], 99))
    return {"distribution": distribution}


@router.get("/event-types")
async def get_event_type_distribution():
    """Get event type distribution for charts."""
    pipeline = [
        {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    result = await db["security_events"].aggregate(pipeline).to_list(20)

    return {
        "event_types": [
            {"event_type": doc["_id"] or "UNKNOWN", "count": doc["count"]}
            for doc in result
        ]
    }


@router.get("/timeline")
async def get_timeline():
    """Get alerts over time for line chart (grouped by minute)."""
    # Get last 60 entries grouped by minute
    cursor = db["security_events"].find(
        {}, {"timestamp": 1, "_id": 0}
    ).sort("timestamp", -1).limit(500)

    timestamps = []
    async for doc in cursor:
        timestamps.append(doc.get("timestamp", ""))

    # Group by minute
    minute_counts = Counter()
    for ts in timestamps:
        if ts:
            # Truncate to minute
            minute = ts[:16]  # "YYYY-MM-DD HH:MM"
            minute_counts[minute] += 1

    # Sort and return last 30 minutes
    sorted_minutes = sorted(minute_counts.items())[-30:]

    return {
        "timeline": [
            {"time": m[0], "count": m[1]}
            for m in sorted_minutes
        ]
    }


@router.get("/top-sources")
async def get_top_sources():
    """Get top attacking source IPs."""
    pipeline = [
        {"$group": {
            "_id": "$src_ip",
            "count": {"$sum": 1},
            "last_seen": {"$max": "$timestamp"},
            "events": {"$push": "$event_type"},
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    result = await db["security_events"].aggregate(pipeline).to_list(10)

    sources = []
    for doc in result:
        # Get the most common event type for this IP
        event_counts = Counter(doc.get("events", []))
        primary_attack = event_counts.most_common(1)[0][0] if event_counts else "UNKNOWN"

        sources.append({
            "ip": doc["_id"] or "unknown",
            "count": doc["count"],
            "last_seen": doc.get("last_seen", ""),
            "primary_attack": primary_attack,
        })

    return {"sources": sources}


@router.get("/risk-distribution")
async def get_risk_distribution():
    """Get risk score distribution for analytics."""
    pipeline = [
        {"$match": {"risk_label": {"$exists": True}}},
        {"$group": {"_id": "$risk_label", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    result = await db["security_events"].aggregate(pipeline).to_list(10)

    return {
        "risk_distribution": [
            {"label": doc["_id"] or "Unknown", "count": doc["count"]}
            for doc in result
        ]
    }


@router.get("/geo")
async def get_geo_data():
    """Get geographic threat data for the world map."""
    pipeline = [
        {"$match": {"geo": {"$exists": True}}},
        {"$group": {
            "_id": "$geo.country",
            "count": {"$sum": 1},
            "lat": {"$first": "$geo.lat"},
            "lng": {"$first": "$geo.lng"},
        }},
        {"$sort": {"count": -1}},
    ]
    result = await db["security_events"].aggregate(pipeline).to_list(50)

    return {
        "geo_threats": [
            {
                "country": doc["_id"] or "Unknown",
                "count": doc["count"],
                "lat": doc.get("lat", 0),
                "lng": doc.get("lng", 0),
            }
            for doc in result
        ]
    }
