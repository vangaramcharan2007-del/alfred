from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import threading
import asyncio
from typing import Any

from jarvisx.agents.base import BaseAgent, AgentResponse
from jarvisx.core.events import Event
from jarvisx.core.llm_router import OmniRouterClient
from jarvisx.core.continuous_voice import ContinuousVoiceEngine
from jarvisx.core.distraction_vault import GuardianMonitor
from jarvisx.tools.termux import TermuxTool

def _message(event: Event) -> str:
    return str(event.payload.get("message", "")).strip()

def speak_offline(text: str, voice_gender="female"):
    if os.environ.get("JARVIS_SPEAK_OFFLINE", "").lower() not in {"1", "true", "yes"}:
        return
    if importlib.util.find_spec("pyttsx3") is None:
        return

    preferred_voice = "Zira" if voice_gender == "female" else "David"
    script = (
        "import sys, pyttsx3\n"
        "engine = pyttsx3.init()\n"
        "voices = engine.getProperty('voices')\n"
        f"preferred_voice = {preferred_voice!r}\n"
        "for v in voices:\n"
        "    if preferred_voice in v.name or preferred_voice.lower() in v.name.lower():\n"
        "        engine.setProperty('voice', v.id)\n"
        "        break\n"
        "engine.setProperty('rate', 170)\n"
        "engine.say(sys.stdin.read())\n"
        "engine.runAndWait()\n"
    )

    def run() -> None:
        subprocess.run(
            [sys.executable, "-c", script],
            input=text.encode("utf-8"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

    threading.Thread(target=run, daemon=True, name="JarvisFridaySpeech").start()

class FridayAgent(BaseAgent):
    agent_id = "friday"
    role = "ADHD Cognitive Companion and Executive Enforcer"
    expertise = ("10 CGPA", "ADHD management", "distraction blocking", "termux handoff")
    tone = "friendly, loyal, and proactive"
    personality = "empathetic AI friend"
    capabilities = ("file.read", "file.write", "file.edit", "computer.run_command")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.system_prompt = self._load_system_prompt()
        self.router = OmniRouterClient()
        self.voice_engine = ContinuousVoiceEngine(self._on_voice_input)
        self.voice_engine.start()
        
        # Phase 2: Guardian & Mobile Handoff
        self.guardian = GuardianMonitor(self._on_distraction_killed)
        self.guardian.start()
        self.termux = TermuxTool()
        
    def _on_distraction_killed(self, keyword: str):
        # When the Guardian kills a distraction, Friday speaks up
        msg = f"Focus mode is active. I have intercepted and closed your attempt to access {keyword}. Let's pivot back to the 10 CGPA goal."
        speak_offline(msg, "female")
        
        # Also ping the phone natively
        self.termux.notify("Distraction Intercepted", f"I've closed {keyword} on your PC.")
        self.termux.vibrate(500)

    def _on_voice_input(self, text: str):
        # This is triggered when the continuous mic detects the wake word
        # We run the handle logic asynchronously
        import asyncio
        event = Event(type="voice_input", payload={"message": text})
        asyncio.run(self.handle(event))

    def _load_system_prompt(self) -> str:
        prompt_path = Path("assets/prompts/friday.md")
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return "You are Friday, the ultimate AI Cognitive Companion."

    async def handle(self, event: Event) -> AgentResponse:
        from jarvisx.core.state import get_agent_state, update_agent_state
        text = _message(event).lower()
        
        # Generate response using OmniRoute LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text}
        ]
        
        try:
            response = await self.router.chat(messages, model="omniroute-apex")
        except Exception as e:
            response = "I'm having trouble connecting to the OmniRoute gateway right now, sir. " + str(e)

        speak_offline(response, "female")
        return AgentResponse(agent_id=self.agent_id, content=response, route_to=None)
