"""ADHD-oriented task intake.

The failure mode this targets is not "the agent can't do the work" — it is
**initiation**. A brain dump of nine half-formed things produces paralysis,
because the real question is never "what do I need to do" but "what is the
single smallest thing I can start right now, at the energy I currently have".

So this module does four specific things:

1. **splits** a rambling brain dump into discrete items
2. **classifies** each one — task / idea / worry / thing to delegate
3. **derives a next action** that is small enough to actually start
4. **picks by energy**, not by importance — low energy gets a 2-minute task,
   never the big scary one

Everything here is deterministic and offline. An LLM can improve the
splitting, but it is never required, because the whole point is that this has
to work on the bad days.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence

from jarvisx.agentic.types import new_id

# --------------------------------------------------------------------------- #
# Model
# --------------------------------------------------------------------------- #


class ItemKind(str, Enum):
    TASK = "task"            # has a done state; you could act on it
    IDEA = "idea"            # no done state; capture it and stop thinking about it
    WORRY = "worry"          # anxiety, not work — name it, schedule it, drop it
    DELEGATE = "delegate"    # someone else should do this
    QUESTION = "question"    # needs an answer, not effort


class Energy(str, Enum):
    LOW = "low"        # 2-10 minute tasks only
    MEDIUM = "medium"  # up to ~25 minutes
    HIGH = "high"      # deep work is fine


@dataclass
class CapturedItem:
    """One item pulled out of a brain dump."""

    id: str
    title: str
    raw: str
    kind: ItemKind = ItemKind.TASK
    next_action: str = ""
    est_minutes: int = 15
    urgency: int = 1            # 1 (whenever) .. 5 (today, on fire)
    tags: List[str] = field(default_factory=list)
    done: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


# --------------------------------------------------------------------------- #
# Splitting
# --------------------------------------------------------------------------- #

# Sentences that open a new item rather than continuing the previous one.
_SPLIT_RE = re.compile(
    r"""
      (?<=[.!?])\s+            # after sentence punctuation
    | \s*[;\n]\s*              # semicolons and newlines
    | \s*,\s+(?=(?:
          i\s+(?:need|have|should|must|gotta|am|i'?m)
        | also | and\s+then | plus | oh | btw | don'?t\s+forget
        | remember\s+to | todo:
        | some(?:one|body)\s+(?:else\s+)?(?:should|can|could|needs)
        | someday | one\s+day
        | and\s+(?:i\s+)?(?:need|have|should|must|gotta)
        | gotta
      ))
    """,
    re.VERBOSE | re.IGNORECASE,
)

_FILLER_RE = re.compile(
    r"""^(?:um+|uh+|so|ok(?:ay)?|alright|well|like|basically|anyway|also|and|then|oh|
           btw|by\s+the\s+way|hey|right|yeah|yep|hmm|let'?s\s+see|i\s+guess)\b[\s,]*""",
    re.IGNORECASE | re.VERBOSE,
)

# "I need to X" / "gotta X" / "have to X" -> X
_STRIP_MODAL_RE = re.compile(
    r"""^(?:i\s+)?(?:need|have|got|gotta|must|should|ought)\s+(?:to\s+)?""",
    re.IGNORECASE,
)

# Inflected forms matter: \bstress\b does NOT match "stressed", which would
# file "I'm stressed about the report" as a task and put it back in the queue.
_WORRY_RE = re.compile(
    r"""\b(?:
          worried | anxious | stress(?:ed|es|ing|ful)?
        | scared | afraid | dread(?:s|ed|ing)? | dreading
        | overwhelm(?:s|ed|ing)? | panick?(?:s|ed|ing)? | nervous
        | what\s+if | i\s+hate
    )\b""",
    re.IGNORECASE | re.VERBOSE,
)
# Delegation means "somebody else does this". A bare "email X" is NOT delegation
# — "reply to that email from the professor" is your task, and matching it as
# delegate quietly removes real work from the queue.
_DELEGATE_RE = re.compile(
    r"""\b(?:
          delegate
        | hand\s+(?:it\s+)?off
        | not\s+my\s+(?:job|problem|task)
        | some(?:one|body)\s+(?:else\s+)?(?:should|can|could|needs\s+to|ought\s+to)
        | (?:ask|tell|get)\s+[a-z']+\s+to\b
    )\b""",
    re.IGNORECASE | re.VERBOSE,
)
_IDEA_RE = re.compile(
    r"""\b(?:
          someday | one\s+day | would\s+be\s+cool | idea
        | maybe\s+(?:we|i)\s+could
        | what\s+if\s+(?:we|i)\s+(?:built|build|made|make|could|tried|did)
        | dream
    )\b""",
    re.IGNORECASE | re.VERBOSE,
)
_QUESTION_RE = re.compile(r"\?\s*$|\b(how\s+do\s+i|what\s+is|why\s+is|is\s+there)\b", re.IGNORECASE)

_URGENT_RE = re.compile(
    r"\b(today|tonight|asap|urgent|deadline|due|by\s+(?:friday|monday|tomorrow|eod)|"
    r"overdue|late|emergency)\b",
    re.IGNORECASE,
)

_DONE_MARKERS = re.compile(
    r"\b(done|finished|completed|sent|paid|submitted|shipped|fixed)\b", re.IGNORECASE
)


def split_brain_dump(text: str) -> List[str]:
    """Split a rambling brain dump into candidate items.

    Deliberately conservative: it splits on real boundaries (newlines,
    sentence ends, "also / oh / don't forget") and drops filler. Short noise is
    discarded rather than turned into a fake task.
    """
    if not text or not text.strip():
        return []

    chunks = _SPLIT_RE.split(text)
    items: List[str] = []
    for chunk in chunks:
        cleaned = _clean(chunk)
        if cleaned:
            items.append(cleaned)
    return items


def _clean(chunk: str) -> str:
    cleaned = (chunk or "").strip()
    # Strip leading filler repeatedly ("so um also I need to...")
    for _ in range(4):
        stripped = _FILLER_RE.sub("", cleaned, count=1).strip()
        if stripped == cleaned:
            break
        cleaned = stripped
    cleaned = cleaned.strip(" ,.!")
    cleaned = re.sub(r"\s+", " ", cleaned)
    # Discard fragments too short to be an actionable item.
    if len(cleaned) < 4:
        return ""
    return cleaned


# --------------------------------------------------------------------------- #
# Classification
# --------------------------------------------------------------------------- #


def classify(text: str) -> ItemKind:
    """Decide what kind of thing this is.

    IDEA is checked first because its pattern requires an explicit marker or a
    construction verb ("what if we built..."), while WORRY's "what if" would
    otherwise swallow it and tell you to let go of an idea you wanted to keep.
    """
    if _IDEA_RE.search(text):
        return ItemKind.IDEA
    if _WORRY_RE.search(text):
        return ItemKind.WORRY
    if _DELEGATE_RE.search(text):
        return ItemKind.DELEGATE
    if _QUESTION_RE.search(text):
        return ItemKind.QUESTION
    return ItemKind.TASK


def _urgency(text: str) -> int:
    if not _URGENT_RE.search(text):
        return 1
    if re.search(r"\b(today|tonight|asap|urgent|emergency|overdue)\b", text, re.IGNORECASE):
        return 5
    return 3


def _estimate_minutes(text: str) -> int:
    """Rough effort estimate from the words used.

    Under-estimating is the ADHD trap, so anything that looks like a project
    gets a deliberately uncomfortable number.
    """
    lowered = text.lower()
    explicit = re.search(r"(\d+)\s*(?:min|mins|minute|minutes)", lowered)
    if explicit:
        return max(2, min(int(explicit.group(1)), 480))
    explicit_hours = re.search(r"(\d+)\s*(?:hr|hrs|hour|hours)", lowered)
    if explicit_hours:
        return max(15, min(int(explicit_hours.group(1)) * 60, 480))

    if re.search(r"\b(project|rebuild|migrate|redesign|refactor|research|plan|study)\b", lowered):
        return 90
    if re.search(r"\b(write|build|implement|prepare|report|essay|assignment)\b", lowered):
        return 45
    if re.search(r"\b(email|reply|call|book|schedule|pay|order|text)\b", lowered):
        return 5
    if re.search(r"\b(clean|tidy|organize|sort|file)\b", lowered):
        return 15
    return 20


# --------------------------------------------------------------------------- #
# Next actions — the part that actually breaks paralysis
# --------------------------------------------------------------------------- #

# Turn a vague noun-phrase task into a physical first action.
_FIRST_ACTION_RULES = (
    (r"\b(write|essay|report|document|blog|assignment)\b", "Open the file and write one heading"),
    (r"\b(study|learn|revise|read)\b", "Open the material and read for 10 minutes only"),
    (r"\b(email|reply|message|respond)\b", "Open the thread and write the first sentence"),
    (r"\b(call|phone|ring)\b", "Find the number and dial it"),
    (r"\b(clean|tidy|organize|sort)\b", "Set a 10-minute timer and do one surface"),
    (r"\b(book|schedule|appointment)\b", "Open the calendar and pick a slot"),
    (r"\b(pay|bill|invoice)\b", "Open the banking app"),
    (r"\b(fix|bug|debug|broken)\b", "Reproduce it once and paste the error somewhere"),
    (r"\b(build|implement|code|develop)\b", "Write the function signature only"),
    (r"\b(plan|research|decide)\b", "Write down three options, no more"),
)


def next_action(text: str, kind: ItemKind = ItemKind.TASK) -> str:
    """Return the smallest physical action that starts this task.

    For non-tasks, the "action" is to stop treating it as work — which is the
    actual instruction an ADHD brain needs to hear.
    """
    if kind is ItemKind.WORRY:
        return "Not a task. Write one line about it and let it go for now."
    if kind is ItemKind.IDEA:
        return "Not a task. It is captured — you do not have to hold it in your head."
    if kind is ItemKind.DELEGATE:
        return "Send one message asking for it. That is the whole task."
    if kind is ItemKind.QUESTION:
        return "Ask it once and wait. Do not research it yourself."

    lowered = text.lower()
    for pattern, action in _FIRST_ACTION_RULES:
        if re.search(pattern, lowered):
            return action
    return "Do the first two minutes of it. Nothing more."


def breakdown(text: str, steps: int = 3) -> List[str]:
    """Split a task into micro-steps, each small enough to start.

    Step one is always trivial on purpose: initiation is the bottleneck, not
    capacity. If step one takes effort, it will not happen.
    """
    kind = classify(text)
    if kind is not ItemKind.TASK:
        return [next_action(text, kind)]

    lowered = text.lower()
    for pattern, action in _FIRST_ACTION_RULES:
        if re.search(pattern, lowered):
            return [
                action,
                "Do one small piece and stop.",
                "Decide: keep going, or schedule the rest for later.",
            ][:steps]

    return [
        "Open whatever this lives in.",
        "Do the obvious two-minute part.",
        "Write down the next step so future-you does not have to think.",
    ][:steps]


# --------------------------------------------------------------------------- #
# Engine
# --------------------------------------------------------------------------- #


class IntakeEngine:
    """Captures brain dumps and answers "what do I do right now"."""

    def __init__(self) -> None:
        self.items: List[CapturedItem] = []

    # -- capture ----------------------------------------------------------- #

    def capture(self, brain_dump: str) -> List[CapturedItem]:
        """Split a brain dump into classified items with next actions."""
        created: List[CapturedItem] = []
        for raw in split_brain_dump(brain_dump):
            kind = classify(raw)
            item = CapturedItem(
                id=new_id("item"),
                title=_title(raw),
                raw=raw,
                kind=kind,
                next_action=next_action(raw, kind),
                est_minutes=_estimate_minutes(raw),
                urgency=_urgency(raw),
                tags=_tags(raw),
                done=bool(_DONE_MARKERS.search(raw)),
            )
            self.items.append(item)
            created.append(item)
        return created

    # -- selection --------------------------------------------------------- #

    @property
    def open_items(self) -> List[CapturedItem]:
        return [i for i in self.items if not i.done]

    def pick(
        self,
        energy: Energy = Energy.MEDIUM,
        minutes_available: Optional[int] = None,
    ) -> Optional[CapturedItem]:
        """Choose ONE item to do next, matched to current energy.

        Deliberately does *not* return the most important thing. On low energy
        the most important thing is the thing you will not start, and failing
        to start is worse than doing something small.
        """
        candidates = [i for i in self.open_items if i.kind is ItemKind.TASK]
        if not candidates:
            return None

        ceiling = {
            Energy.LOW: 10,
            Energy.MEDIUM: 25,
            Energy.HIGH: 480,
        }[energy]
        if minutes_available is not None:
            ceiling = min(ceiling, max(2, minutes_available))

        fitting = [i for i in candidates if i.est_minutes <= ceiling]
        # Nothing fits? Take the smallest thing there is, rather than nothing.
        pool = fitting or sorted(candidates, key=lambda i: i.est_minutes)[:1]

        # Within what fits, urgency wins, then the cheapest start.
        return sorted(pool, key=lambda i: (-i.urgency, i.est_minutes))[0]

    def plan(
        self,
        brain_dump: str,
        energy: Energy = Energy.MEDIUM,
        minutes_available: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Capture, then answer "what now" in one call."""
        captured = self.capture(brain_dump)
        chosen = self.pick(energy, minutes_available)
        return {
            "captured": [i.to_dict() for i in captured],
            "counts": {
                kind.value: len([i for i in captured if i.kind is kind])
                for kind in ItemKind
            },
            "do_this_next": chosen.to_dict() if chosen else None,
            "steps": breakdown(chosen.raw, 3) if chosen else [],
            "energy": energy.value,
            "not_your_problem": [
                i.title for i in captured if i.kind in (ItemKind.DELEGATE, ItemKind.WORRY)
            ],
        }

    # -- bookkeeping ------------------------------------------------------- #

    def complete(self, item_id: str) -> bool:
        for item in self.items:
            if item.id == item_id:
                item.done = True
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {"items": [i.to_dict() for i in self.items]}

    def load(self, payload: Dict[str, Any]) -> None:
        for raw in payload.get("items", []):
            self.items.append(
                CapturedItem(
                    id=raw.get("id") or new_id("item"),
                    title=raw.get("title", ""),
                    raw=raw.get("raw", ""),
                    kind=ItemKind(raw.get("kind", "task")),
                    next_action=raw.get("next_action", ""),
                    est_minutes=int(raw.get("est_minutes", 15)),
                    urgency=int(raw.get("urgency", 1)),
                    tags=list(raw.get("tags", [])),
                    done=bool(raw.get("done", False)),
                )
            )


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _title(raw: str, limit: int = 60) -> str:
    """A short label for display, without losing the original in `raw`."""
    stripped = _STRIP_MODAL_RE.sub("", raw, count=1).strip()
    stripped = stripped[0].upper() + stripped[1:] if stripped else raw
    return stripped if len(stripped) <= limit else stripped[: limit - 1] + "…"


def _tags(raw: str) -> List[str]:
    tags: List[str] = []
    lowered = raw.lower()
    if re.search(r"\b(college|assignment|exam|study|lecture|homework|syllabus)\b", lowered):
        tags.append("study")
    if re.search(r"\b(work|boss|client|meeting|project)\b", lowered):
        tags.append("work")
    if re.search(r"\b(bill|pay|bank|money|rent)\b", lowered):
        tags.append("money")
    if re.search(r"\b(health|doctor|gym|medicine|dentist)\b", lowered):
        tags.append("health")
    if re.search(r"\b(email|call|reply|message|text)\b", lowered):
        tags.append("comms")
    return tags
