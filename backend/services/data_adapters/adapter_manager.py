import asyncio
import logging
from typing import List, Dict, Any
from .base_adapter import BaseDataAdapter

logger = logging.getLogger("soc_backend")

class AdapterManager:
    """Manages multiple data adapters and provides a unified event stream."""

    def __init__(self, adapters: List[BaseDataAdapter]):
        self.adapters = adapters
        self._tasks = []
        self._running = False
        self._event_queues = []  # Queues for each adapter
        self._merge_queue = None  # Queue for merged events

    async def start(self):
        """Start all adapters."""
        if self._running:
            return

        self._running = True
        self._event_queues = [asyncio.Queue() for _ in self.adapters]
        self._merge_queue = asyncio.Queue()

        # Start each adapter
        for i, adapter in enumerate(self.adapters):
            try:
                await adapter.start()
                # Start a task to feed events from adapter to its queue
                task = asyncio.create_task(
                    self._adapter_to_queue(adapter, self._event_queues[i])
                )
                self._tasks.append(task)
                logger.info(f"Started adapter: {adapter.__class__.__name__}")
            except Exception as e:
                logger.error(f"Failed to start adapter {adapter.__class__.__name__}: {e}")
                # Continue with other adapters

        # Start the merger task that combines all queues
        merge_task = asyncio.create_task(self._merge_queues())
        self._tasks.append(merge_task)
        logger.info("Started event merger")

    async def stop(self):
        """Stop all adapters."""
        if not self._running:
            return

        self._running = False

        # Cancel all tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete (with timeout)
        if self._tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._tasks, return_exceptions=True),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                logger.warning("Some adapter tasks did not stop gracefully")

        self._tasks.clear()

        # Stop adapters
        for adapter in self.adapters:
            try:
                await adapter.stop()
                logger.info(f"Stopped adapter: {adapter.__class__.__name__}")
            except Exception as e:
                logger.error(f"Error stopping adapter {adapter.__class__.__name__}: {e}")

    async def events(self):
        """
        Async iterator that yields events from all adapters.
        Yields events as they arrive from any adapter.
        """
        while self._running:
            try:
                # Wait for an event with a timeout to allow checking _running
                event = await asyncio.wait_for(self._merge_queue.get(), timeout=1.0)
                yield event
                self._merge_queue.task_done()
            except asyncio.TimeoutError:
                # Continue looping to check _running flag
                continue
            except Exception as e:
                if self._running:  # Only log if we're still supposed to be running
                    logger.error(f"Error getting event from merge queue: {e}")
                break

    async def _adapter_to_queue(self, adapter: BaseDataAdapter, queue: asyncio.Queue):
        """Pull events from an adapter and put them in a queue."""
        try:
            async for event in adapter.events():
                if not self._running:
                    break
                await queue.put(event)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if self._running:  # Only log if we're still supposed to be running
                logger.error(f"Error in adapter {adapter.__class__.__name__}: {e}")
        finally:
            # Signal end of stream from this adapter
            try:
                await queue.put(None)  # None signals end of stream
            except:
                pass  # Queue might be closed

    async def _merge_queues(self):
        """Merge events from all adapter queues into a single queue."""
        # Track which queues are still active
        active_queues = [q for q in self._event_queues if not q.empty()]

        while self._running and any(not q.empty() for q in self._event_queues):
            # Check each queue for available events
            for i, queue in enumerate(self._event_queues):
                try:
                    # Try to get an item without blocking
                    item = queue.get_nowait()

                    if item is None:  # End of stream signal
                        # Mark this queue as drained
                        continue

                    # Put the event in the merge queue
                    await self._merge_queue.put(item)
                    queue.task_done()

                except asyncio.QueueEmpty:
                    # No item available in this queue, check next
                    continue
                except Exception as e:
                    if self._running:
                        logger.error(f"Error in merge queue processing: {e}")

            # Brief pause to prevent busy waiting
            await asyncio.sleep(0.01)

        # Signal end of stream
        try:
            await self._merge_queue.put(None)
        except:
            pass