import asyncio
from typing import Dict, Any, Callable, List
from jarvisx.core.logging import StructuredLogger

class DistributedEventBus:
    """
    Handles real-time publish/subscribe message passing across the mesh.
    """
    def __init__(self, logger: StructuredLogger | None = None):
        self.logger = logger or StructuredLogger()
        self._subscribers: Dict[str, List[Callable]] = {}
        
    def subscribe(self, event_type: str, handler: Callable) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        self.logger.write("info", "event_bus.subscribed", event=event_type)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
            except ValueError:
                pass

    async def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Publishes an event to all subscribers locally. 
        In a full mesh, this would also broadcast via the Gateway.
        """
        self.logger.write("debug", "event_bus.publish", event=event_type)
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(payload))
                else:
                    handler(payload)
