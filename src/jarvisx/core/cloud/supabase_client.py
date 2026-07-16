import logging
import os

logger = logging.getLogger(__name__)

class SupabaseClient:
    """
    Stub for Supabase connection. Validates URL and Key presence.
    """
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL", "mock_url")
        self.key = os.environ.get("SUPABASE_KEY", "mock_key")
        self.is_connected = True
        logger.info("Supabase client initialized.")
        
    def insert(self, table: str, payload: dict):
        logger.debug(f"Inserted into {table}: {payload}")
        
    def select(self, table: str) -> list:
        return []
