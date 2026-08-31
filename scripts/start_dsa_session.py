"""
Jarvis X — Start Interactive DSA Practice Session in VS Code.
Launches VS Code on dsa_practice/module1_arrays_two_pointers.py and starts the live auto-test watcher.
"""

import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from jarvisx.agents.dsa_learner_watcher import get_dsa_watcher


def main():
    print("=" * 70)
    print("   ALFRED OS — INTERACTIVE DSA PRACTICE IN VS CODE")
    print("=" * 70 + "\n")

    practice_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "dsa_practice", "module1_arrays_two_pointers.py")
    )

    # 1. Launch VS Code
    print(f"[1/2] 🖥️ Launching VS Code on '{os.path.basename(practice_file)}'...")
    try:
        subprocess.Popen(["code", practice_file], shell=True)
        print("      [OK] VS Code launched.")
    except Exception as e:
        print(f"      [!] Could not launch VS Code CLI: {e}")

    # 2. Start DSA Learner Watcher
    print("[2/2] 👁️ Starting Real-Time Error-Fixing Watcher...")
    watcher = get_dsa_watcher()
    res = watcher.start_watcher()
    print(f"      {res.get('message')}\n")

    print("=" * 70)
    print("   DSA PRACTICE IS ACTIVE! Edit code & press Ctrl+S to test.")
    print("   Alfred will speak hints aloud automatically when you save.")
    print("=" * 70 + "\n")

    # Run initial check
    eval_res = watcher.evaluate_file(practice_file)
    print(f"Initial Check: {eval_res.get('status').upper()} - {eval_res.get('message')}\n")


if __name__ == "__main__":
    main()
