"""
Live Demonstration & Validation of Jarvis X Phase 4: Mobile Sentinel Bridge & Telegram Gateway.
Demonstrates:
1. Zero-Trust Security Gate (Allowlisted Authorized Users vs Blocked Unauthorized Access).
2. Remote Mobile Commands (/vitals, /mesh, /code).
3. Dynamic Public API & Mesh Routing over Mobile Telegram Bridge.
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

from jarvisx.remote.mobile_gateway import MobileRemoteGateway
from jarvisx.remote.telegram_sentinel_bridge import MobileMessageRequest, TelegramSentinelBridge
from jarvisx.security.audit_ledger import CryptographicAuditLedger


def run_live_mobile_sentinel_demo():
    print("=" * 115)
    print(" [JARVIS X] PHASE 4: MOBILE SENTINEL BRIDGE & TELEGRAM ENCRYPTED GATEWAY")
    print("=" * 115)

    bridge = TelegramSentinelBridge(authorized_user_ids=["charan_master", "vangaramcharan"])

    # 1. Test Zero-Trust Security Gate (Unauthorized vs Authorized)
    print("\n[STEP 1] [+] Testing Zero-Trust Security Allowlist Gate...")
    unauth_req = MobileMessageRequest(
        user_id="unauthorized_hacker",
        user_name="Unknown Phone",
        text="/vitals",
        timestamp=time.time(),
    )
    unauth_resp = bridge.process_mobile_message(unauth_req)
    print(f"  [-] Unauthorized User Request: Status={unauth_resp.status} | Action={unauth_resp.action_type}")
    print(f"      Reply: {unauth_resp.formatted_reply}")
    assert unauth_resp.status == "FORBIDDEN"

    auth_req = MobileMessageRequest(
        user_id="charan_master",
        user_name="Charan",
        text="/vitals",
        timestamp=time.time(),
    )
    auth_resp = bridge.process_mobile_message(auth_req)
    print(f"\n  [+] Authorized User Request: Status={auth_resp.status} | Action={auth_resp.action_type}")
    print(f"      Reply:\n{auth_resp.formatted_reply}")
    assert auth_resp.status == "SUCCESS"

    # 2. Test Mobile Mesh Diagnostic Command
    print("\n[STEP 2] [+] Testing Mobile /mesh Cluster Diagnostic Command...")
    mesh_req = MobileMessageRequest(
        user_id="charan_master",
        user_name="Charan",
        text="/mesh",
        timestamp=time.time(),
    )
    mesh_resp = bridge.process_mobile_message(mesh_req)
    print(f"  [+] Status: {mesh_resp.status} ({mesh_resp.latency_ms:.1f}ms)")
    print(f"      Mobile Telegram View:\n{mesh_resp.formatted_reply}")
    assert mesh_resp.status == "SUCCESS"

    # 3. Test Mobile Dynamic Public API Dispatch
    print("\n[STEP 3] [+] Testing Mobile Dynamic Public API Dispatch ('What is the weather in Tokyo?')...")
    api_req = MobileMessageRequest(
        user_id="charan_master",
        user_name="Charan",
        text="What is the current weather in Tokyo?",
        timestamp=time.time(),
    )
    api_resp = bridge.process_mobile_message(api_req)
    print(f"  [+] Status: {api_resp.status} ({api_resp.latency_ms:.1f}ms)")
    print(f"      Mobile Telegram View:\n{api_resp.formatted_reply}")
    assert api_resp.status == "SUCCESS"

    # 4. Test Mobile Remote Code Generation Dispatch
    print("\n[STEP 4] [+] Testing Mobile Remote /code Command Dispatch...")
    code_req = MobileMessageRequest(
        user_id="charan_master",
        user_name="Charan",
        text="/code Write SQL table schema for Student course enrollment",
        timestamp=time.time(),
    )
    code_resp = bridge.process_mobile_message(code_req)
    print(f"  [+] Status: {code_resp.status} ({code_resp.latency_ms:.1f}ms)")
    print(f"      Mobile Telegram View:\n{code_resp.formatted_reply[:350]}...")
    assert code_resp.status == "SUCCESS"

    # 5. Verify Cryptographic Audit Ledger
    audit = CryptographicAuditLedger(Path("var/db/audit_ledger.db"))
    integrity = audit.verify_integrity()
    print(f"\n[STEP 5] [+] Cryptographic Audit Ledger Integrity: {integrity['status']} (Total Records: {integrity['total_records']})")
    assert integrity["valid"] is True

    print("\n" + "=" * 115)
    print(" [OK] PHASE 4: MOBILE SENTINEL BRIDGE & TELEGRAM GATEWAY FULLY VALIDATED!")
    print("=" * 115)


if __name__ == "__main__":
    run_live_mobile_sentinel_demo()
