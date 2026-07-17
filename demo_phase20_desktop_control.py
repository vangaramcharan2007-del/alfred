"""Validation Script for Alfred Desktop Action & GUI Control Layer.

Tests opening apps, typing, shortcuts, window switching, and closing.
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
from jarvisx.core.desktop.action_verifier import ActionVerifier

logging.disable(logging.CRITICAL)

def test_validation():
    print("=" * 48)
    print("  ALFRED DESKTOP CONTROL VALIDATION")
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

    verifier = commander.action_verifier

    # Sequence of commands to simulate
    test_phrases = [
        "open notepad",
        "focus notepad",
        "type hello world",
        "press ctrl s",       # opens save dialog
        "type test_save.txt", # type filename
        "press enter",        # save
        "close notepad"       # close
    ]

    for i, phrase in enumerate(test_phrases):
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
        
        # Give GUI time to respond between actions
        if i == 0:
            # Wait for notepad to open
            verifier.verify_window_active("Notepad", timeout=3.0)
            time.sleep(1)
        else:
            time.sleep(1)

    # Verification: Check if notepad is closed
    closed = verifier.verify_window_closed("Notepad", timeout=2.0)
    print(f"\nVerification: SUCCESS - Notepad closed" if closed else "\nVerification: FAILED - Notepad still open")
    
    # Check safety intent
    print("\n--- Testing phrase: 'delete file' ---")
    reply, _ = commander.handle("delete file")
    print(f"Alfred speaks: {reply}")

    print("\n" + "=" * 48)
    print("  VALIDATION COMPLETE")
    print("=" * 48)

if __name__ == "__main__":
    test_validation()
