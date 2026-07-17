"""Validation Script for Phase 21: Autonomous Task Execution Engine."""
import os
import sys
import time
import logging

sys.path.insert(0, os.path.abspath("src"))

from jarvisx.core.voice.tts_engine import TTSEngine
from jarvisx.core.voice.alfred_commander import AlfredCommander
from jarvisx.core.presence_manager import PresenceManager
from jarvisx.core.diagnostics_console import DiagnosticsConsole
from jarvisx.core.objective_store import ObjectiveStore
from jarvisx.core.mission_continuity import MissionContinuityManager
from jarvisx.core.notification_policy import NotificationPolicy, NotificationLevel
from jarvisx.core.runtime_visibility import RuntimeVisibility, VisibilityMode

logging.disable(logging.CRITICAL)

def test_validation():
    print("=" * 48)
    print("  ALFRED AUTONOMOUS EXECUTION VALIDATION")
    print("=" * 48)

    RuntimeVisibility.set_mode(VisibilityMode.HEADLESS)
    
    # Initialize subsystems
    presence = PresenceManager.get_instance()
    store = ObjectiveStore()
    continuity = MissionContinuityManager(store, presence_manager=presence)
    policy = NotificationPolicy(minimum_level=NotificationLevel.INFORMATIONAL)
    diagnostics = DiagnosticsConsole(presence)
    tts = TTSEngine()

    commander = AlfredCommander(
        presence=presence,
        diagnostics=diagnostics,
        objective_store=store,
        continuity=continuity,
        notification_policy=policy,
    )

    # Required Test Objectives
    objectives = [
        "create a file called hello.txt containing hello world",
        "create a folder named JarvisTest on the desktop",
        "search google for LangGraph documentation",
        "open vscode and create test.py"
    ]

    for i, obj in enumerate(objectives):
        print(f"\n--- Testing objective {i+1}: '{obj}' ---")
        start = time.time()
        
        # Dispatch to commander (which delegates to TaskExecutor)
        commander.handle(obj)
        
        latency = (time.time() - start) * 1000
        print(f"Objective overall latency: {latency:.2f} ms")
        
        time.sleep(2) # Give OS a moment to settle between objectives

    print("\n" + "=" * 48)
    print("  VALIDATION COMPLETE")
    print("=" * 48)

if __name__ == "__main__":
    test_validation()
