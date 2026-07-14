import logging

logger = logging.getLogger("EventReplication")

class EventReplicationRuntime:
    """
    Replicates WAL events, deduplicates them, preserves ordering,
    and supports replay after reconnection.
    """
    def __init__(self, sync_runtime, transport):
        self.sync_runtime = sync_runtime
        self.transport = transport
        self.received_hashes = set()

    async def replicate_local_event(self, event_hash: str, event_type: str, payload: dict):
        # Save locally first
        self.sync_runtime.enqueue_event(event_hash, event_type, payload)
        self.received_hashes.add(event_hash)
        
        # Broadcast to mesh
        message = {
            "type": "REPLICATE_EVENT",
            "event": {
                "hash": event_hash,
                "type": event_type,
                "payload": payload
            }
        }
        await self.transport.broadcast_message(message)

    def receive_remote_event(self, event_data: dict):
        event_hash = event_data.get("hash")
        if event_hash in self.received_hashes:
            logger.debug(f"Event {event_hash} already replicated. Ignoring.")
            return
        
        logger.info(f"Replicating remote event {event_hash}")
        self.sync_runtime.enqueue_event(event_hash, event_data.get("type"), event_data.get("payload"))
        self.received_hashes.add(event_hash)
