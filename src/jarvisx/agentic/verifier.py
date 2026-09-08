"""Verification gate.

A run is not "done" because the model said so.  Each check below runs real
code against the sandbox and returns a boolean plus evidence.  The
:class:`Verdict` aggregates them into a pass/fail and a 0..1 score, which is
what the scheduler uses to decide whether to retry, escalate or accept.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence

from jarvisx.agentic.sandbox import SandboxedRunner
from jarvisx.agentic.types import RunResult, Verdict

logger = logging.getLogger("jarvisx.agentic.verifier")


@dataclass
class CheckResult:
    name: str
    passed: bool
    evidence: str = ""
    weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "evidence": self.evidence,
            "weight": self.weight,
        }


class Check:
    """Base class for verification checks."""

    # pytest collects anything named Test*/has __init__; these are runtime
    # verification objects, not test cases, so opt the whole family out.
    __test__ = False

    name = "check"
    weight = 1.0

    def run(self, result: RunResult, sandbox: SandboxedRunner) -> CheckResult:
        raise NotImplementedError


class PythonAssertCheck(Check):
    """Runs a Python snippet in the sandbox; passes iff it exits 0."""

    name = "python_assert"

    def __init__(self, code: str, weight: float = 1.0):
        self.code = code
        self.weight = weight

    def run(self, result: RunResult, sandbox: SandboxedRunner) -> CheckResult:
        outcome = sandbox.run_python(self.code)
        return CheckResult(
            name=self.name,
            passed=outcome.ok,
            evidence=outcome.summary(max_chars=600),
            weight=self.weight,
        )


class TestsPassCheck(Check):
    """Passes iff the sandbox's pytest suite exits 0."""

    name = "tests_pass"

    def __init__(self, path: str = ".", weight: float = 1.0):
        self.path = path
        self.weight = weight

    def run(self, result: RunResult, sandbox: SandboxedRunner) -> CheckResult:
        outcome = sandbox.run_pytest(self.path)
        tail = "\n".join((outcome.stdout or outcome.stderr).strip().splitlines()[-5:])
        return CheckResult(
            name=self.name,
            passed=outcome.ok,
            evidence=tail or outcome.summary(max_chars=400),
            weight=self.weight,
        )


class FileExistsCheck(Check):
    """Passes iff a file exists in the sandbox workspace."""

    name = "file_exists"

    def __init__(self, path: str, weight: float = 1.0):
        self.path = path
        self.weight = weight

    def run(self, result: RunResult, sandbox: SandboxedRunner) -> CheckResult:
        try:
            content = sandbox.read_file(self.path)
        except Exception as exc:  # noqa: BLE001 - any failure means "missing"
            return CheckResult(self.name, False, str(exc), self.weight)
        return CheckResult(
            self.name,
            True,
            f"{self.path} exists ({len(content.splitlines())} lines)",
            self.weight,
        )


class OutputContainsCheck(Check):
    """Passes iff every needle appears in the run's final output or transcript."""

    name = "output_contains"

    def __init__(self, needles: Sequence[str], weight: float = 1.0):
        self.needles = list(needles)
        self.weight = weight

    def run(self, result: RunResult, sandbox: SandboxedRunner) -> CheckResult:
        haystack = _transcript(result).lower()
        missing = [n for n in self.needles if n.lower() not in haystack]
        if missing:
            return CheckResult(self.name, False, f"missing: {missing}", self.weight)
        return CheckResult(self.name, True, f"found all of {self.needles}", self.weight)


class NonEmptyOutputCheck(Check):
    """Passes iff the run produced a non-trivial final answer."""

    name = "nonempty_output"

    def __init__(self, min_chars: int = 1, weight: float = 1.0):
        self.min_chars = min_chars
        self.weight = weight

    def run(self, result: RunResult, sandbox: SandboxedRunner) -> CheckResult:
        length = len((result.output or "").strip())
        return CheckResult(
            self.name,
            length >= self.min_chars,
            f"output length {length} (min {self.min_chars})",
            self.weight,
        )


class JsonOutputCheck(Check):
    """Passes iff the final output parses as JSON."""

    name = "json_output"
    weight = 1.0

    def run(self, result: RunResult, sandbox: SandboxedRunner) -> CheckResult:
        try:
            json.loads(result.output or "")
        except (json.JSONDecodeError, TypeError) as exc:
            return CheckResult(self.name, False, str(exc), self.weight)
        return CheckResult(self.name, True, "output is valid JSON", self.weight)


class CustomCheck(Check):
    """Wraps an arbitrary predicate as a check."""

    def __init__(
        self,
        predicate: Callable[[RunResult, SandboxedRunner], Any],
        name: str = "custom",
        weight: float = 1.0,
    ):
        self.predicate = predicate
        self.name = name
        self.weight = weight

    def run(self, result: RunResult, sandbox: SandboxedRunner) -> CheckResult:
        try:
            outcome = self.predicate(result, sandbox)
        except Exception as exc:  # noqa: BLE001
            return CheckResult(self.name, False, f"{type(exc).__name__}: {exc}", self.weight)
        if isinstance(outcome, CheckResult):
            return outcome
        truthy = bool(outcome)
        return CheckResult(self.name, truthy, "predicate returned truthy" if truthy else "predicate returned falsy", self.weight)


# --------------------------------------------------------------------------- #
# Verifier
# --------------------------------------------------------------------------- #


_CHECK_FACTORIES: Dict[str, Callable[[Dict[str, Any]], Check]] = {
    "python_assert": lambda cfg: PythonAssertCheck(cfg["code"], cfg.get("weight", 1.0)),
    "tests_pass": lambda cfg: TestsPassCheck(cfg.get("path", "."), cfg.get("weight", 1.0)),
    "file_exists": lambda cfg: FileExistsCheck(cfg["path"], cfg.get("weight", 1.0)),
    "output_contains": lambda cfg: OutputContainsCheck(
        cfg["needles"], cfg.get("weight", 1.0)
    ),
    "nonempty_output": lambda cfg: NonEmptyOutputCheck(
        cfg.get("min_chars", 1), cfg.get("weight", 1.0)
    ),
    "json_output": lambda cfg: JsonOutputCheck(),
}


class Verifier:
    """Applies a list of checks to a finished run."""

    def __init__(self, checks: Optional[Sequence[Check]] = None, require_all: bool = True):
        self.checks: List[Check] = list(checks or [])
        self.require_all = require_all

    @classmethod
    def from_config(cls, configs: Sequence[Dict[str, Any]]) -> "Verifier":
        """Build a verifier from JSON-safe config dicts (used by the planner)."""
        checks: List[Check] = []
        for cfg in configs or []:
            factory = _CHECK_FACTORIES.get(cfg.get("type", ""))
            if factory is None:
                logger.warning("unknown check type %r ignored", cfg.get("type"))
                continue
            try:
                checks.append(factory(cfg))
            except (KeyError, TypeError) as exc:
                logger.warning("bad check config %r: %s", cfg, exc)
        return cls(checks)

    def verify(self, result: RunResult, sandbox: SandboxedRunner) -> Verdict:
        """Run every check and fold the results into one verdict."""
        results = [check.run(result, sandbox) for check in self.checks]
        if not results:
            # No checks configured: fall back to trusting the run status.
            return Verdict(
                passed=result.ok,
                score=1.0 if result.ok else 0.0,
                checks=[],
                rationale="no checks configured; trusted harness status",
            )

        total_weight = sum(r.weight for r in results) or 1.0
        earned = sum(r.weight for r in results if r.passed)
        score = round(earned / total_weight, 4)
        passed = all(r.passed for r in results) if self.require_all else score > 0.0

        failures = [r.name for r in results if not r.passed]
        rationale = (
            f"{len(results) - len(failures)}/{len(results)} checks passed"
            + (f"; failing: {failures}" if failures else "")
        )
        return Verdict(
            passed=passed,
            score=score,
            checks=[r.to_dict() for r in results],
            rationale=rationale,
        )


def _transcript(result: RunResult) -> str:
    """Flatten a run into one searchable string."""
    parts = [result.output or ""]
    for step in result.steps:
        parts.append(step.thought or "")
        for obs in step.observations:
            parts.append(str(obs.output) if obs.output is not None else "")
            parts.append(obs.error or "")
    return "\n".join(parts)
