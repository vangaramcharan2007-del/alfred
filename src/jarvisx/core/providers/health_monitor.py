from __future__ import annotations

import asyncio
import time
import psutil
from typing import Dict, Any

from jarvisx.core.providers.fallback_manager import FallbackManager
from jarvisx.core.health import HealthMonitor as BaseHealthMonitor, HealthStatus


class ContinuousHealthMonitor:
    """
    Continuously monitors system stats (CPU, RAM) and the health of active providers.
    If a provider degrades or recovers, it triggers the FallbackManager.
    """
    def __init__(self, base_monitor: BaseHealthMonitor, fallback: FallbackManager):
        self.base_monitor = base_monitor
        self.fallback = fallback
        self._running = False
        self.stats: Dict[str, Any] = {}
        
    def start(self) -> asyncio.Task:
        self._running = True
        return asyncio.create_task(self._monitor_loop())
        
    def stop(self) -> None:
        self._running = False
        
    async def _monitor_loop(self) -> None:
        while self._running:
            try:
                await self._collect_system_stats()
                await self._check_providers()
            except Exception as e:
                # Log or handle exceptions silently to not crash the monitor
                pass
            await asyncio.sleep(5)  # Check every 5 seconds
            
    async def _collect_system_stats(self) -> None:
        self.stats["cpu_percent"] = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        self.stats["ram_percent"] = memory.percent
        disk = psutil.disk_usage('/')
        self.stats["disk_percent"] = disk.percent
        
        # Also collect base monitor checks
        base_results = self.base_monitor.run_all()
        for name, status in base_results.items():
            self.stats[f"check_{name}"] = status.healthy

    async def _check_providers(self) -> None:
        """
        Check active providers. If one fails, handle it.
        Also check failed providers to see if they recovered.
        """
        # Check active ones
        for category, provider in list(self.fallback.active_providers.items()):
            is_healthy = await provider.check_health()
            if not is_healthy:
                await self.fallback.handle_failure(category, provider.capability.name)
                
        # Check failed ones for recovery
        # Iterate over a copy since dictionary might change
        for category in self.fallback.registry.get_all_categories():
            all_providers = self.fallback.registry.get_providers(category)
            active = self.fallback.get_active(category)
            
            for provider in all_providers:
                if active and provider.capability.priority >= active.capability.priority:
                    # If this provider has equal or lower priority than the active one, no need to check for recovery
                    continue
                    
                # This provider has HIGHER priority than the active one, let's see if it recovered
                is_healthy = await provider.check_health()
                if is_healthy:
                    # Recovered! Switch back to it
                    self.fallback.active_providers[category] = provider
                    # Remove from failed providers tracking if it was there
                    self.fallback.failed_providers.pop(provider.capability.name, None)
                    break # We found the highest priority one that works, move to next category
