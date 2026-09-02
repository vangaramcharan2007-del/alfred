from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional

from jarvisx.core.events import Event
from jarvisx.core.logging import StructuredLogger

Handler = Callable[[Event], Any | Awaitable[Any]]


@dataclass(frozen=True)
class Subscription:
    event_type: str
    handler: Handler
    subscriber_id: Optional[str] = None


class HermesBus:
    """In-process event bus used by agents and tools during local execution."""

    def __init__(self, *, logger: Optional[StructuredLogger] = None) -> None:
        self._subscriptions: list[Subscription] = []
        self._logger = logger or StructuredLogger()

    def subscribe(
        self,
        event_type: str,
        handler: Handler,
        *,
        subscriber_id: Optional[str] = None,
    ) -> None:
        self._subscriptions.append(
            Subscription(event_type=event_type, handler=handler, subscriber_id=subscriber_id)
        )
        self._logger.write(
            "info",
            "hermes.subscription.created",
            event_type=event_type,
            subscriber_id=subscriber_id,
        )

    async def publish(self, event: Event) -> list[Any]:
        self._logger.write(
            "info",
            "hermes.event.published",
            trace_id=event.trace_id,
            event_type=event.type,
            source=event.source,
            target=event.target,
        )
        responses: list[Any] = []
        for subscription in self._subscriptions:
            if subscription.event_type != event.type:
                continue
            if event.target and subscription.subscriber_id != event.target:
                continue
            result = subscription.handler(event)
            if inspect.isawaitable(result):
                result = await result
            responses.append(result)
        return responses

    @property
    def subscription_count(self) -> int:
        return len(self._subscriptions)
