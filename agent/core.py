"""
Agent Core.

The operating system of the agent:
    * starts all enabled monitors, the sender, and the heartbeat
    * watchdog that restarts failed monitor threads
    * graceful shutdown (flush, ack, durable spool)
    * health checks
"""

import importlib
import logging
import threading
import time
from typing import Dict, List, Optional

from agent import __version__
from agent.queue import EventQueue
from agent.sender import Sender
from agent.heartbeat import Heartbeat
from agent.monitors.base import BaseMonitor

logger = logging.getLogger("soc-agent")

# name -> module path. Add entries here as more monitors are implemented.
MONITOR_REGISTRY: Dict[str, str] = {
    "process": "agent.monitors.process_monitor.ProcessMonitor",
}


class AgentCore:
    def __init__(self, config, config_source: str = "unknown"):
        self._config = config
        self._queue: Optional[EventQueue] = None
        self._sender: Optional[Sender] = None
        self._heartbeat: Optional[Heartbeat] = None
        self._monitors: List[BaseMonitor] = []
        self._stopping = threading.Event()
        self._internal_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        qcfg = self._config.queue
        self._queue = EventQueue(
            spool_path=qcfg["spool_path"],
            max_in_memory=qcfg["max_in_memory"],
            max_spooled=qcfg.get("max_spooled", 0),
        )

        self._sender = Sender(self._queue, self._config)
        self._heartbeat = Heartbeat(
            self._sender,
            interval_seconds=self._config.heartbeat["interval_seconds"],
        )

        self._monitors = self._build_monitors()
        logger.info(
            "Configuration loaded (backend=%s, monitors=%s)",
            self._config.backend_url,
            [m.name for m in self._monitors],
        )

    def _build_monitors(self) -> List[BaseMonitor]:
        monitors: List[BaseMonitor] = []
        enabled = {
            key: bool(value)
            for key, value in (self._config.monitors or {}).items()
        }

        for key, enabled_flag in enabled.items():
            if not enabled_flag:
                continue
            if key not in MONITOR_REGISTRY:
                logger.warning("%s Monitor is enabled but not implemented yet; skipping", key.capitalize())
                continue
            try:
                module_path, cls_name = MONITOR_REGISTRY[key].rsplit(".", 1)
                cls = getattr(importlib.import_module(module_path), cls_name)
                monitor = cls(emit=self.emit, interval=self._config.collection_interval_seconds)
                monitors.append(monitor)
            except Exception as exc:
                logger.error("Failed to load %s monitor: %s", key, exc)
        return monitors

    # ------------------------------------------------------------------
    # Event path
    # ------------------------------------------------------------------

    def emit(self, event: dict) -> bool:
        """Monitors call this to enqueue an event."""
        if self._queue is None:
            return False
        return self._queue.put(event)

    # ------------------------------------------------------------------
    # Startup / shutdown
    # ------------------------------------------------------------------

    def start(self) -> None:
        if self._stopping.is_set():
            raise RuntimeError("Agent has been stopped; cannot restart")
        logger.info("Agent Started (version=%s, backend=%s)", __version__, self._config.backend_url)

        self._sender.start()
        self._heartbeat.start()
        for monitor in self._monitors:
            monitor.start()
        logger.info("All modules started: %d monitor(s), sender, heartbeat", len(self._monitors))

    def stop(self, timeout: float = 10.0) -> None:
        if self._stopping.is_set():
            return
        self._stopping.set()

        # Stop monitors first so they stop producing.
        for monitor in self._monitors:
            try:
                monitor.stop()
            except Exception as exc:
                logger.error("Error stopping %s monitor: %s", monitor.name, exc)

        # Heartbeat
        if self._heartbeat:
            try:
                self._heartbeat.stop()
            except Exception as exc:
                logger.error("Error stopping heartbeat: %s", exc)

        # Sender: drain & flush remaining buffered events.
        if self._sender:
            try:
                self._sender_graceful_flush(timeout)
                self._sender.stop()
            except Exception as exc:
                logger.error("Error stopping sender: %s", exc)

        logger.info("Agent stopped")

    def _sender_graceful_flush(self, timeout: float) -> None:
        """Best-effort flush of remaining in-memory events before stop."""
        if self._sender is None or self._queue is None:
            return
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            items = self._queue.drain(self._config.sender["batch_size"])
            if not items:
                break
            self._sender._deliver(items)
        self._queue.close()

    # ------------------------------------------------------------------
    # Health / watchdog
    # ------------------------------------------------------------------

    def run_watchdog(self, check_interval: float = 5.0, stop_event: Optional[threading.Event] = None) -> None:
        """Supervise monitor threads; restart failed ones up to MAX_RESTARTS."""
        while not (stop_event or self._stopping).is_set():
            for monitor in list(self._monitors):
                if monitor.is_disabled:
                    continue
                if not monitor.is_running:
                    if monitor.restart_count >= monitor.MAX_RESTARTS:
                        logger.error("%s monitor disabled after repeated failures", monitor.name.capitalize())
                        continue
                    monitor._restart_count += 1
                    logger.warning(
                        "%s monitor exited (restart %d/%d, error=%s); restarting",
                        monitor.name.capitalize(),
                        monitor.restart_count,
                        monitor.MAX_RESTARTS,
                        monitor.last_error,
                    )
                    monitor.start()
            (stop_event or self._stopping).wait(check_interval)

    def health(self) -> Dict:
        return {
            "stopping": self._stopping.is_set(),
            "queue_pending": self._queue.pending_count() if self._queue else 0,
            "queue_buffered": self._queue.buffered_count() if self._queue else 0,
            "queue_dropped": self._queue.dropped_count if self._queue else 0,
            "sender": self._sender.stats if self._sender else None,
            "heartbeat_running": bool(self._heartbeat and self._heartbeat.is_running),
            "heartbeat_last_ok": bool(self._heartbeat and self._heartbeat.last_ok),
            "monitors": [
                {"name": m.name, "running": m.is_running, "restarts": m.restart_count}
                for m in self._monitors
            ],
        }