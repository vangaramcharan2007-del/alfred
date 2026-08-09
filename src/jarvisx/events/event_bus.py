"""Asynchronous Thread-Safe Event Bus for Phase 104."""

from __future__ import annotations
import heapq
import logging
import queue
import threading
import time
from typing import Any, Callable, Dict, List, Optional
from jarvisx.events.models import EventType, SystemEvent

logger = logging.getLogger("jarvisx.event_bus")


class EventBus:
    """Central nervous system dispatching system events to registered subscribers."""

    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[SystemEvent], Optional[Dict[str, Any]]]]] = {}
        self._event_queue: queue.PriorityQueue = queue.PriorityQueue()
        self._history: List[SystemEvent] = []
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def subscribe(self, event_type: EventType, handler: Callable[[SystemEvent], Optional[Dict[str, Any]]]):
        """Register a handler for an event type."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)

    def publish(self, event: SystemEvent) -> str:
        """Enqueue an event for processing. Priority is inverted for PriorityQueue (10 -> 0)."""
        priority_key = 10 - event.priority
        self._event_queue.put((priority_key, event.timestamp, event))
        return event.event_id

    def publish_sync(self, event: SystemEvent) -> List[Dict[str, Any]]:
        """Publish and execute handlers synchronously."""
        results: List[Dict[str, Any]] = []
        handlers = []
        with self._lock:
            handlers.extend(self._subscribers.get(event.event_type, []))
            handlers.extend(self._subscribers.get(EventType.CUSTOM, []))

        for h in handlers:
            try:
                res = h(event)
                if res:
                    results.append(res)
            except Exception as e:
                logger.error(f"Error in event handler for {event.event_type}: {e}")

        event.handled = True
        with self._lock:
            self._history.append(event)
        return results

    def start(self):
        """Start the background event consumer loop."""
        if self._running:
            return
        self._running = True
        self._worker_thread = threading.Thread(target=self._process_loop, name="EventBusWorker", daemon=True)
        self._worker_thread.start()

    def stop(self):
        """Stop the background worker."""
        self._running = False
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)

    def _process_loop(self):
        while self._running:
            try:
                _, _, event = self._event_queue.get(timeout=0.2)
                handlers = []
                with self._lock:
                    handlers.extend(self._subscribers.get(event.event_type, []))

                for h in handlers:
                    try:
                        res = h(event)
                        if res and not event.handler_result:
                            event.handler_result = res
                    except Exception as e:
                        logger.error(f"Error in async event handler {event.event_type}: {e}")

                event.handled = True
                with self._lock:
                    self._history.append(event)
                    if len(self._history) > 200:
                        self._history = self._history[-200:]
                self._event_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                if not self._running:
                    break

    def get_recent_events(self, limit: int = 20) -> List[SystemEvent]:
        """Return recently processed events."""
        with self._lock:
            return list(reversed(self._history[-limit:]))
