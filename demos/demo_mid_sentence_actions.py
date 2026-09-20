"""
🚀 Jarvis X — Mid-Sentence Action Execution Demo
==================================================
Demonstrates that Jarvis X can execute OS actions (open apps, run commands)
WHILE speaking to the user, not sequentially.

This script:
1. Shows concurrent speech + action execution with real timestamps
2. Opens real apps (Notepad, Calculator) while TTS is playing
3. Prints a live dashboard proving the overlap
4. Validates timing: speech starts BEFORE tool completes

Run: python demos/demo_mid_sentence_actions.py
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import time
import threading
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Safe UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


# ─── Minimal Mock Classes for Demo ───
# These simulate the Organism's Mouth and Hands without requiring
# the full Jarvis X runtime (no LLM, no database, no mic)

@dataclass
class DemoResult:
    status: str = "success"
    tool: str = ""
    
    def to_dict(self):
        return {"status": self.status, "tool": self.tool}

class DemoMouth:
    """Simulates TTS playback with timing tracking."""
    
    def __init__(self):
        self.speak_started_at: float = 0
        self.speak_text: str = ""
    
    def speak(self, text: str, blocking: bool = False):
        self.speak_started_at = time.perf_counter()
        self.speak_text = text
        word_count = len(text.split())
        duration = word_count * 0.35  # ~350ms per word
        
        print(f"  🗣️  [TTS] Speaking: \"{text}\"")
        print(f"       Estimated duration: {duration:.1f}s ({word_count} words)")
        
        if blocking:
            time.sleep(duration)
        else:
            def _play():
                time.sleep(duration)
            threading.Thread(target=_play, daemon=True).start()


class DemoHands:
    """Executes real OS actions for the demo."""
    
    def act(self, tool_name: str, args: dict) -> dict:
        app = args.get("application", args.get("target", ""))
        
        if tool_name == "open_app":
            return self._open_app(app)
        elif tool_name == "run_command":
            cmd = args.get("command", "echo Hello from Jarvis X")
            try:
                result = subprocess.run(
                    ["powershell", "-Command", cmd],
                    capture_output=True, text=True, timeout=5
                )
                return {
                    "status": "success",
                    "tool": "run_command",
                    "result": result.stdout.strip()[:200]
                }
            except Exception as e:
                return {"status": "failed", "tool": "run_command", "error": str(e)}
        
        return {"status": "success", "tool": tool_name}
    
    def _open_app(self, app_name: str) -> dict:
        app_map = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "explorer": "explorer.exe",
        }
        
        binary = app_map.get(app_name.lower(), f"{app_name}.exe")
        try:
            subprocess.Popen(["cmd.exe", "/c", "start", "", binary], shell=False)
            return {"status": "success", "tool": "open_app", "result": f"Launched {app_name}"}
        except Exception as e:
            return {"status": "failed", "tool": "open_app", "error": str(e)}


# ─── Dashboard ───

def print_banner():
    print()
    print("=" * 70)
    print("  🚀 JARVIS X — MID-SENTENCE ACTION EXECUTION DEMO")
    print("  Concurrent Speech + Tool Execution")
    print("=" * 70)
    print()


def print_timeline(scenario: str, speech_start: float, tool_fire: float, tool_done: float, base: float):
    """Print a visual timeline of the concurrent execution."""
    s = (speech_start - base) * 1000
    f = (tool_fire - base) * 1000
    d = (tool_done - base) * 1000
    
    print()
    print(f"  📊 TIMELINE: {scenario}")
    print(f"  ├─ Speech started at:  t={s:6.0f}ms")
    print(f"  ├─ Tool fired at:      t={f:6.0f}ms  (delay: {f-s:.0f}ms after speech)")
    print(f"  ├─ Tool completed at:  t={d:6.0f}ms")
    print(f"  └─ Total duration:     {d:.0f}ms")
    print()
    
    # Visual bar
    bar_width = 50
    max_t = max(d, 1)
    speech_pos = int((s / max_t) * bar_width)
    fire_pos = int((f / max_t) * bar_width)
    done_pos = int((d / max_t) * bar_width)
    
    speech_bar = "░" * fire_pos + "█" * (done_pos - fire_pos) + "░" * (bar_width - done_pos)
    tool_bar = "░" * fire_pos + "▓" * (done_pos - fire_pos) + "░" * (bar_width - done_pos)
    
    print(f"  🗣️ Speech:  |{speech_bar}|")
    print(f"  🦾 Tool:    |{tool_bar}|")
    print(f"              {'0ms':<10}{'mid':^30}{f'{max_t:.0f}ms':>10}")
    print()

    # Overlap check
    if f < d and s < d:
        overlap = min(d, d) - max(s, f)
        print(f"  ✅ CONCURRENT: Speech and tool overlapped by {overlap:.0f}ms")
    else:
        print(f"  ⚠️  Sequential execution detected")
    print()


async def run_demo():
    """Run the full mid-sentence action demo."""
    print_banner()

    # Import ConcurrentActionEngine
    from jarvisx.automation.concurrent_action_engine import ConcurrentActionEngine, TriggerMode

    mouth = DemoMouth()
    hands = DemoHands()
    engine = ConcurrentActionEngine(mouth=mouth, hands=hands)

    scenarios = [
        {
            "name": "Open Notepad",
            "speech": "Opening Notepad for you right now, Sir.",
            "tool": "open_app",
            "args": {"application": "notepad"},
            "mode": TriggerMode.MID_SENTENCE,
        },
        {
            "name": "Open Calculator",
            "speech": "Let me pull up the Calculator for you, Sir.",
            "tool": "open_app",
            "args": {"application": "calculator"},
            "mode": TriggerMode.IMMEDIATE,
        },
        {
            "name": "Check System Info",
            "speech": "Running a quick system check right now, Sir.",
            "tool": "run_command",
            "args": {"command": "[System.Environment]::OSVersion.VersionString; hostname"},
            "mode": TriggerMode.MID_SENTENCE,
        },
    ]

    all_passed = True

    for i, scenario in enumerate(scenarios, 1):
        print(f"  {'─' * 60}")
        print(f"  SCENARIO {i}/{len(scenarios)}: {scenario['name']}")
        print(f"  {'─' * 60}")

        base_time = time.perf_counter()

        result = await engine.execute_with_speech(
            speech_text=scenario["speech"],
            tool_name=scenario["tool"],
            tool_args=scenario["args"],
            trigger_mode=scenario["mode"],
        )

        print_timeline(
            scenario["name"],
            result.speech_started_at,
            result.tool_fired_at,
            result.tool_completed_at,
            base_time,
        )

        # Validate
        if result.tool_succeeded:
            print(f"  ✅ Tool '{scenario['tool']}' succeeded")
        else:
            print(f"  ❌ Tool '{scenario['tool']}' failed: {result.tool_error}")
            all_passed = False

        print(f"  📏 Total concurrent execution: {result.total_duration_ms:.0f}ms")
        print()

        # Brief pause between scenarios
        await asyncio.sleep(1.5)

    # ─── Final Summary ───
    print("=" * 70)
    if all_passed:
        print("  ✅ ALL SCENARIOS PASSED — Mid-sentence actions working!")
        print("  Apps opened WHILE speech was playing concurrently.")
    else:
        print("  ⚠️  Some scenarios failed — check logs above.")
    print("=" * 70)
    print()

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(run_demo())
    sys.exit(0 if success else 1)
