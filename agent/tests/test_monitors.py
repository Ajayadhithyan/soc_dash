"""Tests for the monitor framework and process monitor."""

import pytest

from agent.monitors.base import PollingMonitor
from agent.monitors.process_monitor import ProcessMonitor


class FakeMonitor(PollingMonitor):
    name = "fake"

    def __init__(self, snapshots, emit=None):
        super().__init__(emit, interval=0.01)
        self._snapshots = list(snapshots)

    def snapshot(self):
        return self._snapshots.pop(0)

    def diff(self, previous, current):
        events = []
        for pid in current:
            if pid not in previous:
                events.append(
                    self._snapshot_event(
                        event_type="PROCESS_STARTED",
                        metadata={"pid": pid},
                    )
                )
        for pid in previous:
            if pid not in current:
                events.append(
                    self._snapshot_event(
                        event_type="PROCESS_EXITED",
                        metadata={"pid": pid},
                    )
                )
        return events


def test_polling_monitor_baseline_first_tick_no_events():
    events = []
    monitor = FakeMonitor([{1: {"pid": 1}}], emit=events.append)
    collected = monitor._collect()
    assert collected == []  # first tick only establishes the baseline


def test_polling_monitor_emits_on_diff():
    events = []
    monitor = FakeMonitor(
        [
            {1: {"pid": 1}, 2: {"pid": 2}},   # baseline
            {1: {"pid": 1}, 3: {"pid": 3}},   # 2 exited, 3 started
        ],
        emit=events.append,
    )
    monitor._collect()  # baseline
    collected = monitor._collect()
    types = sorted(e["event_type"] for e in collected)
    assert types == ["PROCESS_EXITED", "PROCESS_STARTED"]


def test_process_monitor_diff():
    monitor = ProcessMonitor()
    previous = {
        100: {"pid": 100, "ppid": 1, "name": "old.exe", "exe": "C:/old.exe",
              "cmdline": ["old.exe", "-x"], "username": "alice", "create_time": 1},
    }
    current = {
        100: {"pid": 100, "ppid": 1, "name": "old.exe", "exe": "C:/old.exe",
              "cmdline": ["old.exe", "-x"], "username": "alice", "create_time": 1},
        101: {"pid": 101, "ppid": 100, "name": "new.exe", "exe": "C:/new.exe",
              "cmdline": ["new.exe"], "username": "bob", "create_time": 2},
    }
    events = monitor.diff(previous, current)
    assert len(events) == 1
    started = events[0]
    assert started["event_type"] == "PROCESS_STARTED"
    assert started["category"] == "PROCESS"
    assert started["metadata"]["pid"] == 101
    assert started["metadata"]["ppid"] == 100
    assert started["user"] == "bob"

    events = monitor.diff(current, previous)
    assert len(events) == 1
    exited = events[0]
    assert exited["event_type"] == "PROCESS_EXITED"
    assert exited["metadata"]["pid"] == 101