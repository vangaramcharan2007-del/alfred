"""
Live Demonstration & Validation of Jarvis X Phase 5: Self-Evolving Dynamic Tool Forge.
Demonstrates:
1. Adversarial Security Verifier (Blocking malicious imports, eval(), and sandbox escapes).
2. Autonomous Tool Synthesis & AST Verification.
3. Runtime Dynamic Hot-Reloading without server restarts.
4. Live Invocations of newly forged tools (Subnet CIDR calculator, Fibonacci stream, Base64 codec).
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
from jarvisx.toolforge.dynamic_tool_forge import DynamicToolForge
from jarvisx.toolforge.tool_security_verifier import SecurityVerdict, ToolSecurityVerifier


def run_live_tool_forge_demo():
    print("=" * 115)
    print(" [JARVIS X] PHASE 5: SELF-EVOLVING DYNAMIC TOOL FORGE & ADVERSARIAL VERIFIER")
    print("=" * 115)

    verifier = ToolSecurityVerifier()
    forge = DynamicToolForge(verifier=verifier)

    # 1. Adversarial Security Verification (Block malicious tool code)
    print("\n[STEP 1] [+] Testing Adversarial AST Security Scanner against malicious payloads...")
    malicious_code = """
import subprocess
import os

def malicious_backdoor_tool(target_ip: str) -> str:
    \"\"\"Attempts sandbox breakout and shell execution.\"\"\"
    subprocess.run(["cmd.exe", "/c", "dir"], capture_output=True)
    eval("os.system('whoami')")
    return "HACKED"
"""
    bad_report = verifier.verify("malicious_backdoor_tool", malicious_code)
    print(f"  [-] Security Verdict: {bad_report.verdict.value} (Expected: BLOCKED)")
    print(f"  [-] Total Findings  : {len(bad_report.findings)}")
    for f in bad_report.findings:
        print(f"      • [{f.severity}] {f.category}: {f.description}")
    assert bad_report.verdict == SecurityVerdict.BLOCKED

    # 2. Autonomous Tool Synthesis & Hot-Reload (Safe Tools)
    print("\n[STEP 2] [+] Autonomously Synthesizing & Hot-Reloading 3 Safe Dynamic Tools...")

    tools_to_forge = [
        ("subnet_calculator", "Calculates network address, broadcast, and total usable hosts for an IPv4 CIDR block"),
        ("fibonacci_stream", "Generates the first n Fibonacci numbers"),
        ("base64_codec", "Encodes or decodes text to/from standard Base64 representation"),
    ]

    for tool_name, spec in tools_to_forge:
        res = forge.forge_and_register_tool(tool_name, spec)
        print(f"\n  [+] Forged Tool: '{res['tool_name']}'")
        print(f"      • Status     : {res['status']}")
        print(f"      • Description: {res['description']}")
        print(f"      • Latency    : {res['latency_ms']:.1f}ms")
        print(f"      • Audit Hash : {res['audit_hash']}")
        assert res["success"] is True

    # 3. Live Hot-Reloaded Invocations
    print("\n[STEP 3] [+] Executing Newly Forged Tools Live in Active Runtime...")

    # Tool 1: Subnet Calculator
    sub_res = forge.execute_tool("subnet_calculator", cidr="10.0.0.0/22")
    print(f"\n  ⚡ Tool 1 [subnet_calculator]: Input='10.0.0.0/22'")
    print(f"     -> Network: {sub_res['network_address']} | Broadcast: {sub_res['broadcast_address']} | Usable Hosts: {sub_res['usable_hosts']}")
    assert sub_res["usable_hosts"] == 1022

    # Tool 2: Fibonacci Stream
    fib_res = forge.execute_tool("fibonacci_stream", n=10)
    print(f"\n  ⚡ Tool 2 [fibonacci_stream]: Input=n=10")
    print(f"     -> Result: {fib_res}")
    assert fib_res == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

    # Tool 3: Base64 Codec
    b64_enc = forge.execute_tool("base64_codec", text="JarvisX-Sovereign-Core", mode="encode")
    b64_dec = forge.execute_tool("base64_codec", text=b64_enc, mode="decode")
    print(f"\n  ⚡ Tool 3 [base64_codec]: Original='JarvisX-Sovereign-Core'")
    print(f"     -> Encoded: '{b64_enc}'")
    print(f"     -> Decoded: '{b64_dec}'")
    assert b64_dec == "JarvisX-Sovereign-Core"

    # 4. List Active Forged Tools
    print("\n[STEP 4] [+] Active Forged Registry Status:")
    active_tools = forge.list_tools()
    for t in active_tools:
        print(f"  • Tool '{t['name']}': Invocations={t['invocations']} | Active={t['is_active']} | CodeHash={t['code_hash']}")
    assert len(active_tools) >= 3

    # 5. Verify Cryptographic Audit Ledger
    audit = CryptographicAuditLedger(Path("var/db/audit_ledger.db"))
    integrity = audit.verify_integrity()
    print(f"\n[STEP 5] [+] Cryptographic Audit Ledger Integrity: {integrity['status']} (Total Records: {integrity['total_records']})")
    assert integrity["valid"] is True

    print("\n" + "=" * 115)
    print(" [OK] PHASE 5: SELF-EVOLVING DYNAMIC TOOL FORGE FULLY VALIDATED!")
    print("=" * 115)


if __name__ == "__main__":
    run_live_tool_forge_demo()
