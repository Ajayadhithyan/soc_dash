"""
Process Monitor.

Cross-platform process lifecycle telemetry via psutil snapshot diffing:
    * PROCESS_STARTED — new process observed (pid, ppid, exe, cmdline, user)
    * PROCESS_EXITED  — process no longer present
"""

import logging
from typing import Dict, List, Optional

import psutil

from agent.monitors.base import PollingMonitor

logger = logging.getLogger("soc-agent")

_PROC_ATTRS = ["pid", "ppid", "name", "exe", "cmdline", "username", "create_time"]

_SEPARATOR = " \\ "


def _format_cmdline(cmdline: Optional[List[str]]) -> str:
    if not cmdline:
        return ""
    return _SEPARATOR.join(cmdline)


class ProcessMonitor(PollingMonitor):
    name = "process"
    POSITIVE_CACHE_SECONDS = 2.0

    def snapshot(self) -> Dict[int, dict]:
        """Return a map of pid -> process attributes."""
        snapshot: Dict[int, dict] = {}
        for proc in psutil.process_iter(_PROC_ATTRS):
            try:
                info = proc.info
                if info.get("pid") is None:
                    continue
                snapshot[info["pid"]] = {
                    "pid": info["pid"],
                    "ppid": info.get("ppid"),
                    "name": info.get("name") or "",
                    "exe": info.get("exe") or "",
                    "cmdline": info.get("cmdline") or [],
                    "username": info.get("username") or "unknown",
                    "create_time": info.get("create_time"),
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            except Exception as exc:
                logger.debug("Process snapshot entry skipped: %s", exc)
        return snapshot

    def diff(self, previous: Dict[int, dict], current: Dict[int, dict]) -> List[dict]:
        events: List[dict] = []

        for pid, info in current.items():
            if pid not in previous:
                events.append(
                    self._snapshot_event(
                        event_type="PROCESS_STARTED",
                        metadata={
                            "pid": pid,
                            "ppid": info.get("ppid"),
                            "name": info.get("name"),
                            "exe": info.get("exe"),
                            "cmdline": info.get("cmdline"),
                            "create_time": info.get("create_time"),
                            "username": info.get("username"),
                        },
                        severity="LOW",
                        user=info.get("username") or "unknown",
                        raw_log=f"Process started: {info.get('name') or 'unknown'} (pid={pid})",
                    )
                )

        for pid, info in previous.items():
            if pid not in current:
                events.append(
                    self._snapshot_event(
                        event_type="PROCESS_EXITED",
                        metadata={
                            "pid": pid,
                            "ppid": info.get("ppid"),
                            "name": info.get("name"),
                            "exe": info.get("exe"),
                            "username": info.get("username"),
                        },
                        severity="LOW",
                        user=info.get("username") or "unknown",
                        raw_log=f"Process exited: {info.get('name') or 'unknown'} (pid={pid})",
                    )
                )

        return events