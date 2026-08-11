"""
Event Queue with persistent spool.

Monitors never send data directly. Every event goes:
    Monitor -> EventQueue (in-memory + SQLite spool) -> Sender -> Backend

The SQLite spool guarantees events are not lost when the network is down or
the agent restarts: events are durable on disk before they are acknowledged.
"""

import json
import logging
import queue
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("soc-agent")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS spool (
    id          TEXT PRIMARY KEY,
    created_at  TEXT NOT NULL,
    payload     TEXT NOT NULL
);
"""


class EventQueue:
    """Thread-safe FIFO queue with a durable SQLite spool."""

    def __init__(
        self,
        spool_path: str,
        max_in_memory: int = 5000,
        max_spooled: int = 20000,
        spool_max_age_seconds: Optional[int] = None,
    ):
        self._max_in_memory = max_in_memory
        self._max_spooled = max_spooled
        self._spool_max_age_seconds = spool_max_age_seconds
        self._buffer: "queue.Queue[Tuple[str, Dict[str, Any]]]" = queue.Queue(
            maxsize=max_in_memory
        )
        self._lock = threading.Lock()
        self._dropped_count = 0

        Path(spool_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(spool_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(_SCHEMA)
        self._conn.commit()
        self._hydrate_from_spool()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def _hydrate_from_spool(self) -> None:
        """Reload previously-spooled events into the in-memory buffer."""
        with self._lock:
            try:
                rows = self._conn.execute(
                    "SELECT id, payload FROM spool ORDER BY created_at"
                ).fetchall()
                if self._spool_max_age_seconds is not None:
                    now = datetime.now(timezone.utc)
                    stale_ids = [
                        row[0]
                        for row in rows
                        if self._is_stale(row[1], now)
                    ]
                    for sid in stale_ids:
                        self._conn.execute("DELETE FROM spool WHERE id = ?", (sid,))
                    self._conn.commit()
                    rows = self._conn.execute(
                        "SELECT id, payload FROM spool ORDER BY created_at"
                    ).fetchall()
            except sqlite3.Error as e:
                logger.error("Failed to hydrate spool: %s", e)
                return

        for row_id, payload in rows:
            try:
                self._buffer.put_nowait((row_id, json.loads(payload)))
            except queue.Full:
                logger.warning("In-memory queue full while hydrating spool; events remain on disk")
                break

    def _is_stale(self, payload_json: str, now: datetime) -> bool:
        try:
            event = json.loads(payload_json)
            ts = datetime.fromisoformat(event.get("created_at", ""))
            return (now - ts).total_seconds() > self._spool_max_age_seconds
        except (ValueError, TypeError):
            return False

    # ------------------------------------------------------------------
    # Producer side (monitors)
    # ------------------------------------------------------------------

    def put(self, event: Dict[str, Any]) -> bool:
        """
        Enqueue an event. Returns True if accepted, False if dropped due to
        capacity limits. Events are spooled to disk before buffering.
        """
        event["id"] = str(uuid.uuid4())
        event["created_at"] = datetime.now(timezone.utc).isoformat()

        with self._lock:
            try:
                self._conn.execute(
                    "INSERT INTO spool (id, created_at, payload) VALUES (?, ?, ?)",
                    (event["id"], event["created_at"], json.dumps(event)),
                )
                self._conn.commit()
                if self._max_spooled:
                    row = self._conn.execute(
                        "SELECT COUNT(*) FROM spool"
                    ).fetchone()
                    count = int(row[0]) if row else 0
                    if count > self._max_spooled:
                        overflow = count - self._max_spooled
                        self._conn.execute(
                            "DELETE FROM spool WHERE id IN ("
                            "SELECT id FROM spool ORDER BY created_at LIMIT ?)",
                            (overflow,),
                        )
                        self._conn.commit()
                        logger.warning("Spool over capacity; dropped %d oldest events", overflow)
            except sqlite3.Error as e:
                logger.error("Failed to spool event to disk: %s", e)
                return False

            try:
                self._buffer.put_nowait((event["id"], event))
                return True
            except queue.Full:
                self._dropped_count += 1
                logger.warning(
                    "In-memory queue full (dropping in-memory copy; %d dropped total). "
                    "Event remains spooled on disk.",
                    self._dropped_count,
                )
                return True

    # ------------------------------------------------------------------
    # Consumer side (sender)
    # ------------------------------------------------------------------

    def drain(self, max_items: int, timeout: float = 0.1) -> List[Tuple[str, Dict[str, Any]]]:
        """Pop up to `max_items` buffered events, oldest first."""
        items: List[Tuple[str, Dict[str, Any]]] = []
        try:
            for _ in range(max_items):
                items.append(self._buffer.get_nowait())
        except queue.Empty:
            pass
        return items

    def ack(self, event_ids: List[str]) -> None:
        """Remove acknowledged events from the spool (successful send)."""
        if not event_ids:
            return
        with self._lock:
            try:
                self._conn.executemany(
                    "DELETE FROM spool WHERE id = ?", [(eid,) for eid in event_ids]
                )
                self._conn.commit()
            except sqlite3.Error as e:
                logger.error("Failed to ack spooled events: %s", e)

    def requeue(self, items: List[Tuple[str, Dict[str, Any]]]) -> None:
        """Return unsent events to the back of the buffer (failed send)."""
        for item in items:
            try:
                self._buffer.put_nowait(item)
            except queue.Full:
                logger.warning("Queue full during requeue; event remains spooled on disk only")

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def pending_count(self) -> int:
        with self._lock:
            try:
                row = self._conn.execute("SELECT COUNT(*) FROM spool").fetchone()
                return int(row[0]) if row else 0
            except sqlite3.Error:
                return 0

    def buffered_count(self) -> int:
        return self._buffer.qsize()

    @property
    def dropped_count(self) -> int:
        return self._dropped_count