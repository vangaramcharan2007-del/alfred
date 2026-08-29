"""
Alfred Sovereign Master OS — Unified Runtime Engine (Phase 108 Master Release).
Single-entry unified boot orchestrating:
1. Live Code Auto-Pilot (Real-time syntax & bug self-healer on Ctrl+S)
2. Adaptive Game Governor (Continuous 2.5s thermal & load sentinel)
3. Ambient Clipboard Error Interceptor
4. Active Environmental Context Sensor
5. Pure Gemini 3.6 Flash Mission Planner & Voice Engine
6. Sovereign Cybernetic Situation Room HUD
"""

from __future__ import annotations

import os
import sys
import threading
import time
from typing import Any, Dict, Optional

# Ensure UTF-8 console output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add src to sys.path
sys.path.insert(0, os.path.abspath("src"))

from jarvisx.engineering.live_code_autopilot import LiveCodeAutopilot, get_code_autopilot
from jarvisx.gaming.adaptive_game_governor import AdaptiveGameGovernor, get_game_governor
from jarvisx.harness.active_context_sensor import ActiveWindowContextSensor, WindowContext
from jarvisx.harness.clipboard_sensor import AmbientClipboardSensor, ClipboardEvent
from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator


class AlfredMasterOS:
    """The Master Sovereign Operating System uniting all autonomous subsystems."""

    def __init__(self):
        print("\n" + "=" * 75)
        print(" 👑 BOOTING ALFRED MASTER SOVEREIGN OS (ALL SUBSYSTEMS UNIFIED)")
        print("=" * 75)

        # 1. Core Brain & Voice
        self.orchestrator = DynamicOrchestrator()
        self.voice_engine = self.orchestrator.voice_engine

        # 2. Game Governor
        self.game_governor = get_game_governor()

        # 3. Live Code Auto-Pilot
        self.code_autopilot = get_code_autopilot()

        # 4. Clipboard & Context Sensors
        self.clipboard_sensor = AmbientClipboardSensor()
        self.context_sensor = ActiveWindowContextSensor()

        # Hook event listeners
        self.code_autopilot.add_listener(self._on_code_healed)
        self.clipboard_sensor.add_listener(self._on_clipboard_event)
        self.context_sensor.add_listener(self._on_context_change)

    def boot_all_subsystems(self, launch_hud: bool = True):
        """Launches all 6 sovereign pillars in background."""
        print("[*] Pillar 1: Initializing Gemini 3.6 Flash Cloud Brain & Voice Engine... [OK]")
        print("[*] Pillar 2: Engaging Real-Time Adaptive Game Governor (2.5s Sentinel)... [OK]")
        self.game_governor.start()

        print("[*] Pillar 3: Engaging Live Code Auto-Pilot Sentinel (Ctrl+S Healer)... [OK]")
        self.code_autopilot.start()

        print("[*] Pillar 4: Engaging Ambient Clipboard Error Interceptor... [OK]")
        self.clipboard_sensor.start()

        print("[*] Pillar 5: Engaging Active Window Environmental Perception... [OK]")
        self.context_sensor.start()

        self.voice_engine.speak("Alfred Sovereign Master OS is fully online. All autonomous sentinels are guarding your laptop.")

        print("\n" + "=" * 75)
        print(" [OK] ✅ ALFRED MASTER OS IS RUNNING IN THE BACKGROUND")
        print("=" * 75 + "\n")

        if launch_hud:
            print("[*] Pillar 6: Launching Sovereign Situation Room HUD...")
            from jarvisx.runtime.alfred_situation_room_hud import AlfredSituationRoomHUD
            hud = AlfredSituationRoomHUD()
            hud.run()

    def _on_code_healed(self, ev):
        msg = f"🔧 Auto-healed syntax error in {os.path.basename(ev.file_path)} (Line {ev.line_number})"
        print(f"\n[ALFRED AUTOPILOT]: {msg}")
        self.voice_engine.speak(f"Sir, I detected and auto-healed a syntax error in {os.path.basename(ev.file_path)}.")

    def _on_clipboard_event(self, ev: ClipboardEvent):
        if ev.event_type == "PYTHON_ERROR":
            print(f"\n[ALFRED CLIPBOARD]: 🚨 Intercepted Python error in {ev.parsed_metadata.get('file_path')}")
        elif ev.event_type == "TERMINAL_COMMAND":
            print(f"\n[ALFRED CLIPBOARD]: ⚡ Intercepted terminal command: {ev.parsed_metadata.get('command')}")

    def _on_context_change(self, ctx: WindowContext):
        pass


def launch_master_os(launch_hud: bool = True):
    master = AlfredMasterOS()
    master.boot_all_subsystems(launch_hud=launch_hud)


if __name__ == "__main__":
    launch_master_os(launch_hud=True)
