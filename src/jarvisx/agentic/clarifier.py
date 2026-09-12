"""Consequential-ambiguity gate: stop and ask instead of guessing.

OpenAI led its GPT-6 Astra announcement with exactly this behaviour. In its own
side-by-side, GPT-5.6 Sol autonomously built a personal career website in 13
minutes 15 seconds; Astra paused after 20 seconds to ask what career the user
was moving into. Sol's output was not wrong so much as *unanchored* -- thirteen
minutes of confident work aimed at a guess.

Alfred had no equivalent. Before this module, an ambiguous instruction went
straight into the tool loop and whatever the model inferred became the answer.

The design constraint is the hard part, and it is why this is not a big pile of
heuristics. **An agent that asks about everything is worse than one that
guesses**, because every question is a interruption the user did not budget for.
OpenAI describes Astra as "waiting only on consequential decisions", and that
word is doing the work. So this gate fires only when both of these hold:

1. The action is irreversible or externally visible -- it deletes, sends,
   publishes, or spends. Undoing it costs the user something real.
2. The target or recipient is not actually specified -- named only by pronoun,
   or by a vague quantifier like "the old ones".

Read-only work never fires it: asking "which files?" before *listing* files
would be absurd. Fully-specified destructive work never fires it either:
"delete build/ and dist/" says exactly what it means and should just run.

The checks are deterministic and offline on purpose. They must be testable
without a model, and they must behave identically every run -- a gate that asks
on Tuesday and not on Wednesday is worse than no gate, because the user cannot
form an expectation of it. A model-backed clarifier can be layered on later, but
the floor has to be predictable.

Deliberately not attempted here: deciding *which* of several reasonable readings
is best. That needs judgement this module does not claim to have. It only
detects that the instruction does not say, and says so plainly.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

__all__ = [
    "Clarification",
    "ClarificationGate",
    "AMBIGUITY_KINDS",
]


AMBIGUITY_KINDS = (
    "destructive_target",
    "outbound_recipient",
    "empty_goal",
)


#: Verbs whose effect cannot be undone by simply not doing it again.
_IRREVERSIBLE = (
    "delete", "deleting", "remove", "removing", "drop", "dropping",
    "wipe", "wiping", "purge", "purging", "erase", "erasing",
    "destroy", "destroying", "truncate", "truncating", "uninstall",
    "send", "sending", "email", "emailing", "message", "messaging",
    "text", "texting", "post", "posting", "publish", "publishing",
    "push", "pushing", "deploy", "deploying", "release", "releasing",
    "pay", "paying", "buy", "buying", "purchase", "purchasing",
    "transfer", "transferring",
)

#: Outward-facing verbs: the effect leaves the machine and reaches a person.
_OUTBOUND = (
    "send", "sending", "email", "emailing", "message", "messaging",
    "text", "texting", "post", "posting", "publish", "publishing",
    "notify", "notifying", "reply", "replying", "forward", "forwarding",
)

#: Words that stand in for a target without naming one.
_VAGUE_TARGET = (
    "it", "them", "those", "these", "that", "this", "everything",
    "all", "the old ones", "the old", "old ones", "stuff", "things",
    "whatever", "some", "any",
)


@dataclass
class Clarification:
    """The gate's verdict on one instruction."""

    needed: bool
    question: str = ""
    kind: str = ""
    reason: str = ""
    #: The specific words that made the instruction unanchored. Surfaced so the
    #: user can see the gate is reacting to their phrasing, not to a mood.
    unresolved: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.needed


class ClarificationGate:
    """Decides whether an instruction is safe to act on as written.

    Parameters
    ----------
    enabled:
        Master switch. When False, :meth:`inspect` always returns "proceed",
        which makes it trivial to run Alfred in a no-questions mode without
        removing the gate from the call path.
    """

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def inspect(self, task: str) -> Clarification:
        """Return a :class:`Clarification` for ``task``.

        Never raises. A gate that throws would take down the run it was
        supposed to be protecting, which is the exact failure mode the rest of
        this package has been scrubbed of.
        """
        if not self.enabled:
            return Clarification(needed=False)

        try:
            text = (task or "").strip()
        except Exception:  # noqa: BLE001 - defensive by contract
            return Clarification(needed=False)

        if not text:
            return Clarification(
                needed=True,
                kind="empty_goal",
                question="What would you like me to do?",
                reason="The instruction was empty, so there was nothing to anchor on.",
            )

        lowered = text.lower()
        words = re.findall(r"[a-z']+", lowered)

        outbound = self._present(words, _OUTBOUND)
        irreversible = self._present(words, _IRREVERSIBLE)

        if not (outbound or irreversible):
            # Read-only or unspecified-effect work. Guessing here is cheap:
            # the worst case is a wrong answer the user can simply correct.
            return Clarification(needed=False)

        vague = self._present(words, _VAGUE_TARGET)
        if not vague:
            # Consequential but concrete. "delete build/ and dist/" names its
            # target and should run without being second-guessed.
            return Clarification(needed=False)

        if outbound:
            return Clarification(
                needed=True,
                kind="outbound_recipient",
                question=(
                    "Who should that go to? Once it is sent I cannot take it back."
                ),
                reason=(
                    "This reaches someone outside this machine, and the recipient "
                    "is not named."
                ),
                unresolved=vague,
            )

        return Clarification(
            needed=True,
            kind="destructive_target",
            question=(
                "Which ones exactly? I would rather ask than delete something "
                "you wanted kept."
            ),
            reason=(
                "This cannot be undone, and the target is referred to but not "
                "named."
            ),
            unresolved=vague,
        )

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #

    @staticmethod
    def _present(words: List[str], candidates) -> List[str]:
        """Return the members of ``candidates`` that occur in ``words``.

        Multi-word candidates ("the old ones") are matched against the joined
        phrase rather than the word list, so they behave like the single words.
        """
        found: List[str] = []
        joined = " ".join(words)
        for c in candidates:
            if " " in c:
                if c in joined:
                    found.append(c)
            elif c in words:
                found.append(c)
        return found
