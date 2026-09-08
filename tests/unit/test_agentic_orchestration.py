"""Unit tests for the orchestration layer: graph, planner, roles, scheduler."""

from __future__ import annotations

import json
import threading

import pytest

from jarvisx.agentic.backends import HeuristicBackend, ModelBackend, ScriptedBackend
from jarvisx.agentic.graph import GraphError, TaskGraph
from jarvisx.agentic.planner import (
    AutoPlanner,
    HeuristicPlanner,
    LLMPlanner,
    extract_json,
)
from jarvisx.agentic.roles import RoleRegistry, RoleSpec
from jarvisx.agentic.sandbox import SandboxedRunner
from jarvisx.agentic.scheduler import Orchestrator
from jarvisx.agentic.trace import TraceRecorder
from jarvisx.agentic.types import Budget, ModelMessage, RunStatus, TaskNode, ToolCall


class StubBackend(ModelBackend):
    """Stateless, deterministic backend keyed on the task text.

    Thread-safe by construction, so parallel waves behave predictably.
    """

    name = "stub"

    def __init__(self, behaviour=None):
        self.behaviour = behaviour or {}
        self.lock = threading.Lock()
        self.calls: list[str] = []

    def complete(self, messages, tools=None, temperature: float = 0.2) -> ModelMessage:
        task = next(
            (m["content"] for m in messages if m.get("role") == "user"), ""
        ).lower()
        with self.lock:
            self.calls.append(task)

        # Second turn (an observation is already present) -> finish.
        if any(m.get("role") == "tool" for m in messages):
            return ModelMessage(content=f"finished: {task[:40]}", finish_reason="stop")

        action = self.behaviour.get(task.split("\n")[0][:40])
        if action == "fail":
            return ModelMessage(content="giving up", finish_reason="stop")
        if action == "write":
            return ModelMessage(
                content="writing",
                tool_calls=[
                    ToolCall(
                        name="write_file",
                        arguments={"path": "out.txt", "content": f"from {task[:20]}\n"},
                    )
                ],
            )
        return ModelMessage(content=f"handled {task[:40]}", finish_reason="stop")


# --------------------------------------------------------------------------- #
# TaskGraph
# --------------------------------------------------------------------------- #


def _node(node_id: str, deps=None, **kwargs) -> TaskNode:
    return TaskNode(id=node_id, instruction=f"do {node_id}", depends_on=list(deps or []), **kwargs)


def test_graph_computes_parallel_waves():
    graph = TaskGraph(
        [
            _node("a"),
            _node("b"),
            _node("c", deps=["a", "b"]),
            _node("d", deps=["c"]),
        ]
    )
    waves = [[n.id for n in wave] for wave in graph.waves()]
    assert waves == [["a", "b"], ["c"], ["d"]]


def test_graph_topological_order_respects_dependencies():
    graph = TaskGraph([_node("c", deps=["b"]), _node("b", deps=["a"]), _node("a")])
    assert [n.id for n in graph.topological_order()] == ["a", "b", "c"]


def test_graph_rejects_cycles():
    with pytest.raises(GraphError, match="cycle"):
        TaskGraph([_node("a", deps=["b"]), _node("b", deps=["a"])])


def test_graph_rejects_self_dependency():
    with pytest.raises(GraphError, match="depends on itself"):
        TaskGraph([_node("a", deps=["a"])])


def test_graph_rejects_unknown_dependencies():
    with pytest.raises(GraphError, match="unknown node"):
        TaskGraph([_node("a", deps=["ghost"])])


def test_graph_rejects_duplicate_ids():
    with pytest.raises(GraphError, match="duplicate"):
        TaskGraph([_node("a"), _node("a")])


def test_graph_finds_transitive_downstream_nodes():
    graph = TaskGraph(
        [_node("a"), _node("b", deps=["a"]), _node("c", deps=["b"]), _node("d")]
    )
    assert sorted(graph.downstream("a")) == ["b", "c"]
    assert graph.downstream("d") == []


def test_graph_render_shows_waves_and_roles():
    graph = TaskGraph([_node("a", role="coder"), _node("b", deps=["a"], role="tester")])
    rendered = graph.render()
    assert "wave 1" in rendered and "wave 2" in rendered
    assert "coder" in rendered and "tester" in rendered


def test_graph_to_dict_is_json_serializable():
    graph = TaskGraph([_node("a"), _node("b", deps=["a"])])
    payload = json.loads(json.dumps(graph.to_dict()))
    assert payload["waves"] == [["a"], ["b"]]


# --------------------------------------------------------------------------- #
# JSON extraction
# --------------------------------------------------------------------------- #


def test_extract_json_handles_fences_prose_and_bare_objects():
    assert extract_json('{"a": 1}') == {"a": 1}
    assert extract_json('```json\n{"a": 2}\n```') == {"a": 2}
    assert extract_json('Sure! Here you go:\n{"a": 3}\nHope that helps.') == {"a": 3}
    assert extract_json('```{"a": 4}```') == {"a": 4}


def test_extract_json_returns_none_for_garbage():
    assert extract_json("") is None
    assert extract_json("no json here at all") is None
    assert extract_json("[1, 2, 3]") is None  # array, not object


# --------------------------------------------------------------------------- #
# Planners
# --------------------------------------------------------------------------- #


def test_heuristic_planner_routes_by_intent():
    planner = HeuristicPlanner()
    assert [n.id for n in planner.plan("Implement a parser").nodes] == ["implement", "verify"]
    assert [n.id for n in planner.plan("Review this code").nodes] == ["review"]
    assert [n.id for n in planner.plan("Research caching options").nodes] == ["research"]
    assert [n.id for n in planner.plan("Do the thing").nodes] == ["execute"]


def test_heuristic_planner_wires_the_verify_dependency():
    graph = HeuristicPlanner().plan("Build a widget")
    verify = graph.get("verify")
    assert verify.depends_on == ["implement"]
    assert graph.waves()[1][0].id == "verify"


def test_llm_planner_parses_a_model_authored_plan():
    backend = ScriptedBackend(
        [
            ModelMessage(
                content=json.dumps(
                    {
                        "steps": [
                            {"id": "draft", "instruction": "draft it", "role": "coder"},
                            {
                                "id": "check",
                                "instruction": "check it",
                                "role": "tester",
                                "depends_on": ["draft"],
                                "verify": [{"type": "nonempty_output"}],
                            },
                        ]
                    }
                )
            )
        ]
    )
    graph = LLMPlanner(backend=backend).plan("make a thing")
    assert [n.id for n in graph.nodes] == ["draft", "check"]
    assert graph.get("check").depends_on == ["draft"]


def test_llm_planner_tolerates_fenced_json_with_commentary():
    backend = ScriptedBackend(
        [ModelMessage(content='Here is the plan:\n```json\n{"steps": [{"id": "only", "instruction": "x"}]}\n```')]
    )
    graph = LLMPlanner(backend=backend).plan("go")
    assert [n.id for n in graph.nodes] == ["only"]


def test_llm_planner_rewrites_unknown_roles_and_drops_bad_deps():
    backend = ScriptedBackend(
        [
            ModelMessage(
                content=json.dumps(
                    {
                        "steps": [
                            {"id": "a", "instruction": "x", "role": "wizard"},
                            {"id": "b", "instruction": "y", "depends_on": ["a", "ghost"]},
                        ]
                    }
                )
            )
        ]
    )
    graph = LLMPlanner(backend=backend).plan("go")
    assert graph.get("a").role == "generalist"
    assert graph.get("b").depends_on == ["a"]


def test_llm_planner_rejects_unparseable_plans():
    backend = ScriptedBackend([ModelMessage(content="I cannot help with that")])
    with pytest.raises(ValueError, match="no parseable JSON"):
        LLMPlanner(backend=backend).plan("go")


def test_llm_planner_rejects_plans_without_steps():
    backend = ScriptedBackend([ModelMessage(content='{"nope": true}')])
    with pytest.raises(ValueError, match="steps"):
        LLMPlanner(backend=backend).plan("go")


def test_llm_planner_always_attaches_a_default_check():
    backend = ScriptedBackend(
        [ModelMessage(content='{"steps": [{"id": "a", "instruction": "x"}]}')]
    )
    graph = LLMPlanner(backend=backend).plan("go")
    assert graph.get("a").verify == [{"type": "nonempty_output"}]


def test_auto_planner_falls_back_when_the_model_fails():
    planner = AutoPlanner(backend=ScriptedBackend([ModelMessage(content="nonsense")]))
    graph = planner.plan("Implement a thing")
    assert planner.last_strategy == "heuristic"
    assert [n.id for n in graph.nodes] == ["implement", "verify"]


def test_auto_planner_uses_the_model_when_it_returns_a_valid_plan():
    planner = AutoPlanner(
        backend=ScriptedBackend(
            [ModelMessage(content='{"steps": [{"id": "solo", "instruction": "x"}]}')]
        )
    )
    graph = planner.plan("do it")
    assert planner.last_strategy == "llm"
    assert [n.id for n in graph.nodes] == ["solo"]


# --------------------------------------------------------------------------- #
# Roles
# --------------------------------------------------------------------------- #


def test_role_registry_falls_back_to_generalist_for_unknown_roles():
    roles = RoleRegistry()
    assert roles.get("does_not_exist").name == "generalist"


def test_role_registry_holds_the_default_workforce():
    roles = RoleRegistry()
    assert {"generalist", "planner", "coder", "tester", "reviewer", "researcher"} <= set(
        roles.names()
    )


def test_role_system_prompt_injects_tools_without_format_explosions():
    spec = RoleSpec(name="x", title="X", focus="things with {braces} in them")
    prompt = spec.system_prompt("- tool_a: does stuff")
    assert "X" in prompt and "tool_a" in prompt and "{braces}" in prompt


def test_custom_role_can_be_registered():
    roles = RoleRegistry()
    roles.register(RoleSpec(name="auditor", title="Auditor", focus="compliance"))
    assert roles.get("auditor").title == "Auditor"


def test_role_to_dict_exposes_budget_envelope():
    payload = RoleRegistry().get("coder").to_dict()
    assert payload["budget"]["max_steps"] == 10
    assert "write_file" in payload["allowed_tools"]


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #


def test_orchestrator_runs_a_single_node_goal(tmp_path):
    with Orchestrator(
        backend=StubBackend(), sandbox=SandboxedRunner(), trace_root=tmp_path
    ) as orch:
        report = orch.run("Do the thing")
    assert report.ok
    assert report.succeeded == ["execute"]
    assert "handled" in report.final_output()


def test_orchestrator_passes_upstream_output_into_downstream_context(tmp_path):
    with Orchestrator(
        backend=StubBackend(), sandbox=SandboxedRunner(), trace_root=tmp_path
    ) as orch:
        graph = TaskGraph(
            [
                _node("first"),
                TaskNode(id="second", instruction="second step", depends_on=["first"]),
            ]
        )
        report = orch.run("chain", graph=graph)
    assert report.ok
    # RunResult.task holds the *composed* prompt, so it proves the upstream
    # output was injected into the downstream node's context.
    composed = report.outcomes["second"].result.task
    assert "Context from upstream steps" in composed
    assert "--- first ---" in composed
    # StubBackend answers "handled <task>", and the first node's task is "do first".
    assert "handled do first" in composed


def test_orchestrator_skips_everything_downstream_of_a_failure(tmp_path):
    with Orchestrator(
        backend=StubBackend(), sandbox=SandboxedRunner(), trace_root=tmp_path
    ) as orch:
        graph = TaskGraph(
            [
                TaskNode(id="bad", instruction="bad step"),
                TaskNode(id="next", instruction="next", depends_on=["bad"]),
                TaskNode(id="later", instruction="later", depends_on=["next"]),
            ]
        )
        # Force the first node to fail verification.
        from jarvisx.agentic.verifier import PythonAssertCheck, Verifier

        graph.get("bad").verify = [{"type": "python_assert", "code": "assert False"}]
        report = orch.run("doomed", graph=graph)

    assert not report.ok
    assert report.outcomes["bad"].status is RunStatus.FAILED
    assert report.outcomes["next"].status is RunStatus.SKIPPED
    assert report.outcomes["later"].status is RunStatus.SKIPPED
    assert "upstream failed" in report.outcomes["later"].error


def test_orchestrator_retries_a_node_before_giving_up(tmp_path):
    attempts: list[str] = []

    class FlakyBackend(ModelBackend):
        name = "flaky"

        def complete(self, messages, tools=None, temperature: float = 0.2) -> ModelMessage:
            task = next((m["content"] for m in messages if m.get("role") == "user"), "")
            attempts.append(task)
            if len(attempts) < 3:
                raise_runtime_error()
            return ModelMessage(content="recovered")

    def raise_runtime_error():
        from jarvisx.agentic.backends import BackendError

        raise BackendError("transient")

    with Orchestrator(
        backend=FlakyBackend(), sandbox=SandboxedRunner(), trace_root=tmp_path
    ) as orch:
        graph = TaskGraph([TaskNode(id="flaky", instruction="be flaky", max_retries=3)])
        report = orch.run("flaky goal", graph=graph)

    assert report.outcomes["flaky"].status is RunStatus.SUCCEEDED
    assert report.outcomes["flaky"].attempt == 3
    assert len(attempts) == 3


def test_orchestrator_runs_independent_nodes_in_parallel(tmp_path):
    concurrency = {"current": 0, "peak": 0}
    lock = threading.Lock()

    class SlowBackend(ModelBackend):
        name = "slow"

        def complete(self, messages, tools=None, temperature: float = 0.2) -> ModelMessage:
            import time

            with lock:
                concurrency["current"] += 1
                concurrency["peak"] = max(concurrency["peak"], concurrency["current"])
            time.sleep(0.15)
            with lock:
                concurrency["current"] -= 1
            return ModelMessage(content="done")

    with Orchestrator(
        backend=SlowBackend(),
        sandbox=SandboxedRunner(),
        trace_root=tmp_path,
        max_workers=4,
    ) as orch:
        graph = TaskGraph([_node("a"), _node("b"), _node("c")])
        report = orch.run("parallel goal", graph=graph)

    assert report.ok
    assert concurrency["peak"] >= 2, "independent nodes should overlap in time"


def test_orchestrator_rolls_up_resource_usage(tmp_path):
    with Orchestrator(
        backend=StubBackend({"do a": "write", "do b": "write"}),
        sandbox=SandboxedRunner(),
        trace_root=tmp_path,
    ) as orch:
        graph = TaskGraph([_node("a"), _node("b")])
        report = orch.run("two writes", graph=graph)
    assert report.usage.tool_calls == 2
    assert report.usage.steps == 4  # two nodes x (act + finalise)


def test_orchestrator_persists_a_report_and_per_run_traces(tmp_path):
    with Orchestrator(
        backend=StubBackend(), sandbox=SandboxedRunner(), trace_root=tmp_path
    ) as orch:
        report = orch.run("persist me")
        report_path = tmp_path / f"{report.graph_id}.orchestration.json"
        assert report_path.exists()
        payload = json.loads(report_path.read_text())

    assert payload["ok"] is True
    assert payload["succeeded"] == ["execute"]
    assert list(tmp_path.glob("*.jsonl")), "each node run should leave a trace"


def test_orchestrator_emits_lifecycle_events(tmp_path):
    seen: list[str] = []
    with Orchestrator(
        backend=StubBackend(),
        sandbox=SandboxedRunner(),
        trace_root=tmp_path,
        on_event=lambda e: seen.append(e["kind"]),
    ) as orch:
        orch.run("watch me")

    for expected in ("orchestration_start", "wave_start", "node_start", "node_end", "orchestration_end"):
        assert expected in seen, f"missing event {expected}"


def test_orchestrator_reuses_a_shared_sandbox_across_nodes(tmp_path):
    workspace = tmp_path / "shared"
    sandbox = SandboxedRunner(workspace=workspace)
    backend = StubBackend({"write a file": "write", "read what a wrote": "read"})
    with Orchestrator(backend=backend, sandbox=sandbox, trace_root=tmp_path) as orch:
        graph = TaskGraph(
            [
                TaskNode(
                    id="a",
                    instruction="write a file",
                ),
                TaskNode(id="b", instruction="read what a wrote", depends_on=["a"]),
            ]
        )
        report = orch.run("shared workspace", graph=graph)

    assert report.ok
    assert (workspace / "out.txt").exists()
    sandbox.cleanup()


def test_orchestrator_report_serializes_cleanly(tmp_path):
    with Orchestrator(
        backend=StubBackend(), sandbox=SandboxedRunner(), trace_root=tmp_path
    ) as orch:
        report = orch.run("serialize me")
    payload = json.loads(json.dumps(report.to_dict(), default=str))
    assert payload["goal"] == "serialize me"
    assert payload["duration_seconds"] >= 0


def test_orchestrator_offline_backend_completes_a_real_coding_chain(tmp_path):
    """End-to-end: heuristic planner + heuristic backend + real file on disk."""
    workspace = tmp_path / "ws"
    sandbox = SandboxedRunner(workspace=workspace)
    with Orchestrator(
        backend=HeuristicBackend(), sandbox=sandbox, trace_root=tmp_path
    ) as orch:
        report = orch.run("Implement a helper and verify it")

    assert report.ok, [
        (n, o.status.value, o.error) for n, o in report.outcomes.items()
    ]
    assert (workspace / "generated_solution.py").exists()
    sandbox.cleanup()
