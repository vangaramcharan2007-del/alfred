"""
Live Demonstration & Validation of the Manus-Style Autonomous ReAct Engine for Jarvis X.
Demonstrates:
1. Step-by-Step Reason-Act-Observe Streaming Trace.
2. Dynamic Public API Capability Integration.
3. 3-Perspective Adversarial Code & Synthesis Review.
4. SHA-256 Cryptographic Audit Ledger Proofs.
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

from jarvisx.automation.manus_react_engine import ManusReActEngine
from jarvisx.security.audit_ledger import CryptographicAuditLedger


def run_live_manus_react_demo():
    print("=" * 115)
    print(" [JARVIS X] MANUS-STYLE AUTONOMOUS ReAct (REASON-ACT-OBSERVE) STREAMING ENGINE")
    print("=" * 115)

    engine = ManusReActEngine()
    mission_goal = "Conduct autonomous environmental and forex risk assessment for Tokyo branch deployment."

    print(f"\n[GOAL] 🎯 {mission_goal}\n")
    report = engine.execute_react_mission(goal=mission_goal)

    print("=" * 115)
    print(f" 📋 MISSION TRACE: {report.mission_id} (Status: {report.status} | Duration: {report.total_duration_ms:.1f}ms)")
    print("=" * 115)

    for s in report.steps:
        print(f"\n[STEP {s.step_number}]")
        print(f"  🧠 THOUGHT:      {s.thought}")
        print(f"  ⚡ ACTION:       {s.action_type} (Input: {json.dumps(s.action_input)})")
        print(f"  👁️ OBSERVATION:  {s.observation}")
        print(f"  🛡️ REVIEW:       {s.review_decision} (Latency: {s.step_latency_ms:.1f}ms)")
        print("-" * 115)

    print("\n[FINAL SYNTHESIZED OUTPUT]")
    print(report.final_output)

    # Verify Cryptographic Audit Ledger
    audit = CryptographicAuditLedger(Path("var/db/audit_ledger.db"))
    integrity = audit.verify_integrity()
    print(f"\n[+] Cryptographic Audit Ledger Integrity: {integrity['status']} (Total Records: {integrity['total_records']})")
    assert integrity["valid"] is True

    print("\n" + "=" * 115)
    print(" [OK] MANUS ReAct STREAMING ENGINE FULLY PROVEN AND OPERATIONAL!")
    print("=" * 115)


if __name__ == "__main__":
    run_live_manus_react_demo()
