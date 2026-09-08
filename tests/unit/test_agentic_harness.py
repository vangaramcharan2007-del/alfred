"""Unit tests for the agentic harness core: types, registry, sandbox, loop, verifier."""

from __future__ import annotations

import json

import pytest

from jarvisx.agentic.backends import HeuristicBackend, ModelBackend, ScriptedBackend
from jarvisx.agentic.builtin_tools import build_default_tools
from jarvisx.agentic.harness import AgentHarness
from jarvisx.agentic.registry import (
    AgentToolRegistry,
    ToolValidationError,
    UnknownTool,
    validate_arguments,
)
from jarvisx.agentic.sandbox import PathEscape, SandboxedRunner, scrub_env
from jarvisx.agentic.trace import TraceRecorder, render_trace
from jarvisx.agentic.types import (
    Budget,
    ModelMessage,
    Observation,
    RunStatus,
    ToolCall,
    Usage,
)
from jarvisx.agentic.verifier import (
    CustomCheck,
    FileExistsCheck,
    NonEmptyOutputCheck,
    OutputContainsCheck,
    PythonAssertCheck,
    TestsPassCheck,
    Verifier,
)
from jarvisx.tools.tool_kernel import PermissionLevel


# --------------------------------------------------------------------------- #
# Budget
# --------------------------------------------------------------------------- #


def test_budget_flags_the_first_ceiling_breached():
    budget = Budget(max_steps=2, max_tool_calls=10, max_seconds=60.0, max_tokens=1000)
    assert budget.violation(Usage()) is None
    assert "max_steps" in budget.violation(Usage(steps=2))
    assert "max_tool_calls" in budget.violation(Usage(tool_calls=10))
    assert "max_seconds" in budget.violation(Usage(wall_seconds=61.0))
    assert "max_tokens" in budget.violation(Usage(prompt_tokens=600, completion_tokens=500))


def test_usage_merge_accumulates_all_counters():
    a = Usage(steps=1, tool_calls=2, prompt_tokens=10, completion_tokens=5, wall_seconds=1.0)
    b = Usage(steps=3, tool_calls=4, prompt_tokens=20, completion_tokens=7, wall_seconds=2.5)
    a.merge(b)
    assert (a.steps, a.tool_calls) == (4, 6)
    assert (a.prompt_tokens, a.completion_tokens) == (30, 12)
    assert a.wall_seconds == pytest.approx(3.5)


# --------------------------------------------------------------------------- #
# Schema validation
# --------------------------------------------------------------------------- #


def test_validate_arguments_accepts_a_conforming_payload():
    schema = {
        "type": "object",
        "properties": {"path": {"type": "string"}, "n": {"type": "integer"}},
        "required": ["path"],
    }
    validate_arguments(schema, {"path": "a.py", "n": 3})  # no raise


def test_validate_arguments_rejects_missing_required_and_bad_types():
    schema = {
        "type": "object",
        "properties": {"path": {"type": "string"}, "n": {"type": "integer"}},
        "required": ["path"],
    }
    with pytest.raises(ToolValidationError, match="missing required"):
        validate_arguments(schema, {})
    with pytest.raises(ToolValidationError, match="must be string"):
        validate_arguments(schema, {"path": 7})
    with pytest.raises(ToolValidationError, match="unexpected argument"):
        validate_arguments(schema, {"path": "a", "bogus": 1})


def test_validate_arguments_rejects_booleans_masquerading_as_integers():
    schema = {"type": "object", "properties": {"n": {"type": "integer"}}}
    with pytest.raises(ToolValidationError):
        validate_arguments(schema, {"n": True})


def test_validate_arguments_checks_enum_and_array_items():
    schema = {
        "type": "object",
        "properties": {
            "mode": {"type": "string", "enum": ["fast", "safe"]},
            "argv": {"type": "array", "items": {"type": "string"}},
        },
    }
    validate_arguments(schema, {"mode": "fast", "argv": ["ls", "-la"]})
    with pytest.raises(ToolValidationError, match="one of"):
        validate_arguments(schema, {"mode": "yolo"})
    with pytest.raises(ToolValidationError, match="must be string"):
        validate_arguments(schema, {"argv": ["ls", 3]})


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #


def test_registry_decorator_registers_and_derives_schema():
    registry = AgentToolRegistry()

    @registry.tool(name="greet", permission=PermissionLevel.SAFE)
    def greet(name: str, excited: bool = False) -> str:
        return f"hello {name}{'!' if excited else ''}"

    assert "greet" in registry
    schema = registry.get("greet").input_schema
    assert schema["required"] == ["name"]
    assert schema["properties"]["excited"]["type"] == "boolean"

    observation = registry.invoke(ToolCall(name="greet", arguments={"name": "al"}))
    assert observation.ok and observation.output == "hello al"


def test_registry_invoke_reports_unknown_tools_as_observations():
    registry = AgentToolRegistry()
    observation = registry.invoke(ToolCall(name="nope", arguments={}))
    assert not observation.ok
    assert "unknown tool" in (observation.error or "").lower()


def test_registry_invoke_reports_schema_violations_without_raising():
    registry = AgentToolRegistry()

    @registry.tool(name="needs_arg")
    def needs_arg(value: str) -> str:
        return value

    observation = registry.invoke(ToolCall(name="needs_arg", arguments={}))
    assert not observation.ok
    assert "schema violation" in observation.error


def test_registry_blocks_restricted_tools_by_policy():
    registry = AgentToolRegistry()

    @registry.tool(name="nuke", permission=PermissionLevel.RESTRICTED)
    def nuke() -> str:
        return "boom"

    observation = registry.invoke(ToolCall(name="nuke", arguments={}))
    assert observation.denied and not observation.ok


def test_registry_confirm_tier_needs_an_explicit_approver():
    registry = AgentToolRegistry()

    @registry.tool(name="deploy", permission=PermissionLevel.CONFIRM)
    def deploy() -> str:
        return "deployed"

    call = ToolCall(name="deploy", arguments={})
    assert registry.invoke(call).denied  # no approver -> denied
    assert registry.invoke(call, approve=lambda tool, args: False).denied
    assert registry.invoke(call, approve=lambda tool, args: True).ok


def test_registry_handler_exceptions_become_model_readable_errors():
    registry = AgentToolRegistry()

    @registry.tool(name="kaboom")
    def kaboom() -> str:
        raise RuntimeError("intentional")

    observation = registry.invoke(ToolCall(name="kaboom", arguments={}))
    assert not observation.ok
    assert "intentional" in observation.error


def test_registry_openai_schema_shape():
    with SandboxedRunner() as sandbox:
        registry = build_default_tools(sandbox)
        schemas = registry.openai_schemas()
    assert all(s["type"] == "function" for s in schemas)
    names = {s["function"]["name"] for s in schemas}
    assert {"write_file", "read_file", "python_exec", "run_tests", "final_answer"} <= names


# --------------------------------------------------------------------------- #
# Sandbox
# --------------------------------------------------------------------------- #


def test_sandbox_runs_python_and_reports_real_exit_codes():
    with SandboxedRunner() as sandbox:
        good = sandbox.run_python("print('hello sandbox')")
        assert good.ok and good.exit_code == 0
        assert "hello sandbox" in good.stdout

        bad = sandbox.run_python("raise SystemExit(3)")
        assert not bad.ok and bad.exit_code == 3


def test_sandbox_rejects_paths_that_escape_the_jail():
    with SandboxedRunner() as sandbox:
        with pytest.raises(PathEscape):
            sandbox.resolve("../../etc/passwd")
        with pytest.raises(PathEscape):
            sandbox.write_file("../escaped.txt", "nope")


def test_sandbox_lists_only_workspace_files():
    with SandboxedRunner() as sandbox:
        sandbox.write_file("pkg/mod.py", "X = 1\n")
        sandbox.write_file("README.md", "# hi\n")
        assert sandbox.list_files() == ["README.md", "pkg/mod.py"]


def test_sandbox_enforces_timeout():
    with SandboxedRunner(timeout_seconds=1) as sandbox:
        result = sandbox.run_python("import time; time.sleep(10)")
        assert result.timed_out and not result.ok


def test_sandbox_runs_pytest_for_real():
    with SandboxedRunner() as sandbox:
        sandbox.write_file("lib.py", "def add(a, b):\n    return a + b\n")
        sandbox.write_file(
            "test_lib.py",
            "from lib import add\n\n\ndef test_add():\n    assert add(2, 3) == 5\n",
        )
        passing = sandbox.run_pytest("test_lib.py")
        assert passing.ok, passing.summary()

        sandbox.write_file(
            "test_broken.py", "def test_wrong():\n    assert 1 == 2\n"
        )
        failing = sandbox.run_pytest(".")
        assert not failing.ok


def test_sandbox_scrubs_secrets_from_child_environment(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-super-secret")
    monkeypatch.setenv("MY_DB_PASSWORD", "hunter2")
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_xxx")
    monkeypatch.setenv("PLAIN_SETTING", "keep-me")

    env = scrub_env()
    assert "OPENAI_API_KEY" not in env
    assert "MY_DB_PASSWORD" not in env
    assert "GITHUB_TOKEN" not in env
    assert env.get("PLAIN_SETTING") == "keep-me"
    assert "sk-super-secret" not in " ".join(env.values())


def test_sandbox_result_summary_is_compact_and_informative():
    with SandboxedRunner() as sandbox:
        result = sandbox.run_python(
            "print('x' * 5000)\nimport sys\nprint('boom-marker', file=sys.stderr)"
        )
        summary = result.summary(max_chars=100)
        assert "exit_code=0" in summary
        assert "boom-marker" in summary
        # 5000 chars of 'x' must not survive the 100-char cap.
        assert len(summary) < 400


# --------------------------------------------------------------------------- #
# Verifier
# --------------------------------------------------------------------------- #


def _finished_run(output: str = "done"):
    from jarvisx.agentic.types import RunResult

    return RunResult(run_id="run_x", task="t", status=RunStatus.SUCCEEDED, output=output)


def test_verifier_with_no_checks_trusts_run_status():
    with SandboxedRunner() as sandbox:
        verdict = Verifier().verify(_finished_run(), sandbox)
    assert verdict.passed and "no checks configured" in verdict.rationale


def test_python_assert_check_runs_real_code():
    with SandboxedRunner() as sandbox:
        ok = PythonAssertCheck("assert 2 + 2 == 4").run(_finished_run(), sandbox)
        bad = PythonAssertCheck("assert 2 + 2 == 5").run(_finished_run(), sandbox)
    assert ok.passed and not bad.passed


def test_tests_pass_check_detects_a_failing_suite():
    with SandboxedRunner() as sandbox:
        sandbox.write_file("test_ok.py", "def test_ok():\n    assert True\n")
        assert TestsPassCheck("test_ok.py").run(_finished_run(), sandbox).passed

        sandbox.write_file("test_bad.py", "def test_bad():\n    assert False\n")
        assert not TestsPassCheck(".").run(_finished_run(), sandbox).passed


def test_file_exists_and_output_checks():
    with SandboxedRunner() as sandbox:
        sandbox.write_file("present.txt", "hi\n")
        assert FileExistsCheck("present.txt").run(_finished_run(), sandbox).passed
        assert not FileExistsCheck("absent.txt").run(_finished_run(), sandbox).passed

        run = _finished_run(output="the answer is 42")
        assert OutputContainsCheck(["answer", "42"]).run(run, sandbox).passed
        assert not OutputContainsCheck(["nope"]).run(run, sandbox).passed
        assert NonEmptyOutputCheck(min_chars=5).run(run, sandbox).passed
        assert not NonEmptyOutputCheck(min_chars=999).run(run, sandbox).passed


def test_verifier_scores_by_weight_and_requires_all():
    with SandboxedRunner() as sandbox:
        verifier = Verifier(
            [
                NonEmptyOutputCheck(weight=1.0),
                PythonAssertCheck("assert False", weight=3.0),
            ]
        )
        verdict = verifier.verify(_finished_run(), sandbox)
    assert not verdict.passed
    assert verdict.score == pytest.approx(0.25)
    assert "1/2 checks passed" in verdict.rationale


def test_verifier_from_config_skips_unknown_check_types():
    verifier = Verifier.from_config(
        [{"type": "nonempty_output"}, {"type": "invented_check"}, {"type": "json_output"}]
    )
    assert [type(c).__name__ for c in verifier.checks] == [
        "NonEmptyOutputCheck",
        "JsonOutputCheck",
    ]


def test_custom_check_wraps_a_predicate_and_swallows_exceptions():
    with SandboxedRunner() as sandbox:
        good = CustomCheck(lambda r, s: True, name="always").run(_finished_run(), sandbox)
        boom = CustomCheck(lambda r, s: 1 / 0, name="boom").run(_finished_run(), sandbox)
    assert good.passed
    assert not boom.passed and "ZeroDivisionError" in boom.evidence


# --------------------------------------------------------------------------- #
# Tracing
# --------------------------------------------------------------------------- #


def test_trace_records_replays_and_summarizes(tmp_path):
    recorder = TraceRecorder("run_1", root=tmp_path)
    recorder.emit("run_start", task="do a thing")
    recorder.emit("step", index=1, thought="thinking", tool_calls=[], observations=[])
    recorder.emit("run_end", status="succeeded", steps=1, tool_calls=0)

    events = TraceRecorder.read(recorder.path)
    assert [e["kind"] for e in events] == ["run_start", "step", "run_end"]
    assert [e["seq"] for e in events] == [1, 2, 3]

    summary = TraceRecorder.summarize(recorder.path)
    assert summary["events"] == 3
    assert summary["by_kind"]["step"] == 1
    assert summary["final"]["status"] == "succeeded"

    rendered = render_trace(recorder.path)
    assert "step 1" in rendered and "thinking" in rendered


def test_trace_skips_corrupt_lines(tmp_path):
    path = tmp_path / "broken.jsonl"
    path.write_text('{"kind": "a"}\nnot json at all\n{"kind": "b"}\n', encoding="utf-8")
    assert [e["kind"] for e in TraceRecorder.read(path)] == ["a", "b"]


def test_trace_listener_receives_events_but_cannot_break_the_run(tmp_path):
    def exploding_listener(_event):
        raise RuntimeError("listener blew up")

    recorder = TraceRecorder("run_2", root=tmp_path, on_event=exploding_listener)
    recorder.emit("run_start")  # must not raise
    assert len(recorder.events) == 1


# --------------------------------------------------------------------------- #
# Harness loop
# --------------------------------------------------------------------------- #


def _harness(responses, tmp_path, **kwargs):
    sandbox = SandboxedRunner()
    registry = kwargs.pop("registry", None) or build_default_tools(sandbox)
    harness = AgentHarness(
        backend=ScriptedBackend(responses),
        registry=registry,
        sandbox=sandbox,
        trace_root=tmp_path,
        **kwargs,
    )
    return harness, sandbox


def test_harness_completes_a_tool_call_cycle(tmp_path):
    harness, sandbox = _harness(
        [
            ModelMessage(
                content="writing the file",
                tool_calls=[
                    ToolCall(name="write_file", arguments={"path": "a.py", "content": "A = 1\n"})
                ],
                finish_reason="tool_calls",
            ),
            ModelMessage(content="wrote a.py with A = 1", finish_reason="stop"),
        ],
        tmp_path,
    )
    result = harness.run("create a.py")
    assert result.status is RunStatus.SUCCEEDED
    assert result.output == "wrote a.py with A = 1"
    assert result.usage.steps == 2 and result.usage.tool_calls == 1
    assert sandbox.read_file("a.py") == "A = 1\n"
    sandbox.cleanup()


def test_harness_feeds_tool_errors_back_so_the_model_can_recover(tmp_path):
    harness, sandbox = _harness(
        [
            ModelMessage(
                content="reading something that is not there",
                tool_calls=[ToolCall(name="read_file", arguments={"path": "missing.py"})],
            ),
            ModelMessage(content="file was missing, nothing to do", finish_reason="stop"),
        ],
        tmp_path,
    )
    result = harness.run("read missing.py")
    assert result.status is RunStatus.SUCCEEDED
    first_error = result.steps[0].observations[0]
    assert not first_error.ok
    assert "No such file or directory" in (first_error.error or "")
    sandbox.cleanup()


def test_harness_final_answer_tool_terminates_the_run(tmp_path):
    harness, sandbox = _harness(
        [
            ModelMessage(
                content="all done",
                tool_calls=[ToolCall(name="final_answer", arguments={"summary": "shipped it"})],
            ),
            ModelMessage(content="this should never be reached"),
        ],
        tmp_path,
    )
    result = harness.run("ship it")
    assert result.status is RunStatus.SUCCEEDED
    assert result.output == "shipped it"
    assert result.usage.steps == 1
    sandbox.cleanup()


def test_harness_stops_when_the_budget_is_exhausted(tmp_path):
    endless = ModelMessage(
        content="again",
        tool_calls=[ToolCall(name="list_files", arguments={})],
    )
    harness, sandbox = _harness([endless], tmp_path, budget=Budget(max_steps=3, max_seconds=60))
    result = harness.run("loop forever")
    assert result.status is RunStatus.BUDGET_EXCEEDED
    assert "max_steps" in result.error
    sandbox.cleanup()


def test_harness_loop_guard_breaks_a_stuck_agent(tmp_path):
    stuck = ModelMessage(
        content="retrying",
        tool_calls=[ToolCall(name="read_file", arguments={"path": "ghost.py"})],
    )
    harness, sandbox = _harness([stuck], tmp_path, repeat_limit=2, budget=Budget(max_steps=20))
    result = harness.run("read ghost.py over and over")
    assert result.status is RunStatus.FAILED
    assert "loop guard" in result.error
    sandbox.cleanup()


def test_harness_denies_confirm_tier_tools_without_an_approver(tmp_path):
    harness, sandbox = _harness(
        [
            ModelMessage(
                content="running a shell command",
                tool_calls=[ToolCall(name="shell", arguments={"command": ["ls"]})],
            ),
            ModelMessage(content="shell was blocked, stopping", finish_reason="stop"),
        ],
        tmp_path,
    )
    result = harness.run("run ls")
    observation = result.steps[0].observations[0]
    assert observation.denied
    sandbox.cleanup()


def test_harness_verification_failure_downgrades_a_successful_run(tmp_path):
    harness, sandbox = _harness(
        [ModelMessage(content="claiming success without evidence")],
        tmp_path,
        verifier=Verifier([PythonAssertCheck("assert 1 == 2")]),
    )
    result = harness.run("do something")
    assert result.status is RunStatus.FAILED
    assert result.verdict is not None and not result.verdict.passed
    assert "verification failed" in result.error
    sandbox.cleanup()


def test_harness_writes_a_replayable_trace(tmp_path):
    harness, sandbox = _harness(
        [
            ModelMessage(
                content="computing",
                tool_calls=[ToolCall(name="python_exec", arguments={"code": "print(1+1)"})],
            ),
            ModelMessage(content="the answer is 2"),
        ],
        tmp_path,
    )
    result = harness.run("what is 1+1")
    trace_file = tmp_path / f"{result.run_id}.jsonl"
    kinds = [e["kind"] for e in TraceRecorder.read(trace_file)]
    assert kinds[0] == "run_start" and kinds[-1] == "run_end"
    assert "tool_call" in kinds and "observation" in kinds
    sandbox.cleanup()


def test_harness_survives_a_backend_that_raises(tmp_path):
    from jarvisx.agentic.backends import BackendError

    class BrokenBackend(ModelBackend):
        name = "broken"

        def complete(self, messages, tools=None, temperature=0.2):
            raise BackendError("provider exploded")

    sandbox = SandboxedRunner()
    harness = AgentHarness(
        backend=BrokenBackend(),
        registry=build_default_tools(sandbox),
        sandbox=sandbox,
        trace_root=tmp_path,
    )
    result = harness.run("anything")
    assert result.status is RunStatus.FAILED
    assert "provider exploded" in result.error
    sandbox.cleanup()


def test_harness_records_token_usage_from_the_backend(tmp_path):
    harness, sandbox = _harness(
        [
            ModelMessage(
                content="first turn",
                tool_calls=[ToolCall(name="list_files", arguments={})],
                prompt_tokens=100,
                completion_tokens=20,
                model="m1",
            ),
            ModelMessage(
                content="second turn", prompt_tokens=150, completion_tokens=30, model="m1"
            ),
        ],
        tmp_path,
    )
    result = harness.run("count tokens")
    assert result.usage.steps == 2
    assert result.usage.prompt_tokens == 250
    assert result.usage.completion_tokens == 50
    assert result.steps[0].model == "m1"
    sandbox.cleanup()


# --------------------------------------------------------------------------- #
# Offline heuristic backend
# --------------------------------------------------------------------------- #


def test_heuristic_backend_drives_a_real_run_with_no_network(tmp_path):
    sandbox = SandboxedRunner()
    harness = AgentHarness(
        backend=HeuristicBackend(),
        registry=build_default_tools(sandbox),
        sandbox=sandbox,
        trace_root=tmp_path,
        budget=Budget(max_steps=6),
        verifier=Verifier([FileExistsCheck("generated_solution.py")]),
    )
    result = harness.run("Implement a small utility")
    assert result.status is RunStatus.SUCCEEDED
    assert "generated_solution.py" in sandbox.list_files()
    assert result.verdict.passed
    sandbox.cleanup()


def test_observation_render_truncates_huge_outputs():
    observation = Observation(tool="t", call_id="c", ok=True, output="x" * 10_000)
    rendered = observation.render(max_chars=100)
    assert len(rendered) < 300 and "truncated" in rendered


def test_run_result_serializes_to_json():
    harness_result_json = json.dumps(_finished_run().to_dict(), default=str)
    assert json.loads(harness_result_json)["run_id"] == "run_x"


def test_unknown_tool_error_message_lists_registered_tools():
    registry = AgentToolRegistry()

    @registry.tool(name="only_tool")
    def only_tool() -> str:
        return "x"

    with pytest.raises(UnknownTool, match="only_tool"):
        registry.get("other_tool")
