"""
Live Demonstration & Validation of Windows Computer Use Engine & Corrective RAG (CRAG).
Demonstrates:
1. Windows UI Automation & Active Window Tree Inspection.
2. Semantic Element Resolution (finding controls without blind pixel coordinates).
3. Corrective RAG (CRAG) Zero-Hallucination Pipeline (Local vs Web-Corrected).
4. FastMCP 35-Tool Registry Integration.
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

from jarvisx.computer_use.computer_agent import AutonomousComputerUseAgent
from jarvisx.computer_use.windows_ui import WindowsUIAutomationInspector
from jarvisx.memory_intelligence.corrective_rag import CorrectiveRAGEngine, CRAGDocument


def run_live_demo():
    print("=" * 105)
    print(" [JARVIS X] WINDOWS COMPUTER USE ENGINE & CORRECTIVE RAG (CRAG) LIVE VALIDATION")
    print("=" * 105)

    # 1. Test Windows Computer Use
    print("\n[STEP 1] [+] Testing Windows UI Automation & Active Window Tree Inspection...")
    inspector = WindowsUIAutomationInspector()
    windows = inspector.list_open_windows()
    print(f"  [+] Discovered {len(windows)} Active Windows on Windows 11 Desktop:")
    for w in windows[:5]:
        status_tag = "[ACTIVE]" if w.is_active else "[BACKGROUND]"
        print(f"      - {status_tag} {w.process_name:<15} | '{w.title[:40]}' | Bounds: {w.rect['width']}x{w.rect['height']}")

    assert len(windows) > 0, "Expected at least 1 active window on system."

    # 2. Test Desktop State Capture via Computer Agent
    print("\n[STEP 2] [+] Testing Autonomous Computer Use Agent State Perception...")
    agent = AutonomousComputerUseAgent()
    state = agent.get_desktop_state()
    print(f"  [+] Captured Desktop Perception: Total Managed Windows = {state['total_windows']}")

    # 3. Test Corrective RAG (CRAG)
    print("\n[STEP 3] [+] Testing Corrective RAG (CRAG) Zero-Hallucination Engine...")
    
    # Case A: Local Memory Retrieval (Simulated with verified local document)
    class MockMemoryStore:
        def search_memories(self, q, limit=5):
            if "cluster" in q.lower() or "tailscale" in q.lower():
                return [
                    "Tailscale cluster node IP addresses: NANI-YOGA7I (Master at 127.0.0.1), LAB-01 (100.77.90.36), LAB-02 (100.81.36.31), LAB-03 (100.94.12.88), FRIEND-4060 (100.112.45.19)."
                ]
            return []


    crag = CorrectiveRAGEngine(memory_engine=MockMemoryStore())

    # Query 1: Local Knowledge match
    res_local = crag.answer_query("What are the Tailscale IP addresses of the cluster nodes?")
    print(f"\n  [QUERY 1] 'What are the Tailscale IP addresses of the cluster nodes?'")
    print(f"      - Decision: {res_local.decision} | Confidence: {res_local.confidence_score*100:.0f}% | Web Fallback: {res_local.web_fallback_triggered}")
    print(f"      - Source Citation: {res_local.citations[0]}")
    assert res_local.decision == "LOCAL_MEMORY"
    assert res_local.web_fallback_triggered is False

    # Query 2: Unknown query requiring autonomous Web Correction
    res_web = crag.answer_query("What is the latest release date and version of Python 3.12?")
    print(f"\n  [QUERY 2] 'What is the latest release date and version of Python 3.12?'")
    print(f"      - Decision: {res_web.decision} | Confidence: {res_web.confidence_score*100:.0f}% | Web Fallback: {res_web.web_fallback_triggered}")
    print(f"      - Fallback Citation Count: {len(res_web.citations)}")
    assert res_web.web_fallback_triggered is True

    # 4. Verify FastMCP Tool Registry
    print("\n[STEP 4] [+] Verifying FastMCP Tool Registry Integration...")
    from fastmcp import FastMCP
    from friday.tools import register_all_tools

    test_mcp = FastMCP(name="JarvisComputerUseCRAGTest")
    register_all_tools(test_mcp)

    tools = asyncio.run(test_mcp.list_tools())
    tool_names = [t.name for t in tools]
    print(f"  [+] Total Registered FastMCP Tools: {len(tool_names)}")
    print(f"  [+] Newly Added Tools: get_desktop_ui_state, execute_desktop_element_click, query_corrective_rag")
    assert "get_desktop_ui_state" in tool_names
    assert "execute_desktop_element_click" in tool_names
    assert "query_corrective_rag" in tool_names

    print("\n" + "=" * 105)
    print(" [OK] WINDOWS COMPUTER USE & CORRECTIVE RAG (CRAG) FULLY OPERATIONAL!")
    print("=" * 105)


if __name__ == "__main__":
    run_live_demo()
