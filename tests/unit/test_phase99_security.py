"""Unit and Adversarial Security Tests for Phase 99: Security & Trust Layer."""

import pytest
import sqlite3
import time
from pathlib import Path
from jarvisx.security.models import (
    PermissionScope,
    RiskBreakdown,
    RiskLevel,
)
from jarvisx.security.security_memory import SecurityMemory
from jarvisx.security.secret_vault import SecretVault
from jarvisx.security.audit_log import AuditLogger
from jarvisx.security.sandbox_guardrails import SandboxGuardrails
from jarvisx.security.permission_enforcer import PermissionEnforcer
from jarvisx.security.trust_engine import TrustEngine


def test_security_memory_persistence_and_schema_version():
    db_file = "var/test_sec/test_mem.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = SecurityMemory(db_file)
    mem.save_permission("p1", "Coder", "write", "project_only", time.time() + 3600)

    new_mem = SecurityMemory(db_file)
    perms = new_mem.list_permissions()
    assert len(perms) == 1
    assert perms[0]["agent"] == "Coder"


def test_secret_vault_aes_gcm_and_zero_leakage_masking():
    db_file = "var/test_sec/test_vault.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = SecurityMemory(db_file)
    vault = SecretVault(mem, passphrase="Test_Passphrase_12345")

    raw_token = "sk-proj-abc123456789xyz"
    item = vault.set_secret("OPENAI_KEY", raw_token)

    assert item.masked_preview != raw_token
    assert "***" in item.masked_preview

    # Decrypt and verify
    decrypted = vault.get_secret("OPENAI_KEY")
    assert decrypted == raw_token


def test_audit_hash_chain_and_tamper_detection():
    db_file = "var/test_sec/test_audit.db"
    if Path(db_file).exists():
        Path(db_file).unlink()

    mem = SecurityMemory(db_file)
    logger = AuditLogger(mem)

    # 1. Log 3 events
    e1 = logger.log_event("Alfred", "decompose_goal", 15, "ALLOWED")
    e2 = logger.log_event("Coder", "synthesize_app", 45, "ALLOWED")
    e3 = logger.log_event("Friday", "verify_sandbox", 20, "ALLOWED")

    # 2. Verify chain is pristine (1 Genesis Anchor + 3 logged events = 4 entries)
    check1 = logger.verify_chain_integrity()
    assert check1["valid"] is True
    assert check1["total_entries"] == 4

    # 3. Adversarial Attack: Modify row in SQLite
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("UPDATE audit_events SET action='tampered_action' WHERE id = ?", (e2.id,))
    conn.commit()
    conn.close()

    # 4. Cryptographic integrity check must fail
    check2 = logger.verify_chain_integrity()
    assert check2["valid"] is False
    assert "tampering detected" in check2["reason"].lower()

    # 5. Adversarial Attack: Wipe complete audit table
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("DELETE FROM audit_events")
    conn.commit()
    conn.close()

    # 6. Chain check must detect audit history destruction
    check3 = logger.verify_chain_integrity()
    assert check3["valid"] is False
    assert check3["status"] == "AUDIT_DESTRUCTION_DETECTED"


def test_sandbox_path_clamping_and_destructive_command_blocking():
    guard = SandboxGuardrails(allowed_workspace=".")

    # 1. Valid workspace path
    v1 = guard.validate_file_path("src/jarvisx/main.py")
    assert v1["allowed"] is True

    # 2. Directory traversal attempt
    v2 = guard.validate_file_path("../../Windows/System32/drivers/etc/hosts")
    assert v2["allowed"] is False
    assert v2["status"] == "BLOCKED"

    # 3. Destructive command injection
    c1 = guard.validate_command("python -m pytest")
    assert c1["allowed"] is True

    c2 = guard.validate_command("rm -rf /")
    assert c2["allowed"] is False
    assert c2["status"] == "BLOCKED"


def test_permission_enforcer_capability_bounds_and_risk_scoring():
    mem = SecurityMemory("var/test_sec/test_enforcer.db")
    enforcer = PermissionEnforcer(mem)

    # 1. ResearchAgent reading -> Low risk (<30) -> auto-approved
    d1 = enforcer.evaluate_action("ResearchAgent", "read_notes", PermissionScope.FILESYSTEM_READ)
    assert d1.allowed is True
    assert d1.risk_level == RiskLevel.LOW

    # 2. Permission escalation attempt -> Coder attempting system mutation -> BLOCKED
    d2 = enforcer.evaluate_action("CodingAgent", "system_reboot", PermissionScope.SYSTEM_MUTATION)
    assert d2.allowed is False
    assert "Escalation Denied" in d2.reason

    # 3. Multi-factor high risk calculation
    high_breakdown = RiskBreakdown(40, 20, 10, 10, 15)  # 95 total
    d3 = enforcer.evaluate_action("FridayTacticalAgent", "format_disk", PermissionScope.TERMINAL_EXECUTE, high_breakdown)
    assert d3.allowed is False
    assert d3.risk_level == RiskLevel.CRITICAL


def test_trust_engine_end_to_end_evaluate_and_audit():
    engine = TrustEngine()
    decision = engine.evaluate_and_audit(
        actor="ResearchAgent",
        action="read_api_docs",
        scope=PermissionScope.FILESYSTEM_READ
    )
    assert decision.allowed is True

    status = engine.status()
    assert status["vault_encrypted"] is True
    assert status["audit_chain_valid"] is True
