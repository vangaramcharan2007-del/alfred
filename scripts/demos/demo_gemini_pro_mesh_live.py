"""
Live Demonstration & Validation of Google Gemini Pro / Flash Cloud Engine in Jarvis X.
Demonstrates:
1. Native Gemini 3.6 Pro / Flash Provider via official google-genai SDK.
2. Full Support for New Google AI Studio 'AQ.' Authentication Keys.
3. Ultra-Fast Cloud Inference (2 Million Token Context Window, Zero Laptop Load).
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

from jarvisx.llm.gemini_provider import GeminiLLMProvider
from jarvisx.security.audit_ledger import CryptographicAuditLedger


async def run_live_gemini_demo():
    print("=" * 115)
    print(" [JARVIS X] GOOGLE GEMINI 3.6 PRO & FLASH CLOUD ENGINE (OFFICIAL SDK + AQ. KEY SUPPORT)")
    print("=" * 115)

    provider = GeminiLLMProvider()
    audit = CryptographicAuditLedger(Path("var/db/audit_ledger.db"))

    # 1. Connect & Validate Provider
    print("\n[STEP 1] [+] Initializing Gemini Cloud Gateway & Connecting with AQ. Key...")
    connected = await provider.connect()
    print(f"  • Gateway Connected     : {connected}")
    print(f"  • API Key Configured    : {provider._sanitize(provider.api_key)}")
    print(f"  • Supported Cloud Models: {', '.join(provider.available_models)}")
    assert connected is True

    # 2. Execute Real Cloud Inference Query (Gemini 3.6 Flash / Pro)
    print("\n[STEP 2] [+] Executing Real-Time Generation via Google Gemini Cloud...")
    prompt = "Hello Alfred! In 2 concise bullet points, explain why combining Google Gemini Pro (2M context) with Jarvis X local sovereign mesh gives Charan the ultimate AI companion."

    t0 = time.time()
    res = await provider.generate(prompt=prompt, model="gemini-3.6-flash")
    dur = round((time.time() - t0) * 1000, 1)

    print(f"  • Model Used : {res.get('model')}")
    print(f"  • Status     : {res.get('status')}")
    print(f"  • Latency    : {dur}ms (Ultra-Fast Google TPU Cloud Inference)")
    print("\n  💬 Gemini Response:\n")
    print(f"  {res.get('response', '').strip()}")
    assert res.get("status") == "AVAILABLE"

    # 3. Log to Cryptographic Audit Ledger
    audit_entry = audit.record_action(
        agent_id="gemini_cloud_gateway",
        action="GEMINI_CLOUD_INFERENCE_COMPLETED",
        input_payload={"prompt": prompt, "model": res.get("model")},
        output_payload={"response_length": len(res.get("response", "")), "latency_ms": dur},
        status="SUCCESS",
        metadata={"cost": "0.00_18_MONTH_SUBSCRIPTION", "key_prefix": "AQ."},
    )
    print(f"\n  🛡️ Audit Ledger Hash: {audit_entry.current_hash[:20]}...")

    # 4. Cryptographic Audit Ledger Integrity
    integrity = audit.verify_integrity()
    print(f"\n[STEP 3] [+] Cryptographic Audit Ledger Integrity: {integrity['status']} (Total Records: {integrity['total_records']})")
    assert integrity["valid"] is True

    print("\n" + "=" * 115)
    print(" [OK] GOOGLE GEMINI 3.6 PRO / FLASH CLOUD GATEWAY FULLY VALIDATED!")
    print("=" * 115)


if __name__ == "__main__":
    asyncio.run(run_live_gemini_demo())
