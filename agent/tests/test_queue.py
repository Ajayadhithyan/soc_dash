"""Tests for the event queue + durable spool."""

import sqlite3

import pytest

from agent.event import build_event
from agent.queue import EventQueue


def _event(**kwargs):
    return build_event(event_type="PROCESS_STARTED", category="PROCESS", **kwargs)


def test_put_drain_ack(tmp_path):
    q = EventQueue(spool_path=str(tmp_path / "spool.db"), max_in_memory=100)
    q.put(_event(metadata={"pid": 1}))
    q.put(_event(metadata={"pid": 2}))

    assert q.pending_count() == 2
    items = q.drain(10)
    assert len(items) == 2

    q.ack([item[0] for item in items])
    assert q.pending_count() == 0
    assert q.buffered_count() == 0
    q.close()


def test_spool_survives_restart(tmp_path):
    path = str(tmp_path / "spool.db")
    q1 = EventQueue(spool_path=path, max_in_memory=10)
    q1.put(_event(metadata={"pid": 1}))
    q1.put(_event(metadata={"pid": 2}))
    q1.close()

    # Simulate agent restart with a fresh queue over the same sqlite file.
    q2 = EventQueue(spool_path=path, max_in_memory=10)
    assert q2.pending_count() == 2
    items = q2.drain(10)
    assert len(items) == 2
    q2.ack([item[0] for item in items])
    assert q2.pending_count() == 0
    q2.close()


def test_requeue_keeps_pending_on_disk(tmp_path):
    q = EventQueue(spool_path=str(tmp_path / "spool.db"), max_in_memory=10)
    q.put(_event(metadata={"pid": 1}))
    items = q.drain(1)
    ids = [i[0] for i in items]
    q.requeue(items)
    # Not acknowledged -> still on spool (offline buffering).
    assert q.pending_count() == 1
    q.ack(ids)
    assert q.pending_count() == 0
    q.close()


def test_in_memory_cap_drops_but_spools(tmp_path):
    q = EventQueue(spool_path=str(tmp_path / "spool.db"), max_in_memory=2)
    for i in range(5):
        q.put(_event(metadata={"pid": i}))
    # All 5 events are durable on disk even if the in-memory buffer was capped.
    assert q.pending_count() == 5
    q.close()


def test_pending_count_empty(tmp_path):
    q = EventQueue(spool_path=str(tmp_path / "spool.db"), max_in_memory=10)
    assert q.pending_count() == 0
    q.close()