"""
BaseMonitor framework.

Every telemetry source implements this contract:
    * `name`      — unique monitor identifier (also the config key)
    * `interval`  — collection cadence in seconds
    * `_collect()` — returns a list of normalized event dicts (see event.py)

Monitors never send data directly — they hand events to the queue callback.
"""

import logging
import threading
import time
from abc import ABC, abstractmethod
from typing import Callable, List, Optional

from agent.event import build_event

logger = logging.getLogger("soc-agent")


class BaseMonitor(ABC):
    name: str = "base"
    interval: float = 5.0
    MAX_RESTARTS = 3

    def __init__(self, emit: Optional[Callable[[dict], bool]] = None):
        self._emit = emit or (lambda event: True)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._restart_count = 0
        self._last_error: Optional[str] = None

    # ------------------------------------------------------------------
    # Public API (used by the core)
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    @property
    def restart_count(self) -> int:
        return self._restart_count

    @property
    def last_error(self) -> Optional[str]:
        return self._last_error

    @property
    def is_disabled(self) -> bool:
        return self._restart_count >= self.MAX_RESTARTS

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name=f"monitor-{self.name}", daemon=True)
        self._thread.start()
        logger.info("%s Monitor started (interval=%.1fs)", self.name.capitalize(), self.interval)

    def stop(self, timeout: float = 5.0) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)
            logger.info("%s Monitor stopped", self.name.capitalize())

    def emit(self, event: dict) -> bool:
        """Hand an event to the queue (and hook for tests)."""
        return bool(self._emit(event))

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _run(self) -> None:
        # First tick baseline-only for monitors that diff snapshots.
        self.on_first_tick()
        while not self._stop_event.wait(self.interval):
            try:
                for event in self._collect() or []:
                    self.emit(event)
            except Exception as exc:
                self._last_error = str(exc)
                logger.error("%s Monitor collection failed: %s", self.name.capitalize(), exc, exc_info=True)
        self.on_last_tick()

    def on_first_tick(self) -> None:
        """Hook for monitors that need an initial baseline (default: no-op)."""

    def on_last_tick(self) -> None:
        """Hook for monitors that emit final events on shutdown (default: no-op)."""

    @abstractmethod
    def _collect(self) -> List[dict]:
        """Collect and return normalized event dicts."""


class PollingMonitor(BaseMonitor):
    """Monitor that compares snapshots between ticks."""

    def __init__(self, emit=None, interval: float = 5.0):
        super().__init__(emit)
        self.interval = interval

    def _collect(self) -> List[dict]:
        previous = getattr(self, "_previous_snapshot", None)
        current = self.snapshot()
        events: List[dict] = []
        if previous is not None:
            events.extend(self.diff(previous, current))
        self._previous_snapshot = current
        return events

    @abstractmethod
    def snapshot(self) -> dict:
        """Return a serializable representation of the current state."""

    @abstractmethod
    def diff(self, previous: dict, current: dict) -> List[dict]:
        """Compare two snapshots and produce events for the changes."""

    def _snapshot_event(
        self,
        event_type: str,
        metadata: dict,
        severity: str = "LOW",
        user: str = "unknown",
        raw_log: str = "",
        **kwargs,
    ) -> dict:
        return build_event(
            event_type=event_type,
            category=self.name.upper(),
            metadata=metadata,
            severity=severity,
            user=user,
            raw_log=raw_log,
            **kwargs,
        )