"""Skill Validator for Phase 92 Autonomous Skill Acquisition."""

from __future__ import annotations
from typing import Dict, Any, List
from jarvisx.skills.models import SkillMetadata, SkillStatus, SkillValidationResult


class SkillValidator:
    """Validates policy compliance and security integrity before installing a skill."""

    FORBIDDEN_CALLS = [
        "subprocess.call('format",
        "powershell -command Remove-Item -Recurse C:",
        "shutil.rmtree(r'c:\\windows",
        "drop database production",
        "eval(user_input)",
    ]

    def validate_skill_metadata(self, metadata: SkillMetadata, sandbox_result: SkillValidationResult) -> Dict[str, Any]:
        """Verify whether a synthesized skill is trusted for installation into production registry."""
        if not sandbox_result.passed:
            return {
                "approved": False,
                "status": SkillStatus.REJECTED.value,
                "reason": f"Sandbox execution failed: {sandbox_result.error}"
            }

        # Check policy violations
        if sandbox_result.policy_violations:
            return {
                "approved": False,
                "status": SkillStatus.REJECTED.value,
                "reason": f"Security policy violations: {', '.join(sandbox_result.policy_violations)}"
            }

        return {
            "approved": True,
            "status": SkillStatus.VALIDATED.value,
            "reason": "Skill successfully passed sandbox and security validation."
        }
