"""
Sender.

Has exactly one responsibility: read events from the queue, batch them
efficiently, and send them securely to the backend. Retries failed batches
with exponential backoff. Never drops events — unsent batches stay on the
spool until acknowledged.
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional

import requests

from agent.event import sanitize_event

logger = logging.getLogger("soc-agent")

SUCCESS_STATUS_CODES = (200, 201, 202, 204)


class SenderError(Exception):
    """Raised when a batch cannot be sent."""


class _Cancelled(Exception):
    """Internal: stop requested while retrying."""


class Sender:
    """Background thread that drains the queue and posts batches over HTTPS."""

    def __init__(
        self,
        queue,
        config,
        agent_auth: Optional[str] = None,
        backend_url: Optional[str] = None,
    ):
        self._queue = queue
        self._batch_size = int(config["sender"]["batch_size"])
        self._flush_interval = float(config["sender"]["flush_interval_seconds"])
        self._max_retries = int(config["sender"]["max_retries"])
        self._backoff_base = float(config["sender"]["backoff_base_seconds"])
        self._backoff_max = float(config["sender"]["backoff_max_seconds"])
        self._timeout = float(config["sender"]["timeout_seconds"])
        self._verify_ssl = bool(config["sender"]["verify_ssl"])

        self._token = agent_auth or config.agent_token
        self._agent_id = config.agent_id
        self._hostname = config.hostname
        self._backend_url = (backend_url or config.backend_url).rstrip("/")

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_send_ok = False
        self._last_error: Optional[str] = None
        self._sent_count = 0

    # ------------------------------------------------------------------
    # Introspection / thread control
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "running": self.is_running,
            "last_send_ok": self._last_send_ok,
            "last_error": self._last_error,
            "sent_events": self._sent_count,
        }

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="sender", daemon=True)
        self._thread.start()
        logger.info("Sender started (url=%s, batch_size=%d)", self._ingest_url, self._batch_size)

    def stop(self, timeout: float = 5.0) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)
            logger.info("Sender stopped")

    @property
    def _ingest_url(self) -> str:
        return f"{self._backend_url}/api/agent/ingest"

    @property
    def _heartbeat_url(self) -> str:
        return f"{self._backend_url}/api/agent/heartbeat"

    # ------------------------------------------------------------------
    # Send loop
    # ------------------------------------------------------------------

    def _run(self) -> None:
        while not self._stop_event.is_set():
            items = self._queue.drain(self._batch_size)
            if not items:
                self._stop_event.wait(self._flush_interval)
                continue

            try:
                self._deliver(items)
            except _Cancelled:
                break
            except Exception as exc:  # defensive: never let the loop die
                logger.error("Unexpected sender error: %s", exc, exc_info=True)
                self._queue.requeue(items)

        self._queue.close()

    def _deliver(self, items: List) -> None:
        """Send a batch with exponential backoff retries."""
        backoff = self._backoff_base
        attempt = 0

        while True:
            if self._stop_event.is_set():
                self._queue.requeue(items)
                raise _Cancelled

            try:
                payload = {
                    "events": [sanitize_event(evt) for _, evt in items],
                    "agent_id": self._agent_id,
                    "hostname": self._hostname,
                }
                self._send_once(payload)
            except SenderError as exc:
                self._last_error = str(exc)
                self._last_send_ok = False
                attempt += 1
                if attempt > self._max_retries:
                    logger.error(
                        "Failed to Send Event (gave up after %d attempts): %s",
                        attempt,
                        exc,
                    )
                    self._queue.requeue(items)
                    return
                logger.warning(
                    "Failed to Send Event (attempt %d/%d): %s",
                    attempt,
                    self._max_retries,
                    exc,
                )
                self._sleep_backoff(backoff)
                backoff = min(backoff * 2, self._backoff_max)
                continue

            # Success
            self._queue.ack([item[0] for item in items])
            self._sent_count += len(items)
            self._last_error = None
            self._last_send_ok = True
            logger.info("Sent %d events to %s", len(items), self._ingest_url)
            if attempt > 0:
                logger.info("Retry successful after %d failure(s)", attempt)
            return

    def _send_once(self, payload: Dict[str, Any]) -> None:
        """POST one batch; raise SenderError on any failure."""
        try:
            resp = requests.post(
                self._ingest_url,
                json=payload,
                headers={"X-Agent-Token": self._token},
                timeout=self._timeout,
                verify=self._verify_ssl,
            )
        except requests.RequestException as exc:
            raise SenderError(f"network error: {exc}") from exc

        if resp.status_code not in SUCCESS_STATUS_CODES:
            raise SenderError(f"HTTP {resp.status_code}: {resp.text[:200]}")

    def _sleep_backoff(self, seconds: float) -> None:
        """Sleep honoring stop requests."""
        self._stop_event.wait(seconds)

    # ------------------------------------------------------------------
    # Heartbeat helper (used by the Heartbeat thread)
    # ------------------------------------------------------------------

    def send_heartbeat(self, payload: Dict[str, Any]) -> bool:
        """One-shot heartbeat POST; returns True on success."""
        try:
            resp = requests.post(
                self._heartbeat_url,
                json=payload,
                headers={"X-Agent-Token": self._token},
                timeout=self._timeout,
                verify=self._verify_ssl,
            )
            ok = resp.status_code in SUCCESS_STATUS_CODES
            if not ok:
                logger.warning("Heartbeat rejected: HTTP %s", resp.status_code)
            return ok
        except Exception as exc:
            logger.warning("Heartbeat send failed: %s", exc)
            return False