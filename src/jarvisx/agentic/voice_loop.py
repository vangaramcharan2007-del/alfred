"""The voice loop: listens, decides, acts, and speaks back.

This is the connective tissue the repository was missing. The pieces already
existed but never met:

    ``SecureVoiceGateway``  wake word + destructive-command policy   (voice/)
    ``FastSTTEngine``       faster-whisper transcription             (voice/)
    ``RealTTSEngine``       pyttsx3 speech output                    (voice/)
    ``IntakeEngine``        brain dump -> one next action            (agentic/)
    ``Orchestrator``        goal -> planned, verified work           (agentic/)

Every audio dependency is optional. With no microphone, no speaker and no
model installed, the loop still runs end to end on text — which is what makes
it testable in CI and usable over SSH.

The routing decision is deliberately conservative: **most speech becomes a
captured item, not an autonomous run.** Firing an agent at every utterance is
how you end up with nine half-finished automations and no idea what happened.
Only an explicit "do/build/write/fix/run" hands work to the orchestrator.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable

from jarvisx.agentic.intake import Energy, IntakeEngine

logger = logging.getLogger("jarvisx.agentic.voice_loop")


# --------------------------------------------------------------------------- #
# Audio I/O contracts
# --------------------------------------------------------------------------- #


@runtime_checkable
class SpeechInput(Protocol):
    """Returns one transcript, or None when nothing intelligible was heard."""

    def listen(self) -> Optional[str]: ...


@runtime_checkable
class SpeechOutput(Protocol):
    def say(self, text: str, context: Optional[Dict[str, Any]] = None) -> None: ...


def _speak(sink: "SpeechOutput", text: str, context: Optional[Dict[str, Any]] = None) -> None:
    """Speak through a sink that may or may not accept context.

    Sinks injected from outside (tests, third-party TTS) may still have a
    one-argument ``say``. Refusing to speak because a persona could not be told
    the intent would be the wrong trade, so fall back to text only.
    """
    try:
        sink.say(text, context)
    except TypeError:
        sink.say(text)


class ConsoleInput:
    """Text fallback for when there is no microphone (or no audio deps)."""

    name = "console"

    def __init__(self, prompt: str = "you> ", lines: Optional[List[str]] = None):
        self.prompt = prompt
        self._lines = list(lines) if lines is not None else None
        self._index = 0

    def listen(self) -> Optional[str]:
        if self._lines is not None:
            if self._index >= len(self._lines):
                return None
            line = self._lines[self._index]
            self._index += 1
            print(f"{self.prompt}{line}")
            return line
        try:
            return input(self.prompt)
        except (EOFError, KeyboardInterrupt):
            return None


class ConsoleOutput:
    """Text fallback speaker. Collects everything it said."""

    name = "console"

    def __init__(self) -> None:
        self.spoken: List[str] = []

    def say(self, text: str, context: Optional[Dict[str, Any]] = None) -> None:
        self.spoken.append(text)
        print(f"alfred> {text}")


class WhisperMicInput:
    """Real microphone input via the repo's existing engines.

    Degrades to :class:`ConsoleInput` when ``sounddevice`` / ``faster_whisper``
    are unavailable, so the loop never hard-fails on a machine without audio.
    """

    name = "whisper-mic"

    def __init__(
        self,
        wake_word: str = "alfred",
        seconds: float = 6.0,
        sample_rate: int = 16_000,
        model_size: str = "base.en",
        fallback: Optional[SpeechInput] = None,
    ):
        self.wake_word = wake_word
        self.seconds = seconds
        self.sample_rate = sample_rate
        self._stt = None
        self._fallback = fallback or ConsoleInput()
        try:
            import sounddevice  # noqa: F401
            from jarvisx.voice.stt_engine import FastSTTEngine

            stt = FastSTTEngine(model_size=model_size)
            # Same trap as TTSOutput: FastSTTEngine swallows a missing
            # faster_whisper and leaves _whisper_model as None. sounddevice can
            # be installed while whisper is not, and then the loop would claim
            # to be listening and hear nothing, forever.
            self.available = getattr(stt, "_whisper_model", None) is not None
            self._stt = stt if self.available else None
            self._sounddevice = sounddevice if self.available else None
            if not self.available:
                logger.info("whisper model unavailable; using text input")
        except Exception as exc:  # noqa: BLE001 - missing audio stack
            logger.info("microphone unavailable (%s); using text input", exc)
            self.available = False

    def listen(self) -> Optional[str]:
        if not self.available:
            return self._fallback.listen()
        import tempfile
        from pathlib import Path

        try:
            recording = self._sounddevice.rec(
                int(self.seconds * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
            )
            self._sounddevice.wait()

            import numpy as np  # local import: only needed on the audio path

            path = Path(tempfile.gettempdir()) / "alfred_utterance.wav"
            import wave

            data = (np.squeeze(recording) * 32767).astype("<i2")
            with wave.open(str(path), "wb") as handle:
                handle.setnchannels(1)
                handle.setsampwidth(2)
                handle.setframerate(self.sample_rate)
                handle.writeframes(data.tobytes())

            result = self._stt.transcribe_audio_file(str(path))
            text = (result.text or "").strip()
            return text or None
        except Exception as exc:  # noqa: BLE001
            logger.warning("microphone capture failed: %s", exc)
            return self._fallback.listen()


class WakeWordInput:
    """Hands-free input: hear a wake word, then take the command after it.

    Wraps the repo's shipped :class:`SovereignWakeWordEngine`, which until now
    was imported by six other modules but never by the agent itself. Two things
    needed fixing to make it usable here:

    - **It ignores the configured wake word.** ``WAKE_WORDS`` is a hardcoded
      class list, so ``--wake-word eevee`` would have been silently unheard.
      The configured word is injected onto the instance, which shadows the
      class attribute without editing the voice module.
    - **"Nothing heard" is not the end of the session.** :meth:`listen` on the
      other sources returns ``None`` to mean *input exhausted*, and
      ``VoiceAgentLoop.run`` stops on that. For a wake word, silence is the
      normal state, so this keeps listening until something is actually said.
    """

    name = "wake-word"

    def __init__(
        self,
        wake_word: str = "alfred",
        fallback: Optional[SpeechInput] = None,
        engine: Optional[Any] = None,
        attempts: int = 1000,
        clip_seconds: float = 3.5,
        should_stop: Optional[Callable[[], bool]] = None,
    ):
        self.wake_word = (wake_word or "alfred").strip().lower()
        self.attempts = max(1, attempts)
        self.clip_seconds = clip_seconds
        self._fallback = fallback or WhisperMicInput(wake_word=self.wake_word)
        self._should_stop = should_stop

        if engine is not None:
            # Injected for tests: no audio stack exists in CI, and the
            # wake-phrase logic should still be exercised.
            self._engine = engine
            self.available = True
        else:
            self._engine = None
            self.available = False
            try:
                from jarvisx.voice.sovereign_wake_word_engine import (
                    SovereignWakeWordEngine,
                )

                engine_ = SovereignWakeWordEngine()
                # Shadow the hardcoded list so the configured word is the one
                # actually listened for. The originals stay, because a user who
                # says "jarvis" out of habit should still be heard.
                engine_.WAKE_WORDS = [self.wake_word, *SovereignWakeWordEngine.WAKE_WORDS]
                self._engine = engine_
                self.available = True
            except Exception as exc:  # noqa: BLE001 - missing audio stack
                logger.info("wake word unavailable (%s); falling back", exc)

    def listen(self) -> Optional[str]:
        """Block until something is actually said, then return the command.

        Silence is the normal state for a hands-free agent, so this keeps
        waiting rather than returning. It gives up only when ``should_stop``
        says so or :attr:`attempts` clips pass, which is what lets the runtime
        shut down cleanly while the room is quiet.
        """
        if not self.available or self._engine is None:
            return self._fallback.listen()

        for _ in range(self.attempts):
            if self._should_stop is not None and self._should_stop():
                return None
            heard = self._capture()
            if not heard:
                continue
            command = self._extract(heard)
            if command:
                return command
        return None

    def _capture(self) -> Optional[str]:
        try:
            text = self._engine.record_and_transcribe_manual(self.clip_seconds)
        except Exception as exc:  # noqa: BLE001 - hardware can fail any time
            logger.warning("wake word capture failed: %s", exc)
            return None
        return (text or "").strip() or None

    # Words that are part of getting someone's attention rather than part of a
    # request. "hey alfred" is a bare wake phrase; stripping only "alfred"
    # would leave "hey" behind, and "hey" would then be routed as a command.
    _FILLER = frozenset({
        "hey", "hi", "hello", "ok", "okay", "yo", "please", "um", "uh",
        "and", "so", "then", "well",
    })

    def _wake_phrases(self) -> List[str]:
        """Every phrase that counts as addressing us, longest first."""
        engine_words = list(getattr(self._engine, "WAKE_WORDS", []) or [])
        phrases = {self.wake_word, *engine_words}
        # Include "<filler> <wake word>" so "hey alfred" is matched whole.
        phrases.update(f"{filler} {self.wake_word}" for filler in ("hey", "hi", "ok", "okay", "yo"))
        return sorted((p.lower() for p in phrases if p), key=len, reverse=True)

    def _extract(self, heard: str) -> Optional[str]:
        """Return the command if this clip was addressed to us, else ``None``.

        Deliberately stricter than the shipped engine's own gate, which also
        fires on any two-word utterance. That means a conversation across the
        room drives the agent, and an agent that acts on things it was not
        asked to do is worse than one that waits.
        """
        clean = heard.strip()
        lower = clean.lower()
        if self.wake_word not in lower:
            return None

        # Strip the longest matching wake phrase here rather than trusting the
        # engine. Its extract_command only knows its own hardcoded list, so a
        # custom --wake-word would survive into the command text and the router
        # would see "eevee what should i do".
        command = clean
        lowered = lower
        for phrase in self._wake_phrases():
            index = lowered.find(phrase)
            if index >= 0:
                command = (
                    command[:index] + " " + command[index + len(phrase):]
                )
                lowered = command.lower()
                break
        # Removing a phrase mid-sentence leaves a gap; collapse it so the
        # router sees one clean sentence rather than "ok   pay the bill".
        command = " ".join(command.split()).strip(" ,:.-\t\n")

        # Also let the engine tidy up any wake word it recognises, then strip
        # ours again in case it handed the prefix straight back.
        strip = getattr(self._engine, "extract_command", None)
        if callable(strip):
            try:
                engine_result = (strip(command) or "").strip()
            except Exception as exc:  # noqa: BLE001 - never lose the utterance
                logger.warning("extract_command failed: %s", exc)
            else:
                if engine_result:
                    command = engine_result
            lowered = command.lower()
            if lowered.startswith(self.wake_word):
                command = command[len(self.wake_word):].strip(" ,:.-\t\n")

        return self._drop_filler(command)

    def _drop_filler(self, command: str) -> Optional[str]:
        """Return ``None`` when all that is left is attention-getting noise."""
        words = [w for w in command.split() if w.strip(" ,:.-")]
        if not words:
            return None
        if all(w.lower().strip(" ,:.-?!") in self._FILLER for w in words):
            return None
        return command or None

        return command or None


class TTSOutput:
    """Real speech output via the repo's existing pyttsx3 engine."""

    name = "tts"

    def __init__(self, fallback: Optional[SpeechOutput] = None, **kwargs: Any):
        self._engine = None
        self._fallback = fallback or ConsoleOutput()
        try:
            from jarvisx.voice.tts_engine import RealTTSEngine

            engine = RealTTSEngine(**kwargs)
            # Importing the engine is not the same as having a working one.
            # RealTTSEngine swallows a missing pyttsx3 and leaves _engine as
            # None, so treating a successful import as success makes `doctor`
            # promise speech that will never come. Check the real signal.
            self.available = getattr(engine, "_engine", None) is not None
            self._engine = engine if self.available else None
            if not self.available:
                logger.info("TTS engine constructed but has no audio backend; using text")
        except Exception as exc:  # noqa: BLE001
            logger.info("TTS unavailable (%s); using text output", exc)
            self.available = False

    def say(self, text: str, context: Optional[Dict[str, Any]] = None) -> None:
        if not self.available:
            self._fallback.say(text, context)
            return
        try:
            self._engine.speak(text)
        except Exception as exc:  # noqa: BLE001 - never lose the message
            logger.warning("TTS failed (%s); falling back to text", exc)
            self._fallback.say(text)


# --------------------------------------------------------------------------- #
# Routing
# --------------------------------------------------------------------------- #


class Intent(str, Enum):
    BRAIN_DUMP = "brain_dump"    # capture everything, suggest one thing
    WHAT_NEXT = "what_next"      # just tell me what to do
    DO_WORK = "do_work"          # hand it to the orchestrator
    OPEN = "open"                # launch an app or site right now
    DONE = "done"                # mark something finished
    STATUS = "status"            # what have I captured / what's the state
    HELP = "help"
    QUIT = "quit"                # stop the loop
    UNKNOWN = "unknown"


def _quit_re():
    import re

    return re.compile(
        r"^(?:quit|exit|stop|goodbye|bye|that'?s\s+all|shut\s+down)\b\.?!?$",
        re.IGNORECASE,
    )


# Explicit verbs that authorise autonomous execution. Anything else is captured.
_DO_WORK_RE = None


def _do_work_re():
    global _DO_WORK_RE
    if _DO_WORK_RE is None:
        import re

        _DO_WORK_RE = re.compile(
            r"""^(?:please\s+)?(?:can\s+you\s+|could\s+you\s+|alfred[,\s]+)?
                (?:do|build|write|create|fix|run|generate|implement|make|refactor|debug)\b""",
            re.IGNORECASE | re.VERBOSE,
        )
    return _DO_WORK_RE


def _open_re():
    """A request to launch something, rather than a task to remember.

    This is the line between an assistant and a notepad. "open spotify" said
    out loud means *open Spotify now*; writing it onto a task list and saying
    "got it, I wrote that down" is the single most disappointing thing a voice
    assistant can do.
    """
    import re

    return re.compile(
        r"""^(?:please\s+)?(?:hey\s+)?(?:alfred[,\s]+|jarvis[,\s]+|eevee[,\s]+)?
            (?:open|launch|start|fire\s+up|bring\s+up|play|put\s+on|load)\b""",
        re.IGNORECASE | re.VERBOSE,
    )


def _artifact_re():
    """Code artifacts. The gate that keeps personal tasks out of the agent.

    "write", "fix" and "make" are the most common verbs in an ADHD brain dump —
    "write the assignment", "fix the sink", "make the appointment". Handing
    those to a coding agent is not just useless, it silently destroys the task,
    because the user believes it is now on their list. So a verb alone is not
    enough: there has to be a thing to build.
    """
    import re

    return re.compile(
        r"""\b(?:
              script | code | coding | function | method | class | module
            | package | library | api | endpoint | server | client | parser
            | cli | tool | utility | program | app | application | website
            | webpage | bot | crawler | scraper | regex | algorithm
            | test(?:s|ing)? | unittest | pytest
            | csv | json | yaml | yml | xml | sql | html | css
            | python | javascript | typescript | java | rust | golang
            | dockerfile | migration | webhook | cron\s*job
            | refactor(?:ing)? | bug\s+fix | stack\s*trace | traceback
            | bug | crash | exception | error\s+(?:message|log)| traceback
            | nullpointer | segfault | deadlock | deadlock
        )\b""",
        re.IGNORECASE | re.VERBOSE,
    )


def _what_next_re():
    import re

    return re.compile(
        r"\b(?:what\s+(?:should\s+i\s+do|now|next)|what'?s\s+next|where\s+do\s+i\s+start|"
        r"i'?m\s+(?:stuck|lost|overwhelmed)|can'?t\s+start|don'?t\s+know\s+where)\b",
        re.IGNORECASE,
    )


def _dump_re():
    import re

    return re.compile(
        r"\b(?:brain\s*dump|here'?s?\s+everything|i\s+have\s+(?:so\s+much|a\s+lot|too\s+much)|"
        r"my\s+head|so\s+much\s+to\s+do|remember\s+(?:all\s+)?this|dump)\b",
        re.IGNORECASE,
    )


def _done_re():
    import re

    return re.compile(
        r"^(?:i'?m\s+done(?:\s+with)?|done(?:\s+with)?|finished|completed|mark\s+done)\b",
        re.IGNORECASE,
    )


def _status_re():
    import re

    return re.compile(
        r"\b(?:status|what'?s?\s+(?:on|in)\s+my\s+(?:list|plate|queue)|"
        r"what\s+have\s+i\s+(?:got|captured)|show\s+me\s+my\s+list|list\s+my\s+tasks)\b",
        re.IGNORECASE,
    )


def _help_re():
    import re

    return re.compile(r"^(?:help|what\s+can\s+you\s+do|how\s+do\s+i\s+use\s+this)\b", re.IGNORECASE)


def _trigger_prefix_re():
    """Leading phrase that signals intent but is not part of the content.

    Without stripping this, "brain dump: write the report" is captured as an
    item literally titled "Brain dump: write the report".
    """
    import re

    return re.compile(
        r"""^\s*(?:
              brain\s*dump | dump | here'?s?\s+everything | everything\s+i\s+(?:have|need)
            | remember\s+(?:all\s+)?this | my\s+head\s+is\s+full
            | i\s+have\s+(?:so\s+much|a\s+lot|too\s+much)\s+(?:to\s+do|on\s+my\s+mind|going\s+on)
            | so\s+much\s+to\s+do | note\s+to\s+self
        )\s*[:\-–,]?\s*""",
        re.IGNORECASE | re.VERBOSE,
    )


def strip_trigger(text: str) -> str:
    """Remove a leading capture trigger so it does not pollute the item text."""
    cleaned = _trigger_prefix_re().sub("", text or "", count=1).strip(" :,-–")
    return cleaned or (text or "").strip()


def route(text: str, addressed: bool = False, physical: bool = False) -> Intent:
    """Decide what an utterance means. Deterministic and offline.

    Order matters: an explicit "write the report" is work, but "what should I
    do" must never trigger an agent — it is a request for a decision.

    ``addressed`` is True when the speaker used the wake word. Naming Alfred is
    an explicit command to Alfred, so it skips the artifact gate that keeps
    personal tasks out of the coding agent.

    ``physical`` is True only when there is something that can actually launch
    an app. Without it, "open spotify" falls through to capture, which is the
    honest degradation: writing it down is better than claiming it opened.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return Intent.UNKNOWN
    if _quit_re().match(cleaned):
        return Intent.QUIT
    if _help_re().search(cleaned):
        return Intent.HELP
    if _status_re().search(cleaned):
        return Intent.STATUS
    if _what_next_re().search(cleaned):
        return Intent.WHAT_NEXT
    if _done_re().search(cleaned):
        return Intent.DONE
    if physical and _open_re().search(cleaned):
        return Intent.OPEN
    if _dump_re().search(cleaned):
        return Intent.BRAIN_DUMP
    if _do_work_re().search(cleaned):
        # A build verb alone is not a build request. "write the assignment" is
        # a task to capture; "write a script that dedupes CSV" is work to run.
        # Without this gate the agent silently swallows half of every brain
        # dump, and the user believes it is safely on their list.
        if addressed or _artifact_re().search(cleaned):
            return Intent.DO_WORK
        return Intent.BRAIN_DUMP
    # A long rambling sentence is almost certainly a dump, not a command.
    if len(cleaned.split()) >= 12:
        return Intent.BRAIN_DUMP
    return Intent.UNKNOWN


# --------------------------------------------------------------------------- #
# The loop
# --------------------------------------------------------------------------- #


@dataclass
class VoiceTurn:
    """One listen -> decide -> act -> speak cycle."""

    transcript: str
    intent: Intent
    spoken: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    blocked: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transcript": self.transcript,
            "intent": self.intent.value,
            "spoken": self.spoken,
            "payload": self.payload,
            "blocked": self.blocked,
        }


def _context_for(turn: "VoiceTurn") -> Dict[str, Any]:
    """Derive persona context from a finished turn.

    Kept deliberately narrow: only what the payload actually proves. Inventing
    context here would let a persona say something the engine did not decide.
    """
    payload = turn.payload or {}
    if turn.intent in (Intent.WHAT_NEXT, Intent.BRAIN_DUMP):
        item = payload.get("item") or payload.get("do_this_next")
        if item:
            return {
                "kind": "picked",
                "task": item.get("title", ""),
                "minutes": item.get("est_minutes", "?"),
            }
    if turn.intent is Intent.DONE:
        return {"kind": "done"}
    if turn.intent is Intent.UNKNOWN:
        return {"kind": "captured"}
    return {}


class VoiceAgentLoop:
    """Listens, routes, acts, and reports back out loud."""

    def __init__(
        self,
        stt: Optional[SpeechInput] = None,
        tts: Optional[SpeechOutput] = None,
        intake: Optional[IntakeEngine] = None,
        runner: Optional[Callable[[str], Dict[str, Any]]] = None,
        wake_word: str = "alfred",
        energy: Energy = Energy.MEDIUM,
        event_bus: Optional[Any] = None,
        physical: Optional[Any] = None,
    ):
        self.stt: SpeechInput = stt or ConsoleInput()
        self.tts: SpeechOutput = tts or ConsoleOutput()
        self.intake = intake or IntakeEngine()
        # `runner` is the bridge to the orchestrator. Injected so the loop stays
        # testable without spinning up a model or a sandbox.
        self.runner = runner
        # `physical` is an AgentToolRegistry with open_app_or_website in it.
        # Injected for the same reason, and because "open spotify" must only
        # route to OPEN when something can actually open Spotify.
        self.physical = physical
        self.wake_word = wake_word.lower()
        self.energy = energy
        self.turns: List[VoiceTurn] = []

        self._gateway = None
        try:
            from jarvisx.events.event_bus import EventBus
            from jarvisx.voice.voice_gateway import SecureVoiceGateway

            self._gateway = SecureVoiceGateway(
                event_bus=event_bus or EventBus(), wake_word=wake_word
            )
        except Exception as exc:  # noqa: BLE001 - loop works without the gateway
            logger.info("voice gateway unavailable (%s); policy checks inline", exc)

    # ------------------------------------------------------------------ #
    # Core
    # ------------------------------------------------------------------ #

    def handle(self, transcript: str) -> VoiceTurn:
        """Process one transcript. Pure text in, structured turn out."""
        text = (transcript or "").strip()
        turn = VoiceTurn(transcript=text, intent=Intent.UNKNOWN)

        if not text:
            turn.spoken = "I did not catch that."
            self._finish(turn)
            return turn

        # Policy gate first: wake-word stripping and destructive-command block.
        body = text
        if self._gateway is not None:
            gate = self._gateway.process_spoken_utterance(text)
            status = gate.get("status")
            if status == "BLOCKED_BY_POLICY":
                turn.blocked = True
                turn.spoken = "I am not running that without you confirming it first."
                turn.payload = {"gate": gate}
                self._finish(turn)
                return turn
            if status == "WAKE_ACKNOWLEDGED":
                turn.intent = Intent.HELP
                turn.spoken = "I am listening. Tell me everything, or say what to do."
                self._finish(turn)
                return turn
            body = gate.get("intent") or text
        else:
            body = self._strip_wake_word(text)

        turn.intent = route(
            body,
            addressed=self._addresses_wake_word(text),
            physical=self.physical is not None,
        )
        handler = {
            Intent.BRAIN_DUMP: self._on_brain_dump,
            Intent.WHAT_NEXT: self._on_what_next,
            Intent.DO_WORK: self._on_do_work,
            Intent.OPEN: self._on_open,
            Intent.DONE: self._on_done,
            Intent.STATUS: self._on_status,
            Intent.HELP: self._on_help,
            Intent.QUIT: self._on_quit,
            Intent.UNKNOWN: self._on_unknown,
        }[turn.intent]
        handler(body, turn)
        self._finish(turn)
        return turn

    def listen_once(self) -> Optional[VoiceTurn]:
        """One full cycle: hear something, deal with it, say the result."""
        transcript = self.stt.listen()
        if transcript is None:
            return None
        turn = self.handle(transcript)
        if turn.spoken:
            # Pass the turn's context so a persona can re-voice by intent
            # rather than guessing from prose. Without this every reply takes
            # the persona's fall-through branch and the templates are dead code.
            _speak(self.tts, turn.spoken, _context_for(turn))
        return turn


    def run(self, max_turns: int = 20) -> List[VoiceTurn]:
        """Loop until input is exhausted, the user quits, or `max_turns`."""
        for _ in range(max_turns):
            turn = self.listen_once()
            if turn is None:
                break
            if turn.intent is Intent.QUIT:
                break
        return self.turns

    # ------------------------------------------------------------------ #
    # Handlers
    # ------------------------------------------------------------------ #

    def _on_brain_dump(self, body: str, turn: VoiceTurn) -> None:
        plan = self.intake.plan(strip_trigger(body), energy=self.energy)
        turn.payload = plan
        turn.spoken = _speak_plan(plan)

    def _on_what_next(self, body: str, turn: VoiceTurn) -> None:
        pick = self.intake.pick(self.energy)
        if pick is None:
            turn.spoken = "Nothing captured yet. Tell me everything that is on your mind."
            turn.payload = {"open_items": 0}
            return
        steps = _breakdown(pick.raw)
        turn.payload = {"item": pick.to_dict(), "steps": steps}
        turn.spoken = (
            f"Do this one: {pick.title}. "
            f"Start by {steps[0].lower() if steps else 'doing two minutes of it'}. "
            f"About {pick.est_minutes} minutes. Nothing else until that is done."
        )

    def _on_do_work(self, body: str, turn: VoiceTurn) -> None:
        if self.runner is None:
            turn.spoken = (
                "I can run that, but no agent backend is wired up right now. "
                "Run python -m jarvisx.agentic doctor to see what is missing."
            )
            return
        try:
            result = self.runner(body)
        except Exception as exc:  # noqa: BLE001 - never crash the loop
            logger.exception("agent run failed")
            turn.spoken = f"That failed: {exc}"
            turn.payload = {"error": str(exc)}
            return
        turn.payload = result
        turn.spoken = _speak_run(result)

    def _on_done(self, body: str, turn: VoiceTurn) -> None:
        target = _done_re().sub("", body).strip(" .,")
        matched = _match_item(self.intake, target)
        if matched is None:
            turn.spoken = f"I could not find '{target or 'that'}' in your list."
            return
        self.intake.complete(matched.id)
        nxt = self.intake.pick(self.energy)
        turn.payload = {"completed": matched.to_dict()}
        turn.spoken = (
            f"Done: {matched.title}. "
            + (f"Next, if you want: {nxt.title}." if nxt else "Nothing else captured. Nice.")
        )

    def _on_status(self, body: str, turn: VoiceTurn) -> None:
        open_items = self.intake.open_items
        turn.payload = {"open_items": len(open_items), "items": [i.to_dict() for i in open_items]}
        if not open_items:
            turn.spoken = "Your list is empty. Either you are free, or you have not told me anything yet."
            return
        tasks = [i for i in open_items if i.kind.value == "task"]
        turn.spoken = (
            f"You have {len(open_items)} open items, {len(tasks)} of them actual tasks. "
            f"The rest are ideas, worries or somebody else's problem."
        )

    def _on_quit(self, body: str, turn: VoiceTurn) -> None:
        open_items = len(self.intake.open_items)
        turn.spoken = (
            f"Stopping. You have {open_items} open item"
            f"{'s' if open_items != 1 else ''} saved for next time."
        )

    def _on_help(self, body: str, turn: VoiceTurn) -> None:
        turn.spoken = (
            "Tell me everything on your mind and I will pick one thing for you. "
            "Say 'what next' for a decision, 'done with X' to close it, "
            "or 'build X' to hand real work to an agent."
        )

    def _on_open(self, body: str, turn: VoiceTurn) -> None:
        """Launch an app or site now, rather than writing it onto a list."""
        from jarvisx.agentic.types import ToolCall

        if self.physical is None:
            # Cannot happen via route(), which needs physical to pick OPEN,
            # but a handler must never assume its caller checked.
            turn.spoken = "I cannot open anything right now — no desktop reach."
            return

        target = strip_trigger(body).strip()
        obs = self.physical.invoke(
            ToolCall(name="open_app_or_website", arguments={"target": target}),
            approve=lambda tool, args: True,   # opening a tab is SAFE, never ask
        )
        turn.payload = {"target": target, "observation": obs.to_dict()}

        if obs.denied:
            turn.spoken = f"I am not opening that: {obs.error}"
        elif not obs.ok:
            turn.spoken = f"That did not open — {obs.error}"
        else:
            label = (obs.output or {}).get("label", target)
            turn.spoken = f"Opening {label}."

    def _on_unknown(self, body: str, turn: VoiceTurn) -> None:
        """Ambiguous speech is captured, not guessed at."""
        captured = self.intake.capture(strip_trigger(body))
        turn.payload = {"captured": [i.to_dict() for i in captured]}
        if captured:
            turn.spoken = (
                f"Got it, I wrote that down as {len(captured)} item"
                f"{'s' if len(captured) != 1 else ''}. Say 'what next' when you want a task."
            )
        else:
            turn.spoken = "Say 'help' if you want to know what I can do."

    # ------------------------------------------------------------------ #
    # Plumbing
    # ------------------------------------------------------------------ #

    def _addresses_wake_word(self, text: str) -> bool:
        """True when the speaker named Alfred, i.e. is issuing a command.

        Naming the assistant is the clearest signal that what follows is work
        for it rather than a thought to capture. Checked on the raw text,
        because _strip_wake_word removes it before routing.
        """
        lowered = (text or "").lower()
        return self.wake_word.lower() in lowered

    def _strip_wake_word(self, text: str) -> str:
        cleaned = text.lower()
        for phrase in (f"hey {self.wake_word}", self.wake_word):
            cleaned = cleaned.replace(phrase, "")
        return cleaned.strip(" ,.!?") or text.strip()

    def _finish(self, turn: VoiceTurn) -> None:
        self.turns.append(turn)
        logger.info("voice turn intent=%s blocked=%s", turn.intent.value, turn.blocked)


# --------------------------------------------------------------------------- #
# Phrasing — keep it short; long speech is unusable
# --------------------------------------------------------------------------- #


def _speak_plan(plan: Dict[str, Any]) -> str:
    counts = plan.get("counts", {})
    captured = sum(counts.values())
    not_yours = plan.get("not_your_problem") or []
    chosen = plan.get("do_this_next")

    parts = [f"Wrote down {captured} things."]
    if not_yours:
        parts.append(f"{len(not_yours)} of them are not yours to do.")
    if chosen:
        parts.append(
            f"Do this one: {chosen['title']}. "
            f"Start by {(_breakdown(chosen['raw'])[0]).lower()}."
        )
    else:
        parts.append("Nothing in there is a task you need to start right now.")
    return " ".join(parts)


def _speak_run(result: Dict[str, Any]) -> str:
    if not isinstance(result, dict):
        return "Done."
    if result.get("ok") is True:
        succeeded = result.get("succeeded") or []
        return f"Done. {len(succeeded)} step{'s' if len(succeeded) != 1 else ''} finished."
    if result.get("status") == "succeeded":
        return "Done."
    error = result.get("error") or (result.get("failed") or ["something"])[0]
    return f"That did not work: {str(error)[:120]}"


def _breakdown(raw: str) -> List[str]:
    from jarvisx.agentic.intake import breakdown

    return breakdown(raw, 3)


def _match_item(intake: IntakeEngine, target: str):
    """Fuzzy-match spoken text against captured items."""
    if not target:
        open_items = intake.open_items
        return open_items[-1] if open_items else None

    needle = target.lower()
    best = None
    best_score = 0.0
    for item in intake.open_items:
        haystack = f"{item.title} {item.raw}".lower()
        words = [w for w in needle.split() if len(w) > 3]
        if not words:
            continue
        hits = sum(1 for w in words if w in haystack)
        score = hits / len(words)
        if score > best_score:
            best_score = score
            best = item
    return best if best_score >= 0.5 else None
