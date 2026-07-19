"""Alfred Voice Runtime — the single visible entry point for Jarvis X.

Initialises STT, TTS, and every existing subsystem, then runs a continuous
conversation loop.  Internal agents execute silently in HEADLESS mode.
The user interacts exclusively through voice with Alfred.
"""
import os
import sys
import time
import logging
import subprocess
from typing import List

# ── path setup ──────────────────────────────────────────────────────────
sys.path.insert(0, os.path.abspath("src"))

# ── subsystem imports ───────────────────────────────────────────────────
from jarvisx.core.voice.tts_engine import TTSEngine
from jarvisx.core.voice.stt_listener import STTListener
from jarvisx.core.voice.voice_bus import VoiceBus
from jarvisx.core.voice.alfred_commander import AlfredCommander
from jarvisx.core.presence_manager import PresenceManager, HealthStatus
from jarvisx.core.runtime_visibility import RuntimeVisibility, VisibilityMode
from jarvisx.core.diagnostics_console import DiagnosticsConsole
from jarvisx.core.objective_store import ObjectiveStore
from jarvisx.core.mission_continuity import MissionContinuityManager
from jarvisx.core.notification_policy import NotificationPolicy, NotificationLevel
from jarvisx.core.alfred_summarizer import AlfredSummarizer
from jarvisx.core.agents.agent_coordinator import AgentCoordinator
from jarvisx.core.whatsapp.manager import WhatsAppAutomationManager

# Silence internal module logging — only Alfred speaks
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("alfred.runtime")
logger.setLevel(logging.INFO)


class VoiceRuntime:
    """Alfred's main runtime — owns the conversation loop and all subsystem wiring."""

    def __init__(self):
        # ── visibility ──────────────────────────────────────────────────
        RuntimeVisibility.set_mode(VisibilityMode.HEADLESS)

        # ── core singletons ─────────────────────────────────────────────
        self.presence = PresenceManager.get_instance()
        self.store = ObjectiveStore()
        self.continuity = MissionContinuityManager(self.store, presence_manager=self.presence)
        self.policy = NotificationPolicy(minimum_level=NotificationLevel.INFORMATIONAL)
        self.diagnostics = DiagnosticsConsole(self.presence)

        # ── voice ───────────────────────────────────────────────────────
        self.tts = TTSEngine()
        self.stt = STTListener()
        self.bus = VoiceBus(tts_engine=self.tts)

        # ── command dispatch ────────────────────────────────────────────
        self.whatsapp_manager = WhatsAppAutomationManager(tts_engine=self.tts)
        
        self.commander = AlfredCommander(
            presence=self.presence,
            diagnostics=self.diagnostics,
            objective_store=self.store,
            continuity=self.continuity,
            notification_policy=self.policy,
            whatsapp_manager=self.whatsapp_manager,
        )

        # ── hidden background agents ────────────────────────────────────
        self._bg_procs: list = []

    # ── lifecycle ───────────────────────────────────────────────────────

    def startup(self):
        """Boot all hidden subsystems and greet the user."""

        # Register background agents silently
        agent_names = ["planner_agent", "execution_agent", "memory_agent", "initiative_agent"]
        for name in agent_names:
            self.presence.register_agent(name)

        # Launch hidden processes (HEADLESS — no console windows)
        self._launch_hidden_agents(agent_names)

        # Register background jobs
        self.presence.register_background_job("monitoring resources")
        self.presence.register_background_job("updating memory index")

        # Startup voice event
        self.bus.publish("startup", "Good evening. Alfred is online.")

        # Check for interrupted work (Mission Continuity)
        interrupted = self.continuity.detect_interrupted_work()
        if interrupted:
            count = len(interrupted)
            self.bus.publish(
                "recovery_started",
                f"I discovered {count} piece{'s' if count > 1 else ''} of unfinished work "
                "from a previous session. Say 'continue my work' when you are ready.",
            )

    def run_conversation_loop(self):
        """Main loop — listen, dispatch, speak, repeat."""
        print("\n[Alfred is listening.  Speak naturally.  Say 'exit' to quit.]\n")

        while True:
            text = self.stt.listen(timeout=12.0)

            if text is None:
                continue  # silence or unrecognised — keep listening

            print(f"  You: {text}")

            reply, extra = self.commander.handle(text)

            if reply:
                print(f"  Alfred: {reply}")
                self.tts.speak(reply)

            if extra == "__EXIT__":
                break

            if extra and extra != "__EXIT__":
                print(extra)

    def shutdown(self):
        """Tear down background processes."""
        if self.whatsapp_manager:
            self.whatsapp_manager.stop()
            
        for name, proc in self._bg_procs:
            try:
                proc.terminate()
            except Exception:
                pass
        for name in list(self.presence._agents.keys()):
            self.presence.unregister_agent(name)

    # ── internal helpers ────────────────────────────────────────────────

    def _launch_hidden_agents(self, agent_names: List[str]):
        """Spawn agent processes with no visible windows."""
        env = os.environ.copy()
        env["PYTHONPATH"] = "src"
        flags = AgentCoordinator.get_process_creation_flags()

        for name in agent_names:
            cmd = [sys.executable, "visual_agent.py", name, "execution_tool", "0.5"]
            try:
                proc = subprocess.Popen(
                    cmd, env=env, creationflags=flags,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                self._bg_procs.append((name, proc))
            except Exception:
                pass  # agent script may not exist — runtime still works


def main():
    runtime = VoiceRuntime()
    try:
        runtime.startup()
        runtime.run_conversation_loop()
    except KeyboardInterrupt:
        print("\n[Interrupted]")
    finally:
        runtime.shutdown()


if __name__ == "__main__":
    main()
