"""
Live Demonstration & Validation of:
1. Autonomous Morning Wake-Up & Telegram Executive Routine.
2. End-to-End Golden Master System Audit Across All 18 Subsystems.
3. Cryptographic SHA-256 Merkle Audit Ledger Integrity.
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

from jarvisx.cron.morning_routine import MorningWakeUpRoutine
from jarvisx.security.audit_ledger import CryptographicAuditLedger
from jarvisx.system.golden_master_audit import GoldenMasterAuditor


async def run_live_golden_suite_demo():
    print("=" * 115)
    print(" [JARVIS X] LIVE DEMONSTRATION OF MORNING ROUTINE & GOLDEN MASTER SYSTEM AUDIT (18 SUBSYSTEMS)")
    print("=" * 115)

    morning_agent = MorningWakeUpRoutine.get_instance()
    golden_auditor = GoldenMasterAuditor.get_instance()
    audit = CryptographicAuditLedger(Path("var/db/audit_ledger.db"))

    # ---------------------------------------------------------
    # 1. AUTONOMOUS MORNING WAKE-UP & TELEGRAM DISPATCH
    # ---------------------------------------------------------
    print("\n[STEP 1] ☀️ EXECUTING AUTONOMOUS MORNING WAKE-UP ROUTINE...")
    morning_res = await morning_agent.execute_morning_routine()

    print(f"  [+] Routine ID          : {morning_res.routine_id}")
    print(f"  [+] Wake-Up Timestamp   : {morning_res.wake_time}")
    print(f"  [+] Vocal Audio Spoken  : {morning_res.audio_spoken} (Speaker Out)")
    print(f"  [+] Telegram Dispatched : {morning_res.telegram_dispatched} (Zero-Trust Mobile Bot)")
    print(f"  [+] Execution Duration  : {morning_res.duration_sec}s")

    print("\n  📱 Mobile Telegram Message Dispatch Preview:\n")
    for line in morning_res.telegram_message_preview.strip().split("\n")[:14]:
        print(f"     {line}")
    assert morning_res.telegram_dispatched is True

    # ---------------------------------------------------------
    # 2. FULL-SPECTRUM GOLDEN MASTER SYSTEM AUDIT (18 SUBSYSTEMS)
    # ---------------------------------------------------------
    print("\n" + "=" * 115)
    print("[STEP 2] 🏛️ EXECUTING FULL-SPECTRUM GOLDEN MASTER AUDIT ACROSS ALL 18 SUBSYSTEMS...")
    print("=" * 115)

    cert = await golden_auditor.run_full_golden_audit()

    print(f"\n  📋 GOLDEN MASTER CERTIFICATE: {cert.audit_id}")
    print(f"    • Certification Status : 🎖️ {cert.certification_status}")
    print(f"    • Total Subsystems     : {cert.total_subsystems_audited} Audited")
    print(f"    • Passed Subsystems    : {cert.passed_subsystems} / {cert.total_subsystems_audited} (100% Operational)")
    print(f"    • Audit Ledger Blocks  : {cert.audit_ledger_blocks} Verified Blocks")
    print(f"    • Master Certificate Hash: {cert.audit_hash[:24]}...")

    print("\n  📊 Subsystem Diagnostic Results Breakdown:")
    print("  " + "-" * 110)
    print(f"  {'#':<3} | {'Subsystem Pillar':<58} | {'Category':<22} | {'Status'}")
    print("  " + "-" * 110)

    for r in cert.subsystem_results:
        print(f"  {r.pillar_id:<3} | {r.name:<58} | {r.category:<22} | {r.status}")

    print("  " + "-" * 110)
    assert cert.passed_subsystems == 18
    assert cert.certification_status == "GOLDEN_MASTER_CERTIFIED"

    # ---------------------------------------------------------
    # 3. CRYPTOGRAPHIC AUDIT LEDGER INTEGRITY
    # ---------------------------------------------------------
    print("\n[STEP 3] 🛡️ CRYPTOGRAPHIC AUDIT LEDGER VERIFICATION...")
    integrity = audit.verify_integrity()
    print(f"  [+] Audit Ledger Status: {integrity['status']} (Total Blocks: {integrity['total_records']})")
    assert integrity["valid"] is True

    print("\n" + "=" * 115)
    print(" [OK] GOLDEN MASTER AUDIT COMPLETE — JARVIS X & ALFRED CERTIFIED GOLDEN RELEASE!")
    print("=" * 115)


if __name__ == "__main__":
    asyncio.run(run_live_golden_suite_demo())
