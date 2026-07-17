"""Validation Script for Alfred Voice Runtime Stabilization.

Tests fuzzy intent recognition and TTS reliability automatically.
"""
import os
import sys
import time

sys.path.insert(0, os.path.abspath("src"))

from jarvisx.core.voice.tts_engine import TTSEngine
from jarvisx.core.voice.alfred_commander import AlfredCommander
from jarvisx.core.presence_manager import PresenceManager
from jarvisx.core.diagnostics_console import DiagnosticsConsole
from jarvisx.core.objective_store import ObjectiveStore
from jarvisx.core.mission_continuity import MissionContinuityManager
from jarvisx.core.notification_policy import NotificationPolicy, NotificationLevel
import logging

logging.disable(logging.CRITICAL)

def test_validation():
    print("=" * 48)
    print("  ALFRED VOICE VALIDATION TEST")
    print("=" * 48)

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
        "hello Alfred",
        "what is the time now",
        "what are you doing",
        "show diagnostics",
        "continue my work",
        "goodbye"
    ]

    for phrase in test_phrases:
        print(f"\n--- Testing phrase: '{phrase}' ---")
        reply, extra = commander.handle(phrase)
        if reply:
            print(f"Alfred speaks: {reply}")
            tts.speak(reply)
        if extra and extra != "__EXIT__":
            print(f"Extra output:\n{extra}")
        if extra == "__EXIT__":
            print("Exit command received.")
        time.sleep(0.5)

    print("\n" + "=" * 48)
    print("  VALIDATION COMPLETE")
    print("=" * 48)

if __name__ == "__main__":
    test_validation()
