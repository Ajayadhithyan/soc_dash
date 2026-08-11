"""Tests for the configuration manager."""

import copy

import pytest

from agent.config import (
    DEFAULT_CONFIG,
    ConfigError,
    load_config,
    validate_config,
)

EXAMPLE_CONFIG = str(__import__("pathlib").Path(__file__).resolve().parents[1] / "agent_config.example.yaml")


def _valid_data() -> dict:
    data = copy.deepcopy(DEFAULT_CONFIG)
    data["agent_token"] = "test-token"
    data["agent_id"] = "endpoint-01"
    return data


def test_load_example_config_is_valid():
    # The shipped example requires a token; env override must satisfy validation.
    import os

    os.environ["AGENT_TOKEN"] = "env-token"
    try:
        cm = load_config(EXAMPLE_CONFIG)
        assert cm.backend_url == "http://localhost:8000"
        assert cm.agent_token == "env-token"
        assert cm.collection_interval_seconds > 0
        assert cm.monitors["process"] is True
    finally:
        os.environ.pop("AGENT_TOKEN", None)


def test_defaults_have_required_keys():
    data = _valid_data()
    validate_config(data)  # must not raise
    assert "process" in data["monitors"]


@pytest.mark.parametrize(
    "mutate,error_fragment",
    [
        (lambda d: d.update({"backend_url": "localhost:8000"}), "backend_url"),
        (lambda d: d.update({"agent_token": ""}), "agent_token"),
        (lambda d: d.update({"collection_interval_seconds": 0}), "collection_interval_seconds"),
        (lambda d: d["queue"].update({"max_in_memory": 0}), "max_in_memory"),
        (lambda d: d["sender"].update({"batch_size": 0}), "batch_size"),
        (
            lambda d: d["sender"].update({"backoff_max_seconds": 0}),
            "backoff_max_seconds",
        ),
        (lambda d: d["heartbeat"].update({"interval_seconds": -1}), "interval_seconds"),
    ],
)
def test_invalid_configs_raise(mutate, error_fragment):
    data = _valid_data()
    mutate(data)
    with pytest.raises(ConfigError) as exc_info:
        validate_config(data)
    assert error_fragment in str(exc_info.value)


def test_missing_config_file_uses_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENT_TOKEN", "t")
    monkeypatch.setenv("AGENT_CONFIG", str(tmp_path / "nope.yaml"))
    cm = load_config()
    assert cm.backend_url == "http://localhost:8000"


def test_env_overrides_backend_url(monkeypatch, tmp_path):
    monkeypatch.setenv("AGENT_TOKEN", "t")
    monkeypatch.setenv("AGENT_BACKEND_URL", "https://soc.example.com")
    monkeypatch.setenv("AGENT_CONFIG", str(tmp_path / "nope.yaml"))
    cm = load_config()
    assert cm.backend_url == "https://soc.example.com"