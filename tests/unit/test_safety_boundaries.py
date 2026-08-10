"""Regression coverage for Phase 104.9 safety boundaries."""

from __future__ import annotations

import asyncio
import sys
from unittest.mock import patch

from jarvisx.capabilities.coding.sandbox.sandbox_manager import SandboxManager, SandboxSecurityError
from jarvisx.core.safety import ProductionSafetyGate, RiskLevel
from jarvisx.tools.git_sync import GitSyncAgent


class NonInteractiveInput:
    def isatty(self) -> bool:
        return False


def test_non_interactive_approval_is_denied_even_for_legacy_auto_approval_calls():
    with patch("jarvisx.core.safety.sys.stdin", NonInteractiveInput()):
        assert ProductionSafetyGate.request_approval(
            command="delete temporary files",
            reason="regression test",
            risk_level=RiskLevel.HIGH,
            auto_approve_non_interactive=True,
        ) is False


def test_sandbox_uses_direct_exec_and_rejects_shell_chaining():
    sandbox = SandboxManager(allowed_commands=["python"])

    command = f'"{sys.executable}" -c "print(\'safe\')"'
    result = asyncio.run(sandbox.execute_command(command))

    assert result["exit_code"] == 0
    assert result["stdout"].strip() == "safe"
    try:
        asyncio.run(sandbox.execute_command(f'{command} && whoami'))
    except SandboxSecurityError:
        pass
    else:
        raise AssertionError("Sandbox accepted a shell control operator.")


def test_git_sync_denies_push_without_explicit_permissions(tmp_path):
    result = GitSyncAgent(repo_dir=str(tmp_path)).execute_secure_push()

    assert result["status"] == "denied"
    assert set(result["missing_permissions"]) == {"WRITE", "EXECUTE", "NETWORK"}
