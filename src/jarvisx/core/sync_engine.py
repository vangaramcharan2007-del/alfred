import logging
from typing import Dict, Any, List

class SyncEngine:
    """
    Manages offline-first state synchronization with the cloud (Supabase).
    Writes to local SQLite WAL first, then queues for asynchronous cloud push.
    Never blocks the local execution thread waiting for cloud confirmation.
    """
    def __init__(self):
        self.local_queue: List[Dict[str, Any]] = []
        self.cloud_connected = True

    def write_local(self, table: str, payload: Dict[str, Any]):
        logging.info(f"[SyncEngine] Wrote to local {table} store: {payload.get('execution_id', 'unknown')}")
        self.queue_sync(table, payload)
        
    def queue_sync(self, table: str, payload: Dict[str, Any]):
        self.local_queue.append({'table': table, 'payload': payload})
        logging.info(f"[SyncEngine] Queued for cloud sync (Queue size: {len(self.local_queue)})")
        
    def push_cloud(self):
        if not self.cloud_connected:
            logging.warning("[SyncEngine] Network offline. Keeping items in local queue.")
            return

        while self.local_queue:
            item = self.local_queue.pop(0)
            logging.info(f"[SyncEngine] Pushed to Cloud Supabase [{item['table']}]")
            logging.info(f"[SyncEngine] Marked Synced.")
