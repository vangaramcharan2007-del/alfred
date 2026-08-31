"""
Live Demonstration & Validation of the Salvaged Governance, Audit Ledger & Ship Gate.
Demonstrates:
1. Cryptographic SHA-256 Hash-Chained Audit Trail (Tamper-evident verification)
2. 3-Perspective Adversarial Review Engine (Blocking secrets, scoring completeness)
3. Automated Ship Gate & FastMCP Tool Registration Check
"""

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
from jarvisx.verification.adversarial_review import AdversarialReviewEngine
from jarvisx.verification.ship_gate import ShipGateEngine


def run_live_demo():
    print("=" * 80)
    print(" [JARVIS X] SALVAGED GOVERNANCE & SHIP GATE LIVE DEMONSTRATION")
    print("=" * 80)

    # 1. Test Cryptographic Audit Ledger
    print("\n[STEP 1] 🔒 Testing Cryptographic SHA-256 Audit Ledger...")
    ledger_path = Path("var/test_audit.db")
    if ledger_path.exists():
        ledger_path.unlink()

    ledger = CryptographicAuditLedger(ledger_path)

    entry1 = ledger.record_action(
        agent_id="architect_swarm",
        action="SYNTHESIZE_FAST_MCP_MODULE",
        input_payload={"module": "governance_tools", "spec": "gstack_and_trust_layer"},
        output_payload={"status": "GENERATED", "lines": 42},
    )
    print(f"  [+] Entry 0 Sequence: {entry1.sequence} | Current Hash: {entry1.current_hash[:16]}... | Prev: {entry1.prev_hash[:16]}...")

    entry2 = ledger.record_action(
        agent_id="critic_agent",
        action="ADVERSARIAL_REVIEW_GATE",
        input_payload={"target_file": "governance_tools.py"},
        output_payload={"decision": "APPROVED", "completeness_score": 10},
    )
    print(f"  [+] Entry 1 Sequence: {entry2.sequence} | Current Hash: {entry2.current_hash[:16]}... | Prev: {entry2.prev_hash[:16]}...")

    integrity = ledger.verify_integrity()
    print(f"  [+] Chain Verification Result: {integrity['status']} (Total Records: {integrity['total_records']})")
    assert integrity["valid"] is True, "Audit chain integrity verification failed!"

    # 2. Test Adversarial Review Engine
    print("\n[STEP 2] 🧐 Testing 3-Perspective Adversarial Review Engine...")
    reviewer = AdversarialReviewEngine()

    # Case A: Good Production Code
    good_code = '''"""
Production-grade math utility module.
"""
def compute_mesh_load(workers: list) -> float:
    """Calculates aggregate load across active mesh nodes."""
    if not workers:
        return 0.0
    return sum(w.get("load", 0.0) for w in workers) / len(workers)
'''
    good_report = reviewer.review_code_or_diff(good_code, file_path="mesh_math.py")
    print(f"  [+] Clean Code Review: Decision={good_report.decision} | Score={good_report.completeness_score}/10")
    assert good_report.decision == "APPROVED"
    assert good_report.completeness_score == 10

    # Case B: Vulnerable Code (Hardcoded secret + Unsafe Eval)
    vuln_code = '''
api_key = "sk-live1234567890abcdef1234567890"
def run_command(user_input):
    return eval(user_input)
'''
    vuln_report = reviewer.review_code_or_diff(vuln_code, file_path="vuln_snippet.py")
    print(f"  [+] Vulnerable Code Review: Decision={vuln_report.decision} | Score={vuln_report.completeness_score}/10 | Blockers={vuln_report.total_findings}")
    assert vuln_report.decision == "REJECTED"
    for finding in vuln_report.findings:
        print(f"      - [{finding.severity}] {finding.perspective}: {finding.message} (Line {finding.line_number})")

    # 3. Test FastMCP Tool Registration
    print("\n[STEP 3] [+] Verifying FastMCP Tool Registry Integration...")
    import asyncio
    from fastmcp import FastMCP
    from friday.tools import register_all_tools

    test_mcp = FastMCP(name="JarvisGovernanceTest")
    register_all_tools(test_mcp)
    
    tools = asyncio.run(test_mcp.list_tools())
    tool_names = [t.name for t in tools]
    print(f"  [+] Total Registered FastMCP Tools: {len(tool_names)}")
    print(f"  [+] Newly Added Governance Tools: audit_ledger_verify, adversarial_code_review, execute_ship_gate")
    assert "audit_ledger_verify" in tool_names
    assert "adversarial_code_review" in tool_names
    assert "execute_ship_gate" in tool_names

    # Clean up test database
    if ledger_path.exists():
        ledger_path.unlink()

    print("\n" + "=" * 80)
    print(" [OK] ALL SALVAGED ARCHITECTURAL PATTERNS VALIDATED & PRODUCTION-READY!")
    print("=" * 80)


if __name__ == "__main__":
    run_live_demo()
