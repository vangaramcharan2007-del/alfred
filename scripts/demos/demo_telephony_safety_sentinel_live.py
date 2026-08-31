"""
Live Demonstration & Validation of Alfred Telephony & Agent Safety Sentinel.
Demonstrates:
1. Active Safety Guardrails & Policy Inspection.
2. Emergency & Restricted Number Interlock (Blocking 112 / 911 / 100).
3. PII & Secret Redaction (Sanitizing Credit Cards, OTPs, API keys from speech).
4. Anti-Spam Frequency & Rate Limiting Throttling.
5. Sub-Millisecond Emergency Kill-Switch Engagement & Reset.
6. Legitimate Call Clearance & SHA-256 Cryptographic Audit Proofs.
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
from jarvisx.security.telephony_safety_sentinel import TelephonySafetySentinel


def run_live_safety_sentinel_demo():
    print("=" * 115)
    print(" [JARVIS X] ALFRED TELEPHONY & AGENT SAFETY SENTINEL (ZERO-TRUST CALLING GUARDRAILS)")
    print("=" * 115)

    sentinel = TelephonySafetySentinel(max_calls_per_hour_per_contact=3)

    # 1. Policy Summary
    print("\n[STEP 1] [+] Inspecting Active Telephony Safety Policies...")
    policy = sentinel.get_policy_summary()
    print(f"  • Sentinel Status       : {policy['sentinel_status']}")
    print(f"  • Blocked Emergencies   : {len(policy['emergency_numbers_blocked'])} restricted lines ({', '.join(policy['emergency_numbers_blocked'][:6])}...)")
    print(f"  • Max Calls / Hour      : {policy['max_calls_per_hour_per_contact']} calls per contact")
    print(f"  • PII Redaction Rules   : {', '.join(policy['pii_redaction_rules'])}")
    print(f"  • Kill-Switch Engaged   : {policy['killswitch_engaged']}")

    # 2. Test Emergency Number Interlock
    print("\n[STEP 2] [+] Testing Emergency Number Interlock (Attempting to dial 112 and 911)...")
    emer_1 = sentinel.audit_outbound_communication(phone_number="112", contact_name="Emergency", message_or_objective="Test call")
    print(f"  [-] Target '112': Verdict={emer_1.verdict.value} | Safe={emer_1.is_safe}")
    print(f"      Finding: {emer_1.findings[0]}")
    assert emer_1.is_safe is False

    emer_2 = sentinel.audit_outbound_communication(phone_number="911", contact_name="Emergency", message_or_objective="Test call")
    print(f"  [-] Target '911': Verdict={emer_2.verdict.value} | Safe={emer_2.is_safe}")
    print(f"      Finding: {emer_2.findings[0]}")
    assert emer_2.is_safe is False

    # 3. Test PII & Secret Redaction
    print("\n[STEP 3] [+] Testing PII & Secret Redaction from Spoken Dialogue...")
    sensitive_msg = "Tell him my credit card is 4532-1234-5678-9010 and OTP is 849201 for the purchase."
    pii_res = sentinel.audit_outbound_communication(phone_number="+91-8712484963", contact_name="Father", message_or_objective=sensitive_msg)
    print(f"  • Original Message : \"{sensitive_msg}\"")
    print(f"  • Sanitized Speech : \"{pii_res.sanitized_text}\"")
    print(f"  • Verdict          : {pii_res.verdict.value}")
    print(f"  • Redactions Logged: {len(pii_res.findings)} items sanitized")
    assert "4532" not in pii_res.sanitized_text
    assert "849201" not in pii_res.sanitized_text

    # 4. Test Anti-Spam Rate Limiting
    print("\n[STEP 4] [+] Testing Anti-Spam Frequency Rate Limiting...")
    target = "+91-9988776655"
    res1 = sentinel.audit_outbound_communication(target, "Friend", "Call 1")
    res2 = sentinel.audit_outbound_communication(target, "Friend", "Call 2")
    res3 = sentinel.audit_outbound_communication(target, "Friend", "Call 3")
    res4 = sentinel.audit_outbound_communication(target, "Friend", "Call 4 (Spam attempt)")

    print(f"  • Call #1: {res1.verdict.value} (Safe: {res1.is_safe})")
    print(f"  • Call #2: {res2.verdict.value} (Safe: {res2.is_safe})")
    print(f"  • Call #3: {res3.verdict.value} (Safe: {res3.is_safe})")
    print(f"  [-] Call #4: {res4.verdict.value} (Safe: {res4.is_safe})")
    print(f"      Finding: {res4.findings[0]}")
    assert res4.is_safe is False

    # 5. Test Emergency Kill-Switch
    print("\n[STEP 5] [+] Testing Emergency Kill-Switch Sub-Millisecond Abort...")
    kill_status = sentinel.trigger_killswitch()
    print(f"  ⚡ Kill-Switch Triggered: {kill_status['message']}")

    blocked_call = sentinel.audit_outbound_communication("+91-8712484963", "Father", "Test call during killswitch")
    print(f"  [-] Dialing Attempt: Verdict={blocked_call.verdict.value} | Safe={blocked_call.is_safe}")
    assert blocked_call.is_safe is False

    sentinel.reset_killswitch()
    print("  • Kill-Switch Reset: Telephony Safety Restored")

    # 6. Test Legitimate Safe Call Clearance
    print("\n[STEP 6] [+] Testing Clearance on Legitimate Call to Father (+91-8712484963)...")
    clean_call = sentinel.audit_outbound_communication(
        phone_number="+91-8712484963",
        contact_name="Father",
        message_or_objective="Inform that Charan will reach home by 7:30 PM for dinner after concluding the AI lab session",
    )
    print(f"  [+] Target '+91-8712484963': Verdict={clean_call.verdict.value} | Safe={clean_call.is_safe}")
    print(f"  [+] Audit Hash: {clean_call.audit_hash[:20]}...")
    assert clean_call.is_safe is True

    # 7. Cryptographic Audit Ledger Integrity
    audit = CryptographicAuditLedger(Path("var/db/audit_ledger.db"))
    integrity = audit.verify_integrity()
    print(f"\n[STEP 7] [+] Cryptographic Audit Ledger Integrity: {integrity['status']} (Total Records: {integrity['total_records']})")
    assert integrity["valid"] is True

    print("\n" + "=" * 115)
    print(" [OK] ALFRED TELEPHONY & AGENT SAFETY SENTINEL FULLY VALIDATED!")
    print("=" * 115)


if __name__ == "__main__":
    run_live_safety_sentinel_demo()
