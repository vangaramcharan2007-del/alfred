"""Alfred Commander — maps spoken commands to existing Jarvis X subsystems.

This is NOT a new orchestrator.  It is a thin dispatch layer that translates
natural-language voice commands into calls to the systems that already exist.
"""
import time
import datetime
from typing import Optional, Tuple

from jarvisx.core.presence_manager import PresenceManager
from jarvisx.core.diagnostics_console import DiagnosticsConsole
from jarvisx.core.objective_store import ObjectiveStore
from jarvisx.core.mission_continuity import MissionContinuityManager
from jarvisx.core.alfred_summarizer import AlfredSummarizer
from jarvisx.core.notification_policy import NotificationPolicy, NotificationLevel


class AlfredCommander:
    """Thin dispatch layer — voice command -> existing subsystem."""

    def __init__(
        self,
        presence: PresenceManager,
        diagnostics: DiagnosticsConsole,
        objective_store: ObjectiveStore,
        continuity: MissionContinuityManager,
        notification_policy: NotificationPolicy,
    ):
        self.presence = presence
        self.diagnostics = diagnostics
        self.store = objective_store
        self.continuity = continuity
        self.policy = notification_policy
        self.summarizer = AlfredSummarizer()

    def handle(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Process spoken text.

        Returns (spoken_reply, optional_display_text).
        spoken_reply is what Alfred says aloud.
        display_text is optional extra output for the terminal (e.g. diagnostics).
        """
        lower = text.lower().strip()

        # --- Greeting ---
        if any(w in lower for w in ["hello", "hi alfred", "hey alfred", "good evening", "good morning"]):
            hour = datetime.datetime.now().hour
            if hour < 12:
                greeting = "Good morning."
            elif hour < 17:
                greeting = "Good afternoon."
            else:
                greeting = "Good evening."
            return f"{greeting} How may I assist you?", None

        # --- Time ---
        if "what time" in lower or "tell me the time" in lower:
            now = datetime.datetime.now().strftime("%I:%M %p")
            return f"It is currently {now}.", None

        # --- Diagnostics ---
        if "diagnostic" in lower or "show diagnostic" in lower:
            display = self.diagnostics.render()
            return "Here are the current diagnostics.", display

        # --- What are you doing ---
        if "what are you doing" in lower or "what's going on" in lower or "status" in lower:
            summary = self.presence.get_active_summary()
            agents = self.presence.get_running_agent_names()
            agent_note = self.summarizer.summarize_agents_hidden(agents)
            return f"{summary} {agent_note}", None

        # --- Continue my work / resume ---
        if "continue" in lower or "resume" in lower:
            interrupted = self.continuity.detect_interrupted_work()
            if interrupted:
                count = len(interrupted)
                titles = ", ".join(o.get("title", "unknown") for o in interrupted[:3])
                return (
                    f"I found {count} interrupted objective{'s' if count > 1 else ''}: {titles}. "
                    "Resuming execution now.",
                    None,
                )
            else:
                return "There is no interrupted work. Standing by.", None

        # --- Stop / Exit ---
        if lower in ("stop", "exit", "quit", "goodbye", "shut down", "shutdown"):
            return "Understood. Shutting down. Good night.", "__EXIT__"

        # --- Fallback ---
        return "I'm here. Could you clarify what you'd like me to do?", None
