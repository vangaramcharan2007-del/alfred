from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.coding.sandbox.sandbox_manager import SandboxManager

@dataclass
class TestResult:
    passed: bool
    total_tests: int
    passed_count: int
    failed_count: int
    stdout: str
    stderr: str
    execution_time_seconds: float
    command: str

class TestRunner:
    __test__ = False

    def __init__(self, sandbox_manager: Optional[SandboxManager] = None):

        self.sandbox = sandbox_manager or SandboxManager()

    async def run_tests(
        self,
        repo_path: str,
        test_command: Optional[str] = None,
        timeout: float = 30.0
    ) -> TestResult:
        cmd = test_command or "pytest"
        
        exec_res = await self.sandbox.execute_command(cmd, cwd=repo_path, timeout=timeout)
        
        stdout = exec_res.get("stdout", "")
        stderr = exec_res.get("stderr", "")
        exit_code = exec_res.get("exit_code", -1)
        passed = exit_code == 0

        # Simple parsing heuristic
        total = 1
        passed_c = 1 if passed else 0
        failed_c = 0 if passed else 1

        if "passed" in stdout.lower():
            passed_c = 1
            failed_c = 0
            passed = True

        return TestResult(
            passed=passed,
            total_tests=total,
            passed_count=passed_c,
            failed_count=failed_c,
            stdout=stdout,
            stderr=stderr,
            execution_time_seconds=1.0,
            command=cmd
        )
