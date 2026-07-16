import pytest
from unittest.mock import AsyncMock

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from backend.routes import auth as auth_routes
from backend.services.auth import create_access_token
from backend.services.container import container


@pytest.fixture(autouse=True)
def setup_mock_auth():
    container._auth_service = AsyncMock()
    container._auth_service.authenticate = AsyncMock()
    yield
    container._auth_service = None


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.include_router(auth_routes.router)
    return test_app


@pytest.mark.asyncio
async def test_login_success(app, setup_mock_auth):
    container._auth_service.authenticate.return_value = {"username": "admin", "role": "admin"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_failure(app, setup_mock_auth):
    container._auth_service.authenticate.return_value = None
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={"username": "admin", "password": "wrong1"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_endpoint():
    from backend.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
