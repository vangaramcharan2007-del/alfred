from __future__ import annotations

import os
from jarvisx.core.providers.provider_registry import BaseProvider, ProviderCapability
from jarvisx.clients.supabase_client import SupabaseClient


class SupabaseProvider(BaseProvider):
    def __init__(self):
        self.client = SupabaseClient()
        
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("MEMORY", "Supabase", 10, False)
        
    async def check_health(self) -> bool:
        return self.client.is_configured
        
    async def benchmark(self) -> float:
        return 100.0 if self.client.is_configured else float('inf')


class SQLiteProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("MEMORY", "SQLite", 20, True)
        
    async def check_health(self) -> bool:
        return os.path.exists("var/jarvisx_op.db") or True
        
    async def benchmark(self) -> float:
        return 10.0


class LocalFilesProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("MEMORY", "Local Files", 30, True)
        
    async def check_health(self) -> bool:
        return True
        
    async def benchmark(self) -> float:
        return 5.0
