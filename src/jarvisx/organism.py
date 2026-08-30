"""
Alfred OS — The Living Organism Architecture
===========================================
A clean, elegant, unified biological architecture for the Jarvis/Alfred system:

  🧠 BRAIN  : LLM Reasoning and Autonomous Decision Engine
  👂 EARS   : Audio Stream Capture and Speech-to-Text (STT)
  🗣️ MOUTH  : Neural Speech Synthesis (TTS) and Pygame Playback
  👁️ EYES   : Screen Capture, OCR, and Visual Scene Understanding
  🦾 HANDS  : Tools, Sub-Agents, OS Actions, and MCP Tool Integrations
  ⚡ NERVES : High-Speed Asynchronous Event Bus and Neural Reflexes
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("jarvisx.organism")


# ===========================================================================
# 🧠 1. BRAIN: LLM Reasoning and Cognition
# ===========================================================================
class Brain:
    """The central intelligence: reasons, plans, decides tools, and synthesizes thoughts."""

    def __init__(self, model: str = "gemini-3.6-flash", persona: str = "ALFRED") -> None:
        self.model = model
        self.persona = persona
        self._router = None

    def _get_router(self):
        if self._router is None:
            from jarvisx.llm.llm_router import LLMRouter
            self._router = LLMRouter()
        return self._router


    async def think(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """General reasoning / conversation turn."""
        salutation = "Sir" if self.persona == "ALFRED" else "Boss"
        system = f"You are Alfred, Charan's witty, charismatic, loyal British AI butler. Speak directly to {salutation}."
        full_prompt = f"{system}\n\nContext: {json.dumps(context or {})}\nUser: {prompt}"
        router = self._get_router()
        res = await router.route_request(full_prompt, require_offline=False)
        return res.get("result", {}).get("response", "").strip() or f"At your service, {salutation}."

    async def decide_action(self, prompt: str, available_tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Autonomously decide whether to speak or execute a tool."""
        salutation = "Sir" if self.persona == "ALFRED" else "Boss"
        system = f"""You are the central Brain of Alfred OS — an autonomous agentic system.
CRITICAL MANDATE: NEVER give manual steps, tutorials, or textual instructions. You are an autonomous agent with real hands: ALWAYS execute the appropriate tool directly to do the work for the user!

Available Tools:
{json.dumps(available_tools, indent=2)}

User Request: "{prompt}"

You must respond ONLY in valid JSON matching one of these formats:
1. Tool Call (for actions like sending WhatsApp messages, opening apps, searching, controlling PC, running agents):
{{
  "action": "tool_call",
  "tool": "<tool_name>",
  "args": {{ "<param>": "<value>" }}
}}

2. Conversational Speech (ONLY for pure questions/pleasantries like 'how are you'):
{{
  "action": "speak",
  "response": "<1-2 sentences of charismatic speech to {salutation}>"
}}
"""
        router = self._get_router()
        res = await router.route_request(system, require_offline=False)
        raw = res.get("result", {}).get("response", "").strip()
        
        # Parse decision
        import re
        try:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception:
            pass
        return {"action": "speak", "response": raw or f"Standing by, {salutation}."}



# ===========================================================================
# 👂 2. EARS: Audio Stream and Speech-to-Text (STT)
# ===========================================================================
class Ears:
    """Listens to the user via microphone and transcribes audio to text."""

    def __init__(self, wake_words: Optional[List[str]] = None) -> None:
        self.wake_words = [w.lower() for w in (wake_words or ["alfred", "jarvis", "computer"])]
        self._stt = None

    def _get_stt(self):
        if self._stt is None:
            try:
                from jarvisx.voice.stt_engine import FastSTTEngine
                self._stt = FastSTTEngine()
            except Exception:
                pass
        return self._stt

    def listen_and_transcribe(self, timeout_sec: float = 4.0) -> Optional[str]:
        """Record a voice snippet from microphone and transcribe it."""
        try:
            from jarvisx.voice.acoustic_trigger import AcousticTrigger
            trigger = AcousticTrigger()
            return trigger.record_and_transcribe(duration_sec=timeout_sec)
        except Exception as e:
            logger.debug(f"[Ears] Voice capture fallback: {e}")
            return None

    def has_wake_word(self, text: str) -> bool:
        """Check if any wake word was uttered in the text."""
        lower = text.lower()
        return any(w in lower for w in self.wake_words)


# ===========================================================================
# 🗣️ 3. MOUTH: Neural Speech Synthesis (TTS)
# ===========================================================================
class Mouth:
    """Speaks with charismatic neural voice."""

    def __init__(self, voice_name: str = "british_butler") -> None:
        self.voice_name = voice_name
        self._tts = None

    def _get_tts(self):
        if self._tts is None:
            from jarvisx.voice.sovereign_neural_tts import SovereignNeuralTTS
            self._tts = SovereignNeuralTTS(default_voice_key=self.voice_name)
        return self._tts

    def speak(self, text: str, blocking: bool = False) -> None:
        """Synthesize audio and speak to Charan."""
        if not text or not text.strip():
            return
        tts = self._get_tts()
        tts.speak(text, blocking=blocking)

    async def speak_async(self, text: str) -> None:
        """Asynchronously speak text."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.speak, text, False)



# ===========================================================================
# 👁️ 4. EYES: Screen Capture, OCR, and Vision Perception
# ===========================================================================
class Eyes:
    """Observes the screen, extracts OCR text, and inspects active application windows."""

    def __init__(self) -> None:
        pass

    def capture_screen(self) -> Dict[str, Any]:
        """Capture screenshot and inspect active window metadata."""
        try:
            from jarvisx.tools.builtin_tools import CaptureScreenTool
            tool = CaptureScreenTool()
            res = tool.execute({})
            return res.to_dict()
        except Exception as e:
            logger.warning(f"[Eyes] Screen capture failed: {e}")
            return {"status": "failed", "error": str(e)}

    def read_screen_text(self) -> str:
        """Extract text from the current screen via OCR."""
        try:
            from jarvisx.vision.ocr_engine import OCREngine
            ocr = OCREngine()
            return ocr.extract_screen_text()
        except Exception as e:
            logger.debug(f"[Eyes] OCR extraction fallback: {e}")
            return "Active Desktop Window"


# ===========================================================================
# 🦾 5. HANDS: Tools, Sub-Agents, OS Actions, and MCP Tools
# ===========================================================================
class Hands:
    """Executes actions in the physical/operating system world."""

    def __init__(self) -> None:
        from jarvisx.tools.tool_kernel import ToolRegistry
        from jarvisx.tools.builtin_tools import register_builtin_tools
        from jarvisx.tools.tool_executor import ToolExecutor
        
        self.registry = ToolRegistry.get_instance()
        if not self.registry.list_tools():
            register_builtin_tools(self.registry)
        self.executor = ToolExecutor(registry=self.registry)

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get all JSON schemas of available tools for the Brain."""
        return self.registry.get_schemas_for_llm()

    def act(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool or agent action with full safety verification."""
        args = dict(arguments)
        if tool_name == "open_app" and "application" not in args:
            for alt in ("app", "app_name", "name", "target"):
                if alt in args:
                    args["application"] = args[alt]
                    break
        
        # WhatsApp & Messaging Normalization
        if tool_name in ("send_whatsapp_message", "whatsapp_send", "send_whatsapp", "whatsapp"):
            tool_name = "send_whatsapp_message"
            if "recipient" not in args:
                for alt in ("to", "target", "contact", "person", "name"):
                    if alt in args:
                        args["recipient"] = args[alt]
                        break
            if "message" not in args:
                for alt in ("text", "msg", "content", "body"):
                    if alt in args:
                        args["message"] = args[alt]
                        break
            recip = str(args.get("recipient", "")).lower()
            if "dakshith" in recip and not any(c.isdigit() for c in recip):
                args["recipient"] = "917794979595"

        # Telephony & Calling Normalization

        if tool_name in ("place_carrier_call", "make_phone_call", "call_phone", "call", "phone_call"):
            tool_name = "place_carrier_call"
            if "to" not in args:
                for alt in ("recipient", "target", "contact", "person", "number", "phone"):
                    if alt in args:
                        args["to"] = args[alt]
                        break
            if "speech_text" not in args:
                for alt in ("message", "text", "msg", "prompt", "say"):
                    if alt in args:
                        args["speech_text"] = args[alt]
                        break
            to_val = str(args.get("to", "")).lower()
            if "dakshith" in to_val and not any(c.isdigit() for c in to_val):
                args["to"] = "+917794979595"

        # SMS Normalization
        if tool_name in ("send_sms", "sms_send", "sms", "text_message"):
            tool_name = "send_sms"
            if "to" not in args:
                for alt in ("recipient", "target", "contact", "person", "number", "phone"):
                    if alt in args:
                        args["to"] = args[alt]
                        break
            if "message" not in args:
                for alt in ("text", "msg", "body", "content"):
                    if alt in args:
                        args["message"] = args[alt]
                        break
            to_val = str(args.get("to", "")).lower()
            if "dakshith" in to_val and not any(c.isdigit() for c in to_val):
                args["to"] = "+917794979595"

        # WhatsApp Voice Note Normalization
        if tool_name in ("send_whatsapp_voice_note", "whatsapp_voice_note", "voice_note_whatsapp"):
            tool_name = "send_whatsapp_voice_note"
            if "recipient" not in args:
                for alt in ("to", "target", "contact", "person", "name"):
                    if alt in args:
                        args["recipient"] = args[alt]
                        break
            if "message" not in args:
                for alt in ("text", "msg", "content", "prompt", "speech"):
                    if alt in args:
                        args["message"] = args[alt]
                        break
            recip = str(args.get("recipient", "")).lower()
            if "dakshith" in recip and not any(c.isdigit() for c in recip):
                args["recipient"] = "917794979595"

        # WhatsApp Call Normalization
        if tool_name in ("call_whatsapp", "whatsapp_call", "call_on_whatsapp"):
            tool_name = "call_whatsapp"
            if "recipient" not in args:
                for alt in ("to", "target", "contact", "person", "name"):
                    if alt in args:
                        args["recipient"] = args[alt]
                        break
            recip = str(args.get("recipient", "")).lower()
            if "dakshith" in recip and not any(c.isdigit() for c in recip):
                args["recipient"] = "917794979595"

        # Instagram DM Normalization
        if tool_name in ("send_instagram_dm", "instagram_dm", "dm_instagram", "instagram_message", "instagram"):
            tool_name = "send_instagram_dm"
            if "username" not in args:
                for alt in ("to", "target", "user", "recipient", "person"):
                    if alt in args:
                        args["username"] = args[alt]
                        break
            if "message" not in args:
                for alt in ("text", "msg", "content", "body"):
                    if alt in args:
                        args["message"] = args[alt]
                        break

        # Voice Note Generation Normalization
        if tool_name in ("create_voice_note", "record_audio", "generate_voice_note", "voice_note", "audio_note"):
            tool_name = "create_voice_note"
            if "message" not in args:
                for alt in ("text", "msg", "content", "prompt", "speech"):
                    if alt in args:
                        args["message"] = args[alt]
                        break
            if "recipient" not in args:
                for alt in ("to", "target", "contact"):
                    if alt in args:
                        args["recipient"] = args[alt]
                        break


        res = self.executor.execute(tool_name, args)
        return res.to_dict()



    def open_app(self, app_name: str) -> Dict[str, Any]:
        """Fast helper to open native applications."""
        return self.act("open_app", {"application": app_name})



# ===========================================================================
# ⚡ 6. NERVES: High-Speed Neural Event Bus
# ===========================================================================
@dataclass
class OrganismEvent:
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class Nerves:
    """Asynchronous nervous system connecting Ears, Eyes, Brain, Hands, and Mouth."""

    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[[OrganismEvent], Any]]] = {}

    def on(self, event_type: str, callback: Callable[[OrganismEvent], Any]) -> None:
        """Subscribe an organ or handler to a specific event."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    async def pulse(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Transmit a neural impulse through the organism."""
        event = OrganismEvent(event_type=event_type, data=data or {})
        for cb in self._listeners.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(event)
                else:
                    cb(event)
            except Exception as e:
                logger.error(f"[Nerves] Reflex handler error on '{event_type}': {e}")


# ===========================================================================
# 🌟 THE LIVING ORGANISM: ALFRED
# ===========================================================================
class AlfredOrganism:
    """
    Unified Living Organism coordinating all biological systems:
    Ears (STT) -> Nerves (Bus) -> Brain (LLM) -> Eyes/Hands (Tools/Vision) -> Mouth (TTS)
    """

    def __init__(self, persona: str = "ALFRED") -> None:
        self.persona = persona
        self.brain = Brain(persona=persona)
        self.ears = Ears()
        self.mouth = Mouth()
        self.eyes = Eyes()
        self.hands = Hands()
        self.nerves = Nerves()

        # Connect internal neural reflexes
        self._wire_nervous_system()

    def _wire_nervous_system(self) -> None:
        """Wire automatic reflexes across all biological organs."""
        # When brain wants to speak, activate mouth
        self.nerves.on("speech_requested", lambda e: self.mouth.speak(e.data.get("text", "")))
        # When visual anomaly happens, notify brain
        self.nerves.on("visual_pulse", lambda e: logger.debug(f"[Nerves] Visual pulse received: {e.data}"))

    async def react_turn(self, user_intent: str) -> Dict[str, Any]:
        """
        Execute a complete end-to-end reflex cycle:
        1. Brain evaluates user_intent with Hands tool schemas.
        2. If tool required, Hands act upon the world.
        3. If speech required, Brain synthesizes and Mouth speaks.
        """
        t0 = time.perf_counter()
        tools = self.hands.get_tool_schemas()
        decision = await self.brain.decide_action(user_intent, tools)
        
        action = decision.get("action", "speak")
        tool_name = decision.get("tool")
        tool_args = decision.get("args", {})
        
        # Handle flexible LLM output formats
        if action not in ("speak", "message", "chat") and action in [t["name"] for t in tools]:
            tool_name = action
            tool_args = {k: v for k, v in decision.items() if k != "action"}
            action = "tool_call"

        tool_result = None
        spoken_response = ""

        if action == "tool_call" and tool_name:
            if tool_name == "open_app" and not tool_args.get("application"):
                inferred = user_intent.lower().replace("open", "").replace("launch", "").replace("start", "").strip()
                if inferred:
                    tool_args["application"] = inferred

            # Hands act!
            tool_result = self.hands.act(tool_name, tool_args)
            
            # Brain synthesizes charismatic reaction
            salutation = "Sir" if self.persona == "ALFRED" else "Boss"
            synth_prompt = f"Alfred butler speech: you just executed '{tool_name}' for Charan's goal: '{user_intent}'. Say 1 charismatic sentence to {salutation}."
            spoken_response = await self.brain.think(synth_prompt, context=tool_result)

        else:
            spoken_response = decision.get("response") or await self.brain.think(user_intent)

        # Mouth speaks!
        if spoken_response:
            self.mouth.speak(spoken_response, blocking=False)
            await self.nerves.pulse("speech_uttered", {"text": spoken_response})

        latency = (time.perf_counter() - t0) * 1000.0
        return {
            "status": "success",
            "intent": user_intent,
            "decision": action,
            "tool": tool_name,
            "tool_result": tool_result,
            "spoken": spoken_response,
            "latency_ms": round(latency, 2)
        }


# Singleton accessor
_organism_instance: Optional[AlfredOrganism] = None

def get_organism() -> AlfredOrganism:
    """Get the global unified Alfred Organism instance."""
    global _organism_instance
    if _organism_instance is None:
        _organism_instance = AlfredOrganism()
    return _organism_instance
