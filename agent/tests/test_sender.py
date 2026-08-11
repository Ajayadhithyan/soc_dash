"""Tests for the sender: batching, retries with backoff, and heartbeat posts."""

import time
from unittest.mock import MagicMock

import pytest

from agent.event import build_event
from agent.queue import EventQueue
from agent.sender import Sender, SenderError, SUCCESS_STATUS_CODES
from agent.config import Config


def _event(**kwargs):
    return build_event(event_type="PROCESS_STARTED", category="PROCESS", **kwargs)


def _config(tmp_path):
    from agent.config import DEFAULT_CONFIG
    import copy

    data = copy.deepcopy(DEFAULT_CONFIG)
    data["agent_token"] = "test-token"
    data["agent_id"] = "endpoint-01"
    data["backend_url"] = "http://test"
    data["sender"]["batch_size"] = 2
    data["sender"]["flush_interval_seconds"] = 0.05
    data["sender"]["max_retries"] = 2
    data["sender"]["backoff_base_seconds"] = 0.01
    data["sender"]["backoff_max_seconds"] = 0.05
    data["queue"]["spool_path"] = str(tmp_path / "spool.db")
    return Config(data)


class FakeResponse:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text


def test_send_success_acks_batch(tmp_path, monkeypatch):
    cfg = _config(tmp_path)
    queue = EventQueue(spool_path=cfg.queue["spool_path"], max_in_memory=10)
    queue.put(_event(metadata={"pid": 1}))
    queue.put(_event(metadata={"pid": 2}))
    queue.put(_event(metadata={"pid": 3}))  # third event stays buffered

    sent = {}

    def fake_post(url, **kwargs):
        sent["url"] = url
        sent["payload"] = kwargs["json"]
        sent["headers"] = kwargs["headers"]
        return FakeResponse(202)

    monkeypatch.setattr("agent.sender.requests.post", fake_post)

    sender = Sender(queue, cfg)
    sender._deliver(queue.drain(2))

    assert sent["url"] == "http://test/api/agent/ingest"
    assert sent["headers"]["X-Agent-Token"] == "test-token"
    assert len(sent["payload"]["events"]) == 2
    assert sent["payload"]["agent_id"] == "endpoint-01"
    # First batch acknowledged; third event remains pending.
    assert queue.pending_count() == 1
    queue.close()


def test_retries_then_succeeds(tmp_path, monkeypatch):
    cfg = _config(tmp_path)
    queue = EventQueue(spool_path=cfg.queue["spool_path"], max_in_memory=10)
    queue.put(_event(metadata={"pid": 1}))
    attempts = {"n": 0}
    times = []

    def fake_post(url, **kwargs):
        attempts["n"] += 1
        times.append(time.monotonic())
        if attempts["n"] == 1:
            raise SenderError("network error: connection refused")
        if attempts["n"] == 2:
            return FakeResponse(503, "service unavailable")
        return FakeResponse(202)

    monkeypatch.setattr("agent.sender.requests.post", fake_post)

    sender = Sender(queue, cfg)
    sender._deliver(queue.drain(2))

    assert attempts["n"] == 3
    assert queue.pending_count() == 0  # eventually acknowledged
    assert sender.stats["sent_events"] == 1
    assert sender.stats["last_send_ok"] is True
    queue.close()


def test_failure_requeues_for_next_flush(tmp_path, monkeypatch):
    cfg = _config(tmp_path)
    cfg["sender"]["max_retries"] = 1
    queue = EventQueue(spool_path=cfg.queue["spool_path"], max_in_memory=10)
    queue.put(_event(metadata={"pid": 1}))

    def fake_post(url, **kwargs):
        raise SenderError("network error: down")

    monkeypatch.setattr("agent.sender.requests.post", fake_post)

    sender = Sender(queue, cfg)
    items = queue.drain(2)
    sender._deliver(items)

    assert sender.stats["last_send_ok"] is False
    assert sender.stats["last_error"] is not None
    # Events stay on the spool for the next flush cycle.
    assert queue.pending_count() == 1
    queue.close()


def test_backoff_is_exponential(tmp_path, monkeypatch):
    cfg = _config(tmp_path)
    cfg["sender"]["max_retries"] = 3
    cfg["sender"]["backoff_base_seconds"] = 0.05
    cfg["sender"]["backoff_max_seconds"] = 0.20
    queue = EventQueue(spool_path=cfg.queue["spool_path"], max_in_memory=10)
    queue.put(_event(metadata={"pid": 1}))
    waits = []

    def fake_post(url, **kwargs):
        raise SenderError("boom")

    def fake_wait(seconds):
        waits.append(seconds)
        time.sleep(0)

    monkeypatch.setattr("agent.sender.requests.post", fake_post)
    sender = Sender(queue, cfg)
    monkeypatch.setattr(sender, "_sleep_backoff", fake_wait)

    sender._deliver(queue.drain(2))
    # backoff sequence: 0.05, 0.10, 0.20 then give up
    assert waits == [0.05, 0.10, 0.20]
    queue.close()


def test_send_heartbeat(tmp_path, monkeypatch):
    cfg = _config(tmp_path)
    queue = EventQueue(spool_path=cfg.queue["spool_path"], max_in_memory=10)
    calls = {}

    def fake_post(url, **kwargs):
        calls["url"] = url
        calls["payload"] = kwargs["json"]
        return FakeResponse(200)

    monkeypatch.setattr("agent.sender.requests.post", fake_post)

    sender = Sender(queue, cfg)
    ok = sender.send_heartbeat({"hostname": "laptop-1", "cpu_percent": 10.0})
    assert ok is True
    assert calls["url"] == "http://test/api/agent/heartbeat"
    queue.close()


def test_heartbeat_reports_failure(tmp_path, monkeypatch):
    cfg = _config(tmp_path)
    queue = EventQueue(spool_path=cfg.queue["spool_path"], max_in_memory=10)

    def fake_post(url, **kwargs):
        raise SenderError("down")

    monkeypatch.setattr("agent.sender.requests.post", fake_post)
    sender = Sender(queue, cfg)
    assert sender.send_heartbeat({"hostname": "x"}) is False
    queue.close()