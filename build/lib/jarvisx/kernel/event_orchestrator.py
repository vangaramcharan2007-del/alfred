from __future__ import annotations
from typing import Dict, Any, List, Optional, Callable
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event

class EventOrchestrator:
    def __init__(self, bus: Optional[HermesBus] = None):
        self.bus = bus or HermesBus()
        self.event_log: List[Dict[str, Any]] = []

    async def publish(self, event_type: str, source: str, payload: Dict[str, Any]) -> None:
        event = Event(type=event_type, source=source, payload=payload)
        self.event_log.append({"type": event_type, "source": source, "payload": payload})
        await self.bus.publish(event)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        self.bus.subscribe(event_type, handler)

    def get_event_log(self) -> List[Dict[str, Any]]:
        return self.event_log
