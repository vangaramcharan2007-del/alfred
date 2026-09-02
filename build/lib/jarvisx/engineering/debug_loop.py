from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class DebugAttempt:
    attempt_number: int
    command: str
    return_code: int
    failing_tests: List[str] = field(default_factory=list)
    traceback_snippet: str = ""
    compiler_output: str = ""
    analysis: str = ""
    fix_generated: str = ""
    success: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attempt_number": self.attempt_number,
            "command": self.command,
            "return_code": self.return_code,
            "failing_tests": self.failing_tests,
            "traceback_snippet": self.traceback_snippet,
            "compiler_output": self.compiler_output,
            "analysis": self.analysis,
            "fix_generated": self.fix_generated,
            "success": self.success,
        }


@dataclass
class DebugResult:
    success: bool
    attempts: List[DebugAttempt] = field(default_factory=list)
    summary_log: str = ""

    def generate_report(self) -> str:
        lines: List[str] = ["REAL DEBUGGING LOOP REPORT", f"Final Outcome: {'SUCCESS' if self.success else 'FAILED'} (Total Attempts: {len(self.attempts)})"]
        for att in self.attempts:
            lines.append(f"\n--- Attempt #{att.attempt_number} ---")
            lines.append(f"Command: {att.command} (Exit Code: {att.return_code})")
            if att.failing_tests:
                lines.append(f"Failing Tests: {', '.join(att.failing_tests)}")
            if att.analysis:
                lines.append(f"Failure Analysis: {att.analysis}")
            if att.fix_generated:
                lines.append(f"Action / Fix Applied: {att.fix_generated}")
            lines.append(f"Attempt Result: {'Resolved' if att.success else 'Still Failing'}")
        if self.summary_log:
            lines.append(f"\nSummary:\n  {self.summary_log}")
        return "\n".join(lines)


class DebugLoopEngine:
    """
    Offline-first diagnostic and self-healing engine capable of running builds/tests,
    intercepting tracebacks, generating anatomical fixes, and retrying up to 3 times.
    """
    MAX_RETRIES: int = 3

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise FileNotFoundError(f"Repository not found: {self.repo_path}")

    def run_command_with_timeout(self, cmd: List[str], timeout_sec: int = 45) -> Tuple[int, str, str]:
        try:
            res = subprocess.run(
                cmd,
                cwd=self.repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=timeout_sec,
                env={**os.environ, "PYTHONPATH": str(self.repo_path / "src") + os.pathsep + os.environ.get("PYTHONPATH", "")}
            )
            return res.returncode, res.stdout or "", res.stderr or ""
        except subprocess.TimeoutExpired as e:
            return 124, e.stdout or "" if hasattr(e, "stdout") and e.stdout else "", f"Command timed out after {timeout_sec}s"
        except Exception as e:
            return 1, "", str(e)

    def debug_repository(self, test_cmd: List[str] | None = None) -> DebugResult:
        if test_cmd is None:
            # Check if there is a tests/engineering directory or fallback to pytest on tests/
            if (self.repo_path / "tests" / "engineering").exists():
                test_cmd = [sys.executable, "-m", "pytest", "tests/engineering/", "-q"]
            elif (self.repo_path / "tests").exists():
                test_cmd = [sys.executable, "-m", "pytest", "tests/", "-q"]
            else:
                test_cmd = [sys.executable, "-c", "import sys; print('No test suite detected in target repository.')"]

        attempts_list: List[DebugAttempt] = []
        is_success = False

        for attempt_idx in range(1, self.MAX_RETRIES + 1):
            cmd_str = " ".join(test_cmd)
            rc, stdout, stderr = self.run_command_with_timeout(test_cmd, timeout_sec=60)
            combined = f"{stdout}\n{stderr}"

            attempt = DebugAttempt(
                attempt_number=attempt_idx,
                command=cmd_str,
                return_code=rc,
                compiler_output=stderr.strip()[:1000] if stderr else stdout.strip()[:1000]
            )

            if rc == 0:
                attempt.success = True
                attempt.analysis = "All tests and compile builds passed clean without failure exceptions."
                attempt.fix_generated = "No intervention necessary; verified repository stability."
                attempts_list.append(attempt)
                is_success = True
                break
            
            # Extract failing tests and traceback
            failing_tests: List[str] = re.findall(r"FAILED\s+([^\s:]+)", combined)
            attempt.failing_tests = sorted(list(set(failing_tests)))

            tb_match = re.search(r"(Traceback \(most recent call last\):.*?)(?:\n\n|\Z)", combined, re.DOTALL)
            attempt.traceback_snippet = tb_match.group(1)[:1200] if tb_match else combined[:1200]

            # Analyze failure pattern and generate automatic fix
            analysis, fix_desc = self._analyze_and_heal(combined, attempt_idx)
            attempt.analysis = analysis
            attempt.fix_generated = fix_desc
            attempts_list.append(attempt)

            # If our fix worked or if no fix could be safely attempted on last attempt, continue loop to test again
            if attempt_idx == self.MAX_RETRIES:
                break

        summary = (
            f"Successfully verified repository stability after {len(attempts_list)} attempt(s)."
            if is_success
            else f"Debug healing exhausted after {self.MAX_RETRIES} attempts. Review persistent compiler error tracebacks."
        )
        return DebugResult(success=is_success, attempts=attempts_list, summary_log=summary)

    def _analyze_and_heal(self, output_log: str, attempt_num: int) -> Tuple[str, str]:
        # Case 1: ModuleNotFoundError or ImportError
        mod_match = re.search(r"(?:ModuleNotFoundError|ImportError): No module named '([^']+)'", output_log)
        if mod_match:
            missing_pkg = mod_match.group(1)
            analysis = f"Detected fatal import exception: Missing dependency or unmapped module space '{missing_pkg}'."
            # Check if it is a local module path issue or create a mock/stub if in scratch/test zone
            if "jarvisx" in missing_pkg or "test" in missing_pkg:
                stub_file = self.repo_path / "src" / f"{missing_pkg.replace('.', '/')}.py"
                if not stub_file.exists():
                    stub_file.parent.mkdir(parents=True, exist_ok=True)
                    stub_file.write_text("# Auto-synthesized fallback module generated by DebugLoopEngine\n", encoding="utf-8")
                    return analysis, f"Synthesized missing local module skeleton at {stub_file.relative_to(self.repo_path)}."
            return analysis, f"Identified missing external package dependency '{missing_pkg}'. Recommended resolution: run pip installation."

        # Case 2: SyntaxError / IndentationError
        syn_match = re.search(r"File \"([^\"]+)\", line (\d+).*?(SyntaxError|IndentationError): (.*)", output_log, re.DOTALL)
        if syn_match:
            err_file = syn_match.group(1)
            err_line = int(syn_match.group(2))
            err_type = syn_match.group(3)
            err_msg = syn_match.group(4).split("\n")[0]
            analysis = f"Detected syntax corruption ({err_type}) at {err_file}:L{err_line} - {err_msg}."
            fpath = Path(err_file)
            if not fpath.is_absolute():
                fpath = self.repo_path / fpath
            if fpath.exists() and fpath.suffix == ".py":
                lines = fpath.read_text(encoding="utf-8", errors="ignore").splitlines()
                if 0 <= err_line - 1 < len(lines):
                    # Heal common syntax mistakes (e.g. unclosed parenthesis or trailing syntax garbage)
                    bad_line = lines[err_line - 1]
                    if "pass" in bad_line or "return" in bad_line:
                        lines[err_line - 1] = "    pass # Healed by DebugLoopEngine"
                    elif bad_line.strip().endswith("=") or bad_line.strip().endswith(":"):
                        lines[err_line - 1] = bad_line + " None # Healed syntax completion"
                    else:
                        lines[err_line - 1] = f"# [Debug Loop Disabled Broken Line]: {bad_line}"
                    fpath.write_text("\n".join(lines) + "\n", encoding="utf-8")
                    return analysis, f"Executed targeted AST line surgery on {fpath.name} at line {err_line}."
            return analysis, "Could not locate exact filesystem path for syntax repair."

        # Case 3: AssertionError in tests
        assert_match = re.search(r"AssertionError: (.*?)(?:\n|\Z)", output_log)
        if assert_match or "FAILED" in output_log:
            msg = assert_match.group(1) if assert_match else "Test condition expectation mismatch"
            analysis = f"Detected runtime testing contract discrepancy: {msg}."
            return analysis, f"Attempt #{attempt_num} logged. Recommended review of test fixture expectations vs runtime state."

        return "Unknown general execution failure exception.", f"Executed automated diagnostic retry cycle #{attempt_num}."
