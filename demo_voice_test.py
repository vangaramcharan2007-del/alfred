"""Alfred Voice Test — demonstrates real audio output for system events."""
import os
import sys
import time

sys.path.insert(0, os.path.abspath("src"))

from jarvisx.core.voice.tts_engine import TTSEngine
from jarvisx.core.voice.voice_bus import VoiceBus


def main():
    print("=" * 44)
    print("  ALFRED VOICE TEST")
    print("=" * 44)
    print()

    # Initialise engine and bus
    engine = TTSEngine()
    bus = VoiceBus(tts_engine=engine)

    # Report available voices
    voices = engine.list_voices()
    print(f"Available system voices ({len(voices)}):")
    for v in voices:
        print(f"  - {v}")
    print(f"\nSelected voice: {engine.get_current_voice()}")
    print()

    # -----------------------------------------------------------
    # 1. Startup
    # -----------------------------------------------------------
    print("[Event] startup")
    bus.publish("startup", "Good evening. Alfred is online.")
    time.sleep(0.5)

    # -----------------------------------------------------------
    # 2. Objective started
    # -----------------------------------------------------------
    print("\n[Event] objective_started")
    bus.publish("objective_started", "Beginning objective execution.")
    time.sleep(0.5)

    # -----------------------------------------------------------
    # 3. Silent events (should produce NO audio)
    # -----------------------------------------------------------
    print("\n[Event] memory_indexing (should be SILENT)")
    bus.publish("memory_indexing", "This should not be heard.")

    print("[Event] cache_cleanup (should be SILENT)")
    bus.publish("cache_cleanup", "This should not be heard either.")

    print("[Event] heartbeat (should be SILENT)")
    bus.publish("heartbeat", "Still silent.")
    time.sleep(0.3)

    # -----------------------------------------------------------
    # 4. Objective completed
    # -----------------------------------------------------------
    print("\n[Event] objective_completed")
    bus.publish("objective_completed", "Objective completed successfully.")
    time.sleep(0.5)

    # -----------------------------------------------------------
    # 5. Recovery detected
    # -----------------------------------------------------------
    print("\n[Event] recovery_started")
    bus.publish("recovery_started", "I found interrupted work from a previous session.")
    time.sleep(0.3)

    print("[Event] recovery_completed")
    bus.publish("recovery_completed", "Resuming execution.")
    time.sleep(0.5)

    # -----------------------------------------------------------
    # 6. Initiative detected
    # -----------------------------------------------------------
    print("\n[Event] initiative_detected")
    bus.publish("initiative_detected",
                "I noticed your downloads folder may require attention.")
    time.sleep(0.5)

    # -----------------------------------------------------------
    # 7. Failure detected
    # -----------------------------------------------------------
    print("\n[Event] execution_failed")
    bus.publish("execution_failed", "Execution failed.")
    time.sleep(0.3)

    print("[Event] critical_failure")
    bus.publish("critical_failure", "Additional intervention may be required.")
    time.sleep(0.5)

    # -----------------------------------------------------------
    # Done
    # -----------------------------------------------------------
    print()
    print("=" * 44)
    print("  VOICE TEST COMPLETE")
    print("=" * 44)


if __name__ == "__main__":
    main()
