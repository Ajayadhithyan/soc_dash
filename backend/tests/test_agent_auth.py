"""
Unit tests for the agent authentication service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from backend import config
from backend.services.agent_auth import AgentAuthService


def make_db():
    db = MagicMock()
    collections = {"agent_tokens": AsyncMock()}
    db.__getitem__.side_effect = lambda key: collections.get(key, MagicMock())
    db["agent_tokens"].find_one.return_value = None
    return db


@pytest.mark.asyncio
async def test_register_and_verify_roundtrip():
    db = make_db()
    service = AgentAuthService(db)
    await service._upsert_token("super-secret-token", "endpoint-01", hostname="laptop-1")

    calls = db["agent_tokens"].replace_one.await_args_list
    assert len(calls) == 1
    filter_used = calls[0].args[0]
    doc = calls[0].args[1]
    assert doc["token_id"] == filter_used["token_id"]
    assert doc["token_hash"] != "super-secret-token"  # plaintext never stored
    assert doc["agent_id"] == "endpoint-01"

    # Simulate the stored document being returned by find_one on the next call
    db["agent_tokens"].find_one.return_value = doc
    identity = await service.verify("super-secret-token")
    assert identity is not None
    assert identity["agent_id"] == "endpoint-01"
    assert identity["hostname"] == "laptop-1"


@pytest.mark.asyncio
async def test_wrong_token_rejected():
    db = make_db()
    service = AgentAuthService(db)
    await service._upsert_token("correct-token", "endpoint-01")

    db["agent_tokens"].find_one.return_value = {
        "token_id": "x",
        "agent_id": "endpoint-01",
        "salt": "salt",
        "token_hash": "stub",
        "active": True,
    }
    assert await service.verify("wrong-token") is None
    assert await service.verify(None) is None
    assert await service.verify("") is None


@pytest.mark.asyncio
async def test_ensure_bootstrap_token_from_env(monkeypatch):
    monkeypatch.setattr(config, "AGENT_TOKEN", "env-configured-token")
    db = make_db()
    service = AgentAuthService(db)
    token = await service.ensure_bootstrap_token()
    assert token == "env-configured-token"
    assert db["agent_tokens"].replace_one.await_count >= 1


@pytest.mark.asyncio
async def test_ensure_bootstrap_token_generates_when_missing(monkeypatch):
    monkeypatch.setattr(config, "AGENT_TOKEN", "")
    db = make_db()
    service = AgentAuthService(db)
    token = await service.ensure_bootstrap_token()
    assert token and len(token) >= 20
    assert db["agent_tokens"].replace_one.await_count == 1


@pytest.mark.asyncio
async def test_ensure_bootstrap_token_reuses_existing(monkeypatch):
    monkeypatch.setattr(config, "AGENT_TOKEN", "")
    db = make_db()
    db["agent_tokens"].find_one.return_value = {"agent_id": config.AGENT_AGENT_ID}
    service = AgentAuthService(db)
    token = await service.ensure_bootstrap_token()
    assert token is None
    assert db["agent_tokens"].replace_one.await_count == 0