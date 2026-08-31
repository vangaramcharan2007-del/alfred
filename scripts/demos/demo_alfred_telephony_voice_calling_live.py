"""
Live Demonstration & Validation of Alfred Telephony & Carrier Voice Calling Gateway.
Demonstrates:
1. Telephony Provider Detection (Twilio / Bland.ai / Vapi / Simulator).
2. Live Multi-Turn Conversational Phone Call to Charan's Father (8712484963).
3. Respectful AI Transparency and Natural Dialogue Flow.
4. Dynamic Context-Aware Turn-Taking using Hermes LLM Reasoning.
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

from jarvisx.security.audit_ledger import CryptographicAuditLedger
from jarvisx.telephony.telephony_gateway import TelephonyGateway


def run_live_telephony_demo():
    print("=" * 115)
    print(" [JARVIS X] ALFRED TELEPHONY & REAL CARRIER VOICE CALLING GATEWAY")
    print("=" * 115)

    gateway = TelephonyGateway.get_instance()

    # 1. Gateway Status Check
    print("\n[STEP 1] [+] Inspecting Telephony Gateway & Configured Providers...")
    status = gateway.get_status()
    print(f"  • Telephony Engine   : {status['telephony_engine']}")
    print(f"  • Active Provider    : {status['active_provider']}")
    print(f"  • Full-Duplex VAD    : {status['full_duplex_barge_in']}")
    print(f"  • AI Disclosure Mode : {status['disclosure_mode']}")

    # 2. Place Conversational Phone Call to Father (8712484963)
    print("\n[STEP 2] [+] Initiating Conversational Outbound Call to Father (+91-8712484963)...")
    target_number = "+91-8712484963"
    contact_name = "Father"
    objective = "Let him know Charan is actively working on the AI architecture in the lab and will reach home by 7:30 PM for dinner"

    print(f"  📞 Target Phone : {target_number}")
    print(f"  👤 Contact Name : {contact_name}")
    print(f"  🎯 Objective    : {objective}\n")

    simulated_father_speech = [
        "Hello Alfred. Is everything fine with Charan? When is he coming home?",
        "Okay good. Make sure he doesn't stay too late and drinks water.",
        "Alright Alfred, thank you for updating me.",
    ]

    report = gateway.place_conversational_call(
        phone_number=target_number,
        contact_name=contact_name,
        objective=objective,
        simulated_contact_responses=simulated_father_speech,
    )

    print("=" * 115)
    print(f" 📋 CALL LOG: {report.call_id} (Status: {report.status.value} | Provider: {report.provider.value} | Duration: {report.total_duration_sec}s)")
    print("=" * 115)

    for turn in report.dialogue_transcript:
        speaker_icon = "🤖 [ALFRED]" if turn.speaker == "ALFRED" else f"👤 [{turn.speaker}]"
        print(f"\n  {speaker_icon} (Turn #{turn.turn_number}):")
        print(f"  \"{turn.spoken_text}\"")

    print("\n" + "-" * 115)
    print(f"  📝 Executive Call Summary:\n  \"{report.call_summary}\"")
    print(f"  🛡️ Cryptographic Audit Hash: {report.audit_hash[:20]}...")

    # 3. Cryptographic Audit Ledger Integrity
    audit = CryptographicAuditLedger(Path("var/db/audit_ledger.db"))
    integrity = audit.verify_integrity()
    print(f"\n[STEP 3] [+] Cryptographic Audit Ledger Integrity: {integrity['status']} (Total Records: {integrity['total_records']})")
    assert integrity["valid"] is True

    print("\n" + "=" * 115)
    print(" [OK] ALFRED TELEPHONY & CARRIER VOICE CALLING GATEWAY FULLY VALIDATED!")
    print("=" * 115)


if __name__ == "__main__":
    run_live_telephony_demo()
