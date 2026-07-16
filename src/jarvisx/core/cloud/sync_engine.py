import logging
from .supabase_client import SupabaseClient
from .conflict_resolver import ConflictResolver

logger = logging.getLogger(__name__)

class SyncEngine:
    """
    Synchronizes local var/*.db state with Supabase cloud.
    """
    def __init__(self):
        self.client = SupabaseClient()
        self.resolver = ConflictResolver()
        self.offline_queue = []

    def sync_objective(self, objective_id: str, state: dict):
        if self.client.is_connected:
            self.client.insert("objectives", {"id": objective_id, **state})
            logger.info(f"Synchronized objective {objective_id} to cloud.")
        else:
            self.offline_queue.append({"id": objective_id, **state})
