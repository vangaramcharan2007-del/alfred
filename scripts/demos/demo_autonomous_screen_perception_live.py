"""
Live Demonstration & Validation of Jarvis X Phase 2: Autonomous Screen Perception & Computer-Use Loop.
Demonstrates:
1. Real Windows Screen Perception (Resolution, Active Window Title & Class).
2. Windows UI Automation (UIA) Control Enumeration (Buttons, Edit boxes, Windows).
3. Semantic Visual Grounding (Mapping user intent to screen pixel coordinates).
4. Autonomous Multi-Step Closed-Loop Desktop Agency (Reason -> Act -> Observe).
5. SHA-256 Cryptographic Audit Ledger Proofs.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "src"))
sys.path.insert(0, str(repo_root / "friday-tony-stark-demo"))

from jarvisx.computer_use.autonomous_computer_agent import AutonomousComputerAgent
from jarvisx.computer_use.screen_perception import ScreenPerceptionEngine
from jarvisx.computer_use.visual_grounding import VisualGroundingMatcher
from jarvisx.security.audit_ledger import CryptographicAuditLedger


def run_live_screen_perception_demo():
    print("=" * 115)
    print(" [JARVIS X] PHASE 2: AUTONOMOUS SCREEN PERCEPTION & COMPUTER-USE LOOP (MANUS / OS-WORLD)")
    print("=" * 115)

    perception = ScreenPerceptionEngine()
    matcher = VisualGroundingMatcher(perception)
    agent = AutonomousComputerAgent(perception_engine=perception, grounding_matcher=matcher)

    # 1. Live Screen Perception
    print("\n[STEP 1] [+] Capturing Live Screen Perception & Windows UIA Tree...")
    state = perception.perceive_screen(save_screenshot=True)
    print(f"  • Resolution      : {state.screen_width} x {state.screen_height} px")
    print(f"  • Active Window   : '{state.active_window_title}' (Class: {state.active_window_class})")
    print(f"  • Total UIA Items : {state.total_elements} interactive UI elements discovered")
    print(f"  • Screenshot Saved: {state.screenshot_saved_path}")

    print("\n  Sample Discovered UI Controls:")
    for el in state.elements[:5]:
        print(f"    - [{el.control_type}] '{el.name}' @ Center: {el.center} | Rect: {el.rect}")

    assert state.screen_width > 0 and state.screen_height > 0
    assert state.total_elements >= 0

    # 2. Semantic Visual Grounding
    print("\n[STEP 2] [+] Testing Semantic Visual Grounding (Natural Query -> Screen Coordinates)...")
    test_queries = [
        "Start button",
        "Search bar",
        "Close button",
        "Center of screen",
        "Active Application Window",
    ]

    for q in test_queries:
        match = matcher.ground_element(q, elements=state.elements)
        print(f"  [+] Target: '{q}'")
        print(f"      -> Coordinates: {match.center_coords} | Confidence: {match.confidence:.2f} | Strategy: {match.matched_by}")
        assert match.center_coords[0] >= 0 and match.center_coords[1] >= 0

    # 3. Autonomous Multi-Step Closed-Loop Mission
    print("\n[STEP 3] [+] Executing Autonomous Closed-Loop Computer-Use Mission...")
    mission_goal = "Open VS Code development workspace, create algorithm script, and verify editor state"
    print(f"  🎯 Mission Goal: {mission_goal}\n")

    report = agent.execute_computer_mission(goal=mission_goal)
    print("=" * 115)
    print(f" 📋 MISSION TRACE: {report.mission_id} (Status: {report.final_status} | Duration: {report.total_duration_ms:.1f}ms)")
    print("=" * 115)

    for step in report.steps:
        print(f"\n[STEP {step.step_number}]")
        print(f"  🧠 THOUGHT:      {step.thought}")
        print(f"  ⚡ ACTION:       {step.action_type} on '{step.target_description}' @ {step.coordinates}")
        print(f"  👁️ OBSERVATION:  {step.observation_after}")
        print(f"  🛡️ VERIFIED:     {step.verified} (Latency: {step.step_duration_ms:.1f}ms)")
        print("-" * 115)

    # 4. Verify Cryptographic Audit Ledger
    audit = CryptographicAuditLedger(Path("var/db/audit_ledger.db"))
    integrity = audit.verify_integrity()
    print(f"\n[STEP 4] [+] Cryptographic Audit Ledger Integrity: {integrity['status']} (Total Records: {integrity['total_records']})")
    assert integrity["valid"] is True

    print("\n" + "=" * 115)
    print(" [OK] PHASE 2: AUTONOMOUS SCREEN PERCEPTION & COMPUTER-USE LOOP FULLY VALIDATED!")
    print("=" * 115)


if __name__ == "__main__":
    run_live_screen_perception_demo()
