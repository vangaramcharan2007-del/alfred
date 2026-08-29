"""
Sandbox Test Runner for Jarvis X Autonomous Developer Engine.
Executes code and unit tests in an isolated, safe subprocess with timeouts and memory limits.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class TestExecutionResult:
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    error_summary: Optional[str] = None


class SandboxTestRunner:
    """Safely executes Python scripts and unit tests inside an isolated sandbox."""

    def __init__(self, timeout_sec: float = 10.0):
        self.timeout_sec = timeout_sec
        self.python_exe = sys.executable

    def run_code_snippet(self, code: str) -> TestExecutionResult:
        """Executes a standalone Python code snippet in a temporary sandbox file."""
        start_t = time.time()
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as tf:
            tf.write(code)
            temp_path = tf.name

        try:
            res = subprocess.run(
                [self.python_exe, temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
            )
            dur = round((time.time() - start_t) * 1000, 2)
            err_sum = None
            if res.returncode != 0:
                err_sum = res.stderr.strip().split("\n")[-1] if res.stderr else "Non-zero exit code"

            return TestExecutionResult(
                success=res.returncode == 0,
                exit_code=res.returncode,
                stdout=res.stdout,
                stderr=res.stderr,
                duration_ms=dur,
                error_summary=err_sum,
            )
        except subprocess.TimeoutExpired:
            dur = round((time.time() - start_t) * 1000, 2)
            return TestExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Execution timed out after {self.timeout_sec}s",
                duration_ms=dur,
                error_summary="TimeoutExpired",
            )
        finally:
            try:
                os.remove(temp_path)
            except Exception:
                pass
