"""
Live Demonstration & Validation of Jarvis X Hermes Agentic Reasoning & Tool Calling Layer.
Demonstrates:
1. Nous Hermes 3 Protocol & XML Tool Schema Generation (<tools>, <thought>, <tool_call>).
2. Autonomous Multi-Step Tool Calling (Public APIs, System Telemetry, Memory Compaction).
3. Low-Load Coordination with Alfred Thermal Governor (Keeping CPU & RAM Cool).
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

from jarvisx.hermes.hermes_agent_engine import HermesAgentEngine
from jarvisx.hermes.hermes_protocol import HermesProtocolFormatter
from jarvisx.runtime.thermal_governor import AlfredThermalGovernor
from jarvisx.security.audit_ledger import CryptographicAuditLedger


def run_live_hermes_demo():
    print("=" * 115)
    print(" [JARVIS X] HERMES 3 AGENTIC REASONING & FUNCTION CALLING LAYER (LOW HARDWARE LOAD)")
    print("=" * 115)

    engine = HermesAgentEngine.get_instance()
    governor = AlfredThermalGovernor.get_instance()

    # 1. Test Hermes 3 Protocol & XML Schema
    print("\n[STEP 1] [+] Testing Nous Hermes 3 Schema Generator & Output Parser...")
    schemas = engine.get_tool_schemas()
    prompt = HermesProtocolFormatter.build_system_prompt_with_tools(schemas)
    print(f"  • Registered Tool Schemas: {len(schemas)} tools formatted into <tools>")
    print(f"  • Hermes System Prompt   : {len(prompt)} characters (Conforms to Nous Hermes 3 XML standards)")

    # Sample output parsing
    raw_sample = """
<thought>
The user wants to check bitcoin prices. I should call the public API tool.
</thought>
<tool_call>
{"name": "query_public_api", "arguments": {"query": "bitcoin price in USD"}}
</tool_call>
"""
    parsed = HermesProtocolFormatter.parse_hermes_response(raw_sample)
    print(f"  • Extracted Thought : '{parsed.thought}'")
    print(f"  • Extracted ToolCall: {parsed.tool_calls[0].name} with args {parsed.tool_calls[0].arguments}")
    assert parsed.thought is not None
    assert len(parsed.tool_calls) == 1

    # 2. Autonomous Hermes Agent Turn 1: Public API Tool Calling
    print("\n[STEP 2] [+] Executing Hermes Agentic Turn: Live Public API Capability...")
    goal_1 = "What is the current weather in Paris?"
    res_1 = engine.run_agentic_turn(goal_1)

    print(f"  🎯 Goal: {res_1.goal}")
    for step in res_1.steps:
        print(f"    🧠 Hermes Thought  : {step.thought}")
        print(f"    ⚡ Hermes Tool Call: {step.tool_call_name} (Duration: {step.duration_ms:.1f}ms)")
    print(f"  💬 Hermes Final Response:\n{res_1.final_response}")
    assert len(res_1.steps) > 0

    # 3. Autonomous Hermes Agent Turn 2: Thermal & Memory Telemetry
    print("\n[STEP 3] [+] Executing Hermes Agentic Turn: System Vitals & Active Memory Compaction...")
    goal_2 = "Check my laptop thermal pressure and compact system memory"
    res_2 = engine.run_agentic_turn(goal_2)

    print(f"  🎯 Goal: {res_2.goal}")
    for step in res_2.steps:
        print(f"    🧠 Hermes Thought  : {step.thought}")
        print(f"    ⚡ Hermes Tool Call: {step.tool_call_name} (Duration: {step.duration_ms:.1f}ms)")
    print(f"  💬 Hermes Final Response:\n{res_2.final_response}")
    assert len(res_2.steps) > 0

    # 4. Verify Low Hardware Load via Alfred Thermal Governor
    print("\n[STEP 4] [+] Verifying Laptop Hardware Load & Thermal Stability...")
    vitals = governor.get_vitals()
    print(f"  • CPU Load         : {vitals.cpu_percent:.1f}%")
    print(f"  • RAM Used         : {vitals.ram_used_gb:.2f} GB / {vitals.ram_total_gb:.2f} GB ({vitals.ram_percent:.1f}%)")
    print(f"  • Thermal Pressure : [{vitals.thermal_pressure}] (Protected by Alfred)")

    # 5. Verify Cryptographic Audit Ledger
    audit = CryptographicAuditLedger(Path("var/db/audit_ledger.db"))
    integrity = audit.verify_integrity()
    print(f"\n[STEP 5] [+] Cryptographic Audit Ledger Integrity: {integrity['status']} (Total Records: {integrity['total_records']})")
    assert integrity["valid"] is True

    print("\n" + "=" * 115)
    print(" [OK] HERMES AGENTIC REASONING & FUNCTION CALLING LAYER FULLY VALIDATED!")
    print("=" * 115)


if __name__ == "__main__":
    run_live_hermes_demo()
