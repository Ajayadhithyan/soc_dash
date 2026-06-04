"""
Audit Log API routes.
Provides endpoints for retrieving action logs executed on the platform.
"""

from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/audit", tags=["audit"])

# Will be set from main.py
db = None


def set_db(database):
    global db
    db = database


@router.get("")
async def get_audit_logs(limit: int = Query(50, ge=1, le=100)):
    """Get the most recent SOAR audit logs."""
    if db is None:
        return {"audit_logs": [], "count": 0}

    cursor = db["audit_logs"].find(
        {}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit)

    logs = []
    async for doc in cursor:
        logs.append(doc)

    return {"audit_logs": logs, "count": len(logs)}
