"""Validation Script for Alfred Browser Automation.

Tests browser intent recognition, TTS response, and Playwright execution.
"""
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
from jarvisx.core.browser.browser_controller import BrowserController

logging.disable(logging.CRITICAL)

def test_validation():
    print("=" * 48)
    print("  ALFRED BROWSER AUTOMATION VALIDATION")
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

    test_phrases = [
        "search youtube for python tutorials",
        "search google for langgraph documentation",
        "open github",
        "open chatgpt"
    ]

    for phrase in test_phrases:
        print(f"\n--- Testing phrase: '{phrase}' ---")
        start = time.time()
        reply, extra = commander.handle(phrase)
        latency = (time.time() - start) * 1000
        print(f"Command latency: {latency:.2f} ms")
        if reply:
            print(f"Alfred speaks: {reply}")
            tts.speak(reply)
        if extra and extra != "__EXIT__":
            print(f"Extra output:\n{extra}")
        time.sleep(2)  # Give playwright some time to close or settle if needed
        
    # Clean up playwright
    BrowserController.get_instance().driver.stop()

    print("\n" + "=" * 48)
    print("  VALIDATION COMPLETE")
    print("=" * 48)

if __name__ == "__main__":
    test_validation()
