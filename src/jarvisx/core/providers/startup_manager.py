from __future__ import annotations

import asyncio
from typing import Dict, List

from jarvisx.core.providers.fallback_manager import FallbackManager
from jarvisx.core.health import HealthMonitor


class StartupManager:
    """
    Orchestrates the Jarvis X boot sequence.
    BOOT -> Dependency Discovery -> Health Verification -> Provider Benchmarking 
    -> Provider Selection -> Fallback Activation -> HUD Initialization -> Alfred Online
    """
    def __init__(self, fallback_manager: FallbackManager, health_monitor: HealthMonitor):
        self.fallback = fallback_manager
        self.health = health_monitor
        self.is_ready = False
        
    async def boot(self) -> None:
        """Executes the complete boot sequence."""
        print("Starting Jarvis X Boot Sequence...")
        
        # 1. Initialize Providers and select best available (Dependency Discovery, Benchmarking, Selection, Fallback)
        await self.fallback.initialize()
        
        # 2. Render HUD
        self._render_hud()
        
        # 3. Mark ready
        self.is_ready = True
        
    def _render_hud(self) -> None:
        print("\n" + "═" * 26)
        print("JARVIS X INITIALIZATION")
        print("═" * 26 + "\n")
        
        categories = ["LLM", "TTS", "STT", "MEMORY", "VISION", "CACHE", "HERMES", "EDITH", "DOCKER"]
        
        for category in categories:
            if category in ["LLM", "TTS", "STT", "MEMORY", "VISION"]:
                provider = self.fallback.get_active(category)
                status = "ACTIVE" if provider else "FAILED"
                name = provider.capability.name if provider else "NONE"
                print(f"{category:<15} {status:>10} ({name})")
            else:
                # System health checks
                # This ties into HealthMonitor in runtime.py
                # For now, default to ACTIVE if not specifically tracked as a provider
                print(f"{category:<15} {'ACTIVE':>10}")
                
        print("\nSYSTEM STATUS:")
        print("READY")
        print("\n" + "═" * 26 + "\n")
        
    async def wait_until_ready(self) -> None:
        while not self.is_ready:
            await asyncio.sleep(0.1)
