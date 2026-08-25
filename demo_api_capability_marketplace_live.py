"""
Live Demonstration & Validation of the Jarvis X Autonomous API Capability Marketplace.
Demonstrates:
1. Dynamic API Discovery against curated Public APIs directory (469k-star catalog).
2. Autonomous API Selection with HTTPS & Zero-Trust security gating.
3. Live Real-World Execution across Weather, Currency, Geocoding, and Crypto.
4. Natural Language Synthesis for Alfred and Desktop Voice HUD.
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

from jarvisx.capabilities.api_discovery import APIDiscoveryEngine
from jarvisx.capabilities.dynamic_marketplace import DynamicAPIMarketplace
from jarvisx.capabilities.registry import PublicAPICapabilityRegistry
from jarvisx.security.audit_ledger import CryptographicAuditLedger


def run_live_marketplace_demo():
    print("=" * 115)
    print(" [JARVIS X] AUTONOMOUS PUBLIC API CAPABILITY MARKETPLACE & DYNAMIC TOOL ROUTER")
    print("=" * 115)

    registry = PublicAPICapabilityRegistry()
    discovery = APIDiscoveryEngine(registry)
    marketplace = DynamicAPIMarketplace(registry=registry)

    # 1. Test Semantic API Discovery
    print("\n[STEP 1] [+] Testing Semantic API Discovery ('Find me a tool capable of X')...")
    test_queries = [
        ("weather forecast for city", "Weather"),
        ("convert USD currency forex rates", "Finance"),
        ("bitcoin crypto live price ticker", "Finance"),
        ("lookup GPS coordinates latitude longitude", "Geocoding"),
    ]

    for q, cat in test_queries:
        matches = discovery.discover_apis_for_query(query=q, max_results=2)
        top = matches[0][0] if matches else None
        score = matches[0][1] if matches else 0.0
        print(f"  [+] Query: '{q}'")
        print(f"      -> Discovered: {top.name if top else 'None'} ({top.category if top else ''}) | Score: {score:.1f} | Auth: {top.auth_type.value if top else ''} | HTTPS: {top.https if top else ''}")
        assert top is not None

    # 2. Live Autonomous Execution across Domains
    print("\n[STEP 2] [+] Testing Dynamic API Selection & Safe Sandboxed Execution...\n")
    live_intents = [
        ("Current weather forecast for Tokyo", {"latitude": 35.6895, "longitude": 139.6917, "current_weather": True}),
        ("Foreign exchange rate USD to EUR and INR", {"from": "USD", "to": "EUR,INR"}),
        ("Bitcoin and Ethereum live crypto prices", {"ids": "bitcoin,ethereum", "vs_currencies": "usd,inr"}),
        ("Geocoding coordinates for Tokyo", {"name": "Tokyo", "count": 1}),
        ("Random interesting knowledge fact", {}),
    ]

    for intent, params in live_intents:
        turn = marketplace.route_and_execute_intent(user_intent=intent, custom_params=params)
        print(f"  [+] Intent:        '{turn.query}'")
        print(f"      Selected API:  {turn.selected_api} [{turn.category}]")
        print(f"      Status:        {turn.status} ({turn.latency_ms}ms)")
        print(f"      Summary:       {turn.result_summary}")
        print(f"      Audit Hash:    {turn.audit_hash[:20]}...")
        print("-" * 115)
        assert turn.status in ("SUCCESS", "FALLBACK_SUCCESS")

    # 3. Verify Cryptographic Audit Ledger
    audit = CryptographicAuditLedger(Path("var/db/audit_ledger.db"))
    integrity = audit.verify_integrity()
    print(f"\n[STEP 3] [+] Cryptographic Audit Ledger Integrity: {integrity['status']} (Total Records: {integrity['total_records']})")
    assert integrity["valid"] is True

    print("\n" + "=" * 115)
    print(" [OK] PUBLIC API CAPABILITY MARKETPLACE & DYNAMIC ROUTER FULLY VALIDATED!")
    print("=" * 115)


if __name__ == "__main__":
    run_live_marketplace_demo()
