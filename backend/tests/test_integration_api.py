import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from backend.routes import alerts as alert_routes
from backend.services.auth import create_access_token
from backend.services.container import container


@pytest.fixture(autouse=True)
def setup_mock_db():
    mock_db = MagicMock()
    collections = {
        "security_events": AsyncMock(),
        "audit_logs": AsyncMock(),
    }
    collections["security_events"].find_one = AsyncMock(return_value={"_id": "test_id", "id": "test_alert_id", "src_ip": "10.0.0.1"})
    collections["security_events"].update_one = AsyncMock(return_value=AsyncMock(matched_count=1))
    mock_db.__getitem__.side_effect = lambda key: collections.get(key, MagicMock())
    
    old_db = container._db
    old_threat_intel = container._threat_intel
    
    container._db = mock_db
    container._threat_intel = MagicMock()
    
    yield
    
    container._db = old_db
    container._threat_intel = old_threat_intel


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.include_router(alert_routes.router)
    return test_app


@pytest.mark.asyncio
async def test_viewer_role_restrictions(app):
    token = create_access_token("viewer_user", "viewer")
    headers = {"Authorization": f"Bearer {token}"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Try to toggle synthetic config (should fail/deny)
        resp1 = await ac.post("/api/alerts/config/synthetic?enabled=true", headers=headers)
        assert resp1.status_code == 200
        assert resp1.json()["success"] is False
        assert "Insufficient permissions" in resp1.json()["message"]

        # 2. Try to respond to alert (should fail/deny)
        resp2 = await ac.post("/api/alerts/test_alert_id/respond?action=block_ip", headers=headers)
        assert resp2.status_code == 200
        assert resp2.json()["success"] is False
        assert "Insufficient permissions" in resp2.json()["message"]

        # 3. Try to verify alert (should fail/deny)
        resp3 = await ac.post("/api/alerts/test_alert_id/verify?status=TRUE_POSITIVE", headers=headers)
        assert resp3.status_code == 200
        assert resp3.json()["success"] is False
        assert "Insufficient permissions" in resp3.json()["message"]


@pytest.mark.asyncio
async def test_analyst_role_capabilities(app):
    token = create_access_token("analyst_user", "analyst")
    headers = {"Authorization": f"Bearer {token}"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Can verify alert (should succeed)
        resp1 = await ac.post("/api/alerts/test_alert_id/verify?status=TRUE_POSITIVE", headers=headers)
        assert resp1.status_code == 200
        assert resp1.json()["success"] is True

        # 2. Can run non-destructive respond (should succeed)
        resp2 = await ac.post("/api/alerts/test_alert_id/respond?action=create_ticket", headers=headers)
        assert resp2.status_code == 200
        assert resp2.json()["success"] is True

        # 3. Cannot run destructive respond (should fail/deny)
        resp3 = await ac.post("/api/alerts/test_alert_id/respond?action=block_ip", headers=headers)
        assert resp3.status_code == 200
        assert resp3.json()["success"] is False
        assert "Insufficient permissions" in resp3.json()["message"]


@pytest.mark.asyncio
async def test_admin_role_capabilities(app):
    token = create_access_token("admin_user", "admin")
    headers = {"Authorization": f"Bearer {token}"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Can toggle synthetic config (should succeed)
        resp1 = await ac.post("/api/alerts/config/synthetic?enabled=true", headers=headers)
        assert resp1.status_code == 200
        assert resp1.json()["success"] is True

        # 2. Can run destructive respond (should succeed)
        resp2 = await ac.post("/api/alerts/test_alert_id/respond?action=block_ip", headers=headers)
        assert resp2.status_code == 200
        assert resp2.json()["success"] is True
