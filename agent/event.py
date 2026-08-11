"""
Normalized Event Schema.

Every monitor — regardless of what it observes — emits events in this exact
shape. The backend only ever processes this normalized format, so the schema
is the single contract between the agent and the SOC platform.

Field contract (mirrored by the backend's AgentEvent model):
    timestamp   ISO 8601 UTC (server fills it in if missing)
    hostname    endpoint hostname
    agent_id    unique agent identity (backend overrides from the verified token)
    os          operating system (e.g. "Windows 11", "Linux Ubuntu 22.04")
    event_type  telemetry type, e.g. PROCESS_STARTED, NETWORK_CONNECTION
    severity    LOW | MEDIUM | HIGH | CRITICAL
    user        username associated with the event ("unknown" if not applicable)
    src_ip      source IP ("0.0.0.0" when not applicable)
    dest_ip     destination IP ("0.0.0.0" when not applicable)
    category    telemetry source: PROCESS, NETWORK, LOGIN, FILE, REGISTRY,
                SERVICE, USB, DNS
    metadata    monitor-specific details (free-form dict)
    raw_log     human-readable description of the event
"""

import platform
import socket
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import agent as agent_pkg

EVENT_REQUIRED_FIELDS = (
    "timestamp",
    "hostname",
    "agent_id",
    "os",
    "event_type",
    "severity",
    "user",
    "src_ip",
    "dest_ip",
    "category",
    "metadata",
    "raw_log",
)

SEVERITY_LEVELS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


class EventError(Exception):
    """Raised when an event cannot be built or normalized."""


def current_timestamp() -> str:
    """ISO 8601 UTC timestamp string, matching the backend's expectation."""
    return datetime.now(timezone.utc).isoformat()


def system_identity() -> Dict[str, str]:
    """Static endpoint identity shared by all events."""
    return {
        "hostname": socket.gethostname(),
        "os": f"{platform.system()} {platform.release()}",
        "agent_version": agent_pkg.__version__,
    }


def build_event(
    event_type: str,
    category: str,
    metadata: Optional[Dict[str, Any]] = None,
    severity: str = "LOW",
    user: str = "unknown",
    src_ip: str = "0.0.0.0",
    dest_ip: str = "0.0.0.0",
    raw_log: str = "",
    hostname: str = "",
    agent_id: str = "",
    os_name: str = "",
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a normalized event dict with safe defaults for every field.
    `hostname`/`agent_id`/`os` fall back to the endpoint's identity when not
    provided by the caller.
    """
    if not event_type:
        raise EventError("event_type is required")
    if not category:
        raise EventError("category is required")
    if severity not in SEVERITY_LEVELS:
        raise EventError(f"invalid severity {severity!r}; must be one of {SEVERITY_LEVELS}")

    identity = system_identity()
    event = {
        "timestamp": timestamp or current_timestamp(),
        "hostname": hostname or identity["hostname"],
        "agent_id": agent_id,
        "os": os_name or identity["os"],
        "event_type": event_type,
        "severity": severity,
        "user": user or "unknown",
        "src_ip": src_ip or "0.0.0.0",
        "dest_ip": dest_ip or "0.0.0.0",
        "category": category,
        "metadata": metadata or {},
        "raw_log": raw_log,
    }
    return event


def validate_event(event: Dict[str, Any]) -> None:
    """Ensure an event dict conforms to the schema; raise EventError if not."""
    missing = [f for f in EVENT_REQUIRED_FIELDS if f not in event]
    if missing:
        raise EventError(f"event missing required fields: {', '.join(missing)}")
    if not event.get("event_type"):
        raise EventError("event_type must not be empty")
    if not event.get("category"):
        raise EventError("category must not be empty")
    if event.get("severity") not in SEVERITY_LEVELS:
        raise EventError(f"invalid severity {event.get('severity')!r}")


def sanitize_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Return a JSON-safe copy of an event (no non-serializable values)."""
    import json

    def _clean(value: Any) -> Any:
        if isinstance(value, dict):
            return {str(k): _clean(v) for k, v in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [_clean(v) for v in value]
        try:
            json.dumps(value)
            return value
        except (TypeError, ValueError):
            return str(value)

    return {k: _clean(v) for k, v in event.items()}