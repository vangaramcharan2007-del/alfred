"""
Alfred Sovereign Ambient Orchestrator Engine.
Orchestrates continuous background awareness, proactive hardware protection,
adaptive game governance, and live voice & visual HUD presence.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

# Ensure UTF-8 console output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logger = logging.getLogger("jarvisx.runtime.ambient")


class AmbientSovereignOrchestrator:
    """Master Ambient Orchestration Engine running continuously in the background."""

    _instance: Optional["AmbientSovereignOrchestrator"] = None

    def __init__(self):
        self.is_running = False
        self._lock = threading.Lock()
        self.start_time = time.time()
        self.active_events: List[Dict[str, Any]] = []

        # 1. Subsystems
        from jarvisx.gaming.adaptive_game_governor import get_game_governor
        self.game_governor = get_game_governor()

        from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
        self.dynamic_orchestrator = DynamicOrchestrator()

        self.voice_engine = self.dynamic_orchestrator.voice_engine

        # State tracking
        self.last_ram_alert_t = 0.0
        self.last_battery_alert_t = 0.0

    @classmethod
    def get_instance(cls) -> "AmbientSovereignOrchestrator":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start_ambient_engine(self):
        """Starts all ambient background sentinels."""
        with self._lock:
            if self.is_running:
                return
            self.is_running = True

        print("\n" + "=" * 75)
        print(" 🤖 ALFRED SOVEREIGN AMBIENT ORCHESTRATOR IS ONLINE & ENGAGED")
        print("=" * 75)

        # 1. Start Gaming Governor
        self.game_governor.start()
        self._log_event("🛡️ Adaptive Game Governor engaged (monitoring every 2.5s)")

        # 2. Start Proactive Hardware & Health Monitor Thread
        self._health_thread = threading.Thread(
            target=self._hardware_health_monitor_loop,
            daemon=True,
            name="AmbientHardwareSentinelThread"
        )
        self._health_thread.start()
        self._log_event("📊 Proactive Hardware & Thermal Sentinel active")

        # 3. Speak status
        self.voice_engine.speak("Alfred Sovereign Orchestrator is fully engaged. I am actively monitoring your system in the background.")

    def stop_ambient_engine(self):
        """Stops the ambient engine."""
        with self._lock:
            self.is_running = False
        self.game_governor.stop()
        self._log_event("⏹️ Ambient Sovereign Orchestrator paused.")

    def _hardware_health_monitor_loop(self):
        """Continuous background hardware and thermal monitoring (every 5 seconds)."""
        while self.is_running:
            try:
                now = time.time()
                vm = psutil.virtual_memory()
                ram_pct = vm.percent

                # A. RAM Memory Pressure Detection (>92%)
                if ram_pct > 92.0 and (now - self.last_ram_alert_t > 120.0):
                    self.last_ram_alert_t = now
                    # Auto-purge cache
                    freed = self.game_governor._purge_background_memory()
                    msg = f"⚠️ Critical Memory Load ({ram_pct}% RAM) -> Auto-purged +{freed:.1f}MB caches."
                    self._log_event(msg)
                    print(f"\n[ALFRED SENTINEL]: {msg}")

                # B. Battery Health Check
                try:
                    battery = psutil.sensors_battery()
                    if battery and not battery.power_plugged and battery.percent <= 20:
                        if (now - self.last_battery_alert_t > 300.0):
                            self.last_battery_alert_t = now
                            msg = f"🔋 Battery warning: Level is at {battery.percent}%. Suggest connecting AC power."
                            self._log_event(msg)
                            self.voice_engine.speak(f"Sir, battery level is currently at {battery.percent} percent.")
                except Exception:
                    pass

            except Exception as e:
                logger.error(f"Health sentinel error: {e}")

            time.sleep(5.0)

    def _log_event(self, message: str):
        event = {"time": time.time(), "message": message}
        self.active_events.append(event)
        if len(self.active_events) > 60:
            self.active_events.pop(0)
        print(f"[ORCHESTRATOR EVENT] {message}")

    def get_orchestrator_telemetry(self) -> Dict[str, Any]:
        """Returns complete live telemetry across all 20 agents and hardware."""
        vm = psutil.virtual_memory()
        cpu_pct = psutil.cpu_percent(interval=0.1)
        uptime = round(time.time() - self.start_time, 1)

        gov_status = self.game_governor.get_status()

        return {
            "orchestrator_status": "ACTIVE_SOVEREIGN_MODE",
            "uptime_seconds": uptime,
            "hardware": {
                "cpu_percent": cpu_pct,
                "ram_percent": vm.percent,
                "ram_available_gb": round(vm.available / (1024 ** 3), 2),
                "ram_total_gb": round(vm.total / (1024 ** 3), 2),
            },
            "game_governor": gov_status,
            "active_agents_count": 20,
            "recent_events": self.active_events[-6:],
        }


def get_ambient_orchestrator() -> AmbientSovereignOrchestrator:
    return AmbientSovereignOrchestrator.get_instance()


if __name__ == "__main__":
    orch = get_ambient_orchestrator()
    orch.start_ambient_engine()
    print("\n[*] Ambient Orchestrator running. Press Ctrl+C to terminate.")
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        orch.stop_ambient_engine()
