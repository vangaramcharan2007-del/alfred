"""Compatibility event bus shared by the runtime composition root."""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Optional

from jarvisx.core.events import Event
from jarvisx.core.hermes import HermesBus
from jarvisx.events.event_bus import EventBus
from jarvisx.events.models import EventType, SystemEvent


class RuntimeEventBus:
    """Expose Hermes and legacy daemon event APIs through one shared dependency.

    Hermes callers retain their async ``Event`` interface. Phase 104 daemon callers
    retain their synchronous ``SystemEvent`` interface while their events are also
    mirrored to Hermes when the runtime loop is available.
    """

    def __init__(self) -> None:
        self.hermes = HermesBus()
        self.daemon_events = EventBus()
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None

    def bind_event_loop(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        """Bind the application loop used to mirror legacy daemon events."""
        self._event_loop = loop or asyncio.get_running_loop()

    def subscribe(
        self,
        event_type: str | EventType,
        handler: Callable[..., Any],
        *,
        subscriber_id: Optional[str] = None,
    ) -> None:
        if isinstance(event_type, EventType):
            self.daemon_events.subscribe(event_type, handler)
            return
        self.hermes.subscribe(event_type, handler, subscriber_id=subscriber_id)

    def publish(self, event: Event | SystemEvent) -> Awaitable[list[Any]] | str:
        if isinstance(event, Event):
            return self.hermes.publish(event)
        if isinstance(event, SystemEvent):
            event_id = self.daemon_events.publish(event)
            self._mirror_daemon_event(event)
            return event_id
        raise TypeError(f"Unsupported runtime event type: {type(event)!r}")

    def publish_sync(self, event: SystemEvent) -> list[dict[str, Any]]:
        return self.daemon_events.publish_sync(event)

    def start(self) -> None:
        self.daemon_events.start()

    def stop(self) -> None:
        self.daemon_events.stop()

    def get_recent_events(self, limit: int = 20) -> list[SystemEvent]:
        return self.daemon_events.get_recent_events(limit)

    @property
    def subscription_count(self) -> int:
        return self.hermes.subscription_count

    def _mirror_daemon_event(self, event: SystemEvent) -> None:
        if not self._event_loop or not self._event_loop.is_running():
            return

        hermes_event = Event(
            type=f"daemon.{event.event_type.value.lower()}",
            source=event.origin,
            payload=dict(event.payload),
        )
        self._event_loop.call_soon_threadsafe(
            asyncio.create_task,
            self.hermes.publish(hermes_event),
        )
