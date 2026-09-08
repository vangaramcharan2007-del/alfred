"""Tests for the real (formerly simulated) SandboxHarness evaluation."""

from __future__ import annotations

import pytest

from jarvisx.orchestration.sandbox_harness import SandboxHarness, _parse_pytest_summary

SIEVE = (
    "def primes_upto(n):\n"
    "    sieve = [True] * (n + 1)\n"
    "    sieve[0] = sieve[1] = False\n"
    "    for i in range(2, int(n ** 0.5) + 1):\n"
    "        if sieve[i]:\n"
    "            for j in range(i * i, n + 1, i):\n"
    "                sieve[j] = False\n"
    "    return [i for i, v in enumerate(sieve) if v]\n"
)

PASSING_SUITE = (
    "from candidate import primes_upto\n\n\n"
    "def test_small():\n    assert primes_upto(10) == [2, 3, 5, 7]\n\n\n"
    "def test_count():\n    assert len(primes_upto(100)) == 25\n"
)


@pytest.fixture()
def harness(tmp_path):
    instance = SandboxHarness(workspace=tmp_path / "ws")
    try:
        yield instance
    finally:
        instance.cleanup()


# --------------------------------------------------------------------------- #
# Summary parsing
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "line,expected",
    [
        ("==== 3 passed, 1 failed in 0.42s ====", (3, 1)),
        ("===== 5 passed in 0.11s =====", (5, 0)),
        ("===== 2 failed in 0.11s =====", (0, 2)),
        ("===== 1 failed, 2 errors in 0.11s =====", (0, 1)),
        ("no summary here", (0, 0)),
    ],
)
def test_parse_pytest_summary(line, expected):
    assert _parse_pytest_summary(line) == expected


def test_parse_pytest_summary_reads_the_last_summary_line():
    output = "2 passed in 0.01s\nsome noise\n===== 7 passed in 0.30s =====\n"
    assert _parse_pytest_summary(output) == (7, 0)


# --------------------------------------------------------------------------- #
# Evaluation
# --------------------------------------------------------------------------- #


def test_passing_submission_scores_100(harness):
    result = harness.evaluate_agent_code("coder", SIEVE, PASSING_SUITE)
    assert result["passed"] is True
    assert result["reward_score"] == 100
    assert result["simulated"] is False


def test_crashing_payload_scores_zero(harness):
    result = harness.evaluate_agent_code("coder", 'raise ValueError("boom")', PASSING_SUITE)
    assert result["passed"] is False
    assert result["reward_score"] == 0
    assert "boom" in result["sandbox_logs"]


def test_failing_tests_score_zero(harness):
    broken = "def primes_upto(n):\n    return []\n"
    result = harness.evaluate_agent_code("coder", broken, PASSING_SUITE)
    assert result["passed"] is False
    assert result["reward_score"] == 0


def test_partial_pass_scores_proportionally(harness):
    partial = (
        "from candidate import primes_upto\n\n\n"
        "def test_small():\n    assert primes_upto(10) == [2, 3, 5, 7]\n\n\n"
        "def test_wrong():\n    assert len(primes_upto(100)) == 99\n"
    )
    result = harness.evaluate_agent_code("coder", SIEVE, partial)
    assert result["passed"] is False
    assert result["reward_score"] == 50


def test_empty_payload_is_rejected(harness):
    result = harness.evaluate_agent_code("coder", "   ", PASSING_SUITE)
    assert result["passed"] is False
    assert result["reward_score"] == 0
    assert "empty" in result["sandbox_logs"]


def test_missing_suite_gives_honest_partial_credit(harness):
    """Without executable tests, correctness is unverified — say so."""
    result = harness.evaluate_agent_code("coder", "print(1 + 1)", "not-a-suite")
    assert result["passed"] is True
    assert result["reward_score"] == 70
    assert "unverified" in result["sandbox_logs"]


def test_evaluation_reports_real_exit_codes(harness):
    result = harness.evaluate_agent_code("coder", "import sys\nsys.exit(4)\n", "")
    assert result["passed"] is False
    assert result["execution"]["exit_code"] == 4


def test_repeated_evaluation_is_not_fooled_by_stale_bytecode(tmp_path):
    """Regression: same-size rewrites used to execute the previous .pyc."""
    harness = SandboxHarness(workspace=tmp_path / "ws")
    try:
        partial = (
            "\nfrom candidate import primes_upto\n\n\n"
            "def test_small():\n    assert primes_upto(10) == [2, 3, 5, 7]\n\n\n"
            "def test_wrong():\n    assert len(primes_upto(100)) == 99\n"
        )
        passing = (
            "\nfrom candidate import primes_upto\n\n\n"
            "def test_small():\n    assert primes_upto(10) == [2, 3, 5, 7]\n\n\n"
            "def test_count():\n    assert len(primes_upto(100)) == 25\n"
        )
        # Both suites are byte-for-byte the same length on purpose.
        assert len(partial) == len(passing)

        assert harness.evaluate_agent_code("c", SIEVE, partial)["reward_score"] == 50
        assert harness.evaluate_agent_code("c", SIEVE, passing)["reward_score"] == 100
    finally:
        harness.cleanup()


def test_evaluate_agent_files_grades_a_multi_file_submission(harness):
    files = {
        "mathlib.py": "def double(x):\n    return x * 2\n",
        "test_mathlib.py": "from mathlib import double\n\n\ndef test_double():\n    assert double(3) == 6\n",
    }
    result = harness.evaluate_agent_files("coder", files, test_suite="test_mathlib.py")
    assert result["passed"] is True
    assert result["reward_score"] == 100


def test_evaluate_agent_files_reports_failures(harness):
    files = {
        "mathlib.py": "def double(x):\n    return x + 2\n",
        "test_mathlib.py": "from mathlib import double\n\n\ndef test_double():\n    assert double(3) == 6\n",
    }
    result = harness.evaluate_agent_files("coder", files, test_suite="test_mathlib.py")
    assert result["passed"] is False
    assert result["reward_score"] == 0


def test_singleton_can_be_reset(tmp_path):
    SandboxHarness.reset_instance()
    first = SandboxHarness.get_instance()
    assert SandboxHarness.get_instance() is first
    SandboxHarness.reset_instance()
    assert SandboxHarness.get_instance() is not first
    SandboxHarness.reset_instance()
