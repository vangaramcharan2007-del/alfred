"""Voice and personality, kept strictly separate from judgement.

The repo already had two competing personas — ``EeveeCompanion`` plays Tony
Stark calling the user "kid", ``EeveeGroq`` plays "E.V." calling them "Boss" —
hard-coded as system prompts buried in thousand-line classes, so you could not
use one without dragging the other's mic handling and tool loop with it.

Here a persona is just something that can rewrite a sentence. That separation
is the point:

    IntakeEngine decides WHAT you should do next.
    Persona decides HOW that lands when it is spoken.

A persona must never change the substance. If Stark could talk you out of the
task the engine picked, you would have a sarcastic procrastination engine, and
for an ADHD brain that is the worst possible failure mode. So ``render()``
receives the already-decided message and may only re-voice it.

The house rules every persona here follows:

- Short. Two sentences. Long speech is unusable when you are listening.
- Never shaming. "You wasted an hour" produces avoidance, which is the actual
  problem, not a lack of discipline.
- Always leave one concrete next action on the table.
"""

from __future__ import annotations

import random
import re
from typing import Any, Dict, List, Optional

from jarvisx.agentic.voice_loop import SpeechOutput


class Persona:
    """Rewrites a decided message in a consistent voice. Never decides."""

    name = "plain"
    address = ""

    def render(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        return message

    def greet(self, energy: str = "medium") -> str:
        return "Ready."

    def farewell(self, open_items: int = 0) -> str:
        return f"Stopped. {open_items} item(s) saved."


class StarkPersona(Persona):
    """Tony Stark mentoring Peter Parker. Sarcastic, warm, protective, brief.

    Lifted from the persona the repo already shipped in ``eevee_companion.py``,
    but as a rewrite layer rather than a system prompt, so it can sit on top of
    any backend — including no backend at all.
    """

    name = "stark"
    address = "kid"

    _OPENERS = ("Alright, kid.", "Okay, kid.", "Right.", "Here's the thing, kid.", "Kid.")

    _PICKED = (
        "One thing. {task}. {minutes} minutes, then you are done with it.",
        "{task}. That is the whole job, kid. About {minutes} minutes.",
        "Do not look at the rest of the list. {task}. {minutes} minutes.",
    )

    _DONE = (
        "Done. That is one less thing in your head.",
        "Good. That one is actually finished, not 'basically finished'.",
        "Cleared. See, that took less than the dread did.",
    )

    _NOT_YOURS = (
        "That one is not yours, kid. Put it down.",
        "Not your problem. Someone else owns that one.",
        "You are holding that for no reason. Drop it.",
    )

    _DRIFT = (
        "You drifted. No lecture — come back, or I move the task to later.",
        "That is not the task. Your call: switch back, or reschedule it.",
    )

    def render(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        ctx = context or {}
        kind = ctx.get("kind")

        if kind == "picked":
            return random.choice(self._PICKED).format(
                task=ctx.get("task", message),
                minutes=ctx.get("minutes", "?"),
            )
        if kind == "done":
            return random.choice(self._DONE)
        if kind == "not_yours":
            return random.choice(self._NOT_YOURS)
        if kind == "drift":
            return random.choice(self._DRIFT)
        if kind == "nudge":
            return self._de_shame(message)

        # Anything unrecognised passes through, prefixed. Rewriting content we
        # do not understand is how a persona starts lying.
        return f"{random.choice(self._OPENERS)} {message}"

    def greet(self, energy: str = "medium") -> str:
        return {
            "low": "Rough day? Fine. We will keep it small, kid.",
            "high": "You have got charge today. Let us use some of it.",
        }.get(energy, "Alright, kid. What is in the way?")

    def farewell(self, open_items: int = 0) -> str:
        return f"Go on. {open_items} thing(s) are still on the list for later."

    # Shaming vocabulary. Detecting it and deleting those words from the
    # sentence cannot work — strip words out of prose and you get
    # "an hour on YouTube again? time.", which is worse than the original.
    # So detection and replacement are separate: find it, then substitute a
    # whole clean line that says the same useful thing without the judgement.
    _SHAME_RE = re.compile(
        r"\b(?:you\s+wasted|wasting\s+time|stop\s+wasting|you\s+should\s+have|"
        r"lazy|you\s+always|you\s+never|again\?|as\s+usual|like\s+always|"
        r"you\s+failed|disappointing|pathetic)\b",
        re.IGNORECASE,
    )

    def _de_shame(self, message: str) -> str:
        """Replace a judgemental nudge wholesale. Never patch it in place."""
        if not self._SHAME_RE.search(message):
            return message
        return random.choice(self._DRIFT)


class FridayPersona(Persona):
    """F.R.I.D.A.Y. / E.V. — precise, competent, zero fluff.

    The voice ``eevee_groq.py`` already uses, kept as its own option because
    some people want a copilot and not a mentor.
    """

    name = "friday"
    address = "Boss"

    def render(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        ctx = context or {}
        kind = ctx.get("kind")
        if kind == "picked":
            return f"{ctx.get('task', message)}. About {ctx.get('minutes', '?')} minutes, Boss."
        if kind == "done":
            return "Marked complete, Boss."
        if kind == "not_yours":
            return "Not yours to carry, Boss."
        return message

    def greet(self, energy: str = "medium") -> str:
        return "Systems nominal, Boss. What are we clearing first?"

    def farewell(self, open_items: int = 0) -> str:
        return f"Standing by. {open_items} item(s) remain queued."


PERSONAS = {
    "plain": Persona,
    "stark": StarkPersona,
    "friday": FridayPersona,
}


def get_persona(name: Optional[str]) -> Persona:
    """Look a persona up by name. Unknown names fall back to plain, never raise.

    A bad --persona flag should not stop the agent from starting; it should
    just make it sound less interesting.
    """
    return PERSONAS.get((name or "plain").lower(), Persona)()


class PersonaOutput:
    """Wraps a :class:`SpeechOutput` so every line is spoken in character.

    Drop-in compatible, which means the voice loop, the watcher's nudges and
    the runtime all get a personality without any of them knowing about it.
    """

    def __init__(self, inner: SpeechOutput, persona: Persona):
        self.inner = inner
        self.persona = persona
        self.name = f"{persona.name}->{getattr(inner, 'name', 'output')}"
        self.spoken: List[str] = []

    @property
    def available(self) -> bool:
        return getattr(self.inner, "available", True)

    def say(self, text: str, context: Optional[Dict[str, Any]] = None) -> None:
        rendered = self.persona.render(text, context)
        self.spoken.append(rendered)
        # The inner sink has a plain say(text) contract; context stays here.
        self.inner.say(rendered)
