from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncIterator
import asyncio
import logging

logger = logging.getLogger("soc_backend")

class BaseDataAdapter(ABC):
    """Abstract base class for all data adapters."""

    def __init__(self, config: dict):
        self.config = config
        self._running = False

    @abstractmethod
    async def start(self):
        """Start the adapter and begin listening for events."""
        pass

    @abstractmethod
    async def stop(self):
        """Stop the adapter and cleanup resources."""
        pass

    @abstractmethod
    async def events(self) -> AsyncIterator[Dict[str, Any]]:
        """
        Async iterator that yields events in the format expected by the processing pipeline.

        Expected event format:
        {
            "timestamp": str,  # ISO format or similar
            "src_ip": str,
            "dest_ip": str,
            "event_type": str,  # One of the known event types
            "severity": str,    # LOW, MEDIUM, HIGH, CRITICAL
            "user": str,
            "raw_log": str,
            # Optional fields that will be added during processing:
            # "asset_type": str,
            # "geo": {"country": str, "lat": float, "lng": float}
        }
        """
        pass

    def _normalize_event(self, raw_event: dict) -> dict:
        """
        Normalize incoming event to the expected format.
        Override in subclasses if needed.
        """
        # Ensure required fields exist with sensible defaults
        event = {
            "timestamp": raw_event.get("timestamp", self._get_current_timestamp()),
            "src_ip": raw_event.get("src_ip", "0.0.0.0"),
            "dest_ip": raw_event.get("dest_ip", "0.0.0.0"),
            "event_type": raw_event.get("event_type", "FAILED_LOGIN"),
            "severity": raw_event.get("severity", "LOW"),
            "user": raw_event.get("user", "unknown"),
            "raw_log": raw_event.get("raw_log", str(raw_event)),
        }

        # Add optional fields if present
        if "asset_type" in raw_event:
            event["asset_type"] = raw_event["asset_type"]
        if "geo" in raw_event:
            event["geo"] = raw_event["geo"]

        return event

    def _get_current_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")