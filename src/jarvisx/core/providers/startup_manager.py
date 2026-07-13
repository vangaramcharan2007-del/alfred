from __future__ import annotations

import asyncio
from typing import Dict, List

from jarvisx.core.providers.fallback_manager import FallbackManager
from jarvisx.core.health import HealthMonitor


from jarvisx.core.configuration import ConfigurationManager


class StartupManager:
    """
    Orchestrates the Jarvis X boot sequence.
    BOOT -> Dependency Discovery -> Health Verification -> Provider Benchmarking 
    -> Provider Selection -> Fallback Activation -> HUD Initialization -> Alfred Online
    """
    def __init__(self, fallback_manager: FallbackManager, health_monitor: HealthMonitor, config_manager: ConfigurationManager):
        self.fallback = fallback_manager
        self.health = health_monitor
        self.config = config_manager
        self.is_ready = False
        self.setup_mode = not self.config.is_setup_completed
        self._setup_event = asyncio.Event()
        if not self.setup_mode:
            self._setup_event.set()
        
    async def boot(self) -> None:
        """Executes the complete boot sequence."""
        if self.setup_mode:
            print("Jarvis X is in SETUP MODE. Please visit the dashboard to complete setup.")
            await self._setup_event.wait()
            print("Setup completed. Resuming boot sequence...")

        import time
        start_time = time.time()
        print("Starting Jarvis X Boot Sequence...")
        
        # 1. Initialize Providers and select best available (Dependency Discovery, Benchmarking, Selection, Fallback)
        await self.fallback.initialize()
        
        # 2. Render HUD
        self._render_hud()
        
        # 3. Mark ready
        self.is_ready = True
        
        boot_time = time.time() - start_time
        print(f"Boot sequence completed in {boot_time:.2f} seconds.")
        
    def _render_hud(self) -> None:
        print("\n" + "=" * 40)
        print(" JARVIS X SYSTEM STARTUP - HUD")
        print("=" * 40 + "\n")
        
        categories = ["LLM", "TTS", "STT", "MEMORY", "VISION"]
        
        for category in categories:
            provider = self.fallback.get_active(category)
            if provider:
                print(f"[OK]   {category:<8}: {provider.capability.name}")
            else:
                print(f"[FAIL] {category:<8}: OFFLINE")
                
        # System health checks
        print("\n--- System Health ---")
        health_status = self.health.run_all()
        for name, status in health_status.items():
            lat_str = f"({status.latency_ms:.1f}ms)"
            if status.healthy:
                print(f"[OK]   {name:<20} OK {lat_str:>10}")
            else:
                print(f"[FAIL] {name:<20} ERROR: {status.message} {lat_str:>10}")
                
        print("\n" + "=" * 40)
        print("Jarvis systems online.")
        print("=" * 40 + "\n")
        
    async def wait_until_ready(self) -> None:
        while not self.is_ready:
            await asyncio.sleep(0.1)
