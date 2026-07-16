import logging

logger = logging.getLogger(__name__)

class RealtimeListener:
    """
    Listens to Supabase pg_realtime subscriptions.
    """
    def __init__(self):
        pass

    def on_event(self, payload: dict):
        logger.info(f"Received realtime event: {payload}")
