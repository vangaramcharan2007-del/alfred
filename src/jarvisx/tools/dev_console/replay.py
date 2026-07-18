"""Replay functionality for the Developer Console."""
import time
from jarvisx.tools.dev_console.state import ConsoleState

class ConsoleReplay:
    """Replays execution events with timestamps."""
    
    @staticmethod
    def prompt_and_replay(state: ConsoleState):
        ans = input("\nReplay execution? [Y/N]: ").strip().lower()
        if ans == 'y':
            print("\n--- REPLAY TIMELINE ---")
            with state.lock:
                timeline = list(state.events)
            for timestamp, event in timeline:
                print(f"[{timestamp}] {event}")
                time.sleep(0.1) # Brief pause for effect
            print("--- REPLAY COMPLETE ---\n")
