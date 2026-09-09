"""Tests for the persona layer.

Two properties matter more than any particular line of dialogue:

1. A persona re-voices a decision, it never changes it. If Stark could talk you
   out of the task the engine picked, this would be a sarcastic procrastination
   engine — the worst possible outcome for an ADHD brain.
2. Nothing shaming is ever spoken. Shame produces avoidance, and avoidance is
   the actual problem, not a lack of discipline.
"""

from __future__ import annotations

import pytest

from jarvisx.agentic.persona import (
    PERSONAS,
    FridayPersona,
    Persona,
    PersonaOutput,
    StarkPersona,
    get_persona,
)
from jarvisx.agentic.voice_loop import ConsoleInput, ConsoleOutput


# --------------------------------------------------------------------------- #
# Lookup
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("name", ["plain", "stark", "friday"])
def test_known_personas_resolve(name):
    assert get_persona(name).name == name


def test_lookup_is_case_insensitive():
    assert get_persona("STARK").name == "stark"


@pytest.mark.parametrize("name", ["does-not-exist", "", None, "jarvis"])
def test_an_unknown_persona_falls_back_instead_of_raising(name):
    # A bad --persona flag should make the agent less fun, not stop it starting.
    assert get_persona(name).name == "plain"


def test_every_persona_can_render_and_greet():
    for name, cls in PERSONAS.items():
        persona = cls()
        assert isinstance(persona.render("hello"), str)
        assert isinstance(persona.greet("low"), str)
        assert isinstance(persona.farewell(2), str)


# --------------------------------------------------------------------------- #
# Stark
# --------------------------------------------------------------------------- #


def test_stark_addresses_the_user_as_kid():
    persona = StarkPersona()
    assert persona.address == "kid"
    assert "kid" in persona.greet().lower()


def test_stark_keeps_a_picked_task_concrete():
    line = StarkPersona().render(
        "ignored", {"kind": "picked", "task": "Write the OS assignment", "minutes": 45}
    )
    assert "Write the OS assignment" in line
    assert "45" in line


def test_stark_says_something_useful_on_completion():
    line = StarkPersona().render("x", {"kind": "done"})
    assert line and len(line) < 90


def test_stark_tells_you_when_something_is_not_yours():
    # Any of the variants is fine, but it must release the item, not add to it.
    line = StarkPersona().render("x", {"kind": "not_yours"}).lower()
    assert any(w in line for w in ("not your", "someone else", "put it down", "drop it")), line


def test_stark_passes_through_what_it_does_not_understand():
    """Rewriting unknown content is how a persona starts lying."""
    message = "The build failed on step 3 with a timeout."
    out = StarkPersona().render(message)
    assert message in out


@pytest.mark.parametrize(
    "shaming",
    [
        "You wasted an hour on YouTube again? Stop wasting time.",
        "You should have started earlier, as usual.",
        "You always leave this to the last minute.",
        "That was lazy.",
        "You never finish anything.",
        "Disappointing.",
    ],
)
def test_no_shaming_vocabulary_is_ever_spoken(shaming):
    out = StarkPersona().render(shaming, {"kind": "nudge"})
    assert not StarkPersona._SHAME_RE.search(out), out


def test_a_shaming_nudge_is_replaced_wholesale_not_patched():
    """Regression: deleting the bad words left "an hour on YouTube again? time." """
    out = StarkPersona().render("You wasted an hour on YouTube again?", {"kind": "nudge"})
    # A complete sentence, not a pile of surviving fragments.
    assert out.endswith((".", "!", "?")), out
    assert "an hour on YouTube" not in out
    assert len(out.split()) >= 4


def test_a_clean_nudge_is_left_alone():
    clean = "You are 5 minutes into chrome. Want to switch back?"
    assert StarkPersona().render(clean, {"kind": "nudge"}) == clean


def test_stark_greet_adapts_to_energy():
    persona = StarkPersona()
    assert persona.greet("low") != persona.greet("high")
    assert "small" in persona.greet("low")


# --------------------------------------------------------------------------- #
# Friday
# --------------------------------------------------------------------------- #


def test_friday_addresses_the_user_as_boss():
    assert FridayPersona().address == "Boss"
    assert "Boss" in FridayPersona().render("x", {"kind": "picked", "task": "Pay bill", "minutes": 5})


def test_friday_does_not_add_colour_it_was_not_given():
    assert FridayPersona().render("plain message") == "plain message"


# --------------------------------------------------------------------------- #
# The output wrapper
# --------------------------------------------------------------------------- #


def test_persona_output_speaks_in_character_through_the_real_sink():
    inner = ConsoleOutput()
    out = PersonaOutput(inner, StarkPersona())
    out.say("Pay the bill", {"kind": "picked", "task": "Pay the bill", "minutes": 5})
    assert inner.spoken and "Pay the bill" in inner.spoken[0]
    assert inner.spoken[0] == out.spoken[0]


def test_persona_output_preserves_the_availability_of_its_sink():
    class NoSpeaker:
        name = "none"
        available = False

        def say(self, text):
            pass

    assert PersonaOutput(NoSpeaker(), StarkPersona()).available is False


def test_persona_output_reports_both_layers_in_its_name():
    out = PersonaOutput(ConsoleOutput(), StarkPersona())
    assert "stark" in out.name and "console" in out.name


def test_a_plain_persona_leaves_the_sink_unwrapped():
    """The default must add no behaviour, so nothing depends on it."""
    from jarvisx.agentic.runtime import AlfredRuntime, RuntimeConfig

    runtime = AlfredRuntime(RuntimeConfig(force_text=True, watch=False))
    assert type(runtime.tts) is ConsoleOutput
    assert runtime.persona.name == "plain"
    assert "plain" not in runtime.status.voice_output


def test_a_persona_actually_reaches_the_sink_in_the_runtime():
    from jarvisx.agentic.runtime import AlfredRuntime, RuntimeConfig

    # A scripted ear: listen_once() reads from stt, and pytest blocks stdin.
    runtime = AlfredRuntime(
        RuntimeConfig(force_text=True, watch=False, persona="stark"),
        stt=ConsoleInput(lines=["what should I do"]),
    )
    assert isinstance(runtime.tts, PersonaOutput)
    runtime.intake.plan("write the OS assignment its due today")
    # listen_once(), not handle(): handle() is text-in/turn-out by design and
    # never speaks, so it can never exercise the persona.
    runtime.voice.listen_once()
    spoken = runtime.tts.spoken
    assert spoken, "nothing was spoken"
    line = spoken[0]
    # The persona must have re-voiced the engine's decision, not echoed it.
    assert "Write the OS assignment" in line
    assert "45" in line
    raw = runtime.voice.turns[-1].spoken
    assert line != raw, "the persona passed the message through untouched"
    # And it must have used the "picked" template, not the generic prefix.
    assert any(t.format(task="Write the OS assignment its due today", minutes=45) == line
               for t in StarkPersona._PICKED), line


def test_the_persona_cannot_change_which_task_was_picked():
    """The decision belongs to the engine, not the voice."""
    from jarvisx.agentic.runtime import AlfredRuntime, RuntimeConfig

    picks = {}
    for persona in ("plain", "stark", "friday"):
        runtime = AlfredRuntime(
            RuntimeConfig(force_text=True, watch=False, persona=persona),
            stt=ConsoleInput(lines=["what should I do"]),
        )
        runtime.intake.plan(
            "write the OS assignment its due today, pay the electricity bill"
        )
        runtime.voice.listen_once()
        picks[persona] = runtime.ledger.intended_task
    assert len(set(picks.values())) == 1, picks
