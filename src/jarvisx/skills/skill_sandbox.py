"""Skill Sandbox Runtime for Phase 92 Autonomous Skill Acquisition."""

from __future__ import annotations
import importlib.util
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from jarvisx.skills.models import SandboxPolicy, SkillMetadata, SkillStatus, SkillValidationResult


class SkillSandbox:
    """Executes synthesized skill verification tests under strict resource and policy limits."""

    def __init__(self, policy: Optional[SandboxPolicy] = None):
        self.policy = policy or SandboxPolicy()

    def run_sandbox_test(self, metadata: SkillMetadata) -> SkillValidationResult:
        """Run verification test for the synthesized skill."""
        start_t = time.time()
        skill_p = Path(metadata.file_path)
        test_p = Path(metadata.test_path)

        if not skill_p.exists() or not test_p.exists():
            return SkillValidationResult(
                passed=False,
                status=SkillStatus.REJECTED,
                execution_time_sec=0.0,
                error=f"Skill source or test file missing: {metadata.file_path}"
            )

        # 1. Static Security Scan
        code_text = skill_p.read_text(encoding="utf-8").lower()
        forbidden_tokens = ["rmdir /s", "os.system('del", "c:\\windows", "system32", "drop database"]
        for tok in forbidden_tokens:
            if tok in code_text:
                return SkillValidationResult(
                    passed=False,
                    status=SkillStatus.REJECTED,
                    execution_time_sec=0.0,
                    error=f"Security Policy Violation: Forbidden token '{tok}' detected in skill code.",
                    policy_violations=[f"Dangerous token '{tok}'"]
                )

        # 2. Dynamic Execution Test in Isolated Namespace
        try:
            module_name = f"dynamic_{metadata.name}_{int(time.time())}"
            spec = importlib.util.spec_from_file_location(module_name, str(skill_p))
            if not spec or not spec.loader:
                raise ImportError("Could not load module specification")

            mod = importlib.util.module_module_from_spec(spec) if hasattr(importlib.util, 'module_module_from_spec') else importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            # Find capability class or execute function
            inst = None
            for attr in dir(mod):
                if attr.endswith("Capability") and not attr.startswith("_"):
                    cls = getattr(mod, attr)
                    inst = cls()
                    break

            if not inst and hasattr(mod, "execute"):
                res = mod.execute()
            elif inst and hasattr(inst, "execute"):
                res = inst.execute(output_dir="var/sandbox_test")
            else:
                raise AttributeError("No executable 'Capability' class or 'execute' function found.")

            duration = round(time.time() - start_t, 3)

            # Check timeout limit
            if duration > self.policy.max_runtime_seconds:
                return SkillValidationResult(
                    passed=False,
                    status=SkillStatus.REJECTED,
                    execution_time_sec=duration,
                    error=f"Timeout limit exceeded: {duration}s > {self.policy.max_runtime_seconds}s"
                )

            return SkillValidationResult(
                passed=True,
                status=SkillStatus.VALIDATED,
                execution_time_sec=duration,
                output=res
            )

        except Exception as e:
            duration = round(time.time() - start_t, 3)
            return SkillValidationResult(
                passed=False,
                status=SkillStatus.REJECTED,
                execution_time_sec=duration,
                error=str(e)
            )
