"""One agent that talks, listens, watches and does — at the same time.

Until this, the four capabilities were three separate CLI commands
(``talk``, ``watch``, ``next``) that each built their own ``IntakeEngine``, so
what you *said* and what you *copied* landed in two different lists, and the
watcher had no idea what task you had just committed to.

:class:`AlfredRuntime` composes them over one shared state:

    IntakeEngine   one list, fed by speech, clipboard and both commands
    VoiceAgentLoop foreground: listen -> decide -> act -> speak
    ContextWatcher background thread: notice drift, fragmentation, stray notes
    Orchestrator   optional, and only on an explicit "build/write/fix" verb

The integration that makes it more than four parts in a trench coat: when the
voice loop picks a task, the runtime calls
``AttentionLedger.set_intended_task()``. That is what lets drift detection
work at all — the watcher cannot tell you that you wandered off a task it never
knew you had.

Every layer degrades independently. No microphone, no speaker, no desktop, no
model key: you still get a working typed agent with capture and nudges.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from jarvisx.agentic.clarifier import ClarificationGate
from jarvisx.agentic.intake import Energy, IntakeEngine
from jarvisx.agentic.persona import Persona, PersonaOutput, get_persona
from jarvisx.agentic.voice_loop import (
    ConsoleInput,
    ConsoleOutput,
    Intent,
    InterruptibleOutput,
    SpeechInput,
    SpeechOutput,
    TTSOutput,
    VoiceAgentLoop,
    WakeWordInput,
    WhisperMicInput,
)
from jarvisx.agentic.watch import (
    ActiveWindowSource,
    AttentionLedger,
    ClipboardSource,
    ContextWatcher,
    Nudge,
    ScriptedSource,
)

logger = logging.getLogger("jarvisx.agentic.runtime")


@dataclass
class RuntimeConfig:
    """Everything the runtime needs, in one place."""

    energy: Energy = Energy.MEDIUM
    wake_word: str = "alfred"
    speak_nudges: bool = True
    enable_agent: bool = False
    watch: bool = True
    watch_interval: float = 15.0
    switch_window_minutes: int = 5
    switch_threshold: int = 6
    off_task_grace_minutes: int = 5
    break_after_minutes: int = 50
    auto_capture: bool = True
    force_text: bool = False
    demo_watch: bool = False
    state_path: Optional[str] = None
    trace_root: Optional[str] = None
    max_turns: int = 200
    # "plain" | "stark" | "friday". Cosmetic only: the persona re-voices what
    # the intake engine already decided, it never changes the decision.
    persona: str = "plain"
    # Give the agent real reach: open apps, run gated shell commands. Off by
    # default, because an assistant that can touch your machine should only do
    # so when you asked for that.
    enable_physical: bool = False
    physical_dry_run: bool = False
    # Stop and ask before an irreversible or externally visible action whose
    # target was never actually named. On by default here because the agent is
    # talking to someone who can answer, and _speak_run() speaks the question.
    # Turn it off only for an unattended run, where a question nobody can answer
    # is not a pause but a stall.
    ask_when_ambiguous: bool = True
    workspace: Optional[str] = None


@dataclass
class RuntimeStatus:
    """What actually came up. Reported honestly, never optimistically."""

    voice_input: str = "none"
    voice_output: str = "none"
    watching: bool = False
    watch_source: str = "none"
    agent_enabled: bool = False
    backend: str = "none"
    notes: List[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [
            f"  ears      {self.voice_input}",
            f"  mouth     {self.voice_output}",
            f"  eyes      {self.watch_source if self.watching else 'off'}",
            f"  hands     {self.backend if self.agent_enabled else 'off (say build/write/fix)'}",
        ]
        for note in self.notes:
            lines.append(f"  note      {note}")
        return "\n".join(lines)


class AlfredRuntime:
    """Composes the four capabilities over one shared state."""

    def __init__(
        self,
        config: Optional[RuntimeConfig] = None,
        intake: Optional[IntakeEngine] = None,
        stt: Optional[SpeechInput] = None,
        tts: Optional[SpeechOutput] = None,
        runner: Optional[Callable[[str], Dict[str, Any]]] = None,
        ledger: Optional[AttentionLedger] = None,
        on_event: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        self.config = config or RuntimeConfig()
        self.intake = intake or self._load_intake()
        self.on_event = on_event

        self.status = RuntimeStatus()
        self._stop = threading.Event()
        self._watch_thread: Optional[threading.Thread] = None
        self._nudge_lock = threading.Lock()
        self.spoken_nudges: List[Nudge] = []

        # -- ears and mouth ------------------------------------------------- #
        if stt is not None:
            self.stt = stt
            self.status.voice_input = getattr(stt, "name", "injected")
        elif self.config.force_text:
            self.stt = ConsoleInput()
            self.status.voice_input = "keyboard"
        else:
            # Wake word first: that is what makes this hands-free. It falls
            # back to push-to-talk whisper, then to the keyboard, and the
            # status line always says which one actually won.
            mic = WhisperMicInput(wake_word=self.config.wake_word)
            wake = WakeWordInput(
                wake_word=self.config.wake_word,
                fallback=mic,
                should_stop=self._stop.is_set,
            )
            self.stt = wake
            if wake.available:
                self.status.voice_input = f"microphone (wake word: {self.config.wake_word})"
            elif mic.available:
                self.status.voice_input = "microphone (whisper)"
                self.status.notes.append("wake word engine unavailable — press enter, then speak")
            else:
                self.status.voice_input = "keyboard (no microphone)"
                self.status.notes.append("no microphone — type instead of speaking")

        # Set before the branch below so every construction path has the
        # attribute; only the TTS path actually gets a duplex controller.
        self.interruptible: Optional[InterruptibleOutput] = None

        if tts is not None:
            self.tts = tts
            self.status.voice_output = getattr(tts, "name", "injected")
        elif self.config.force_text:
            self.tts = ConsoleOutput()
            self.status.voice_output = "text"
        else:
            speaker = TTSOutput()
            # Make speech interruptible. This is what lets you talk over the
            # assistant instead of waiting for it to finish its paragraph --
            # the difference between a scripted reader and a conversation.
            # InterruptibleOutput degrades to a pass-through if the duplex
            # controller cannot be built, so this cannot cost us the message.
            self.interruptible = InterruptibleOutput(fallback=speaker)
            self.tts = self.interruptible
            if speaker.available:
                self.status.voice_output = "speakers (tts)"
            else:
                self.status.voice_output = "text (no TTS engine)"
                self.status.notes.append("no TTS engine — replies are printed")
            if self.interruptible.available:
                self.status.voice_output += ", interruptible"
            else:
                self.status.notes.append("full-duplex controller unavailable — cannot be interrupted mid-sentence")

        # -- voice ---------------------------------------------------------- #
        # Wrapped after the sink is chosen, so the persona sits on top of
        # whichever output actually came up, including an injected one.
        self.persona = get_persona(self.config.persona)
        if self.persona.name != "plain":
            self.tts = PersonaOutput(self.tts, self.persona)
            self.status.voice_output = f"{self.persona.name} -> {self.status.voice_output}"

        # -- eyes ----------------------------------------------------------- #
        self.ledger = ledger or AttentionLedger(
            switch_window_seconds=self.config.switch_window_minutes * 60,
            fragmentation_threshold=self.config.switch_threshold,
            off_task_seconds=self.config.off_task_grace_minutes * 60,
            break_after_seconds=self.config.break_after_minutes * 60,
        )
        self.watcher = ContextWatcher(
            ledger=self.ledger,
            source=self._make_watch_source(),
            clipboard=None if self.config.force_text else ClipboardSource(),
            intake=self.intake,          # shared, not a second list
            on_nudge=self._on_nudge,
            auto_capture=self.config.auto_capture,
        )
        source = self.watcher.source
        self.status.watching = bool(self.config.watch and source and source.available)
        self.status.watch_source = (
            getattr(source, "name", "sensor") if source else "none"
        )

        # -- hands ---------------------------------------------------------- #
        self.runner = runner or (self._make_runner() if self.config.enable_agent else None)
        self.status.agent_enabled = self.runner is not None
        self.status.backend = getattr(
            getattr(self, "_backend", None), "name", "not configured"
        )

        # The voice loop gets its own registry, separate from whatever the
        # orchestrator builds. Speech needs to open Spotify *now*; it should not
        # have to spin up a sandbox, a planner and a model to do it.
        self.physical = None
        if self.config.enable_physical:
            from jarvisx.agentic.actions import build_action_tools

            self.physical = build_action_tools(
                confirm=self._confirm,
                workspace=self.config.workspace,
                dry_run=self.config.physical_dry_run,
            )
            self.status.notes.append(
                "you can say 'open spotify' and it will actually open"
                + (" (dry run)" if self.config.physical_dry_run else "")
            )

        # -- the voice loop, sharing our state ------------------------------ #
        self.voice = VoiceAgentLoop(
            stt=self.stt,
            tts=self.tts,
            intake=self.intake,
            runner=self.runner,
            physical=self.physical,
            wake_word=self.config.wake_word,
            energy=self.config.energy,
        )
        # Let the loop tell us when it commits to a task, so the watcher can
        # notice drift away from it. Without this hook the watcher would be
        # judging you against a task it never knew about.
        self._original_what_next = self.voice._on_what_next
        self.voice._on_what_next = self._what_next_with_intent  # type: ignore[method-assign]
        self._original_brain_dump = self.voice._on_brain_dump
        self.voice._on_brain_dump = self._brain_dump_with_intent  # type: ignore[method-assign]

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    def start(self) -> None:
        """Start the background watcher. Idempotent."""
        if not self.status.watching or self._watch_thread is not None:
            return
        self._stop.clear()
        self._watch_thread = threading.Thread(
            target=self._watch_loop, name="alfred-watch", daemon=True
        )
        self._watch_thread.start()
        logger.info("watcher started (interval=%.1fs)", self.config.watch_interval)

    def stop(self) -> None:
        """Stop the watcher and persist shared state."""
        self._stop.set()
        if self._watch_thread is not None:
            self._watch_thread.join(timeout=2.0)
            self._watch_thread = None
        self._save_intake()

    def serve(self) -> List[Any]:
        """Run the whole thing: watcher in the background, voice in front."""
        self.start()
        print("\nAlfred is up.\n")
        print(self.status.render())
        print()
        try:
            return self.voice.run(max_turns=self.config.max_turns)
        except KeyboardInterrupt:
            print("\nstopping")
            return self.voice.turns
        finally:
            self.stop()

    # ------------------------------------------------------------------ #
    # Integration hooks
    # ------------------------------------------------------------------ #

    def _what_next_with_intent(self, body: str, turn) -> None:
        """Pick a task, then tell the watcher that this is the task."""
        self._original_what_next(body, turn)
        item = (turn.payload or {}).get("item")
        if item:
            self.commit_to(item["title"])

    def _brain_dump_with_intent(self, body: str, turn) -> None:
        self._original_brain_dump(body, turn)
        chosen = (turn.payload or {}).get("do_this_next")
        if chosen:
            self.commit_to(chosen["title"])

    def commit_to(self, task: str) -> None:
        """Declare the current task so drift detection has something to compare against."""
        self.ledger.set_intended_task(task)
        self._emit("task_committed", {"task": task})

    def _on_nudge(self, nudge: Nudge) -> None:
        """Speak nudges on the same channel as replies, serialised."""
        self._emit("nudge", {"kind": nudge.kind.value, "message": nudge.message})
        if not self.config.speak_nudges:
            return
        with self._nudge_lock:
            self.spoken_nudges.append(nudge)
            try:
                self.tts.say(nudge.message)
            except Exception as exc:  # noqa: BLE001 - a nudge must never kill the watcher
                logger.warning("could not speak nudge: %s", exc)

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #

    def _voiced_roles(self):
        """The default roles, talking in the active persona's voice.

        Same jobs, same budgets, same tool allowances — only the voice changes.
        Without this the persona decorates decisions it did not make, and the
        moment a real model starts doing the work it reverts to the generic
        engineering voice, which is exactly when the character matters most.
        """
        from jarvisx.agentic.roles import RoleRegistry

        registry = RoleRegistry()
        voice = self.persona.voice_prompt
        if not voice:
            return registry
        for name in registry.names():
            role = registry.get(name)
            registry.register(role.with_voice(voice))
        return registry

    def _confirm(self, command: str) -> bool:
        """Ask the human before anything hard to undo.

        Defaults to refusing when there is no interactive input, so an
        unattended or scripted run can never execute a CONFIRM-level command.
        Guessing "yes" here is the single worst thing this agent could do.
        """
        if self.config.physical_dry_run:
            return True
        try:
            answer = input(
                f"\n  {self.persona.address and self.persona.address + ', this'} needs your say-so:\n"
                f"    {command}\n  run it? [y/N] "
            )
        except (EOFError, KeyboardInterrupt):
            return False
        return answer.strip().lower() in ("y", "yes")

    def _watch_loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.watcher.tick()
            except Exception as exc:  # noqa: BLE001 - watcher must never die
                logger.warning("watch tick failed: %s", exc)
            self._stop.wait(self.config.watch_interval)

    def _make_watch_source(self):
        if not self.config.watch:
            return None
        if self.config.demo_watch:
            script = []
            for index in range(60):
                app = "code" if index % 2 == 0 else "chrome"
                from jarvisx.agentic.watch import Observation

                script.append(
                    Observation(
                        app=app,
                        title="YouTube - lofi beats" if app == "chrome" else "assignment.py",
                        mode="CODING" if app == "code" else "WEB_RESEARCH",
                        timestamp=float(index * 60),
                    )
                )
            return ScriptedSource(script)
        return ActiveWindowSource()

    def _make_runner(self) -> Optional[Callable[[str], Dict[str, Any]]]:
        """Build the bridge to the orchestrator, or explain why it is missing."""
        try:
            from jarvisx.agentic.backends import AutoBackend
            from jarvisx.agentic.scheduler import Orchestrator
            from jarvisx.agentic.types import Budget

            backend = AutoBackend()
            self._backend = backend
            if backend.name == "heuristic":
                self.status.notes.append(
                    "no model key — agent work will write a placeholder, not real code"
                )

            # Physical reach is opt-in. When enabled the model gets the real
            # desktop tools, but still through the harness: policy gate,
            # CONFIRM permission, trace and budget all still apply.
            tool_factory = None
            if self.config.enable_physical:
                from jarvisx.agentic.actions import build_action_tools
                from jarvisx.agentic.builtin_tools import build_default_tools

                def tool_factory(sandbox, _confirm=self._confirm):  # noqa: ANN001
                    reg = build_default_tools(sandbox)
                    return build_action_tools(
                        registry=reg,
                        confirm=_confirm,
                        workspace=str(sandbox.workspace),
                        dry_run=self.config.physical_dry_run,
                    )

                self.status.notes.append(
                    "physical reach ON — the agent can open apps and run gated commands"
                    + (" (dry run)" if self.config.physical_dry_run else "")
                )

            def run_goal(goal: str) -> Dict[str, Any]:
                with Orchestrator(
                    backend=backend,
                    roles=self._voiced_roles(),
                    default_budget=Budget(max_steps=10, max_tool_calls=24, max_seconds=300),
                    trace_root=self.config.trace_root,
                    tool_factory=tool_factory,
                    clarifier=ClarificationGate() if self.config.ask_when_ambiguous else None,
                ) as orch:
                    return orch.run(goal).to_dict()

            return run_goal
        except Exception as exc:  # noqa: BLE001 - hands are optional
            logger.warning("agent backend unavailable: %s", exc)
            self.status.notes.append(f"agent disabled: {exc}")
            return None

    def _load_intake(self) -> IntakeEngine:
        intake = IntakeEngine()
        path = self.config.state_path
        if not path:
            return intake
        from pathlib import Path

        target = Path(path)
        if target.exists():
            try:
                import json

                intake.load(json.loads(target.read_text(encoding="utf-8")))
                logger.info("restored %d items from %s", len(intake.items), target)
            except Exception as exc:  # noqa: BLE001 - start fresh rather than crash
                logger.warning("could not load state %s: %s", target, exc)
        return intake

    def _save_intake(self) -> None:
        path = self.config.state_path
        if not path:
            return
        from pathlib import Path
        import json

        try:
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(self.intake.to_dict(), indent=2), encoding="utf-8")
        except OSError as exc:  # pragma: no cover - disk/permission issues
            logger.warning("could not save state: %s", exc)

    def _emit(self, kind: str, payload: Dict[str, Any]) -> None:
        if self.on_event:
            try:
                self.on_event(kind, payload)
            except Exception as exc:  # noqa: BLE001
                logger.warning("event listener failed: %s", exc)

    # ------------------------------------------------------------------ #
    # Introspection
    # ------------------------------------------------------------------ #

    def summary(self) -> Dict[str, Any]:
        return {
            "status": self.status.render(),
            "intake_items": len(self.intake.items),
            "open_items": len(self.intake.open_items),
            "watcher": self.watcher.summary() if self.status.watching else None,
            "turns": len(self.voice.turns),
            "nudges_spoken": len(self.spoken_nudges),
        }
