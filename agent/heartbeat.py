"""
Heartbeat reporter.

Periodically reports endpoint liveness and resource usage to the backend so
the dashboard can show endpoint status (ONLINE / OFFLINE) with: hostname, OS,
agent version, CPU usage, memory usage, disk usage, and last check-in.
"""

import logging
import socket
import threading
import time
from typing import Dict, Optional

import psutil

import agent as agent_pkg
from agent.event import system_identity

logger = logging.getLogger("soc-agent")


def collect_metrics() -> Dict:
    """Collect hostname, OS, agent version, and resource usage."""
    identity = system_identity()
    try:
        disk_usage = psutil.disk_usage("/")
        ip = _local_ip()
    except Exception:
        ip = "0.0.0.0"
        disk_usage = None

    return {
        "hostname": identity["hostname"],
        "os": platform_system_name(),
        "os_version": platform_release(),
        "agent_version": agent_pkg.__version__,
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": disk_usage.percent if disk_usage else 0.0,
        "ip": ip,
    }


def platform_system_name() -> str:
    import platform

    return platform.system()


def platform_release() -> str:
    import platform

    return platform.release()


def _local_ip() -> str:
    """Best-effort discovery of the primary outbound IP address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except (socket.error, OSError):
        try:
            return socket.gethostbyname(socket.gethostname())
        except (socket.error, OSError):
            return "0.0.0.0"


class Heartbeat:
    """Background thread posting periodic heartbeat payloads."""

    def __init__(self, sender, interval_seconds: float):
        self._sender = sender
        self._interval = float(interval_seconds)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_ok = False

    @property
    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    @property
    def last_ok(self) -> bool:
        return self._last_ok

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="heartbeat", daemon=True)
        self._thread.start()
        logger.info("Heartbeat started (every %.0fs)", self._interval)

    def stop(self, timeout: float = 5.0) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)
            logger.info("Heartbeat stopped")

    def _run(self) -> None:
        # Send an immediate heartbeat on startup, then periodically.
        self._send()
        while not self._stop_event.wait(self._interval):
            self._send()

    def _send(self) -> None:
        try:
            payload = collect_metrics()
        except Exception as exc:
            logger.warning("Heartbeat metrics collection failed: %s", exc)
            return
        self._last_ok = self._sender.send_heartbeat(payload)