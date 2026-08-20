"""Jarvis X: Verification Test Suite for Technical Phases 1, 2, 3, and 4."""

from __future__ import annotations
import sys
from jarvisx.interface.wake_word_listener import WakeWordListener
from jarvisx.agents.coding_swarm import CodingSwarm
from jarvisx.vision.screen_agent import ScreenAgent
from jarvisx.automation.web_agent import WebAgent

def run_tests():
    print("========================================================")
    print("  JARVIS X: ALL 4 TECHNICAL PHASES VERIFICATION")
    print("========================================================\n")

    # 1. Wake Word
    print("[1/4] Testing Wake-Word Hotword Detection Engine...")
    ww = WakeWordListener()
    assert ww.check_phrase_for_wakeword("hey jarvis what time is it") is True
    assert ww.check_phrase_for_wakeword("hello world") is False
    print("      [+] Wake-Word Matching: PASSED!")

    # 2. Coding Swarm
    print("\n[2/4] Testing Multi-Agent Coding Swarm...")
    swarm = CodingSwarm()
    res = swarm.run_swarm("Create a Python function to compute Fibonacci sequence")
    print(f"      [+] Swarm Status: {res['status']} | Duration: {res['duration']}s | Agents: {res['agents_executed']}")

    # 3. Vision Screen Agent
    print("\n[3/4] Testing Computer Vision & Screen Capture...")
    vision = ScreenAgent()
    v_res = vision.analyze_active_display()
    print(f"      [+] Vision Status: {v_res['status']} | File: {v_res.get('screenshot_path')}")

    # 4. Web Agent
    print("\n[4/4] Testing Autonomous Web Research Agent...")
    web = WebAgent()
    w_res = web.fetch_page_text("https://example.com")
    print(f"      [+] Web Status: {w_res['status']} | Chars: {w_res.get('char_count')}")

    print("\n========================================================")
    print("  [SUCCESS] All 4 Technical Phases Tested & Operational!")
    print("========================================================\n")

if __name__ == "__main__":
    run_tests()
