import logging

logger = logging.getLogger(__name__)

class EventListener:
    """
    Listens to system-wide events (task completion, timeouts) to trigger detection pipelines.
    """
    def __init__(self):
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def emit(self, event_type: str, payload: dict):
        logger.debug(f"Event emitted: {event_type}")
        for callback in self.subscribers:
            try:
                callback(event_type, payload)
            except Exception as e:
                logger.error(f"Error in event subscriber: {e}")
