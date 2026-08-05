"""Unit and verification tests for Phase 53: Autonomous Skill & Tool Synthesis.

Verifies workflow distillation into SKILL.md packages, capability registration,
quantified HSPW savings (> +5.0 HSPW across standard batch runs), and Layer 3/4 compliance.
"""

import pytest
from jarvisx.automation.skill_synthesis import SkillSynthesisEngine
from jarvisx.agents.synthesizer import SynthesizerAgent
from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.architecture import get_layer_for_module


def test_skill_synthesis_engine_distill_and_register():
    """Verify zero-fluff SkillSynthesisEngine generates valid YAML frontmatter and capability descriptors."""
    engine = SkillSynthesisEngine()

    # 1. Distill workflow into SKILL.md package
    res = engine.distill_workflow(
        name="Database Snapshot Backup",
        description="Automates PostgreSQL volume export and GCS encryption upload",
        steps=["Dump pg_catalog", "GZIP encrypt binary", "Verify upload MD5"],
    )
    assert res["status"] == "success"
    assert "name: database-snapshot-backup" in res["skill"]["skill_content"]
    assert "## Execution Protocol" in res["skill"]["skill_content"]

    # 2. Register runtime capability descriptor
    reg_res = engine.register_synthesized_capability("database-snapshot-backup", handler_action="execute_snapshot")
    assert reg_res["status"] == "registered"
    assert reg_res["descriptor"]["capability_id"] == "custom.database-snapshot-backup"

    cat = engine.get_catalog_summary()
    assert cat["total_skills"] == 1
    assert cat["total_capabilities"] == 1


def test_synthesizer_agent_and_personal_os_routing(monkeypatch):
    """Verify SynthesizerAgent executes missions and accumulates +5.0+ HSPW within Alfred Personal OS."""
    os_kernel = PersonalOSKernel()
    monkeypatch.setattr(os_kernel.guardian_agent.guardian.git_watcher, "check_git_status", lambda cwd: {"status": "CLEAN", "uncommitted_count": 0})

    # Execute 2 autonomous skill synthesis objectives via Personal OS interface
    os_kernel.execute_objective("Synthesize skill for Automated Log Truncation", name="Log Truncation", description="Rotates giant logs", steps=["Scan /var/log", "Compress archives"])
    os_kernel.execute_objective("Distill workflow skill for API Benchmark Smoke Testing", name="API Benchmarker", description="Runs latency profiling", steps=["Send concurrent requests", "Parse P99 latency"])

    # Verify agent accumulated HSPW time savings (2 * 2.5 HSPW = 5.0 HSPW!)
    synth_worker = os_kernel.synthesizer_agent
    assert synth_worker.metrics()["hours_saved"] >= 5.0

    # Verify Master Dashboard reports Skill Synthesis status cleanly
    dashboard = os_kernel.get_master_dashboard()
    assert "[AUTONOMOUS SKILL SYNTHESIS]" in dashboard["output"]
    assert "Synthesized Skills: 2 packages" in dashboard["output"]
    assert "Runtime Capabilities: 2 descriptors" in dashboard["output"]


def test_architecture_layer_compliance_for_synthesis():
    """Verify SkillSynthesisEngine and SynthesizerAgent align strictly to established architectural boundaries."""
    assert get_layer_for_module("jarvisx.automation.skill_synthesis") == "agents"
    assert get_layer_for_module("jarvisx.agents.synthesizer") == "agents"
