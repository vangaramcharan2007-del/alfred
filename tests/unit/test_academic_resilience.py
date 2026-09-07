"""Unit Tests for Academic Resilience and 5 Real-World Failure Mode Fixes."""

import os
import time
import pytest

from jarvisx.academic.models import AcademicTask, ChannelSource, StudentProfile, TaskPriority, TaskType
from jarvisx.academic.session_vault import SessionVault
from jarvisx.academic.resilient_scraper import ResilientScraper
from jarvisx.academic.multimodal_anchor import MultiModalAnchor
from jarvisx.academic.stylometry_engine import StylometryEngine
from jarvisx.academic.resilience_controller import ResilienceController
from jarvisx.academic.sentinel_daemon import AcademicSentinelDaemon


def test_session_vault_decay_and_heal():
    """Fix 1: Test token expiration detection and automatic multi-tier healing."""
    vault = SessionVault(vault_path="var/db/test_sessions.json")
    
    # Check valid session
    sess = vault.get_session("ecurricula")
    assert "token" in sess
    assert sess["status"] == "VALID"
    
    # Simulate decay by pushing expiration into the past
    vault._sessions["ecurricula"]["expires_epoch"] = time.time() - 100
    assert vault.is_session_expired("ecurricula") is True
    
    # Trigger heal
    healed = vault.heal_session("ecurricula")
    assert healed is True
    updated_sess = vault.get_session("ecurricula")
    assert updated_sess["status"] == "VALID"
    assert "live_harvest" in str(updated_sess.get("cookies", {}))


def test_resilient_scraper_route_drift():
    """Fix 2: Test self-healing endpoint route cache and semantic DOM fallback."""
    scraper = ResilientScraper(routes_cache_path="var/db/test_routes.json")
    
    # Test primary endpoint discovery
    res1 = scraper.scrape_assignment_data("ecurricula", "https://academia.srmist.edu.in/curricula/student/session/getsessionstatus")
    assert res1["status"] in ("HEALTHY", "HEALED")
    assert res1["data"]["active_assignments"] == 4
    
    # Test DOM fallback on HTML content
    dummy_html = """
    <html>
      <body>
        <h2>Unit 4 Worksheet - Dynamic Memory Allocation</h2>
        <button class="fui-btn_99x">Turn In Assignment</button>
      </body>
    </html>
    """
    res2 = scraper.scrape_assignment_data("teams", "https://invalid.route.com", html_content=dummy_html)
    assert res2["strategy_used"] in ("self_healed_route", "semantic_dom", "canonical_api")


def test_multimodal_anchor_textbook_citation():
    """Fix 3: Test resolving cryptic textbook / syllabus citations to prevent hallucination."""
    anchor = MultiModalAnchor(reference_dir="var/reference")
    
    # 1. Tanenbaum reference resolution
    query1 = "Please do exercise from Tanenbaum 4th ed pg 182 by tomorrow evening"
    res1 = anchor.resolve_cryptic_citation(query1)
    assert res1 is not None
    assert res1["resolved"] is True
    assert "Banker's Algorithm" in res1["verified_problem"]
    assert res1["page"] == "182"
    
    # 2. SRM STEP Java syllabus resolution
    query2 = "Submit your STEP Java Module 4 banking solution to the portal"
    res2 = anchor.resolve_cryptic_citation(query2)
    assert res2 is not None
    assert "BankAccount" in res2["verified_problem"]
    assert "BankManager" in res2["verified_problem"]
    
    # 3. Image preprocessing readiness score
    img_res = anchor.enhance_image_for_ocr("test_chalkboard.jpg")
    assert img_res["preprocessed"] is True
    assert img_res["ocr_readiness_score"] >= 0.90


def test_stylometry_engine_java_and_text():
    """Fix 4: Test AST identifier morphing, student comment injection, and AI phrase removal."""
    engine = StylometryEngine(student_name="RAM CHARAN VANGA", reg_no="RA2511027010164")
    
    # Java Code Transformation
    sample_code = """
    public class BankManager {
        private BankAccount account;
        private double balance;
        public synchronized void deposit(double amount) {
            balance += amount;
        }
    }
    """
    diversified = engine.diversify_java_code(sample_code, "BankManager.java")
    assert "RAM CHARAN VANGA" in diversified
    assert "RA2511027010164" in diversified
    assert "accObj" in diversified
    assert "currBal" in diversified
    assert "// ensure positive deposit" in diversified
    
    # Text Humanization (Eliminate AI phrasing)
    ai_text = "Furthermore, in conclusion, it is important to note that the algorithm terminates."
    humanized = engine.humanize_report_text(ai_text)
    assert "Furthermore" not in humanized
    assert "In conclusion" not in humanized
    assert "Submitted by: RAM CHARAN VANGA" in humanized


def test_resilience_controller_backoff_and_staging():
    """Fix 5: Test exponential backoff, header rotation, and two-phase safe staging."""
    ctrl = ResilienceController()
    
    # Exponential backoff calculation
    bo1 = ctrl.calculate_backoff(attempt=1)
    bo3 = ctrl.calculate_backoff(attempt=3)
    assert 0.5 <= bo1 <= 10.0
    assert bo3 >= 0.5
    
    # Header rotation
    headers = ctrl.get_browser_headers("ecurricula")
    assert "User-Agent" in headers
    assert "Sec-Ch-Ua" in headers
    
    # Staging & Rubric Checksum
    task = AcademicTask(
        task_id="TEST-STAGE-001",
        channel=ChannelSource.ECURRICULA,
        course_code="21CSC201J",
        course_name="Data Structures",
        title="Unit 4 Session 401",
        description="Solve circular queue implementation",
        deadline_epoch=time.time() + 7200,  # 2 hours away
        priority=TaskPriority.NORMAL,
        task_type=TaskType.WORKSHEET,
    )
    ok, checksum = ctrl.stage_for_submission(task)
    assert ok is True
    assert len(checksum) == 64
    
    # Test Race Condition detection (mid-cycle rubric modification)
    task.description = "MODIFIED RUBRIC: Solve doubly linked list instead"
    can_submit, msg = ctrl.can_safely_submit(task)
    assert can_submit is False
    assert "RACE HAZARD" in msg


def test_full_resilient_sentinel_cycle():
    """Verify complete sentinel daemon cycle with all 5 resilience systems active."""
    daemon = AcademicSentinelDaemon(
        db_path="var/db/test_resilience_sentinel.db",
        enable_voice=False,
        enable_toast=False
    )
    summary = daemon.execute_cycle()
    assert summary["tasks_ingested"] >= 0
    assert "resilience_telemetry" in summary
    tel = summary["resilience_telemetry"]
    assert tel["active_sessions"] >= 4
    assert tel["cached_routes"] >= 3
    assert tel["stylometry_active"] is True
    assert tel["two_phase_staging"] is True
    assert tel["next_sweep_delay_s"] > 0
