"""Tests for the agentic control plane (HTTP API) and the CLI."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from jarvisx.agentic import cli
from jarvisx.agentic.backends import HeuristicBackend
from jarvisx.agentic.control_plane import ControlPlane, _make_handler
from jarvisx.agentic.sandbox import SandboxedRunner


@pytest.fixture()
def server(tmp_path):
    """Start the control plane on an ephemeral port and tear it down after."""
    sandbox = SandboxedRunner(workspace=tmp_path / "ws")
    plane = ControlPlane(
        backend=HeuristicBackend(),
        trace_root=tmp_path / "traces",
        sandbox=sandbox,
        intake_path=tmp_path / "intake.json",
    )
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _make_handler(plane))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    try:
        yield base, plane
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)
        sandbox.cleanup()


def _get(url: str):
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode())


def _post(url: str, payload: dict):
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode())


def test_index_lists_the_available_endpoints(server):
    base, _ = server
    status, body = _get(f"{base}/")
    assert status == 200
    assert "POST /run" in body["endpoints"]


def test_health_reports_backend_and_paths(server):
    base, plane = server
    status, body = _get(f"{base}/health")
    assert status == 200
    assert body["status"] == "ok"
    assert body["backend"] == "heuristic"
    assert body["sandbox"] == str(plane.sandbox.workspace)


def test_tools_endpoint_exposes_the_harness_toolset(server):
    base, _ = server
    status, body = _get(f"{base}/tools")
    assert status == 200
    names = {tool["name"] for tool in body["tools"]}
    assert {"write_file", "read_file", "python_exec", "run_tests"} <= names
    assert body["count"] == len(body["tools"])


def test_roles_endpoint_exposes_the_workforce(server):
    base, _ = server
    status, body = _get(f"{base}/roles")
    assert status == 200
    names = {role["name"] for role in body["roles"]}
    assert {"generalist", "coder", "tester"} <= names


def test_plan_endpoint_returns_a_graph_without_executing(server):
    base, plane = server
    status, body = _post(f"{base}/plan", {"goal": "Implement a thing"})
    assert status == 200
    assert [n["id"] for n in body["graph"]["nodes"]] == ["implement", "verify"]
    assert body["graph"]["waves"] == [["implement"], ["verify"]]


def test_run_endpoint_executes_and_reports(server):
    base, plane = server
    status, body = _post(f"{base}/run", {"goal": "Implement a small utility"})
    assert status == 200
    assert body["ok"] is True
    assert "implement" in body["succeeded"]
    assert (plane.sandbox.workspace / "generated_solution.py").exists()


def test_run_endpoint_honours_a_tight_budget(server):
    base, _ = server
    status, body = _post(
        f"{base}/run",
        {"goal": "Implement a thing", "max_steps": 0},
    )
    assert status == 200
    assert body["ok"] is False


def test_tasks_endpoint_runs_a_single_agent(server):
    base, plane = server
    status, body = _post(f"{base}/tasks", {"task": "Implement a helper", "role": "coder"})
    assert status == 200
    assert body["status"] == "succeeded"
    assert "workspace_files" in body


def test_runs_endpoint_lists_recorded_traces(server):
    base, _ = server
    _post(f"{base}/run", {"goal": "Implement something"})
    status, body = _get(f"{base}/runs")
    assert status == 200
    assert body["count"] >= 1
    assert all("run_id" in run for run in body["runs"])


def test_trace_endpoint_replays_a_recorded_run(server):
    base, _ = server
    _post(f"{base}/tasks", {"task": "Implement a helper"})
    _, listing = _get(f"{base}/runs")
    run_id = listing["runs"][0]["run_id"]

    status, body = _get(f"{base}/runs/{run_id}/trace")
    assert status == 200
    kinds = [event["kind"] for event in body["events"]]
    assert kinds[0] == "run_start" and kinds[-1] == "run_end"


def test_trace_endpoint_404s_for_unknown_runs(server):
    base, _ = server
    status, body = _get(f"{base}/runs/does_not_exist/trace")
    assert status == 404
    assert "no trace" in body["error"]


def test_endpoints_reject_missing_payloads(server):
    base, _ = server
    assert _post(f"{base}/run", {})[0] == 400
    assert _post(f"{base}/plan", {})[0] == 400
    assert _post(f"{base}/tasks", {})[0] == 400


def test_unknown_paths_return_404(server):
    base, _ = server
    status, body = _get(f"{base}/nonsense")
    assert status == 404
    assert "unknown path" in body["error"]


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def test_cli_roles_lists_the_workforce(capsys):
    assert cli.main(["roles"]) == 0
    out = capsys.readouterr().out
    assert "generalist" in out and "reviewer" in out


def test_cli_tools_lists_the_toolset(capsys):
    assert cli.main(["tools"]) == 0
    out = capsys.readouterr().out
    assert "write_file" in out and "SAFE" in out


def test_cli_plan_renders_a_graph(capsys, tmp_path):
    code = cli.main(
        [
            "plan",
            "Implement a parser",
            "--backend",
            "offline",
            "--trace-root",
            str(tmp_path),
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "Task graph" in out and "implement" in out and "verify" in out


def test_cli_plan_json_emits_machine_readable_output(capsys, tmp_path):
    cli.main(
        [
            "plan",
            "Implement a parser",
            "--backend",
            "offline",
            "--json",
            "--trace-root",
            str(tmp_path),
        ]
    )
    out = capsys.readouterr().out
    payload = json.loads(out[out.index("{") : out.rindex("}") + 1])
    assert payload["waves"] == [["implement"], ["verify"]]


def test_cli_run_executes_and_exits_zero_on_success(capsys, tmp_path):
    code = cli.main(
        [
            "run",
            "Implement a small utility",
            "--backend",
            "offline",
            "--trace-root",
            str(tmp_path),
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "WAVE 1" in out and "DONE" in out
    assert list(tmp_path.glob("*.orchestration.json")), "report should be written"


def test_cli_task_runs_one_agent(capsys, tmp_path):
    code = cli.main(
        [
            "task",
            "Implement a helper",
            "--role",
            "coder",
            "--backend",
            "offline",
            "--trace-root",
            str(tmp_path),
        ]
    )
    assert code == 0
    assert "succeeded" in capsys.readouterr().out


def test_cli_runs_lists_then_trace_renders(capsys, tmp_path):
    cli.main(
        [
            "task",
            "Implement a helper",
            "--backend",
            "offline",
            "--trace-root",
            str(tmp_path),
        ]
    )
    capsys.readouterr()

    assert cli.main(["runs", "--trace-root", str(tmp_path)]) == 0
    listing = capsys.readouterr().out
    assert "recorded runs" in listing

    trace_file = next(tmp_path.glob("*.jsonl"))
    assert cli.main(["trace", str(trace_file)]) == 0
    rendered = capsys.readouterr().out
    assert "run_start" in rendered and "run_end" in rendered


def test_cli_trace_fails_cleanly_for_a_missing_file(capsys):
    assert cli.main(["trace", "/nonexistent/trace.jsonl"]) == 2


def test_cli_run_exits_nonzero_when_verification_fails(capsys, tmp_path):
    """A goal whose verification cannot pass must not report success."""
    code = cli.main(
        [
            "run",
            "Implement a thing",
            "--backend",
            "offline",
            "--max-steps",
            "0",
            "--trace-root",
            str(tmp_path),
        ]
    )
    assert code == 1


def test_cli_parser_requires_a_subcommand():
    with pytest.raises(SystemExit):
        cli.main([])


# --------------------------------------------------------------------------- #
# CLI: intake commands
# --------------------------------------------------------------------------- #

DUMP = (
    "um i need to write the OS assignment its due today, "
    "also reply to that email from the professor, "
    "oh and i'm worried about failing, someone should fix the printer"
)


def test_cli_next_captures_each_item_exactly_once(capsys, tmp_path):
    """Regression: cmd_next captured twice because plan() captures internally."""
    state = str(tmp_path / "intake.json")
    assert cli.main(["next", "--dump", DUMP, "--energy", "low", "--state", state]) == 0
    capsys.readouterr()

    payload = json.loads(Path(state).read_text())
    assert len(payload["items"]) == 4, "a brain dump must not be recorded twice"


def test_cli_next_prints_a_single_next_action(capsys, tmp_path):
    cli.main(["next", "--dump", DUMP, "--energy", "low", "--state", str(tmp_path / "s.json")])
    out = capsys.readouterr().out
    assert "DO THIS NEXT" in out
    assert "email" in out.lower(), "low energy should pick the small task"
    assert "1." in out and "2." in out


def test_cli_next_separates_out_things_that_are_not_yours(capsys, tmp_path):
    cli.main(["next", "--dump", DUMP, "--state", str(tmp_path / "s.json")])
    out = capsys.readouterr().out
    assert "not yours" in out


def test_cli_next_with_no_dump_and_no_state_exits_nonzero(capsys, tmp_path):
    assert cli.main(["next", "--state", str(tmp_path / "empty.json")]) == 1
    assert "Nothing captured" in capsys.readouterr().out


def test_cli_talk_runs_a_scripted_conversation(capsys, tmp_path, monkeypatch):
    state = str(tmp_path / "intake.json")
    monkeypatch.setattr("builtins.input", _scripted_input([DUMP, "what should I do", "quit"]))

    assert cli.main(["talk", "--text", "--energy", "low", "--state", state]) == 0
    out = capsys.readouterr().out
    assert "Do this one" in out
    assert "Stopping" in out

    payload = json.loads(Path(state).read_text())
    assert len(payload["items"]) == 4


def test_cli_talk_persists_and_reloads_state(capsys, tmp_path, monkeypatch):
    state = str(tmp_path / "intake.json")
    monkeypatch.setattr("builtins.input", _scripted_input([DUMP, "quit"]))
    cli.main(["talk", "--text", "--state", state])
    capsys.readouterr()

    # Second session must see the first session's items, not duplicate them.
    monkeypatch.setattr("builtins.input", _scripted_input(["status", "quit"]))
    cli.main(["talk", "--text", "--state", state])
    out = capsys.readouterr().out

    assert "4 open items" in out
    payload = json.loads(Path(state).read_text())
    assert len(payload["items"]) == 4


# --------------------------------------------------------------------------- #
# CLI: watch
# --------------------------------------------------------------------------- #


def test_cli_watch_demo_terminates_without_a_tick_cap(capsys, tmp_path):
    """Regression: --demo with no --ticks polled an exhausted source forever."""
    code = cli.main(
        [
            "watch",
            "--demo",
            "--interval",
            "0",
            "--switch-threshold",
            "4",
            "--state",
            str(tmp_path / "s.json"),
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "fragmented" in out
    assert "Session" in out


def test_cli_watch_demo_reports_session_summary(capsys, tmp_path):
    cli.main(["watch", "--demo", "--interval", "0", "--state", str(tmp_path / "s.json")])
    out = capsys.readouterr().out
    assert "samples" in out and "app switches" in out


def test_cli_watch_without_sensors_exits_nonzero(capsys, tmp_path):
    code = cli.main(["watch", "--no-sensors", "--state", str(tmp_path / "s.json")])
    assert code == 1
    assert "nothing to watch" in capsys.readouterr().out


def test_cli_watch_states_the_task(capsys, tmp_path):
    cli.main(
        [
            "watch",
            "--demo",
            "--interval",
            "0",
            "--task",
            "write the OS assignment",
            "--state",
            str(tmp_path / "s.json"),
        ]
    )
    assert "write the OS assignment" in capsys.readouterr().out


def _scripted_input(lines):
    iterator = iter(lines)

    def fake_input(prompt=""):
        try:
            return next(iterator)
        except StopIteration:
            raise EOFError from None

    return fake_input


# --------------------------------------------------------------------------- #
# alfred: the whole agent at once
# --------------------------------------------------------------------------- #


def test_cli_alfred_splits_a_blob_and_persists_it(tmp_path, monkeypatch, capsys):
    """A comma-separated blob must land as several small tasks, not one big one."""
    state = tmp_path / "intake.json"
    monkeypatch.setattr(
        "builtins.input",
        _scripted_input(["write the assignment, pay the bill, call mom", "status", "quit"]),
    )
    assert cli.main([
        "alfred", "--text", "--no-agent", "--no-watch", "--state", str(state),
    ]) == 0
    titles = [i["title"] for i in json.loads(state.read_text(encoding="utf-8"))["items"]]
    assert len(titles) == 3, titles
    assert "Pay the bill" in titles


def test_cli_alfred_reports_what_came_up(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", _scripted_input(["quit"]))
    cli.main([
        "alfred", "--text", "--no-agent", "--no-watch",
        "--state", str(tmp_path / "intake.json"),
    ])
    out = capsys.readouterr().out
    # Honest self-report: no sensors in this sandbox, so it must say so rather
    # than pretend a microphone and a screen reader came up.
    for line in ("ears", "mouth", "eyes", "hands"):
        assert line in out


def test_cli_alfred_rejects_a_bad_energy_level(tmp_path, capsys):
    # argparse rejects an unknown --energy at parse time via SystemExit.
    with pytest.raises(SystemExit) as raised:
        cli.main([
            "alfred", "--energy", "massive", "--no-watch",
            "--state", str(tmp_path / "intake.json"),
        ])
    assert raised.value.code != 0


def test_cli_alfred_restores_the_previous_session(tmp_path, monkeypatch):
    state = tmp_path / "intake.json"
    monkeypatch.setattr(
        "builtins.input",
        _scripted_input(["write the report, pay the bill", "quit"]),
    )
    cli.main(["alfred", "--text", "--no-agent", "--no-watch", "--state", str(state)])

    monkeypatch.setattr("builtins.input", _scripted_input(["status", "quit"]))
    cli.main(["alfred", "--text", "--no-agent", "--no-watch", "--state", str(state)])
    items = json.loads(state.read_text(encoding="utf-8"))["items"]
    assert len(items) == 2, [i["title"] for i in items]


# --------------------------------------------------------------------------- #
# /intake: the shared task list over HTTP, and the dashboard
# --------------------------------------------------------------------------- #


def test_intake_starts_empty_and_honest(server):
    base, _ = server
    code, body = _get(f"{base}/intake")
    assert code == 200
    assert body["items"] == []
    assert body["next_at_energy"]["low"] is None


def test_capture_splits_a_blob_and_shows_it(server):
    base, plane = server
    _post(f"{base}/intake", {"dump": "write the assignment, pay the bill, call mom"})
    _, body = _get(f"{base}/intake")
    assert len(body["items"]) == 3, body["items"]
    # The dashboard reads this file, so capture must actually persist.
    assert plane.intake_path.exists()


def test_capture_requires_a_dump(server):
    base, _ = server
    code, body = _post(f"{base}/intake", {})
    assert code == 400
    assert "dump" in body["error"]


def test_energy_changes_what_is_offered(server):
    """The whole point: low energy never offers the scary task."""
    base, _ = server
    _post(f"{base}/intake", {"dump": "write the OS assignment its due today, pay the bill"})
    _, body = _get(f"{base}/intake")
    assert "Pay the bill" in body["next_at_energy"]["low"]["title"]
    assert "OS assignment" in body["next_at_energy"]["high"]["title"]


def test_completing_an_item_offers_the_next_one(server):
    base, _ = server
    _post(f"{base}/intake", {"dump": "write the report, pay the bill"})
    _, body = _get(f"{base}/intake")
    target = body["next_at_energy"]["low"]
    code, done = _post(f"{base}/intake/{target['id']}/done", {})
    assert code == 200 and done["ok"]
    assert done["next"] is not None
    _, after = _get(f"{base}/intake")
    assert after["tasks_open"] == 1


def test_completing_an_unknown_item_is_a_404(server):
    base, _ = server
    code, body = _post(f"{base}/intake/does-not-exist/done", {})
    assert code == 404
    assert "error" in body


def test_not_your_problem_is_called_out(server):
    base, _ = server
    _post(f"{base}/intake", {"dump": "pay the bill, i'm worried about failing, someone should fix the printer"})
    _, body = _get(f"{base}/intake")
    kinds = {i["kind"] for i in body["not_your_problem"]}
    assert kinds == {"worry", "delegate"}, kinds


def test_dashboard_is_served_to_a_browser_and_json_to_everyone_else(server):
    base, _ = server
    request = urllib.request.Request(f"{base}/", headers={"Accept": "text/html"})
    with urllib.request.urlopen(request, timeout=10) as response:
        html = response.read().decode()
        assert response.status == 200
        assert "text/html" in response.headers["Content-Type"]
    assert "do this next" in html
    assert "dump your head" in html

    # A curl or a test client with no Accept header still gets the API index.
    code, body = _get(f"{base}/")
    assert code == 200
    assert "GET /intake" in body["endpoints"]


def test_intake_endpoints_are_listed_on_the_index(server):
    base, _ = server
    _, body = _get(f"{base}/")
    for endpoint in ("GET /intake", "POST /intake", "POST /intake/{item_id}/done"):
        assert endpoint in body["endpoints"], endpoint


# --------------------------------------------------------------------------- #
# alfred: persona and physical reach
# --------------------------------------------------------------------------- #

from jarvisx.agentic.voice_loop import ConsoleInput as _ConsoleInput
from jarvisx.agentic.voice_loop import ConsoleOutput as _ConsoleOutput


def test_cli_alfred_speaks_in_the_chosen_persona(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", _scripted_input(["quit"]))
    cli.main([
        "alfred", "--text", "--persona", "stark", "--no-agent", "--no-watch",
        "--state", str(tmp_path / "intake.json"),
    ])
    out = capsys.readouterr().out
    assert "stark -> text" in out


def test_cli_alfred_rejects_an_unknown_persona(tmp_path):
    with pytest.raises(SystemExit):
        cli.main([
            "alfred", "--persona", "ultron", "--no-watch",
            "--state", str(tmp_path / "intake.json"),
        ])


def test_cli_alfred_has_no_physical_reach_by_default(tmp_path, monkeypatch):
    """An assistant that can touch your machine must be asked to."""
    from jarvisx.agentic.runtime import AlfredRuntime, RuntimeConfig

    runtime = AlfredRuntime(
        RuntimeConfig(force_text=True, watch=False),
        stt=_ConsoleInput(lines=["quit"]), tts=_ConsoleOutput(),
    )
    assert runtime.config.enable_physical is False
    assert not any("physical reach" in n for n in runtime.status.notes)


def test_physical_reach_is_reported_when_enabled(tmp_path):
    from jarvisx.agentic.runtime import AlfredRuntime, RuntimeConfig

    runtime = AlfredRuntime(
        RuntimeConfig(
            force_text=True, watch=False, enable_agent=True,
            enable_physical=True, physical_dry_run=True,
        ),
        stt=_ConsoleInput(lines=["quit"]), tts=_ConsoleOutput(),
    )
    assert any("physical reach ON" in n for n in runtime.status.notes)
    assert any("dry run" in n for n in runtime.status.notes)
