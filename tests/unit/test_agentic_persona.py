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
    EeveePersona,
    FridayPersona,
    JarvisPersona,
    Persona,
    PersonaOutput,
    StarkPersona,
    get_persona,
)
from jarvisx.agentic.voice_loop import ConsoleInput, ConsoleOutput


# --------------------------------------------------------------------------- #
# Lookup
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("name", ["plain", "stark", "friday", "jarvis", "eevee"])
def test_known_personas_resolve(name):
    assert get_persona(name).name == name


def test_lookup_is_case_insensitive():
    assert get_persona("STARK").name == "stark"


@pytest.mark.parametrize("name", ["does-not-exist", "", None, "ultron"])
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
# JARVIS
# --------------------------------------------------------------------------- #


def test_jarvis_addresses_the_user_as_sir():
    persona = JarvisPersona()
    assert persona.address == "sir"
    assert "sir" in persona.greet().lower()


def test_jarvis_keeps_a_picked_task_concrete():
    line = JarvisPersona().render(
        "ignored", {"kind": "picked", "task": "Write the OS assignment", "minutes": 45}
    )
    assert "Write the OS assignment" in line
    assert "45" in line


@pytest.mark.parametrize(
    "shaming",
    [
        "You wasted an hour again? Stop wasting time.",
        "You should have started earlier, as usual.",
        "That was lazy.",
    ],
)
def test_jarvis_never_repeats_a_shaming_nudge(shaming):
    out = JarvisPersona().render(shaming, {"kind": "nudge"})
    assert not StarkPersona._SHAME_RE.search(out), out
    assert out.endswith((".", "!", "?")), out


def test_jarvis_leaves_a_clean_nudge_alone():
    clean = "You are 5 minutes into chrome. Shall I bring the task back?"
    assert JarvisPersona().render(clean, {"kind": "nudge"}) == clean


def test_jarvis_passes_through_what_it_does_not_understand():
    message = "The build failed on step 3 with a timeout."
    assert message in JarvisPersona().render(message)


def test_jarvis_greet_adapts_to_energy():
    persona = JarvisPersona()
    assert persona.greet("low") != persona.greet("high")
    assert "small" in persona.greet("low")


# --------------------------------------------------------------------------- #
# Eevee (E.V.)
# --------------------------------------------------------------------------- #


def test_eevee_addresses_the_user_by_name():
    persona = EeveePersona()
    assert persona.address == "Charan"
    assert "Charan" in persona.greet()


def test_eevee_is_distinct_from_friday():
    """Both came out of the same E.V./Friday prompt; they must not be twins."""
    ctx = {"kind": "picked", "task": "Pay the bill", "minutes": 5}
    assert EeveePersona().address != FridayPersona().address
    assert EeveePersona().render("", ctx) != FridayPersona().render("", ctx)


def test_eevee_keeps_a_picked_task_concrete():
    line = EeveePersona().render(
        "ignored", {"kind": "picked", "task": "Write the OS assignment", "minutes": 45}
    )
    assert "Write the OS assignment" in line
    assert "45" in line


@pytest.mark.parametrize(
    "shaming",
    ["You wasted an hour again? Stop wasting time.", "That was lazy.", "You always do this."],
)
def test_eevee_never_repeats_a_shaming_nudge(shaming):
    out = EeveePersona().render(shaming, {"kind": "nudge"})
    assert not StarkPersona._SHAME_RE.search(out), out


def test_eevee_passes_through_what_it_does_not_understand():
    message = "The build failed on step 3 with a timeout."
    assert EeveePersona().render(message) == message


def test_all_character_voices_are_mutually_distinct():
    """If they sound the same, offering a choice is theatre."""
    ctx = {"kind": "picked", "task": "Pay the bill", "minutes": 5}
    names = ("stark", "friday", "jarvis", "eevee")
    voices = {n: PERSONAS[n]().render("", ctx) for n in names}
    assert len(set(voices.values())) == len(names), voices
    assert len({PERSONAS[n]().address for n in names}) == len(names)


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


# --------------------------------------------------------------------------- #
# Reaching the model: the persona must survive into a real conversation
# --------------------------------------------------------------------------- #


def test_plain_has_no_voice_prompt():
    """Adding personality to a coding agent's prompt costs tokens and buys nothing."""
    assert Persona().voice_prompt == ""


@pytest.mark.parametrize("name", ["stark", "friday", "jarvis", "eevee"])
def test_a_character_persona_carries_a_model_prompt(name):
    persona = get_persona(name)
    assert persona.voice_prompt
    assert persona.address in persona.voice_prompt


# Each persona forbids contempt in its own words. Assert the property, not one
# phrasing — otherwise adding a persona means editing this list every time.
_PROHIBITION_MARKERS = (
    "never mock", "never belittle", "do not editorialise", "do not scold",
    "never sarcastic at the user", "contempt",
)


@pytest.mark.parametrize("name", ["stark", "friday", "jarvis", "eevee"])
def test_the_voice_prompt_forbids_shaming(name):
    """The same rule applies to a real model as to a re-voiced nudge."""
    prompt = get_persona(name).voice_prompt.lower()
    assert any(marker in prompt for marker in _PROHIBITION_MARKERS), prompt


@pytest.mark.parametrize("name", ["stark", "friday", "jarvis", "eevee"])
def test_the_voice_prompt_mentions_why_shaming_is_harmful(name):
    """Or keeps its own equivalent reason; the point is that it is not arbitrary."""
    prompt = get_persona(name).voice_prompt.lower()
    assert ("executive dysfunction" in prompt or "impatience makes that worse" in prompt
            or "contempt makes that worse" in prompt or "never pad a failure" in prompt), prompt


@pytest.mark.parametrize("name", ["stark", "friday", "jarvis", "eevee"])
def test_the_voice_prompt_keeps_reporting_honest(name):
    """Character must never cost accuracy."""
    assert "accurately" in get_persona(name).voice_prompt


def test_the_voice_prompt_reaches_the_model_system_prompt():
    from jarvisx.agentic.roles import RoleRegistry
    from jarvisx.agentic.runtime import AlfredRuntime, RuntimeConfig

    for name in ("stark", "friday"):
        runtime = AlfredRuntime(
            RuntimeConfig(force_text=True, watch=False, persona=name),
            stt=ConsoleInput(lines=["quit"]), tts=ConsoleOutput(),
        )
        prompt = runtime._voiced_roles().get("coder").system_prompt("(tools)")
        assert runtime.persona.voice_prompt in prompt, name


def test_plain_leaves_the_system_prompt_untouched():
    from jarvisx.agentic.roles import RoleRegistry
    from jarvisx.agentic.runtime import AlfredRuntime, RuntimeConfig

    runtime = AlfredRuntime(
        RuntimeConfig(force_text=True, watch=False, persona="plain"),
        stt=ConsoleInput(lines=["quit"]), tts=ConsoleOutput(),
    )
    default = RoleRegistry().get("coder").system_prompt("(tools)")
    assert runtime._voiced_roles().get("coder").system_prompt("(tools)") == default


@pytest.mark.parametrize("role_name", ["coder", "tester", "reviewer", "planner", "generalist"])
def test_a_voice_changes_how_a_role_talks_but_not_what_it_does(role_name):
    """Same job, same budget, same tools. Only the voice differs."""
    from jarvisx.agentic.roles import RoleRegistry
    from jarvisx.agentic.runtime import AlfredRuntime, RuntimeConfig

    runtime = AlfredRuntime(
        RuntimeConfig(force_text=True, watch=False, persona="stark"),
        stt=ConsoleInput(lines=["quit"]), tts=ConsoleOutput(),
    )
    plain = RoleRegistry().get(role_name)
    voiced = runtime._voiced_roles().get(role_name)
    for attr in ("name", "title", "focus", "budget", "allowed_tools", "temperature"):
        assert getattr(plain, attr) == getattr(voiced, attr), attr
    assert plain.voice != voiced.voice


def test_with_voice_does_not_mutate_the_original():
    from jarvisx.agentic.roles import RoleRegistry

    original = RoleRegistry().get("coder")
    copy = original.with_voice("be dramatic")
    assert original.voice == ""
    assert copy.voice == "be dramatic"
