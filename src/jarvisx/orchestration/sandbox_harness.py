"""Sandbox Harness — real evaluation of agent-generated code.

This used to score agent output with ``random.random()`` and a ``time.sleep``
to imitate a sandbox boot. It now delegates to
:class:`jarvisx.agentic.sandbox.SandboxedRunner`, so ``passed`` and
``reward_score`` describe what the code actually did: it is written into a
jailed workspace, executed in a subprocess with rlimits and a timeout, and
graded from the real exit code and the real pytest summary line.

The public signature of :meth:`evaluate_agent_code` is unchanged, so existing
callers (e.g. ``jarvisx.self_improvement.auto_curriculum``) keep working — they
just stop receiving invented numbers.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from jarvisx.agentic.sandbox import SandboxedRunner, SandboxResult

logger = logging.getLogger("jarvisx.orchestration.sandbox_harness")

_PASSED_RE = re.compile(r"(\d+)\s+passed")
_FAILED_RE = re.compile(r"(\d+)\s+(?:failed|error|errors)")


class SandboxHarness:
    """Executes and grades agent-generated code for real."""

    _instance: Optional["SandboxHarness"] = None

    def __init__(
        self,
        workspace: Optional[str] = None,
        timeout_seconds: float = 20.0,
        max_memory_mb: int = 1024,
    ):
        self._runner = SandboxedRunner(
            workspace=workspace,
            timeout_seconds=timeout_seconds,
            max_memory_mb=max_memory_mb,
        )

    @classmethod
    def get_instance(cls) -> "SandboxHarness":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Drop the singleton (used by tests to get a clean workspace)."""
        if cls._instance is not None:
            cls._instance.cleanup()
        cls._instance = None

    # ------------------------------------------------------------------ #
    # Evaluation
    # ------------------------------------------------------------------ #

    def evaluate_agent_code(
        self,
        agent_id: str,
        code_payload: str,
        test_suite: str,
    ) -> Dict[str, Any]:
        """Write, execute and grade one agent submission.

        ``test_suite`` may be pytest source (anything containing ``def test``
        or a bare ``assert``), a path to tests already in the workspace, or a
        free-form label — in which case only the payload is executed.
        """
        logger.info(
            "[SandboxHarness] %s submitted %d bytes (suite=%r)",
            agent_id,
            len(code_payload or ""),
            test_suite,
        )

        if not (code_payload or "").strip():
            return self._verdict(
                agent_id,
                passed=False,
                score=0,
                logs="empty code payload",
                execution=None,
                tests=None,
            )

        try:
            self._runner.write_file("candidate.py", code_payload)
        except Exception as exc:  # noqa: BLE001 - path escape, disk error, etc.
            return self._verdict(
                agent_id, False, 0, f"could not stage payload: {exc}", None, None
            )

        execution = self._runner.run_python(code_payload, filename="candidate.py")
        if not execution.ok:
            return self._verdict(
                agent_id,
                passed=False,
                score=0,
                logs=f"payload failed to execute.\n{execution.summary()}",
                execution=execution,
                tests=None,
            )

        tests = self._run_suite(test_suite)
        if tests is None:
            # No runnable suite: the payload at least imported and ran clean.
            return self._verdict(
                agent_id,
                passed=True,
                score=70,
                logs=(
                    "Payload executed cleanly; no executable test suite was "
                    "supplied, so correctness is unverified.\n" + execution.summary()
                ),
                execution=execution,
                tests=None,
            )

        passed_tests, failed_tests = _parse_pytest_summary(tests.stdout + tests.stderr)
        total = passed_tests + failed_tests
        if total:
            score = round(100 * passed_tests / total)
        else:
            score = 100 if tests.ok else 0

        return self._verdict(
            agent_id,
            passed=tests.ok and total > 0,
            score=score,
            logs=(
                f"payload: exit_code={execution.exit_code}\n"
                f"tests: {passed_tests} passed, {failed_tests} failed\n"
                f"{tests.summary()}"
            ),
            execution=execution,
            tests=tests,
        )

    def evaluate_agent_files(
        self,
        agent_id: str,
        files: Dict[str, str],
        test_suite: str = ".",
    ) -> Dict[str, Any]:
        """Grade a multi-file submission (implementation + tests together)."""
        for path, content in (files or {}).items():
            self._runner.write_file(path, content)
        tests = self._run_suite(test_suite)
        if tests is None:
            return self._verdict(
                agent_id, False, 0, "no test suite resolved", None, None
            )
        passed_tests, failed_tests = _parse_pytest_summary(tests.stdout + tests.stderr)
        total = passed_tests + failed_tests
        score = round(100 * passed_tests / total) if total else (100 if tests.ok else 0)
        return self._verdict(
            agent_id,
            passed=tests.ok and total > 0,
            score=score,
            logs=f"{passed_tests} passed, {failed_tests} failed\n{tests.summary()}",
            execution=None,
            tests=tests,
        )

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #

    def _run_suite(self, test_suite: str) -> Optional[SandboxResult]:
        """Run `test_suite` if it names tests or looks like pytest source."""
        suite = (test_suite or "").strip()
        if not suite:
            return None

        if "def test" in suite or (suite.startswith("assert") and "\n" not in suite):
            self._runner.write_file("test_candidate.py", suite)
            return self._runner.run_pytest("test_candidate.py")

        # Otherwise treat it as a path inside the workspace, if it exists.
        try:
            self._runner.resolve(suite)
            if (self._runner.workspace / suite).exists():
                return self._runner.run_pytest(suite)
        except Exception:  # noqa: BLE001 - not a path, just a label
            return None
        return None

    @staticmethod
    def _verdict(
        agent_id: str,
        passed: bool,
        score: int,
        logs: str,
        execution: Optional[SandboxResult],
        tests: Optional[SandboxResult],
    ) -> Dict[str, Any]:
        result = {
            "status": "success",
            "agent_id": agent_id,
            "passed": bool(passed),
            "reward_score": int(score),
            "sandbox_logs": logs,
            "simulated": False,
        }
        if execution is not None:
            result["execution"] = execution.to_dict()
        if tests is not None:
            result["tests"] = tests.to_dict()
        logger.info(
            "[SandboxHarness] %s -> %s (score %d/100)",
            agent_id,
            "PASSED" if passed else "FAILED",
            score,
        )
        return result

    @property
    def workspace(self) -> str:
        return str(self._runner.workspace)

    def cleanup(self) -> None:
        self._runner.cleanup()


def _parse_pytest_summary(output: str) -> tuple[int, int]:
    """Extract (passed, failed) counts from pytest's summary line.

    Two independent searches rather than one combined pattern: with optional
    groups plus a lazy quantifier, the combined form matches the line but
    leaves both counts unbound, silently reporting 0 passed / 0 failed.
    """
    best = (0, 0)
    for line in reversed((output or "").splitlines()):
        if "passed" not in line and "failed" not in line and "error" not in line:
            continue
        passed_match = _PASSED_RE.search(line)
        failed_match = _FAILED_RE.search(line)
        if not passed_match and not failed_match:
            continue
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        if passed or failed:
            best = (passed, failed)
            break
    return best
