"""Tests for ambient watching: fragmentation, off-task, breaks, capture."""

from __future__ import annotations

import pytest

from jarvisx.agentic.intake import IntakeEngine
from jarvisx.agentic.watch import (
    AttentionLedger,
    ClipboardSource,
    ContextWatcher,
    NudgeKind,
    Observation,
    ScriptedSource,
    is_distraction,
    looks_capturable,
)


def _obs(app, title="", mode="GENERAL", ts=0.0):
    return Observation(app=app, title=title, mode=mode, timestamp=ts)


# --------------------------------------------------------------------------- #
# Distraction detection
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "obs,expected",
    [
        (_obs("chrome", "YouTube - lofi"), True),
        (_obs("chrome", "Instagram"), True),
        (_obs("chrome", "reddit - r/python"), True),
        (_obs("firefox", "Netflix"), True),
        (_obs("spotify", "Music", mode="MEDIA"), True),
        (_obs("game.exe", "Elden Ring", mode="GAMING"), True),
        (_obs("code", "harness.py - alfred", mode="CODING"), False),
        (_obs("chrome", "docs.python.org", mode="WEB_RESEARCH"), False),
        (_obs("terminal", "zsh", mode="TERMINAL_DEVOPS"), False),
    ],
)
def test_is_distraction(obs, expected):
    assert is_distraction(obs) is expected


def test_is_distraction_ignores_a_substring_that_is_not_a_domain():
    assert is_distraction(_obs("code", "youtubedownloader.py", mode="CODING")) is False


# --------------------------------------------------------------------------- #
# Ledger: fragmentation
# --------------------------------------------------------------------------- #


def test_ledger_counts_app_switches_in_the_window():
    ledger = AttentionLedger(switch_window_seconds=300)
    for index, app in enumerate(["code", "chrome", "code", "slack"]):
        ledger.observe(_obs(app, ts=index * 60.0))
    assert ledger.switches_in_window(180.0) == 3


def test_ledger_does_not_count_staying_in_one_app_as_switching():
    ledger = AttentionLedger()
    for index in range(10):
        ledger.observe(_obs("code", ts=index * 30.0))
    assert ledger.switches_in_window(270.0) == 0


def test_ledger_ignores_switches_outside_the_window():
    ledger = AttentionLedger(switch_window_seconds=60)
    ledger.observe(_obs("code", ts=0.0))
    ledger.observe(_obs("chrome", ts=10.0))
    ledger.observe(_obs("code", ts=1000.0))  # long after
    assert ledger.switches_in_window(1000.0) == 0


def test_fragmentation_nudge_fires_above_the_threshold():
    ledger = AttentionLedger(switch_window_seconds=300, fragmentation_threshold=4)
    nudges = []
    for index, app in enumerate(["code", "chrome", "code", "slack", "code"]):
        nudges.extend(ledger.observe(_obs(app, ts=index * 30.0)))
    assert any(n.kind is NudgeKind.FRAGMENTED for n in nudges)


def test_fragmentation_nudge_stays_silent_below_the_threshold():
    ledger = AttentionLedger(switch_window_seconds=300, fragmentation_threshold=10)
    nudges = []
    for index, app in enumerate(["code", "chrome", "code"]):
        nudges.extend(ledger.observe(_obs(app, ts=index * 30.0)))
    assert not any(n.kind is NudgeKind.FRAGMENTED for n in nudges)


def test_fragmentation_nudge_respects_its_cooldown():
    ledger = AttentionLedger(switch_window_seconds=300, fragmentation_threshold=2)
    ledger.cooldown_seconds = 600
    first = []
    for index, app in enumerate(["a", "b", "a", "b", "a"]):
        first.extend(ledger.observe(_obs(app, ts=index * 10.0)))
    assert sum(n.kind is NudgeKind.FRAGMENTED for n in first) == 1

    # Immediately after, still within cooldown: no second nudge.
    more = []
    for index, app in enumerate(["c", "d", "c", "d"]):
        more.extend(ledger.observe(_obs(app, ts=60.0 + index * 10.0)))
    assert not any(n.kind is NudgeKind.FRAGMENTED for n in more)


def test_fragmentation_nudge_message_is_actionable_not_shaming():
    ledger = AttentionLedger(switch_window_seconds=300, fragmentation_threshold=2)
    nudges = []
    for index, app in enumerate(["a", "b", "a"]):
        nudges.extend(ledger.observe(_obs(app, ts=index * 10.0)))
    message = next(n.message for n in nudges if n.kind is NudgeKind.FRAGMENTED)
    assert "Pick one window" in message
    for word in ("wasting", "lazy", "bad", "should be ashamed"):
        assert word not in message.lower()


# --------------------------------------------------------------------------- #
# Ledger: off-task
# --------------------------------------------------------------------------- #


def test_off_task_nudge_fires_after_the_grace_period():
    ledger = AttentionLedger(off_task_seconds=300)
    ledger.set_intended_task("write the OS assignment", at=1000.0)
    nudges = []
    for index in range(8):
        nudges.extend(
            ledger.observe(_obs("chrome", "YouTube - lofi", ts=1000.0 + index * 60))
        )
    off_task = [n for n in nudges if n.kind is NudgeKind.OFF_TASK]
    assert off_task, "ten minutes on YouTube should register"
    assert "write the OS assignment" in off_task[0].message


def test_no_off_task_nudge_without_a_stated_task():
    """Never judge someone who did not say what they were doing."""
    ledger = AttentionLedger(off_task_seconds=60)
    nudges = []
    for index in range(10):
        nudges.extend(ledger.observe(_obs("chrome", "YouTube", ts=index * 60.0)))
    assert not any(n.kind is NudgeKind.OFF_TASK for n in nudges)


def test_no_off_task_nudge_before_the_grace_period():
    ledger = AttentionLedger(off_task_seconds=600)
    ledger.set_intended_task("the assignment", at=0.0)
    nudges = []
    for index in range(5):
        nudges.extend(ledger.observe(_obs("chrome", "YouTube", ts=index * 60.0)))
    assert not any(n.kind is NudgeKind.OFF_TASK for n in nudges)


def test_no_off_task_nudge_while_actually_working():
    ledger = AttentionLedger(off_task_seconds=60)
    ledger.set_intended_task("the assignment", at=0.0)
    nudges = []
    for index in range(20):
        nudges.extend(ledger.observe(_obs("code", "assignment.py", mode="CODING", ts=index * 60.0)))
    assert not any(n.kind is NudgeKind.OFF_TASK for n in nudges)


def test_off_task_message_offers_a_choice_rather_than_an_order():
    ledger = AttentionLedger(off_task_seconds=60)
    ledger.set_intended_task("the assignment", at=0.0)
    nudges = []
    for index in range(5):
        nudges.extend(ledger.observe(_obs("chrome", "YouTube", ts=index * 60.0)))
    message = next(n.message for n in nudges if n.kind is NudgeKind.OFF_TASK)
    assert "No judgement" in message
    assert "?" in message


# --------------------------------------------------------------------------- #
# Ledger: breaks and focus
# --------------------------------------------------------------------------- #


def test_break_nudge_fires_after_a_long_unbroken_stretch():
    ledger = AttentionLedger(break_after_seconds=300)
    nudges = []
    for index in range(10):
        nudges.extend(ledger.observe(_obs("code", "x.py", ts=index * 60.0)))
    assert any(n.kind is NudgeKind.BREAK for n in nudges)


def test_no_break_nudge_for_a_short_session():
    ledger = AttentionLedger(break_after_seconds=3600)
    nudges = []
    for index in range(5):
        nudges.extend(ledger.observe(_obs("code", ts=index * 60.0)))
    assert not any(n.kind is NudgeKind.BREAK for n in nudges)


def test_focus_streak_tracks_the_longest_unbroken_run():
    ledger = AttentionLedger()
    for index, app in enumerate(["code", "code", "code", "chrome", "code"]):
        ledger.observe(_obs(app, ts=index * 60.0))
    assert ledger.focus_streak() == 120.0


def test_seconds_on_current_resets_on_switch():
    ledger = AttentionLedger()
    ledger.observe(_obs("code", ts=0.0))
    ledger.observe(_obs("code", ts=60.0))
    ledger.observe(_obs("chrome", ts=120.0))
    assert ledger.seconds_on_current(180.0) == 60.0


def test_seconds_since_intent():
    ledger = AttentionLedger()
    ledger.set_intended_task("x", at=100.0)
    ledger.observe(_obs("code", ts=400.0))
    assert ledger.seconds_since_intent(400.0) == 300.0


def test_ledger_survives_an_empty_buffer():
    ledger = AttentionLedger()
    assert ledger.switches_in_window() == 0
    assert ledger.seconds_on_current() == 0.0
    assert ledger.focus_streak() == 0.0
    assert ledger.summary()["observations"] == 0


def test_ledger_bounds_its_buffer():
    ledger = AttentionLedger(switch_window_seconds=60, break_after_seconds=60)
    for index in range(500):
        ledger.observe(_obs("code", ts=index * 10.0))
    assert ledger.summary()["observations"] < 500


# --------------------------------------------------------------------------- #
# Clipboard capture
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "text",
    [
        "todo: email the professor",
        "remember to submit the lab report",
        "don't forget the dentist appointment",
        "need to renew the domain",
        "follow up with Ravi about the repo",
        "remind me to call the bank",
    ],
)
def test_looks_capturable_accepts_task_shaped_notes(text):
    assert looks_capturable(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "",
        "short",
        "def foo():\n    return 1",           # code, not a note
        "x" * 300,                             # too long
        "just a normal sentence about nothing",  # no task marker
        "line1\nline2\nline3\nline4\nline5",   # a pasted block
    ],
)
def test_looks_capturable_rejects_noise(text):
    assert looks_capturable(text) is False


# --------------------------------------------------------------------------- #
# Watcher
# --------------------------------------------------------------------------- #


def test_watcher_captures_task_shaped_clipboard_text():
    watcher = ContextWatcher()
    nudges = watcher.tick(clipboard_text="remember to submit the lab report")
    assert watcher.captured == ["Remember to submit the lab report"]
    assert any(n.kind is NudgeKind.CAPTURED for n in nudges)
    assert len(watcher.intake.items) == 1


def test_watcher_ignores_non_task_clipboard_text():
    watcher = ContextWatcher()
    watcher.tick(clipboard_text="def foo():\n    return 1")
    assert watcher.captured == []
    assert watcher.intake.items == []


def test_watcher_does_not_capture_when_auto_capture_is_off():
    watcher = ContextWatcher(auto_capture=False)
    watcher.tick(clipboard_text="remember to submit the lab report")
    assert watcher.captured == []


def test_watcher_feeds_observations_into_the_ledger():
    source = ScriptedSource(
        [_obs(app, mode="CODING", ts=index * 30.0) for index, app in
         enumerate(["code", "chrome", "code", "slack", "code"])]
    )
    ledger = AttentionLedger(switch_window_seconds=300, fragmentation_threshold=3)
    watcher = ContextWatcher(ledger=ledger, source=source)
    for _ in range(5):
        watcher.tick()
    assert watcher.summary()["switches"] >= 3


def test_watcher_calls_the_nudge_listener():
    seen = []
    ledger = AttentionLedger(switch_window_seconds=300, fragmentation_threshold=2)
    watcher = ContextWatcher(ledger=ledger, on_nudge=seen.append)
    for index, app in enumerate(["a", "b", "a"]):
        watcher.tick(_obs(app, ts=index * 10.0))
    assert seen and seen[0].kind is NudgeKind.FRAGMENTED


def test_watcher_survives_a_listener_that_raises():
    def exploding_listener(_nudge):
        raise RuntimeError("listener blew up")

    ledger = AttentionLedger(switch_window_seconds=300, fragmentation_threshold=2)
    watcher = ContextWatcher(ledger=ledger, on_nudge=exploding_listener)
    for index, app in enumerate(["a", "b", "a"]):
        watcher.tick(_obs(app, ts=index * 10.0))  # must not raise
    assert watcher.nudges


def test_watcher_run_respects_max_ticks():
    slept = []
    source = ScriptedSource([_obs("code", ts=float(i)) for i in range(10)])
    watcher = ContextWatcher(source=source)
    watcher.run(interval=1.0, max_ticks=3, sleep=slept.append)
    assert len(slept) == 3
    assert slept == [1.0, 1.0, 1.0]


def test_watcher_run_without_a_source_is_a_no_op():
    slept = []
    watcher = ContextWatcher()
    watcher.run(interval=0.5, max_ticks=2, sleep=slept.append)
    assert len(slept) == 2
    assert watcher.nudges == []


def test_watcher_summary_reports_source_availability():
    watcher = ContextWatcher(source=ScriptedSource([_obs("code")]))
    watcher.tick()
    summary = watcher.summary()
    assert summary["source_available"] is True
    assert summary["current_app"] == "code"


def test_scripted_source_exhausts_to_none():
    source = ScriptedSource([_obs("code")])
    assert source.poll() is not None
    assert source.poll() is None


def test_clipboard_source_degrades_when_pyperclip_is_missing(monkeypatch):
    """No clipboard library: must report unavailable, not raise."""
    import builtins

    real_import = builtins.__import__

    def no_pyperclip(name, *args, **kwargs):
        if name == "pyperclip":
            raise ImportError("No module named 'pyperclip'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_pyperclip)
    source = ClipboardSource()
    assert source.available is False
    assert source.poll() is None


def test_clipboard_source_poll_is_safe_with_no_clipboard_backend():
    """A present library is not the same as a working clipboard.

    Headless and CI machines import pyperclip fine and then have no clipboard
    to read, so ``poll`` must return None rather than propagate. Asserting on
    ``available`` here would make the test pass or fail on which packages
    happen to be installed rather than on the behaviour that matters.
    """
    source = ClipboardSource()
    assert source.poll() is None
    assert source.poll() is None


def test_nudge_serializes_to_json():
    import json

    ledger = AttentionLedger(switch_window_seconds=300, fragmentation_threshold=2)
    nudges = []
    for index, app in enumerate(["a", "b", "a"]):
        nudges.extend(ledger.observe(_obs(app, ts=index * 10.0)))
    assert json.loads(json.dumps(nudges[0].to_dict()))["kind"] == "fragmented"
