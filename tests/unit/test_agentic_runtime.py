"""Tests for the unified runtime: one agent that talks, listens, watches, does.

The interesting assertions here are about *integration* — the four capabilities
sharing one state. Four parts bolted together would pass every other test in the
suite and still be useless.
"""

from __future__ import annotations

import threading

import pytest

from jarvisx.agentic.intake import Energy, IntakeEngine
from jarvisx.agentic.runtime import AlfredRuntime, RuntimeConfig
from jarvisx.agentic.voice_loop import ConsoleInput, ConsoleOutput
from jarvisx.agentic.watch import Observation


def _runtime(**overrides):
    settings = {"force_text": True, "watch": True}
    settings.update(overrides)
    return AlfredRuntime(
        RuntimeConfig(**settings),
        stt=ConsoleInput(),
        tts=ConsoleOutput(),
    )


# --------------------------------------------------------------------------- #
# Shared state: the thing that makes this one agent and not four
# --------------------------------------------------------------------------- #


def test_speech_and_watching_share_one_task_list():
    runtime = _runtime()
    runtime.voice.handle("write the report")
    # The watcher captures from the clipboard into the same list.
    runtime.watcher.tick(clipboard_text="remember to submit the lab report by friday")
    titles = [i.title.lower() for i in runtime.intake.items]
    assert any("report" in t for t in titles)
    assert any("lab report" in t for t in titles)
    assert len(runtime.intake.items) == 2, titles


def test_picking_a_task_tells_the_watcher_what_the_task_is():
    """Without this, drift detection judges you against a task it never knew."""
    runtime = _runtime()
    runtime.intake.plan("write the OS assignment its due today")
    runtime.voice.handle("what should I do")
    assert runtime.ledger.intended_task is not None
    assert "OS assignment" in runtime.ledger.intended_task


def test_drift_from_the_committed_task_is_detected():
    runtime = _runtime()
    runtime.commit_to("write the OS assignment")
    nudges = []
    for i in range(7):
        nudges += runtime.ledger.observe(
            Observation(app="chrome", title="YouTube", timestamp=1000.0 + i * 60)
        )
    kinds = {n.kind.value for n in nudges}
    assert "off_task" in kinds, kinds


def test_no_off_task_nudge_without_a_committed_task():
    runtime = _runtime()
    nudges = []
    for i in range(7):
        nudges += runtime.ledger.observe(
            Observation(app="chrome", title="YouTube", timestamp=1000.0 + i * 60)
        )
    assert all(n.kind.value != "off_task" for n in nudges)


def test_committing_a_task_emits_an_event():
    events = []
    runtime = AlfredRuntime(
        RuntimeConfig(force_text=True),
        stt=ConsoleInput(),
        tts=ConsoleOutput(),
        on_event=lambda kind, payload: events.append((kind, payload)),
    )
    runtime.commit_to("pay the bill")
    assert ("task_committed", {"task": "pay the bill"}) in events


# --------------------------------------------------------------------------- #
# Nudges reach the same mouth as replies
# --------------------------------------------------------------------------- #


def test_nudges_are_spoken_on_the_reply_channel():
    tts = ConsoleOutput()
    runtime = AlfredRuntime(
        RuntimeConfig(force_text=True, speak_nudges=True),
        stt=ConsoleInput(),
        tts=tts,
    )
    runtime.ledger.set_intended_task("write the assignment")
    from jarvisx.agentic.watch import Nudge, NudgeKind

    nudge = Nudge(kind=NudgeKind.OFF_TASK, message="you drifted")
    runtime._on_nudge(nudge)
    assert any("drifted" in line for line in tts.spoken)
    assert runtime.spoken_nudges == [nudge]


def test_quiet_runtime_does_not_speak_nudges():
    tts = ConsoleOutput()
    runtime = AlfredRuntime(
        RuntimeConfig(force_text=True, speak_nudges=False),
        stt=ConsoleInput(),
        tts=tts,
    )
    from jarvisx.agentic.watch import Nudge, NudgeKind

    runtime._on_nudge(Nudge(kind=NudgeKind.BREAK, message="take a break"))
    assert tts.spoken == []


def test_a_failing_speaker_cannot_kill_the_watcher():
    class BrokenSpeaker:
        name = "broken"

        def say(self, text):
            raise RuntimeError("audio device vanished")

    runtime = AlfredRuntime(
        RuntimeConfig(force_text=True),
        stt=ConsoleInput(),
        tts=BrokenSpeaker(),
    )
    from jarvisx.agentic.watch import Nudge, NudgeKind

    # Must not raise: the watcher runs on a background thread and an exception
    # there would silently end ambient watching for the rest of the session.
    runtime._on_nudge(Nudge(kind=NudgeKind.BREAK, message="break"))


# --------------------------------------------------------------------------- #
# Degradation: every layer is optional
# --------------------------------------------------------------------------- #


def test_runtime_works_with_watching_off():
    runtime = _runtime(watch=False)
    assert runtime.status.watching is False
    runtime.voice.handle("write the report")
    assert len(runtime.intake.items) == 1
    assert runtime.summary()["watcher"] is None


def test_runtime_never_enables_the_agent_by_default():
    runtime = _runtime(enable_agent=False)
    assert runtime.status.agent_enabled is False
    assert runtime.runner is None


def test_forced_text_reports_keyboard_rather_than_a_microphone():
    # No adapters injected: this is the path `alfred --text` really takes, and
    # it must not try to open a microphone that may not be installed.
    runtime = AlfredRuntime(RuntimeConfig(force_text=True, watch=False))
    assert runtime.status.voice_input == "keyboard"
    assert runtime.status.voice_output == "text"


def test_an_injected_adapter_reports_its_own_name():
    runtime = _runtime()
    assert runtime.status.voice_input == "console"
    assert runtime.status.voice_output == "console"


# --------------------------------------------------------------------------- #
# Lifecycle
# --------------------------------------------------------------------------- #


def test_start_is_idempotent():
    runtime = _runtime(watch=False)
    runtime.start()
    runtime.start()
    assert runtime._watch_thread is None  # no source, nothing to start
    runtime.stop()


def test_stop_persists_shared_state(tmp_path):
    state = tmp_path / "intake.json"
    config = RuntimeConfig(force_text=True, watch=False, state_path=str(state))
    runtime = AlfredRuntime(config, stt=ConsoleInput(), tts=ConsoleOutput())
    runtime.voice.handle("write the report, pay the bill")
    runtime.stop()
    assert state.exists()

    # And a fresh runtime picks the list back up.
    revived = AlfredRuntime(config, stt=ConsoleInput(), tts=ConsoleOutput())
    assert len(revived.intake.items) == 2, [i.title for i in revived.intake.items]


def test_serve_runs_a_scripted_session_and_stops(tmp_path):
    state = tmp_path / "intake.json"
    config = RuntimeConfig(
        force_text=True, watch=False, state_path=str(state), max_turns=3
    )
    runtime = AlfredRuntime(
        config,
        stt=ConsoleInput(lines=["write the report", "what should I do", "quit"]),
        tts=ConsoleOutput(),
    )
    turns = runtime.serve()
    assert len(turns) == 3
    assert turns[-1].intent.name == "QUIT"
    assert state.exists()
