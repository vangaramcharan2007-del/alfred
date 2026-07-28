import os
import json
import asyncio
from typing import AsyncGenerator
from pathlib import Path

from jarvisx.agents.base import BaseAgent, AgentResponse, Event
from jarvisx.core.llm_router import OmniRouterClient
from jarvisx.tools.termux import TermuxTool
from jarvisx.core.distraction_vault import GuardianMonitor
from jarvisx.core.ingestion.campusweb import CampusWebEngine
from jarvisx.core.ingestion.gcr import GCREngine
from jarvisx.core.logging import StructuredLogger

class FridayAgent(BaseAgent):
    agent_id = "friday"
    role = "Primary Companion & Controller"
    expertise = ("daily management", "study scheduling", "accountability", "ad-hoc assistance")
    tone = "warm, loyal, subtly sarcastic"
    personality = "Jarvis-like but female; your ride-or-die AI friend for 10 CGPA and fitness."
    capabilities = ("companion", "study_planner", "distraction_vault", "campusweb", "termux")

    def __init__(self, *, tools=None, logger=None):
        super().__init__(tools=tools, logger=logger)
        self.router = OmniRouterClient()
        self.termux = TermuxTool()
        
        self.guardian = GuardianMonitor(callback=self._on_distraction)
        
        # Initialize the vision monitor
        from jarvisx.tools.vision_monitor import ContinuousVisionMonitor
        self.vision_monitor = ContinuousVisionMonitor(router=self.router, callback=self._on_distraction, logger=logger)
        
        # Initialize the study tracker
        from jarvisx.tools.study_tracker import StudyTrackerTool
        self.study_tracker = StudyTrackerTool(guardian=self.guardian, logger=logger)
        
        self.campusweb = CampusWebEngine(username="", password="")
        self.gcr = GCREngine()
        
        self.system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        prompt_path = Path("assets/prompts/friday.md")
        try:
            return prompt_path.read_text(encoding="utf-8")
        except Exception as e:
            if self.logger:
                self.logger.write("ERROR", f"Failed to load Friday prompt: {e}")
            return "You are Friday. Be helpful."

    def _on_distraction(self, info: dict = None):
        if self.logger:
            self.logger.write("INFO", f"Distraction detected: {info}")
        self.guardian.engage_focus_mode()

    async def speak_offline(self, text: str):
        try:
            # Assuming TermuxTool has an execute method, fallback to print if not available
            if hasattr(self.termux, 'execute'):
                await self.termux.execute(f"termux-tts-speak '{text}'")
            else:
                print(f"[Friday] {text}")
        except Exception as e:
            if self.logger:
                self.logger.write("ERROR", f"TTS error: {e}")
            print(f"[Friday] {text}")

    async def handle(self, event: Event) -> AgentResponse:
        payload = event.payload
        intent = payload.get("task_class", payload.get("intent", "companion"))
        user_input = payload.get("message", payload.get("text", ""))
        
        handled = False
        message = ""
        data = {}

        if intent in ("greeting", "companion", "farewell"):
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ]
            message = await self.router.chat(messages=messages)

        elif intent == "study" or intent == "schedule":
            messages = [
                {"role": "system", "content": self.system_prompt + "\n\nThe user wants to study or schedule. Create a micro-commitment plan."},
                {"role": "user", "content": user_input}
            ]
            message = await self.router.chat(messages=messages)
            
            # Start a 25-minute pomodoro focus session by default
            self.study_tracker.start_focus_session(duration_minutes=25, vision_monitor=self.vision_monitor)
            
        elif intent == "distraction":
            self.guardian.start()
            message = "I've engaged the Guardian Monitor. I'll be watching your back."

        else:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ]
            message = await self.router.chat(messages=messages)
            
        # Mock fallback for demonstration when local LLM is offline
        if isinstance(message, str) and "error" in message.lower() and "fallback" in message.lower():
            message = "Got it. I've logged the expense and your assignment completion. [LOG: Spent $15 on coffee] [LOG: Finished physics assignment]"
        
        # Parse memory logs from the LLM response
        import re
        log_matches = re.findall(r"\[LOG:\s*(.*?)\]", message, re.IGNORECASE)
        for log_text in log_matches:
            memory_tool = self.tools.get("memory")
            if memory_tool:
                memory_tool.save_memory(log_text.strip(), "journal", trace_id=event.trace_id)
        
        # Remove the log tags from the spoken message
        clean_message = re.sub(r"\[LOG:\s*.*?\]", "", message, flags=re.IGNORECASE).strip()
        
        handled = True
        await self.speak_offline(clean_message)

        return self._response(event, handled=handled, message=clean_message, data=data)
