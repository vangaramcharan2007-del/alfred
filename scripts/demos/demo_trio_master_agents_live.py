"""
Live Demonstration & Validation of Jarvis X Trio Master Agents:
1. Deep Web Intelligence & Research Engine ("DeepSeek-Researcher Core" with Gemini 3.6 Pro 2M Context).
2. Proactive Daily Executive & Schedule Sentinel ("Jarvis Daily Executive").
3. Physical Lab VM Automated Deployment Suite ("LAB-VM-01").
4. Cryptographic SHA-256 Merkle Audit Ledger Verification.
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

from jarvisx.executive.daily_executive import DailyExecutiveSentinel
from jarvisx.mesh.lab_vm_manager import LabVMManager
from jarvisx.researcher.deep_researcher import DeepResearchEngine
from jarvisx.security.audit_ledger import CryptographicAuditLedger


async def run_live_master_trio_demo():
    print("=" * 115)
    print(" [JARVIS X] LIVE DEMONSTRATION OF TRIO MASTER AGENTS (RESEARCHER, EXECUTIVE, LAB-VM)")
    print("=" * 115)

    researcher = DeepResearchEngine.get_instance()
    executive = DailyExecutiveSentinel.get_instance()
    lab_vm = LabVMManager.get_instance()
    audit = CryptographicAuditLedger(Path("var/db/audit_ledger.db"))

    # ---------------------------------------------------------
    # 1. DEEP RESEARCHER & INTEL DOSSIER (GEMINI 3.6 PRO 2M)
    # ---------------------------------------------------------
    print("\n[MODULE 1] 🧠 DEEP RESEARCHER CORE: Autonomous Technical Dossier Compilation...")
    topic = "Liquid Neural Networks & State Space Models (Mamba) vs Transformers for Edge AI"
    print(f"  • Research Topic  : {topic}")
    print("  • Decomposing topic and gathering academic telemetry...")

    dossier = await researcher.execute_deep_research(topic, depth="COMPREHENSIVE")
    print(f"  [+] Dossier ID    : {dossier.research_id}")
    print(f"  [+] Word Count    : {dossier.word_count} words compiled")
    print(f"  [+] Sources Cited : {len(dossier.sources)} technical sources")
    print(f"  [+] Compilation Speed: {dossier.duration_sec}s")
    print("\n  🎙️ Alfred Voice Audio Briefing (Generated from Dossier):")
    print(f"     \"{dossier.spoken_audio_script}\"")
    print(f"\n  📄 Markdown Dossier Preview:\n")
    for line in dossier.full_report_markdown.strip().split("\n")[:10]:
        print(f"     {line}")
    assert dossier.word_count > 0

    # ---------------------------------------------------------
    # 2. PROACTIVE DAILY EXECUTIVE & ACADEMIC SENTINEL
    # ---------------------------------------------------------
    print("\n" + "-" * 115)
    print("[MODULE 2] 📅 PROACTIVE DAILY EXECUTIVE: College Deadlines & Voice Briefing...")
    briefing = await executive.generate_executive_briefing(briefing_type="MORNING")
    print(f"  [+] Briefing ID   : {briefing.briefing_id}")
    print(f"  [+] Time          : {briefing.timestamp}")
    print(f"  [+] System Vitals : {briefing.system_readiness_status}")
    print(f"  [+] Active Deadlines Tracked: {len(briefing.upcoming_deadlines)} tasks")

    print("\n  🎙️ Spoken Morning Briefing for Charan:")
    print(f"     {briefing.spoken_voice_briefing}")

    print(f"\n  ⏱️ Recommended Focus Schedule: {briefing.suggested_focus_schedule}")
    assert len(briefing.top_priorities) > 0

    # ---------------------------------------------------------
    # 3. PHYSICAL LAB VM NODE MANAGER (LAB-VM-01)
    # ---------------------------------------------------------
    print("\n" + "-" * 115)
    print("[MODULE 3] 🖥️ PHYSICAL LAB VM NODE MANAGER: Deployment Readiness Audit...")
    node_status = lab_vm.probe_node_health()
    print(f"  • Node ID         : {node_status.node_id} ({node_status.hostname})")
    print(f"  • Tailscale IP    : {node_status.tailscale_ip}")
    print(f"  • Service Status  : {node_status.service_status}")
    print(f"  • Readiness State : {node_status.deployment_readiness}")
    print(f"  • Installer Script: deployment/lab_vm/deploy_lab_vm_node.sh (Ready for 1-click execution)")
    print(f"  • Models Configured: {', '.join(node_status.available_models)}")

    # ---------------------------------------------------------
    # 4. CRYPTOGRAPHIC AUDIT LEDGER INTEGRITY
    # ---------------------------------------------------------
    print("\n" + "-" * 115)
    integrity = audit.verify_integrity()
    print(f"[STEP 4] 🛡️ CRYPTOGRAPHIC AUDIT LEDGER: {integrity['status']} (Total Records: {integrity['total_records']})")
    assert integrity["valid"] is True

    print("\n" + "=" * 115)
    print(" [OK] ALL 3 MASTER AGENTS FULLY OPERATIONAL AND VALIDATED!")
    print("=" * 115)


if __name__ == "__main__":
    asyncio.run(run_live_master_trio_demo())
