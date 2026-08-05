"""Unit and verification tests for Phase 54: Proactive Research & Document Curation.

Verifies automated literature surveys, markdown wiki synchronization,
quantified HSPW savings (> +4.0 HSPW across standard batch runs), and Layer 3/4 compliance.
"""

import pytest
from jarvisx.automation.research_curation import ProactiveCurationEngine
from jarvisx.agents.research import ResearchAgent
from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.architecture import get_layer_for_module


def test_proactive_curation_engine():
    """Verify zero-fluff ProactiveCurationEngine conducts literature sweeps and synchronizes wikis."""
    engine = ProactiveCurationEngine()

    # 1. Conduct Literature Sweep
    sweep_res = engine.conduct_literature_sweep(topic="Neural Attention Kernels", sources=["IEEE Xplore", "ArXiv"])
    assert sweep_res["status"] == "success"
    assert "Executive Research Digest: Neural Attention Kernels" in sweep_res["digest"]["digest_content"]

    # 2. Curate Documentation Wiki
    doc_res = engine.curate_documentation(target_dir="docs", doc_name="kernel_specs.md", updates=["Added tensor pipeline shapes"])
    assert doc_res["status"] == "curated"
    assert "Curation Update: docs/kernel_specs.md" in doc_res["document"]["doc_content"]

    summary = engine.get_curation_summary()
    assert summary["total_digests"] == 1
    assert summary["total_curated_docs"] == 1


def test_research_agent_curation_and_os_routing(monkeypatch):
    """Verify upgraded ResearchAgent executes curation objectives and accumulates +4.0+ HSPW."""
    os_kernel = PersonalOSKernel()
    monkeypatch.setattr(os_kernel.guardian_agent.guardian.git_watcher, "check_git_status", lambda cwd: {"status": "CLEAN", "uncommitted_count": 0})

    # Execute 3 proactive research & curation objectives via Personal OS command interface
    os_kernel.execute_objective("Conduct literature survey on Autonomous Memory Architectures", topic="Memory Architectures", action="sweep")
    os_kernel.execute_objective("Curate documentation for system architecture wiki", target_dir="docs", doc_name="architecture.md", action="curate")
    os_kernel.execute_objective("Conduct literature sweep on Graph Rag Vector Indexing", topic="Graph RAG", action="sweep")

    # Verify ResearchAgent accumulated HSPW time savings (3 * 1.5 HSPW = 4.5 HSPW!)
    research_worker = os_kernel.research_agent
    assert research_worker.metrics()["hours_saved"] >= 4.5

    # Verify Master Dashboard reports Research Curation telemetry cleanly
    dashboard = os_kernel.get_master_dashboard()
    assert "[PROACTIVE RESEARCH & DOC CURATION]" in dashboard["output"]
    assert "Literature Sweeps: 2 executive digests synthesized" in dashboard["output"]
    assert "Curated Reference Docs: 1 wikis synchronized" in dashboard["output"]


def test_architecture_layer_compliance_for_curation():
    """Verify ProactiveCurationEngine aligns strictly to established architectural layer boundaries."""
    assert get_layer_for_module("jarvisx.automation.research_curation") == "agents"
