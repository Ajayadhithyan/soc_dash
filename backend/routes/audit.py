"""
Audit Log API routes.
Provides endpoints for retrieving action logs executed on the platform.
"""

from fastapi import APIRouter, Depends, Query

from backend.services.auth import optional_current_user
from backend.services.container import get_db

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("")
async def get_audit_logs(
    db=Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(optional_current_user),
):
    cursor = db["audit_logs"].find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    logs = []
    async for doc in cursor:
        logs.append(doc)
    return {"audit_logs": logs, "count": len(logs)}
