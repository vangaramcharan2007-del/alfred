"""Tests for the physical action layer: policy gate, target resolution, tools.

The security assertions are the ones that matter. A harness with physical reach
and a soft policy gate is worse than no physical reach at all, so "blocked even
when confirmation is granted" is tested explicitly rather than assumed.
"""

from __future__ import annotations

import os

import pytest

from jarvisx.agentic.actions import (
    build_action_tools,
    classify_command,
    resolve_target,
)
from jarvisx.agentic.types import ToolCall

GRANT_ALL = lambda tool, args: True  # noqa: E731


def _invoke(reg, name, args, approve=GRANT_ALL):
    return reg.invoke(ToolCall(name=name, arguments=args), approve=approve)


# --------------------------------------------------------------------------- #
# Policy gate
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "command",
    [
        "rm -rf /",
        "rm -rf ~",
        "rm -fr /home",
        "format c:",
        "shutdown now",
        "reboot",
        "rd /s /q C:\\stuff",
        "mkfs /dev/sda1",
        "dd if=/dev/zero of=/dev/sda",
        "Remove-Item C:\\stuff -Recurse -Force",
    ],
)
def test_destructive_commands_are_blocked(command):
    assert classify_command(command) == "blocked"


@pytest.mark.parametrize(
    "command",
    ["sudo apt install x", "git push origin main", "kill -9 1234", "chmod 777 x", "npm publish"],
)
def test_privileged_commands_need_confirmation(command):
    assert classify_command(command) == "confirm"


@pytest.mark.parametrize("command", ["ls -la", "echo hello", "git status", "python x.py"])
def test_ordinary_commands_are_allowed(command):
    assert classify_command(command) == "allow"


def test_an_empty_command_is_blocked():
    assert classify_command("") == "blocked"
    assert classify_command("   ") == "blocked"


def test_blocked_commands_are_refused_even_when_confirmation_is_granted():
    """The gate that matters: a human yes must not unlock a destructive command."""
    reg = build_action_tools(dry_run=True, confirm=lambda prompt: True)
    for command in ["rm -rf /", "format c:", "shutdown now"]:
        obs = _invoke(reg, "run_system_command", {"command": command})
        assert not obs.ok, command
        assert "destructive pattern" in (obs.error or ""), obs.error


def test_confirm_commands_are_refused_without_a_human_yes():
    reg = build_action_tools(dry_run=True, confirm=lambda prompt: False)
    obs = _invoke(reg, "run_system_command", {"command": "sudo apt install x"})
    assert not obs.ok
    assert "confirmation" in (obs.error or "")


def test_confirm_commands_proceed_once_a_human_says_yes():
    seen = []

    def confirm(prompt):
        seen.append(prompt)
        return True

    reg = build_action_tools(dry_run=True, confirm=confirm)
    obs = _invoke(reg, "run_system_command", {"command": "git push origin main"})
    assert obs.ok
    assert seen == ["git push origin main"]


def test_an_unattended_run_can_never_execute_a_confirm_command():
    # No confirm callback supplied: the default must refuse, not assume yes.
    reg = build_action_tools(dry_run=True)
    obs = _invoke(reg, "run_system_command", {"command": "git push origin main"})
    assert not obs.ok


# --------------------------------------------------------------------------- #
# Target resolution
# --------------------------------------------------------------------------- #


def test_a_natural_youtube_request_becomes_a_youtube_search():
    resolved = resolve_target("play lofi on youtube")
    assert resolved["kind"] == "url"
    assert "youtube.com/results" in resolved["value"]
    assert "lofi" in resolved["value"]
    # Regression: this used to fall through to a Google search because the
    # site name was matched only at the start of the string.
    assert "google.com" not in resolved["value"]


def test_a_bare_site_opens_the_site():
    assert resolve_target("open github")["value"] == "https://github.com"
    assert resolve_target("youtube")["value"] == "https://www.youtube.com"


def test_a_spotify_request_becomes_a_spotify_search():
    resolved = resolve_target("play nightcall on spotify")
    assert "open.spotify.com/search" in resolved["value"]


def test_an_explicit_url_is_passed_through_untouched():
    resolved = resolve_target("https://example.com/a?b=1")
    assert resolved["value"] == "https://example.com/a?b=1"


def test_a_known_app_resolves_to_an_executable():
    resolved = resolve_target("code")
    assert resolved["kind"] == "app"
    assert resolved["value"] == "code"


def test_an_unknown_target_falls_back_to_a_web_search():
    resolved = resolve_target("something weird")
    assert resolved["kind"] == "url"
    assert "google.com/search" in resolved["value"]


def test_target_resolution_never_raises():
    for target in ["", "   ", "!!", "a" * 500, None]:
        assert resolve_target(target)["kind"] in ("url", "app")


# --------------------------------------------------------------------------- #
# Tools
# --------------------------------------------------------------------------- #


def test_the_action_toolset_registers_five_tools():
    reg = build_action_tools(dry_run=True)
    names = set(reg.names())
    assert names == {
        "open_app_or_website",
        "run_system_command",
        "create_file",
        "read_file",
        "system_vitals",
    }


def test_shell_execution_is_not_auto_approved():
    from jarvisx.tools.tool_kernel import PermissionLevel

    reg = build_action_tools(dry_run=True)
    shell = reg.get("run_system_command")
    assert shell.permission is PermissionLevel.CONFIRM
    # Opening a tab is harmless and should not nag.
    assert reg.get("open_app_or_website").permission is PermissionLevel.SAFE


def test_the_path_jail_refuses_an_escape(tmp_path):
    reg = build_action_tools(dry_run=True, workspace=str(tmp_path))
    obs = _invoke(reg, "create_file", {"path": "../../etc/passwd", "content": "x"})
    assert not obs.ok
    assert "outside the workspace" in (obs.error or "")


def test_create_then_read_round_trips_inside_the_workspace(tmp_path):
    reg = build_action_tools(workspace=str(tmp_path))
    written = _invoke(reg, "create_file", {"path": "notes.txt", "content": "hello kid"})
    assert written.ok
    read = _invoke(reg, "read_file", {"path": "notes.txt"})
    assert read.ok
    assert read.output["content"] == "hello kid"


def test_reading_a_missing_file_fails_loudly(tmp_path):
    # A soft {"ok": False} would be invisible to Observation.ok and the harness
    # would grade a failed read as a success.
    reg = build_action_tools(workspace=str(tmp_path))
    obs = _invoke(reg, "read_file", {"path": "nope.txt"})
    assert not obs.ok


def test_dry_run_performs_no_launch():
    reg = build_action_tools(dry_run=True)
    obs = _invoke(reg, "open_app_or_website", {"target": "github"})
    assert obs.ok
    assert obs.output["dry_run"] is True


def test_vitals_degrade_instead_of_crashing_without_psutil():
    reg = build_action_tools(dry_run=False)
    obs = _invoke(reg, "system_vitals", {})
    assert obs.ok, obs.error
    # Either real numbers, or an honest degraded report — never an exception.
    assert "cpu_percent" in obs.output or obs.output.get("degraded") is True


def test_an_unknown_target_falls_back_to_a_web_search_rather_than_failing():
    reg = build_action_tools(dry_run=True)
    obs = _invoke(reg, "open_app_or_website", {"target": "definitely-not-a-real-app-xyz"})
    assert obs.ok
    assert "google.com/search" in obs.output["value"]


def test_a_failed_launch_is_reported_loudly_not_swallowed():
    # No browser exists in a headless sandbox, so webbrowser.open() returns
    # False. That must surface as a failure: a silent no-op would leave the
    # model believing it opened something it did not.
    reg = build_action_tools(dry_run=False)
    obs = _invoke(reg, "open_app_or_website", {"target": "github"})
    assert not obs.ok
    assert "no browser" in (obs.error or ""), obs.error
