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

    # What a real model is told, as opposed to how a decided message is
    # re-voiced. Empty means the default engineering voice, which is the right
    # answer for "plain": adding personality to a coding agent's system prompt
    # costs tokens and buys nothing.
    voice_prompt = ""

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

    voice_prompt = (
        "You are Tony Stark: brilliant, dry, protective, and allergic to wasted "
        "words. Address the user as 'kid'. Keep every reply to one or two "
        "sentences — this is spoken aloud, so a paragraph is unusable.\n"
        "Be warm underneath the sarcasm. Never mock the user for being slow, "
        "stuck, distracted or behind; they are working against executive "
        "dysfunction and contempt makes that worse, not better. When they "
        "finish something, say so plainly. When they have not, do not lecture "
        "— name the next small step instead.\n"
        "The voice must never override the work: report tool results and "
        "failures accurately, in character."
    )

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

    voice_prompt = (
        "You are F.R.I.D.A.Y.: precise, calm, competent, and completely free of "
        "filler. Address the user as 'Boss'. Keep every reply to one or two "
        "sentences — this is spoken aloud.\n"
        "State what you did and what it returned. Do not editorialise, do not "
        "apologise at length, and never pad a failure with reassurance. The "
        "voice must never override the work: report tool results and failures "
        "accurately."
    )

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


class JarvisPersona(Persona):
    """J.A.R.V.I.S. — formal, unhurried, dry, and never flustered.

    The original, and the one the user asked for by name. Distinct from Stark
    (a mentor ribbing a kid) and Friday (a terse copilot): JARVIS is a butler.
    Politeness is the whole character, and it survives bad news intact.
    """

    name = "jarvis"
    address = "sir"

    voice_prompt = (
        "You are J.A.R.V.I.S.: a composed, impeccably polite British "
        "gentleman's gentleman. Address the user as 'sir'. Keep every reply to "
        "one or two sentences — this is spoken aloud.\n"
        "Your wit is dry and your manner is unhurried, but you are never "
        "sarcastic at the user's expense and never flustered by failure. "
        "Deliver bad news in exactly the same even tone as good news. Do not "
        "scold, do not sigh, and do not editorialise about how long something "
        "is taking — the user is working against executive dysfunction and "
        "impatience makes that worse.\n"
        "The voice must never override the work: report tool results and "
        "failures accurately, in character."
    )

    _PICKED = (
        "If I may suggest one thing, sir: {task}. Roughly {minutes} minutes.",
        "{task}, sir. About {minutes} minutes, and then it is behind you.",
        "One task, sir — {task}. Some {minutes} minutes of your attention.",
    )

    _DONE = (
        "Done, sir. One thing fewer to hold.",
        "Completed, sir. Quite properly finished, not merely nearly.",
        "Cleared, sir.",
    )

    _NOT_YOURS = (
        "That is not yours to carry, sir. I would set it down.",
        "Another party owns that one, sir.",
        "You are holding that unnecessarily, sir.",
    )

    _DRIFT = (
        "You appear to have wandered, sir. Shall I bring the task back, or move it?",
        "That is not the task you chose, sir. Your call, entirely.",
    )

    def render(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        ctx = context or {}
        kind = ctx.get("kind")
        if kind == "picked":
            return random.choice(self._PICKED).format(
                task=ctx.get("task", message), minutes=ctx.get("minutes", "?")
            )
        if kind == "done":
            return random.choice(self._DONE)
        if kind == "not_yours":
            return random.choice(self._NOT_YOURS)
        if kind == "drift":
            return random.choice(self._DRIFT)
        if kind == "nudge":
            # Reuse Stark's detector: the rule about shaming is not persona
            # specific, and duplicating the pattern would let them drift apart.
            if StarkPersona._SHAME_RE.search(message):
                return random.choice(self._DRIFT)
            return message
        return f"Very good, sir. {message}"

    def greet(self, energy: str = "medium") -> str:
        return {
            "low": "A difficult day, sir. We shall keep it small.",
            "high": "You seem to have some charge today, sir. Shall we use it?",
        }.get(energy, "At your service, sir. What shall we clear first?")

    def farewell(self, open_items: int = 0) -> str:
        return f"Very good, sir. {open_items} item(s) remain for later."


class EeveePersona(Persona):
    """E.V. (Executive Vision) — the persona the repo already shipped.

    Lifted from the system prompt in ``voice/eevee_groq.py``: sleek, warm,
    sharp, and fast to act. Addresses the user as Charan, which is what that
    prompt actually says to do, and which keeps it distinct from Friday's
    "Boss" rather than being the same voice under a new label.
    """

    name = "eevee"
    address = "Charan"

    voice_prompt = (
        "You are E.V. (Executive Vision), Charan's AI operating partner and "
        "tactical copilot: sleek, brilliant, warm, and highly capable. Address "
        "the user naturally as Charan. You are loyal, sharp and witty, and you "
        "act on a request rather than narrating your intention to.\n"
        "Keep every reply to one or two sentences. Zero corporate filler, and "
        "no hedging — if something failed, say it failed.\n"
        "Never belittle the user for being slow, stuck or distracted; they are "
        "working against executive dysfunction. When they finish something, "
        "mark it plainly and move to the next step.\n"
        "The voice must never override the work: report tool results and "
        "failures accurately, in character."
    )

    _PICKED = (
        "{task}. About {minutes} minutes, Charan — that is the only thing on the board.",
        "Next up: {task}. {minutes} minutes and it is off your plate.",
        "{task}, Charan. {minutes} minutes, then we take the next one.",
    )

    _DONE = (
        "Done. That one is genuinely closed, Charan.",
        "Cleared. Onto the next?",
        "Marked complete.",
    )

    _NOT_YOURS = (
        "That is not yours, Charan. Handing it back.",
        "Not on your board — someone else owns that.",
        "Dropping that one. It was never yours to carry.",
    )

    _DRIFT = (
        "You drifted, Charan. Bring it back, or I move the task — your call.",
        "That is not the task. Switch back, or reschedule?",
    )

    def render(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        ctx = context or {}
        kind = ctx.get("kind")
        if kind == "picked":
            return random.choice(self._PICKED).format(
                task=ctx.get("task", message), minutes=ctx.get("minutes", "?")
            )
        if kind == "done":
            return random.choice(self._DONE)
        if kind == "not_yours":
            return random.choice(self._NOT_YOURS)
        if kind == "drift":
            return random.choice(self._DRIFT)
        if kind == "nudge":
            # Shared detector: the no-shaming rule is not persona specific.
            if StarkPersona._SHAME_RE.search(message):
                return random.choice(self._DRIFT)
            return message
        return f"{message}"

    def greet(self, energy: str = "medium") -> str:
        return {
            "low": "Low battery day, Charan. Small tasks only.",
            "high": "You have got charge today. Let us put it to work.",
        }.get(energy, "Ready when you are, Charan. What is first?")

    def farewell(self, open_items: int = 0) -> str:
        return f"Standing by, Charan. {open_items} item(s) still queued."


PERSONAS = {
    "plain": Persona,
    "stark": StarkPersona,
    "friday": FridayPersona,
    "jarvis": JarvisPersona,
    "eevee": EeveePersona,
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
