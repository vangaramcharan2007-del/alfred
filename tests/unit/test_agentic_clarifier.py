"""Tests for the consequential-ambiguity gate.

The gate's whole value is that it fires *rarely and predictably*. These tests
therefore spend as much effort on the cases that must NOT trigger it as on the
ones that must -- an over-eager gate is a worse product than no gate, because
every spurious question is an interruption the user did not budget for.
"""

import pytest

from jarvisx.agentic.clarifier import ClarificationGate, Clarification
from jarvisx.agentic.backends import ScriptedBackend
from jarvisx.agentic.harness import AgentHarness
from jarvisx.agentic.types import RunStatus, TERMINAL_STATUSES, _FAILURE_STATUSES


@pytest.fixture
def gate():
    return ClarificationGate()


# --------------------------------------------------------------------- #
# Cases that MUST stop and ask
# --------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "task,kind",
    [
        ("delete the old logs", "destructive_target"),
        ("remove them", "destructive_target"),
        ("wipe everything", "destructive_target"),
        ("purge those", "destructive_target"),
        ("drop the stuff I do not need", "destructive_target"),
    ],
)
def test_destructive_with_unnamed_target_asks(gate, task, kind):
    c = gate.inspect(task)
    assert c.needed is True
    assert c.kind == kind
    assert c.question  # a real question, not an empty string
    assert c.unresolved, "must surface the words it could not resolve"


@pytest.mark.parametrize(
    "task",
    [
        "send it",
        "email them the report",
        "message those people",
        "post this",
        "publish it",
        "text them",
    ],
)
def test_outbound_without_recipient_asks(gate, task):
    c = gate.inspect(task)
    assert c.needed is True
    assert c.kind == "outbound_recipient"
    assert c.question


def test_empty_goal_asks(gate):
    for blank in ("", "   ", "\n\t"):
        c = gate.inspect(blank)
        assert c.needed is True
        assert c.kind == "empty_goal"


# --------------------------------------------------------------------- #
# Cases that MUST NOT stop -- this is what keeps the gate from nagging
# --------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "task",
    [
        "list the files in src",
        "what time is it",
        "read the config and summarise it",
        "run the test suite",
        "explain what this function does",
        "how many lines are in harness.py",
    ],
)
def test_read_only_work_never_asks(gate, task):
    assert gate.inspect(task).needed is False


@pytest.mark.parametrize(
    "task",
    [
        "delete build/ and dist/",
        "remove src/jarvisx/legacy/old_module.py",
        "purge __pycache__ directories",
        "email dakshith@example.com the report",
        "send the summary to the #engineering channel",
    ],
)
def test_consequential_but_specific_proceeds(gate, task):
    """Naming the target is enough. The gate must not second-guess it."""
    assert gate.inspect(task).needed is False


def test_disabled_gate_never_asks():
    off = ClarificationGate(enabled=False)
    for task in ("delete them", "send it", ""):
        assert off.inspect(task).needed is False


# --------------------------------------------------------------------- #
# Contract
# --------------------------------------------------------------------- #

def test_gate_is_deterministic(gate):
    """A gate that asks on Tuesday and not Wednesday is worse than none."""
    for task in ("delete the old logs", "list the files", "send it"):
        assert gate.inspect(task).needed == gate.inspect(task).needed


def test_gate_never_raises(gate):
    for bad in (None, "", 12345, ["not", "a", "string"]):
        gate.inspect(bad)  # must not raise


def test_clarification_is_truthy_only_when_needed():
    assert bool(Clarification(needed=True, question="?")) is True
    assert bool(Clarification(needed=False)) is False


def test_needs_input_is_terminal_but_not_a_failure():
    """Pausing to ask is not failing. If it counted as a failure, an
    orchestration report would treat a correct question as a broken run."""
    assert RunStatus.NEEDS_INPUT in TERMINAL_STATUSES
    assert RunStatus.NEEDS_INPUT not in _FAILURE_STATUSES


# --------------------------------------------------------------------- #
# Integration: the harness actually stops
# --------------------------------------------------------------------- #

def test_harness_stops_before_touching_a_tool():
    """The point of the gate is that no work happens. A ScriptedBackend that is
    never consumed proves the run stopped before the model was consulted."""
    backend = ScriptedBackend([{"content": "this should never be used"}])
    harness = AgentHarness(backend=backend, clarifier=ClarificationGate())

    result = harness.run("delete the old logs")

    assert result.status == RunStatus.NEEDS_INPUT
    assert result.clarification is not None
    assert result.clarification.kind == "destructive_target"
    assert result.output == result.clarification.question
    assert result.steps == [], "no tool may run while the question is open"
    assert result.error is None, "asking is not an error"
    assert len(backend.calls) == 0, "the model must not be consulted at all"


def test_harness_without_gate_behaves_as_before():
    """Default is off, so adding this changes nothing for existing callers."""
    backend = ScriptedBackend([{"content": "All done."}])
    harness = AgentHarness(backend=backend)

    result = harness.run("delete the old logs")

    assert result.status != RunStatus.NEEDS_INPUT
    assert len(backend.calls) >= 1


def test_harness_lets_specific_destructive_work_through():
    backend = ScriptedBackend([{"content": "Deleted build/ and dist/."}])
    harness = AgentHarness(backend=backend, clarifier=ClarificationGate())

    result = harness.run("delete build/ and dist/")

    assert result.status != RunStatus.NEEDS_INPUT
    assert len(backend.calls) >= 1


# --------------------------------------------------------------------- #
# The voice path: a question must be spoken, not reported as a failure
# --------------------------------------------------------------------- #

def test_speak_run_speaks_the_question():
    """Without this the question falls through to the error branch, because a
    run that stopped to ask is neither `ok` nor in `failed` -- NEEDS_INPUT is
    deliberately not a failure. The agent would say "That did not work:
    something" while holding a question it never asked."""
    from jarvisx.agentic.voice_loop import _speak_run

    result = {
        "ok": False,
        "succeeded": [],
        "failed": [],
        "clarifications": [
            {"node_id": "execute", "question": "Which ones exactly?", "kind": "destructive_target"}
        ],
    }
    assert _speak_run(result) == "Which ones exactly?"


def test_speak_run_still_reports_real_failures():
    from jarvisx.agentic.voice_loop import _speak_run

    assert "did not work" in _speak_run({"ok": False, "failed": ["boom"], "clarifications": []})
    assert "did not work" in _speak_run({"ok": False, "failed": ["boom"]})
    assert _speak_run({"ok": True, "succeeded": ["a"]}).startswith("Done.")


def test_speak_run_ignores_an_empty_question():
    from jarvisx.agentic.voice_loop import _speak_run

    result = {"ok": True, "succeeded": ["a"], "clarifications": [{"question": ""}]}
    assert _speak_run(result).startswith("Done.")


def test_report_surfaces_clarifications_in_to_dict():
    """The voice loop receives to_dict(), so the question has to survive that
    hop or the whole chain silently degrades."""
    from jarvisx.agentic.types import (
        NodeOutcome, OrchestrationReport, RunResult, TaskNode,
    )

    clarification = Clarification(
        needed=True, kind="destructive_target", question="Which ones exactly?"
    )
    node = TaskNode(id="execute", instruction="delete the old logs")
    outcome = NodeOutcome(
        node_id="execute",
        status=RunStatus.NEEDS_INPUT,
        result=RunResult(
            run_id="r1",
            task="delete the old logs",
            status=RunStatus.NEEDS_INPUT,
            output="Which ones exactly?",
            clarification=clarification,
        ),
    )
    report = OrchestrationReport(goal="delete the old logs", graph_id="g1", nodes=[node])
    report.outcomes["execute"] = outcome

    assert report.ok is False
    assert report.failed == [], "asking is not failing"
    assert report.clarifications == [
        {"node_id": "execute", "question": "Which ones exactly?", "kind": "destructive_target"}
    ]

    d = report.to_dict()
    assert d["clarifications"][0]["question"] == "Which ones exactly?"

    from jarvisx.agentic.voice_loop import _speak_run
    assert _speak_run(d) == "Which ones exactly?"
