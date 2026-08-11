"""
Configuration Manager.

Loads and validates the agent configuration from a YAML file with sensible
defaults. Environment variables override specific values so secrets are never
hardcoded into the config file:
    * AGENT_TOKEN      — agent API token
    * AGENT_BACKEND_URL — SOC backend URL
    * AGENT_CONFIG      — path to the config file
"""

import copy
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_CONFIG: Dict[str, Any] = {
    "backend_url": "http://localhost:8000",
    "agent_token": "",
    "agent_id": "endpoint-01",
    "hostname": "",
    "collection_interval_seconds": 5,
    "log_level": "INFO",
    "log_dir": "logs",
    "log_max_bytes": 5_000_000,
    "log_backups": 3,
    "queue": {
        "max_in_memory": 5000,
        "max_spooled": 20000,
        "spool_path": "data/agent_spool.db",
    },
    "sender": {
        "batch_size": 50,
        "flush_interval_seconds": 5,
        "max_retries": 10,
        "backoff_base_seconds": 1,
        "backoff_max_seconds": 60,
        "timeout_seconds": 10,
        "verify_ssl": True,
    },
    "heartbeat": {
        "interval_seconds": 30,
    },
    "monitors": {
        "process": True,
        "network": False,
        "login": False,
        "file_integrity": False,
        "service": False,
        "registry": False,
        "usb": False,
        "dns": False,
    },
}

ENV_OVERRIDES = {
    "agent_token": "AGENT_TOKEN",
    "backend_url": "AGENT_BACKEND_URL",
}


class ConfigError(Exception):
    """Raised when the agent configuration is invalid."""


class Config:
    """Validated agent configuration."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    @property
    def raw(self) -> Dict[str, Any]:
        return self._data

    @property
    def backend_url(self) -> str:
        return self._data["backend_url"].rstrip("/")

    @property
    def agent_token(self) -> str:
        return self._data["agent_token"]

    @property
    def agent_id(self) -> str:
        return self._data["agent_id"]

    @property
    def hostname(self) -> str:
        return self._data["hostname"]

    @property
    def collection_interval_seconds(self) -> float:
        return float(self._data["collection_interval_seconds"])

    @property
    def log_level(self) -> str:
        return self._data["log_level"].upper()

    @property
    def sender(self) -> Dict[str, Any]:
        return self._data["sender"]

    @property
    def queue(self) -> Dict[str, Any]:
        return self._data["queue"]

    @property
    def heartbeat(self) -> Dict[str, Any]:
        return self._data["heartbeat"]

    @property
    def monitors(self) -> Dict[str, bool]:
        return self._data["monitors"]


def _resolve_path(value: str, base_dir: Path) -> str:
    """Resolve a possibly-relative path against the config file directory."""
    p = Path(value)
    if not p.is_absolute():
        p = base_dir / p
    return str(p)


def load_config(config_path: Optional[str] = None) -> "Config":
    """
    Load configuration from the given file, an `AGENT_CONFIG` environment
    variable, or the default `agent_config.yaml`, then validate it.
    """
    import yaml

    cli_path = config_path
    env_path = os.getenv("AGENT_CONFIG")
    candidate = cli_path or env_path

    if candidate:
        path = Path(candidate)
    else:
        path = Path(__file__).resolve().parent / "agent_config.yaml"

    data = copy.deepcopy(DEFAULT_CONFIG)

    if path.exists():
        with open(path, "r", encoding="utf-8") as fh:
            loaded = yaml.safe_load(fh) or {}
        if not isinstance(loaded, dict):
            raise ConfigError(f"Config file {path} must be a YAML mapping.")
        data = _deep_merge(data, loaded)
    else:
        data["load_source"] = "defaults"

    data["config_file"] = str(path)
    base_dir = path.resolve().parent

    # Environment variable overrides (secrets / deployment-specific values)
    for key, env_name in ENV_OVERRIDES.items():
        value = os.getenv(env_name)
        if value is not None:
            _set_merge(data, key.split("."), value)

    # Resolve relative paths against the config file directory
    data["queue"]["spool_path"] = _resolve_maybe_path(data["queue"]["spool_path"], base_dir)
    data["log_dir"] = _resolve_maybe_path(data["log_dir"], base_dir)

    validate_config(data)
    return Config(data)


def _resolve_maybe_path(value: str, base_dir: Path) -> str:
    p = Path(value)
    return str(base_dir / p) if not p.is_absolute() else str(p)


def _deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge overlay into a copy of base."""
    result = copy.deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _set_merge(data: Dict[str, Any], keys: List[str], value: Any) -> None:
    node = data
    for key in keys[:-1]:
        node = node.setdefault(key, {})
    if keys:
        node[keys[-1]] = value


def validate_config(data: Dict[str, Any]) -> None:
    """Validate types and ranges; raise ConfigError on failures."""
    errors = []

    backend_url = data.get("backend_url", "")
    if not str(backend_url).startswith(("http://", "https://")):
        errors.append("backend_url must start with http:// or https://")

    if not data.get("agent_token"):
        errors.append("agent_token is required (set it in the config or AGENT_TOKEN env)")

    if not data.get("agent_id"):
        errors.append("agent_id must not be empty")

    if data.get("collection_interval_seconds", 0) <= 0:
        errors.append("collection_interval_seconds must be > 0")

    if data.get("queue", {}).get("max_in_memory", 0) <= 0:
        errors.append("queue.max_in_memory must be > 0")

    sender = data.get("sender", {})
    if sender.get("batch_size", 0) <= 0:
        errors.append("sender.batch_size must be > 0")
    if sender.get("backoff_base_seconds", 0) <= 0:
        errors.append("sender.backoff_base_seconds must be > 0")
    if sender.get("backoff_max_seconds", 0) < sender.get("backoff_base_seconds", 0):
        errors.append("sender.backoff_max_seconds must be >= backoff_base_seconds")

    if data.get("heartbeat", {}).get("interval_seconds", 0) <= 0:
        errors.append("heartbeat.interval_seconds must be > 0")

    if errors:
        raise ConfigError(
            "Invalid configuration:\n  - " + "\n  - ".join(errors)
        )


# Monitors known to the framework. Each key maps to a monitor module if implemented.
VALID_MONITORS = ["process", "network", "login", "file_integrity", "service", "registry", "usb", "dns"]