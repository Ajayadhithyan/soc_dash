"""
API tests for the endpoint agent routes (/api/agent/*).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from backend.routes import agent as agent_routes
from backend.services.auth import create_access_token
from backend.services.container import container


class FakeCursor:
    """Async-iterable stand-in for a Motor cursor."""

    def __init__(self, docs):
        self.docs = list(docs)
        self._pos = 0

    def sort(self, *args, **kwargs):
        return self

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._pos >= len(self.docs):
            raise StopAsyncIteration
        doc = self.docs[self._pos]
        self._pos += 1
        return doc


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.include_router(agent_routes.router)
    return test_app


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    auth = AsyncMock()
    auth.verify.return_value = None
    monkeypatch.setattr(container, "_agent_auth", auth)
    db = MagicMock()
    collections = {
        "security_events": AsyncMock(),
        "agent_tokens": AsyncMock(),
        "endpoints": AsyncMock(),
        "audit_logs": AsyncMock(),
    }
    db.__getitem__.side_effect = lambda key: collections.get(key, MagicMock())
    monkeypatch.setattr(container, "_db", db)
    yield db
    monkeypatch.setattr(container, "_db", None)
    monkeypatch.setattr(container, "_agent_auth", None)


VALID_IDENTITY = {"agent_id": "endpoint-01", "hostname": "laptop-1", "is_bootstrap": False}


async def _post_events(ac, events, token="valid-token"):
    headers = {"X-Agent-Token": token}
    return await ac.post(
        "/api/agent/ingest",
        json={"events": events, "agent_id": "endpoint-01", "hostname": "laptop-1"},
        headers=headers,
    )


@pytest.mark.asyncio
async def test_ingest_rejects_missing_token(app, mock_env):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/agent/ingest", json={"events": []})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_ingest_rejects_invalid_token(app, mock_env):
    container._agent_auth.verify.return_value = None
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await _post_events(ac, [{"event_type": "PROCESS_STARTED"}])
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_ingest_batch_success(app, mock_env):
    container._agent_auth.verify.return_value = VALID_IDENTITY
    events = [
        {
            "timestamp": "2026-08-06T10:00:00Z",
            "event_type": "PROCESS_STARTED",
            "severity": "LOW",
            "user": "alice",
            "raw_log": "Process started: powershell.exe",
            "metadata": {"pid": 1234},
        },
        {
            "event_type": "NETWORK_CONNECTION",
            "src_ip": "10.0.0.5",
            "dest_ip": "8.8.8.8",
            "raw_log": "Outbound connection to 8.8.8.8:443",
        },
    ]
    with patch(
        "backend.routes.agent.process_and_persist", new=AsyncMock(return_value={"id": "e1"})
    ) as mock_pipeline:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await _post_events(ac, events)

    assert response.status_code == 202
    data = response.json()
    assert data["accepted"] == 2
    assert data["total"] == 2
    assert data["agent_id"] == "endpoint-01"

    # Every event passed to the pipeline must be tagged with the verified identity
    assert mock_pipeline.await_count == 2
    for call in mock_pipeline.await_args_list:
        raw = call.args[1]
        assert raw["agent_id"] == "endpoint-01"
        assert raw["event_type"] in {"PROCESS_STARTED", "NETWORK_CONNECTION"}


@pytest.mark.asyncio
async def test_heartbeat_upserts_endpoint(app, mock_env):
    container._agent_auth.verify.return_value = VALID_IDENTITY
    update_one = AsyncMock(return_value=MagicMock())
    mock_env["endpoints"].update_one = update_one

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/agent/heartbeat",
            json={
                "hostname": "laptop-1",
                "os": "Windows",
                "os_version": "11",
                "agent_version": "0.1.0",
                "cpu_percent": 12.5,
                "memory_percent": 44.0,
                "disk_percent": 60.1,
                "ip": "10.0.0.5",
            },
            headers={"X-Agent-Token": "valid-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"

    filter_used = update_one.call_args.args[0]
    update_used = update_one.call_args.args[1]
    upsert = update_one.call_args.kwargs["upsert"]
    assert filter_used == {"agent_id": "endpoint-01"}
    assert upsert is True
    assert update_used["$set"]["os"] == "Windows"
    assert update_used["$set"]["cpu_percent"] == 12.5


@pytest.mark.asyncio
async def test_endpoints_list_requires_jwt(app, mock_env):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/agent/endpoints")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_endpoints_list_success(app, mock_env):
    docs = [
        {
            "agent_id": "endpoint-01",
            "hostname": "laptop-1",
            "os": "Windows",
            "os_version": "11",
            "agent_version": "0.1.0",
            "cpu_percent": 10.0,
            "memory_percent": 30.0,
            "disk_percent": 55.0,
            "ip": "10.0.0.5",
            "last_seen": "2026-08-18T10:00:00+00:00",
        },
        {
            "agent_id": "endpoint-02",
            "hostname": "server-1",
            "os": "Linux",
            "os_version": "Ubuntu 22.04",
            "agent_version": "0.1.0",
            "cpu_percent": 5.0,
            "memory_percent": 20.0,
            "disk_percent": 40.0,
            "ip": "10.0.0.6",
            "last_seen": "2020-01-01T00:00:00+00:00",
        },
    ]
    mock_env["endpoints"].find = MagicMock(return_value=FakeCursor(docs))
    mock_env["security_events"].count_documents = AsyncMock(return_value=7)

    token = create_access_token("admin", "admin")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/api/agent/endpoints", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    by_id = {e["agent_id"]: e for e in data["endpoints"]}
    assert by_id["endpoint-01"]["status"] == "ONLINE"
    assert by_id["endpoint-02"]["status"] == "OFFLINE"
    assert by_id["endpoint-02"]["is_online"] is False
    assert by_id["endpoint-01"]["event_count"] == 7