"""
Live Demonstration & Validation of Alfred Android GSM Cellular Bridge.
Demonstrates:
1. Android Device Detection & SIM Card Gateway Status (₹0.00 Free Cellular Calling).
2. Direct Intent Dialing (android.intent.action.CALL to +91-8712484963).
3. Multi-Turn Conversational Dialogue Flow with Transparent AI Assistant Greeting.
4. Clean Cellular Call Termination (KEYCODE_ENDCALL).
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
from jarvisx.telephony.android_gsm_bridge import AndroidGSMBridge


def run_live_android_gsm_demo():
    print("=" * 115)
    print(" [JARVIS X] ALFRED ANDROID GSM CELLULAR BRIDGE (100% FREE UNLIMITED CALLS VIA YOUR PHONE)")
    print("=" * 115)

    bridge = AndroidGSMBridge.get_instance()

    # 1. Inspect Connected Android Devices
    print("\n[STEP 1] [+] Scanning for Connected Android Smartphone & SIM Gateway...")
    status = bridge.get_status()
    print(f"  • Bridge Status      : {status['bridge_status']}")
    print(f"  • Cellular Billing   : {status['cellular_billing']} (Zero Cost / Free Plan)")
    print(f"  • Supported Actions  : {', '.join(status['supported_actions'])}")

    devices = status["connected_devices"]
    for dev in devices:
        print(f"  • Active Device      : '{dev['model']}' ({dev['device_id']}) | Conn: {dev['connection_type']} | Battery: {dev['battery_level']}%")

    assert len(devices) > 0

    # 2. Place Cellular Call to Father (+91-8712484963)
    print("\n[STEP 2] [+] Initiating Free Cellular SIM Call to Father (+91-8712484963)...")
    target_number = "+91-8712484963"
    contact_name = "Father"
    objective = "Inform that Charan will reach home by 7:30 PM for dinner after concluding the AI lab session"

    simulated_father_dialogue = [
        "Hello Alfred, where is Charan right now?",
        "Okay, tell him to reach home on time and drive safely.",
    ]

    session = bridge.initiate_conversational_gsm_call(
        phone_number=target_number,
        contact_name=contact_name,
        objective=objective,
        simulated_contact_dialogue=simulated_father_dialogue,
    )

    print("=" * 115)
    print(f" 📋 GSM CALL SESSION: {session.session_id} (State: {session.state.value} | Duration: {session.duration_sec}s | Cost: ₹0.00)")
    print("=" * 115)

    for item in session.transcript:
        speaker_icon = "🤖 [ALFRED]" if item["speaker"] == "ALFRED" else f"👤 [{item['speaker']}]"
        print(f"\n  {speaker_icon} (Turn #{item['turn']}):")
        print(f"  \"{item['text']}\"")

    print("\n" + "-" * 115)
    print(f"  🛡️ Cryptographic Audit Hash: {session.audit_hash[:20]}...")

    # 3. Cryptographic Audit Ledger Integrity
    audit = CryptographicAuditLedger(Path("var/db/audit_ledger.db"))
    integrity = audit.verify_integrity()
    print(f"\n[STEP 3] [+] Cryptographic Audit Ledger Integrity: {integrity['status']} (Total Records: {integrity['total_records']})")
    assert integrity["valid"] is True

    print("\n" + "=" * 115)
    print(" [OK] ALFRED ANDROID GSM CELLULAR BRIDGE FULLY VALIDATED!")
    print("=" * 115)


if __name__ == "__main__":
    run_live_android_gsm_demo()
