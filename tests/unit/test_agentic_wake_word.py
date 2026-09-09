"""Tests for hands-free wake-word input.

The audio stack does not exist in CI, so these drive the wake-phrase logic
through an injected engine. What they protect:

- The configured wake word is the one actually listened for. The shipped engine
  hardcodes its own list, so without this ``--wake-word eevee`` would be unheard.
- Speech not addressed to the agent is ignored. The shipped engine's own gate
  also fires on any two-word utterance, which would let a conversation across
  the room drive the agent.
- Silence does not end the session. Every other input source returns ``None``
  to mean "input exhausted" and ``VoiceAgentLoop.run`` stops on that; for a
  hands-free agent, quiet is the normal state.
"""

from __future__ import annotations

import pytest

from jarvisx.agentic.intake import Energy
from jarvisx.agentic.voice_loop import (
    ConsoleInput,
    ConsoleOutput,
    Intent,
    VoiceAgentLoop,
    WakeWordInput,
)


class FakeWakeEngine:
    """Stands in for SovereignWakeWordEngine without its audio dependencies."""

    # Mirrors the shipped class list, which notably lacks "eevee".
    WAKE_WORDS = ["hey alfred", "alfred", "jarvis", "hey jarvis", "nani", "friday", "edith", "wake up"]

    def __init__(self, clips):
        self.clips = list(clips)
        self.calls = 0

    def record_and_transcribe_manual(self, duration_sec: float = 4.0):
        self.calls += 1
        return self.clips.pop(0) if self.clips else ""

    def extract_command(self, text: str) -> str:
        """Same behaviour as the shipped engine: only strips words it knows."""
        clean = text.strip()
        lower = clean.lower()
        for word in sorted(self.WAKE_WORDS, key=len, reverse=True):
            if lower.startswith(word):
                cmd = clean[len(word):].strip(" ,:.-")
                if cmd:
                    return cmd
        return clean


class BoomEngine:
    """A microphone that fails every time."""

    def record_and_transcribe_manual(self, duration_sec: float = 4.0):
        raise RuntimeError("device gone")

    def extract_command(self, text: str) -> str:
        return text


# --------------------------------------------------------------------------- #
# The configured wake word is honoured
# --------------------------------------------------------------------------- #


def test_the_configured_wake_word_is_stripped():
    source = WakeWordInput(wake_word="alfred", engine=FakeWakeEngine(["alfred open spotify"]), attempts=1)
    assert source.listen() == "open spotify"


def test_a_custom_wake_word_works_even_though_the_engine_lacks_it():
    """The shipped engine's list has no 'eevee'; it must still be heard."""
    source = WakeWordInput(wake_word="eevee", engine=FakeWakeEngine(["eevee what should i do"]), attempts=1)
    assert source.listen() == "what should i do"


def test_the_wake_word_may_appear_mid_sentence():
    """A non-filler lead-in survives; the wake phrase itself does not."""
    source = WakeWordInput(wake_word="alfred", engine=FakeWakeEngine(["later alfred pay the bill"]), attempts=1)
    assert source.listen() == "later pay the bill"


def test_a_filler_lead_in_is_removed_with_the_wake_word():
    """'ok alfred pay the bill' is a request to pay the bill, not to 'ok'."""
    source = WakeWordInput(wake_word="alfred", engine=FakeWakeEngine(["ok alfred pay the bill"]), attempts=1)
    assert source.listen() == "pay the bill"


def test_removing_a_mid_sentence_word_leaves_no_double_space():
    """'ok   pay the bill' would reach the router looking like two sentences."""
    source = WakeWordInput(wake_word="alfred", engine=FakeWakeEngine(["ok alfred pay the bill"]), attempts=1)
    assert "  " not in source.listen()


def test_case_and_punctuation_do_not_matter():
    source = WakeWordInput(wake_word="alfred", engine=FakeWakeEngine(["Alfred, open GitHub."]), attempts=1)
    assert source.listen() == "open GitHub"


@pytest.mark.parametrize("clip", ["alfred", "ALFRED", "alfred.", "  alfred  ", "hey alfred"])
def test_a_bare_wake_word_is_not_a_command(clip):
    source = WakeWordInput(wake_word="alfred", engine=FakeWakeEngine([clip]), attempts=1)
    assert source.listen() is None


# --------------------------------------------------------------------------- #
# Ignore what it was not asked about
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "clip",
    [
        "who left the printer on",
        "i wonder about that",
        "did you see the game last night",
        "",
        "   ",
    ],
)
def test_speech_not_addressed_to_the_agent_is_ignored(clip):
    """The shipped gate fires on any two-word utterance; that is too loose."""
    source = WakeWordInput(wake_word="alfred", engine=FakeWakeEngine([clip]), attempts=1)
    assert source.listen() is None


def test_it_waits_past_unaddressed_speech_for_a_real_command():
    engine = FakeWakeEngine(["who left the printer on", "alfred pay the bill"])
    source = WakeWordInput(wake_word="alfred", engine=engine)
    assert source.listen() == "pay the bill"
    assert engine.calls == 2


# --------------------------------------------------------------------------- #
# Silence is not the end of the session
# --------------------------------------------------------------------------- #


def test_silence_keeps_it_waiting_rather_than_ending_the_run():
    engine = FakeWakeEngine(["", "", "", "alfred quit"])
    source = WakeWordInput(wake_word="alfred", engine=engine)
    assert source.listen() == "quit"
    assert engine.calls == 4


def test_the_attempt_cap_is_the_safety_valve():
    engine = FakeWakeEngine([""] * 50)
    source = WakeWordInput(wake_word="alfred", engine=engine, attempts=3)
    assert source.listen() is None
    assert engine.calls == 3


def test_a_stop_signal_ends_a_quiet_session():
    """Shutdown must work while the room is silent, not just after speech."""
    stopped = {"now": False}
    calls = {"n": 0}

    class SlowEngine(FakeWakeEngine):
        def record_and_transcribe_manual(self, duration_sec=4.0):
            calls["n"] += 1
            if calls["n"] >= 2:
                stopped["now"] = True
            return ""

    source = WakeWordInput(
        wake_word="alfred", engine=SlowEngine([]), attempts=1000, should_stop=lambda: stopped["now"]
    )
    assert source.listen() is None
    assert calls["n"] < 1000, "the stop signal was not honoured"


# --------------------------------------------------------------------------- #
# Failure modes
# --------------------------------------------------------------------------- #


def test_a_failing_microphone_does_not_crash_the_loop():
    source = WakeWordInput(wake_word="alfred", engine=BoomEngine(), attempts=2)
    assert source.listen() is None


def test_a_broken_extract_command_still_yields_the_utterance():
    class BadExtract(FakeWakeEngine):
        def extract_command(self, text):
            raise ValueError("nope")

    source = WakeWordInput(wake_word="alfred", engine=BadExtract(["alfred pay the bill"]), attempts=1)
    assert source.listen() == "pay the bill"


def test_an_engine_with_no_extract_command_still_works():
    class Minimal:
        def record_and_transcribe_manual(self, duration_sec=4.0):
            return "alfred open spotify"

    source = WakeWordInput(wake_word="alfred", engine=Minimal(), attempts=1)
    assert source.listen() == "open spotify"


# --------------------------------------------------------------------------- #
# Honest degradation
# --------------------------------------------------------------------------- #


def test_no_audio_stack_degrades_to_the_fallback_instead_of_claiming_to_listen():
    """A false 'listening' is worse than none — the loop would hear nothing forever."""
    source = WakeWordInput(wake_word="alfred", fallback=ConsoleInput(lines=["typed instead"]))
    assert source.available is False
    assert source.listen() == "typed instead"


def test_the_fallback_chain_is_wake_word_then_whisper_then_keyboard():
    source = WakeWordInput(wake_word="alfred", fallback=ConsoleInput(lines=["x"]))
    assert source.name == "wake-word"
    assert source._fallback.name == "console"


def test_an_empty_wake_word_falls_back_to_a_sane_default():
    source = WakeWordInput(wake_word="", engine=FakeWakeEngine(["alfred open spotify"]), attempts=1)
    assert source.wake_word == "alfred"
    assert source.listen() == "open spotify"


def test_a_bare_greeting_after_the_wake_word_is_not_a_command():
    """'alfred hi' is someone saying hello, not a request to 'hi'."""
    source = WakeWordInput(wake_word="alfred", engine=FakeWakeEngine(["alfred hi"]), attempts=1)
    assert source.listen() is None


def test_attempts_cannot_be_zero():
    source = WakeWordInput(wake_word="alfred", engine=FakeWakeEngine([""]), attempts=0)
    assert source.attempts >= 1


# --------------------------------------------------------------------------- #
# Integration: the stripped command must actually route
# --------------------------------------------------------------------------- #


def test_a_spoken_command_routes_like_a_typed_one():
    """The whole point: 'alfred open spotify' behaves as 'open spotify'."""
    from jarvisx.agentic.actions import build_action_tools

    source = WakeWordInput(wake_word="alfred", engine=FakeWakeEngine(["alfred open spotify"]), attempts=1)
    loop = VoiceAgentLoop(
        stt=source,
        tts=ConsoleOutput(),
        physical=build_action_tools(dry_run=True),
        energy=Energy.HIGH,
    )
    turn = loop.handle(source.listen())
    assert turn.intent is Intent.OPEN


def test_a_spoken_brain_dump_is_captured_not_executed():
    source = WakeWordInput(
        wake_word="alfred",
        engine=FakeWakeEngine(["alfred write the report, pay the bill, call mom"]),
        attempts=1,
    )
    loop = VoiceAgentLoop(stt=source, tts=ConsoleOutput(), energy=Energy.HIGH)
    turn = loop.handle(source.listen())
    assert turn.intent is Intent.BRAIN_DUMP
    assert len(turn.payload["captured"]) == 3
