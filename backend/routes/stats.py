"""
Statistics API routes.
Provides endpoints for dashboard KPI metrics, charts, and analytics.
"""

from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta
from collections import Counter

from backend.services.auth import optional_current_user
from backend.services.container import get_db

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview")
async def get_overview(db=Depends(get_db), current_user: dict = Depends(optional_current_user)):
    total = await db["security_events"].count_documents({})
    critical = await db["security_events"].count_documents({"severity": "CRITICAL"})
    high = await db["security_events"].count_documents({"severity": "HIGH"})
    medium = await db["security_events"].count_documents({"severity": "MEDIUM"})
    low = await db["security_events"].count_documents({"severity": "LOW"})

    pipeline = [
        {"$match": {"risk_score": {"$exists": True}}},
        {"$group": {"_id": None, "avg_risk": {"$avg": "$risk_score"}}},
    ]
    avg_result = await db["security_events"].aggregate(pipeline).to_list(1)
    avg_risk = round(avg_result[0]["avg_risk"], 1) if avg_result else 0.0

    one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    active = await db["security_events"].count_documents({
        "severity": {"$in": ["HIGH", "CRITICAL"]},
        "timestamp": {"$gte": one_hour_ago},
    })
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
async def get_severity_distribution(db=Depends(get_db), current_user: dict = Depends(optional_current_user)):
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
async def get_event_type_distribution(db=Depends(get_db), current_user: dict = Depends(optional_current_user)):
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
async def get_timeline(
    db=Depends(get_db),
    range: str = Query("6h", pattern="^(1h|6h|24h|7d)$"),
    current_user: dict = Depends(optional_current_user),
):
    range_map = {
        "1h": timedelta(hours=1),
        "6h": timedelta(hours=6),
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
    }
    td = range_map.get(range, timedelta(hours=6))
    cutoff = (datetime.now() - td).strftime("%Y-%m-%d %H:%M:%S")

    query = {"timestamp": {"$gte": cutoff}}
    cursor = db["security_events"].find(query, {"timestamp": 1, "_id": 0}).sort("timestamp", -1).limit(2000)

    timestamps = []
    async for doc in cursor:
        timestamps.append(doc.get("timestamp", ""))

    minute_counts = Counter()
    for ts in timestamps:
        if ts:
            minute = ts[:16]
            minute_counts[minute] += 1

    max_points = 60 if range in ("1h", "6h") else 168 if range == "7d" else 96
    sorted_minutes = sorted(minute_counts.items())[-max_points:]

    return {
        "timeline": [{"time": m[0], "count": m[1]} for m in sorted_minutes],
        "range": range,
    }


@router.get("/top-sources")
async def get_top_sources(
    db=Depends(get_db),
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(optional_current_user),
):
    pipeline = [
        {"$group": {
            "_id": "$src_ip",
            "count": {"$sum": 1},
            "last_seen": {"$max": "$timestamp"},
            "events": {"$push": "$event_type"},
        }},
        {"$sort": {"count": -1}},
        {"$limit": limit},
    ]
    result = await db["security_events"].aggregate(pipeline).to_list(limit)

    sources = []
    for doc in result:
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
async def get_risk_distribution(db=Depends(get_db), current_user: dict = Depends(optional_current_user)):
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
async def get_geo_data(db=Depends(get_db), current_user: dict = Depends(optional_current_user)):
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
