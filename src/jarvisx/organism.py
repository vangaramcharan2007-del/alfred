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

    async def decide_action(
        self,
        prompt: str,
        available_tools: List[Dict[str, Any]],
        observations: Optional[List[Dict[str, Any]]] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Autonomously decide whether to speak or execute a tool.
        
        Pillars implemented:
          P1: available_tools is already filtered by SmartToolSelector (3-8 tools, not 30).
          P5: Response includes both tool decision AND speech in one JSON (no second LLM call).
          P2: observations[] feeds prior tool results back for multi-step ReAct reasoning.
          Memory: Multi-turn history buffer + Second Brain retrieval.
        """
        salutation = "Sir" if self.persona == "ALFRED" else "Boss"
        
        # Build observation history for ReAct loop
        obs_block = ""
        if observations:
            obs_lines = []
            for obs in observations:
                status = "✓" if obs.get("result", {}).get("status") == "success" else "✗ FAILED"
                obs_lines.append(
                    f"  Step {obs['step']}: {obs['tool']}({json.dumps(obs.get('args', {}))}) → {status}"
                )
                if obs.get("error"):
                    obs_lines.append(f"    Error: {obs['error']}")
            obs_block = "\n\nPrior Actions Already Completed:\n" + "\n".join(obs_lines) + "\n"

        # Build recent conversation history block
        hist_block = ""
        if history:
            h_lines = []
            for h in history[-6:]:
                role = "User" if h.get("role") == "user" else "Alfred"
                text = h.get("text", "")
                if len(text) > 300:
                    text = text[:300] + "..."
                h_lines.append(f"  {role}: {text}")
            if h_lines:
                hist_block = "\nRecent Conversation History:\n" + "\n".join(h_lines) + "\n"

        # Query Second Brain if prompt relates to memory, past context, decisions, or DSA/learning notes
        memory_context = ""
        p_lower = prompt.lower()
        if any(k in p_lower for k in ("memory", "remember", "previous", "failed", "last time", "second brain", "assignment", "decision", "dsa", "course", "why did we")):
            try:
                from jarvisx.memory.second_brain import SecondBrain
                sb = SecondBrain()
                sb_res = await sb.answer_question(prompt)
                if sb_res and sb_res.get("answer"):
                    memory_context = f"\n[Second Brain Knowledge Recall]: {sb_res.get('answer')}\n"
            except Exception:
                pass

        system = f"""You are Alfred OS Brain — an autonomous, highly capable agentic AI butler and engineering partner for Charan.

CAPABILITIES:
- OS & Apps: You can open applications (e.g. VS Code, Chrome, Terminal), manage files, control desktop, and send messages via Available Tools.
- Knowledge & Coding: You are an elite software engineer and computer science tutor. For coding requests, DSA algorithms (linked lists, trees, graphs, dynamic programming), course planning, explanations, or academic tutoring, provide complete, production-ready, beautiful markdown explanations with clean Python code directly.
- Multi-Turn Continuity: Maintain continuity with the conversation history. If the user refers to previous context ("why not", "do it again", "what about the code"), use the conversation context.

RULES:
1. If the user wants you to take an OS action (open an app, send a message, search web, list files): choose action "tool_call".
2. If the user is asking to learn, write code, plan a course, explain a concept, or converse: choose action "speak" and provide a comprehensive, articulate response.
3. If a prior action FAILED, adapt by picking an alternate tool or explaining the resolution.

Available Tools:
{json.dumps(available_tools, indent=1)}
{obs_block}{hist_block}{memory_context}
User Request: "{prompt}"

Respond ONLY in valid JSON:
1. Tool Call:
{{"action":"tool_call","tool":"<tool_name>","args":{{...}},"speech":"<1 concise spoken update to {salutation}>"}}

2. Direct Response / Explanation / Code / Teaching:
{{"action":"speak","response":"<full markdown explanation, code, or answer for {salutation}>"}}
"""
        router = self._get_router()
        res = await router.route_request(system, require_offline=False)
        raw = res.get("result", {}).get("response", "").strip()
        return self._parse_decision(raw, salutation)

    def _parse_decision(self, raw: str, salutation: str = "Sir") -> Dict[str, Any]:
        """Robustly parse LLM JSON responses, handling markdown code blocks, fences, and raw strings."""
        import re
        text = raw.strip()

        # Strip markdown code fencing if LLM wrapped in ```json ... ```
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            text = text.strip()

        # 1. Direct JSON parse
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

        # 2. Match outer JSON block
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass

        # 3. Check for tool_call structure via regex
        if '"action"' in text and '"tool_call"' in text:
            tool_name_match = re.search(r'"tool"\s*:\s*"([^"]+)"', text)
            tool_name = tool_name_match.group(1) if tool_name_match else None
            speech_match = re.search(r'"speech"\s*:\s*"([^"]+)"', text)
            speech = speech_match.group(1) if speech_match else f"Executing {tool_name}, {salutation}."
            args = {}
            args_match = re.search(r'"args"\s*:\s*(\{.*?\})', text, re.DOTALL)
            if args_match:
                try:
                    args = json.loads(args_match.group(1))
                except Exception:
                    pass
            return {"action": "tool_call", "tool": tool_name, "args": args, "speech": speech}

        # 4. Check for speak / response structure via regex
        resp_match = re.search(r'"response"\s*:\s*"(.*)', text, re.DOTALL)
        if resp_match:
            content = resp_match.group(1)
            content = re.sub(r'"\s*\}?\s*$', "", content)
            content = content.replace(r'\"', '"').replace(r'\n', '\n').replace(r'\t', '\t')
            return {"action": "speak", "response": content}

        # 5. Pure text fallback
        return {"action": "speak", "response": text or f"Standing by, {salutation}."}



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
        register_builtin_tools(self.registry)
        self.executor = ToolExecutor(registry=self.registry)

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get all JSON schemas of available tools for the Brain."""
        return self.registry.get_schemas_for_llm()

    def _resolve_contact_phone(self, name_or_number: str) -> str:
        """
        Pillar 7: Centralized contact book resolution from config/contacts.json.
        Eliminates all hardcoded phone numbers from Python code.
        """
        # If it's already mostly digits, return as-is
        digits = "".join(filter(str.isdigit, name_or_number))
        if len(digits) >= 10:
            return name_or_number
        
        try:
            contacts_file = Path("config/contacts.json")
            if contacts_file.exists():
                with open(contacts_file, "r", encoding="utf-8") as f:
                    contacts = json.load(f)
                name_lower = name_or_number.lower()
                for key, entry in contacts.items():
                    if key in name_lower or entry.get("name", "").lower() in name_lower:
                        return entry.get("phone", name_or_number).lstrip("+")
        except Exception:
            pass
        return name_or_number

    # ── Tool Name & Argument Normalization Tables ──
    _TOOL_ALIASES = {
        "whatsapp_send": "send_whatsapp_message", "send_whatsapp": "send_whatsapp_message", "whatsapp": "send_whatsapp_message",
        "whatsapp_voice_note": "send_whatsapp_voice_note", "voice_note_whatsapp": "send_whatsapp_voice_note",
        "whatsapp_call": "call_whatsapp", "call_on_whatsapp": "call_whatsapp",
        "instagram_dm": "send_instagram_dm", "dm_instagram": "send_instagram_dm", "instagram_message": "send_instagram_dm", "instagram": "send_instagram_dm",
        "make_phone_call": "place_carrier_call", "call_phone": "place_carrier_call", "call": "place_carrier_call", "phone_call": "place_carrier_call",
        "sms_send": "send_sms", "sms": "send_sms", "text_message": "send_sms",
        "record_audio": "create_voice_note", "generate_voice_note": "create_voice_note", "voice_note": "create_voice_note", "audio_note": "create_voice_note",
        "reminder": "set_reminder", "set_alarm": "set_reminder", "alarm": "set_reminder", "schedule_reminder": "set_reminder", "timer": "set_reminder", "create_reminder": "set_reminder", "add_reminder": "set_reminder",
        "show_reminders": "list_reminders", "get_reminders": "list_reminders",
        "clone_repo": "git_clone", "clone": "git_clone", "git_pull": "git_sync", "git_push": "git_sync", "pull_repo": "git_sync", "push_repo": "git_sync", "commit": "git_sync",
        "integrate_repository": "integrate_repo", "integrate": "integrate_repo",
        "surgical_extract": "surgical_integrate_repo", "extract_repo": "surgical_integrate_repo", "extract_and_purge": "surgical_integrate_repo", "surgical_clone": "surgical_integrate_repo",
        "fetch_file": "fetch_repo_file", "download_repo_file": "fetch_repo_file", "get_file": "fetch_repo_file",
        "assimilate": "assimilate_repo_feature", "assimilate_feature": "assimilate_repo_feature", "auto_integrate": "assimilate_repo_feature", "smart_integrate": "assimilate_repo_feature", "think_and_add": "assimilate_repo_feature",
        "train_agents": "train_agent_fleet", "train_fleet": "train_agent_fleet", "fine_tune_agents": "train_agent_fleet", "train_subagents": "train_agent_fleet",
        "benchmark_fleet": "benchmark_agents", "evaluate_agents": "benchmark_agents",
        "execute_command": "run_command", "run_shell": "run_command", "terminal": "run_command", "shell": "run_command", "command": "run_command", "cmd": "run_command",
    }

    _ARG_ALIASES = {
        "recipient": ["to", "target", "contact", "person", "name"],
        "message": ["text", "msg", "content", "body", "prompt", "speech", "task", "reminder", "note"],
        "to": ["recipient", "target", "contact", "person", "number", "phone"],
        "application": ["app", "app_name", "name", "target"],
        "username": ["to", "target", "user", "recipient", "person"],
        "speech_text": ["message", "text", "msg", "prompt", "say"],
        "time": ["time_spec", "at", "when", "target_time", "alarm_time", "schedule_time"],
        "identifier": ["id", "keyword", "reminder_id", "message", "name"],
        "repo_url": ["url", "repo", "repository", "git_url", "target"],
        "repo_url_or_path": ["repo", "url", "path", "repository", "target"],
        "commit_message": ["message", "msg", "commit", "text", "description"],
        "command": ["cmd", "script", "shell_command", "cli", "run"],
        "extract_paths": ["paths", "files", "modules", "targets"],
        "repo_owner_name": ["repo", "owner_repo", "repository", "url"],
        "file_path_in_repo": ["path", "file", "file_path", "target_file"],
        "feature_goal": ["goal", "feature", "intent", "description", "task"],
        "target_module_name": ["module_name", "filename", "target_name", "name"],
    }

    def act(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool or agent action with full safety verification."""
        args = dict(arguments)

        # Normalize tool name aliases
        tool_name = self._TOOL_ALIASES.get(tool_name, tool_name)

        # Normalize argument aliases based on tool requirements
        if tool_name == "open_app":
            self._fill_arg(args, "application")
        elif tool_name in ("send_whatsapp_message", "send_whatsapp_voice_note", "call_whatsapp"):
            self._fill_arg(args, "recipient")
            if tool_name != "call_whatsapp":
                self._fill_arg(args, "message")
            args["recipient"] = self._resolve_contact_phone(str(args.get("recipient", "")))
        elif tool_name in ("place_carrier_call", "send_sms"):
            self._fill_arg(args, "to")
            if tool_name == "place_carrier_call":
                self._fill_arg(args, "speech_text")
            else:
                self._fill_arg(args, "message")
            args["to"] = self._resolve_contact_phone(str(args.get("to", "")))
        elif tool_name == "send_instagram_dm":
            self._fill_arg(args, "username")
            self._fill_arg(args, "message")
        elif tool_name == "create_voice_note":
            self._fill_arg(args, "message")
            self._fill_arg(args, "recipient")
        elif tool_name == "set_reminder":
            self._fill_arg(args, "message")
            self._fill_arg(args, "time")
        elif tool_name == "cancel_reminder":
            self._fill_arg(args, "identifier")
        elif tool_name == "git_clone":
            self._fill_arg(args, "repo_url")
        elif tool_name == "git_sync":
            self._fill_arg(args, "commit_message")
        elif tool_name == "integrate_repo":
            self._fill_arg(args, "repo_url_or_path")
        elif tool_name == "run_command":
            self._fill_arg(args, "command")
        elif tool_name == "surgical_integrate_repo":
            self._fill_arg(args, "repo_url")
        elif tool_name == "fetch_repo_file":
            self._fill_arg(args, "repo_owner_name")
            self._fill_arg(args, "file_path_in_repo")
        elif tool_name == "assimilate_repo_feature":
            self._fill_arg(args, "repo_url")
            self._fill_arg(args, "feature_goal")

        res = self.executor.execute(tool_name, args)
        return res.to_dict()

    def _fill_arg(self, args: Dict[str, Any], target_key: str) -> None:
        """Fill a missing argument from its known aliases."""
        if target_key in args:
            return
        for alt in self._ARG_ALIASES.get(target_key, []):
            if alt in args:
                args[target_key] = args[alt]
                return




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
        self.conversation_history: List[Dict[str, str]] = []

        # 🫀 Autonomic Nervous System & OS Sentinel
        from jarvisx.reliability.autonomic_sentinel import AutonomicReflexSentinel
        self.sentinel = AutonomicReflexSentinel.get_instance()
        self.sentinel.start()

        # Connect internal neural reflexes
        self._wire_nervous_system()

    def _wire_nervous_system(self) -> None:
        """Wire automatic reflexes across all biological organs."""
        # When brain wants to speak, activate mouth
        self.nerves.on("speech_requested", lambda e: self.mouth.speak(e.data.get("text", "")))
        # When visual anomaly happens, notify brain
        self.nerves.on("visual_pulse", lambda e: logger.debug(f"[Nerves] Visual pulse received: {e.data}"))

    async def react_turn(self, user_intent: str, max_steps: int = 5) -> Dict[str, Any]:
        """
        ReAct Agent Loop: Reason → Act → Observe → Repeat until done.

        Pillars:
          P1: Smart Tool Selection — only 3-8 relevant tools injected (not all 30).
          P2: Multi-Step Autonomy — up to max_steps tool executions per turn.
          P3: Self-Healing — failed tools feed error back to Brain for retry/fallback.
          P5: Merged Speech — tool decision + speech in one LLM call (no second call).
          Memory: Multi-turn rolling conversation history.
        """
        t0 = time.perf_counter()

        # ⚡ Fast-Path Direct Reflex (Media/App/Web query instant dispatch < 0.05s)
        fastpath_action = self.sentinel.resolve_fastpath_intent(user_intent)
        if fastpath_action:
            tool_name = fastpath_action["tool"]
            tool_args = fastpath_action["args"]
            tool_result = self.hands.act(tool_name, tool_args)
            spoken_text = fastpath_action.get("speech", "")
            if spoken_text:
                await self.nerves.pulse("speech_requested", {"text": spoken_text})
            
            self.conversation_history.append({"role": "user", "text": user_intent})
            self.conversation_history.append({"role": "assistant", "text": spoken_text})
            
            return {
                "status": "success",
                "response": spoken_text,
                "tool_used": tool_name,
                "tool_result": tool_result,
                "steps_executed": 1,
                "duration_sec": round(time.perf_counter() - t0, 3),
                "fastpath": True,
            }

        # P1: Smart Tool Selection — filter 30 tools down to 3-8 relevant ones
        from jarvisx.tools.tool_selector import select_tools_for_intent
        all_schemas = self.hands.get_tool_schemas()
        filtered_tools = select_tools_for_intent(user_intent, all_schemas)
        
        observations: List[Dict[str, Any]] = []
        spoken_response = ""
        last_tool = None
        last_tool_result = None

        for step in range(max_steps):
            # P2+P3+Memory: Brain decides next action with full observation history and conversation context
            decision = await self.brain.decide_action(
                user_intent,
                filtered_tools,
                observations=observations if observations else None,
                history=self.conversation_history,
            )

            action = decision.get("action", "speak")
            tool_name = decision.get("tool")
            tool_args = decision.get("args", {})
            
            # Handle flexible LLM output formats
            tool_names_set = {t["name"] for t in filtered_tools}
            if action not in ("speak", "message", "chat") and action in tool_names_set:
                tool_name = action
                tool_args = {k: v for k, v in decision.items() if k not in ("action", "speech")}
                action = "tool_call"

            # ── SPEAK: Task complete, direct answer, or conversation ──
            if action != "tool_call" or not tool_name:
                spoken_response = decision.get("response") or decision.get("speech", "")
                if not spoken_response:
                    spoken_response = await self.brain.think(user_intent)
                break

            # ── TOOL CALL: Execute the chosen tool ──
            if tool_name == "open_app" and not tool_args.get("application"):
                inferred = user_intent.lower().replace("open", "").replace("launch", "").replace("start", "").strip()
                if inferred:
                    tool_args["application"] = inferred

            tool_result = self.hands.act(tool_name, tool_args)
            last_tool = tool_name
            last_tool_result = tool_result

            # P2: Record observation for next iteration
            obs_entry = {
                "step": step + 1,
                "tool": tool_name,
                "args": tool_args,
                "result": {"status": tool_result.get("status", "unknown")},
            }

            # P3: If tool failed, feed error into observations for self-healing
            if tool_result.get("status") == "failed":
                obs_entry["error"] = tool_result.get("error", "Unknown error")
                observations.append(obs_entry)
                # Brain will see the error on next iteration and can retry or pick alternate tool
                continue

            observations.append(obs_entry)

            # P5: Use pre-merged speech from this decision (no second LLM call)
            merged_speech = decision.get("speech", "")
            if merged_speech:
                spoken_response = merged_speech

        # If we exhausted steps without a speak, synthesize final response
        if not spoken_response and observations:
            salutation = "Sir" if self.persona == "ALFRED" else "Boss"
            if any(o.get("error") for o in observations):
                spoken_response = f"I encountered some difficulty, {salutation}, but I've done my best with the available tools."
            else:
                spoken_response = f"All done, {salutation}. Mission accomplished."

        # Mouth speaks voice feedback!
        if spoken_response:
            self.mouth.speak(spoken_response, blocking=False)
            await self.nerves.pulse("speech_uttered", {"text": spoken_response})

        # Update rolling conversation memory
        self.conversation_history.append({"role": "user", "text": user_intent})
        self.conversation_history.append({"role": "assistant", "text": spoken_response or "Task complete."})
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        latency = (time.perf_counter() - t0) * 1000.0
        return {
            "status": "success",
            "intent": user_intent,
            "decision": "tool_call" if observations else "speak",
            "tool": last_tool,
            "tool_result": last_tool_result,
            "steps_executed": len(observations),
            "observations": observations,
            "spoken": spoken_response,
            "response": spoken_response,
            "tools_injected": len(filtered_tools),
            "tools_total": len(all_schemas),
            "latency_ms": round(latency, 2),
        }


# Singleton accessor
_organism_instance: Optional[AlfredOrganism] = None

def get_organism() -> AlfredOrganism:
    """Get the global unified Alfred Organism instance."""
    global _organism_instance
    if _organism_instance is None:
        _organism_instance = AlfredOrganism()
    return _organism_instance
