import asyncio
import logging
import random
from datetime import datetime
from typing import Dict, Any, AsyncIterator
from .base_adapter import BaseDataAdapter

logger = logging.getLogger("soc_backend")

class SyslogAdapter(BaseDataAdapter):
    """
    Simulates a Syslog adapter that listens for incoming RFC-5424 syslog messages.
    Converts syslog format to normalized security events.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.port = config.get("port", 514)
        self.host = config.get("host", "0.0.0.0")
        self._event_queue = asyncio.Queue()

    async def start(self):
        self._running = True
        # Simulate network listener in the background
        self._listener_task = asyncio.create_task(self._simulate_listener())
        logger.info(f"[SyslogAdapter] Listening on {self.host}:{self.port} (simulated)")

    async def stop(self):
        self._running = False
        if hasattr(self, "_listener_task"):
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        logger.info("[SyslogAdapter] Stopped listening.")

    async def events(self) -> AsyncIterator[Dict[str, Any]]:
        while self._running:
            try:
                # Wait for an event from the listener queue
                raw_event = await self._event_queue.get()
                if raw_event is None:
                    break
                normalized = self._normalize_event(raw_event)
                yield normalized
                self._event_queue.task_done()
            except Exception as e:
                logger.error(f"[SyslogAdapter] Error reading event: {e}")
                break

    async def _simulate_listener(self):
        """Simulates incoming syslog packets from network devices."""
        syslog_templates = [
            "<13>1 {ts} firewall.local filter - - - BLOCK src=192.168.10.15 dst=10.0.0.42 proto=tcp sport=5432 dport=22",
            "<86>1 {ts} mail.company.com postfix/smtpd - - - auth failure for user=support from=185.220.101.42",
            "<14>1 {ts} endpoint-win10 web_gateway - - - Malicious download blocked: Trojan.Win32 from 10.0.5.12"
        ]

        while self._running:
            # Simulate random delay between syslog messages
            await asyncio.sleep(random.uniform(10.0, 30.0))
            if not self._running:
                break

            try:
                template = random.choice(syslog_templates)
                ts = datetime.utcnow().isoformat() + "Z"
                raw_log = template.format(ts=ts)
                
                # Parse raw log into event fields
                event_data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "raw_log": raw_log
                }

                if "BLOCK" in raw_log:
                    event_data.update({
                        "event_type": "PORT_SCAN",
                        "src_ip": "192.168.10.15",
                        "dest_ip": "10.0.0.42",
                        "severity": "MEDIUM",
                        "user": "system"
                    })
                elif "auth failure" in raw_log:
                    event_data.update({
                        "event_type": "SSH_BRUTE_FORCE",
                        "src_ip": "185.220.101.42",
                        "dest_ip": "10.0.0.5",
                        "severity": "HIGH",
                        "user": "support"
                    })
                elif "Malicious" in raw_log:
                    event_data.update({
                        "event_type": "MALWARE_DETECTION",
                        "src_ip": "185.220.100.1",
                        "dest_ip": "10.0.5.12",
                        "severity": "CRITICAL",
                        "user": "unknown"
                    })

                await self._event_queue.put(event_data)
            except Exception as e:
                logger.error(f"[SyslogAdapter] Failed to parse simulated syslog packet: {e}")
