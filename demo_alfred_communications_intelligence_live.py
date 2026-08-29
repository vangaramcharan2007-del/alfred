"""
Live Demonstration & Validation of Alfred Communications & Dispatch Intelligence.
Zero hardcoded if-statements: All importance deduction, sorting, texting, and call answering
are performed purely through Neural LLM inference and RAG context.

Demonstrates:
1. Multi-channel Ingestion (Email, WhatsApp, Notification, Phone Call).
2. Semantic Neural Deduction (Categorization, Urgency 1-10, Suggested Action).
3. Executive Spoken Briefing Generation.
4. Outbound Neural Text Message Composition & Dispatch.
5. Autonomous AI Voice Call Answering Script Synthesis.
6. SHA-256 Cryptographic Audit Ledger Proofs.
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

from jarvisx.communications.autonomous_call_and_text_dispatcher import AutonomousCommunicationsAgent
from jarvisx.communications.models import CommunicationChannel, ImportanceCategory, InboundCommunication
from jarvisx.security.audit_ledger import CryptographicAuditLedger


def run_live_communications_demo():
    print("=" * 115)
    print(" [JARVIS X] ALFRED COMMUNICATIONS & DISPATCH INTELLIGENCE (NEURAL DEDUCTION & ZERO IF-STATEMENTS)")
    print("=" * 115)

    agent = AutonomousCommunicationsAgent.get_instance()

    # 1. Multi-Channel Inbound Feed
    print("\n[STEP 1] [+] Ingesting Multi-Channel Communications Feed...")
    inbound_items = [
        InboundCommunication(
            id="msg_001",
            channel=CommunicationChannel.EMAIL,
            sender="advisor@university.edu",
            sender_name="Prof. Harrison",
            subject="URGENT: Production API 500 error on cluster - deadline 6 PM today",
            body="Charan, the master API endpoint on the cluster is returning 500 internal server error. We need the hotfix deployed before the review at 6 PM.",
        ),
        InboundCommunication(
            id="msg_002",
            channel=CommunicationChannel.EMAIL,
            sender="deals@retailmart.com",
            sender_name="RetailMart Offers",
            subject="Exclusive 50% OFF on Summer Apparel & Footwear!",
            body="Don't miss our flash weekend sale. Click here to claim your coupon code now.",
        ),
        InboundCommunication(
            id="msg_003",
            channel=CommunicationChannel.WHATSAPP,
            sender="+91-9876543210",
            sender_name="Aryan (Mesh Teammate)",
            subject="TUF GPU Node Status",
            body="Hey Charan, I joined the ASUS TUF RTX 4060 laptop to your Tailscale mesh with worker_daemon.py. Let me know when you run benchmark!",
        ),
        InboundCommunication(
            id="msg_004",
            channel=CommunicationChannel.SYSTEM_NOTIFICATION,
            sender="Windows Security",
            sender_name="System",
            subject="Security Intelligence Update",
            body="Windows Defender antimalware definitions have been successfully updated to version 1.417.320.0.",
        ),
    ]

    for item in inbound_items:
        print(f"  • [{item.channel.value}] From: '{item.sender_name}' | Subject: '{item.subject[:55]}...'")

    # 2. Neural LLM Deduction & Executive Briefing
    print("\n[STEP 2] [+] Executing Neural LLM Semantic Deductions (Zero Hardcoded If-Statements)...")
    briefing = agent.process_and_brief(inbound_items)

    print(f"\n  📊 Processing Summary:")
    print(f"    - Total Ingested       : {briefing['total_processed']}")
    print(f"    - Critical Actions Req : {briefing['critical_count']}")
    print(f"    - Important FYI Updates: {briefing['fyi_count']}")
    print(f"    - Spam / Noise Filtered: {briefing['spam_filtered_count']}")
    print(f"    - Latency              : {briefing['latency_ms']:.1f}ms")

    print("\n  🧠 Neural Deduction Details:")
    for d in briefing["deductions"]:
        print(f"    - [{d['importance_category']}] Urgency: {d['urgency_score']}/10 | Alert Charan: {d['should_alert_user']}")
        print(f"      Summary: {d['executive_summary']}")
        print(f"      Action : {d['recommended_action']}")
        print(f"      Reason : {d['reasoning_trace'][:90]}...")
        print("-" * 115)

    print(f"\n  🎙️ Alfred Spoken HUD Briefing:\n  \"{briefing['spoken_briefing'].strip()}\"")

    # 3. Outbound Neural Text Message Dispatch
    print("\n[STEP 3] [+] Testing Outbound Neural Text Message Dispatch...")
    out_res = agent.compose_and_send_message(
        recipient="Aryan (Mesh Teammate)",
        channel=CommunicationChannel.WHATSAPP,
        user_intent="Tell Aryan the TUF node is receiving neural tokens smoothly and thank him for setting up the daemon",
    )
    print(f"  • Channel   : {out_res.channel.value} -> {out_res.recipient}")
    print(f"  • Status    : {out_res.status} ({out_res.latency_ms:.1f}ms)")
    print(f"  • Rationale : {out_res.llm_rationale}")
    print(f"  • Message   :\n    \"{out_res.generated_content}\"")
    print(f"  • Audit Hash: {out_res.audit_hash[:20]}...")

    # 4. Autonomous AI Voice Call Answering
    print("\n[STEP 4] [+] Testing Autonomous AI Voice Call Answering...")
    call_res = agent.answer_incoming_call_neural(
        caller_name="Prof. Harrison",
        caller_phone="+1-415-555-0199",
        call_context="Calling regarding the cluster 500 error hotfix patch status before 6 PM",
    )
    print(f"  • Incoming Call From: {call_res.recipient}")
    print(f"  • Status            : {call_res.status} ({call_res.latency_ms:.1f}ms)")
    print(f"  • Strategy          : {call_res.llm_rationale}")
    print(f"  • Spoken Script     :\n    \"{call_res.generated_content}\"")
    print(f"  • Audit Hash        : {call_res.audit_hash[:20]}...")

    # 5. Cryptographic Audit Ledger Integrity
    audit = CryptographicAuditLedger(Path("var/db/audit_ledger.db"))
    integrity = audit.verify_integrity()
    print(f"\n[STEP 5] [+] Cryptographic Audit Ledger Integrity: {integrity['status']} (Total Records: {integrity['total_records']})")
    assert integrity["valid"] is True

    print("\n" + "=" * 115)
    print(" [OK] ALFRED COMMUNICATIONS & DISPATCH INTELLIGENCE FULLY VALIDATED!")
    print("=" * 115)


if __name__ == "__main__":
    run_live_communications_demo()
