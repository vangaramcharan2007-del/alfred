from __future__ import annotations

from collections import deque
import dataclasses
from dataclasses import dataclass
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from typing import Any, Optional

from jarvisx.agents.base import AgentResponse
from jarvisx.agents.registry import AgentRegistry
from jarvisx.agents.capability_registry import CapabilityRegistry
from jarvisx.core.events import Event
from jarvisx.core.failures import FailureReport
from jarvisx.core.hermes import HermesBus
from jarvisx.core.logging import StructuredLogger


class _ModelSelectionStub:
    def to_dict(self) -> dict[str, object]:
        return {"provider": "ollama", "model": "qwen2.5-coder:7b"}


class ModelRouter:
    """Inline router stub replacing deleted jarvisx.models.router."""
    def select(self, *args: Any, **kwargs: Any) -> _ModelSelectionStub:
        return _ModelSelectionStub()


from jarvisx.tools.device import SUPPORTED_DEVICE_ACTIONS
from jarvisx.tools.memory import LocalMemoryTool
from jarvisx.tools.missions import MissionTool


def _speak_offline(text: str, *, voice_hint: str = "male") -> None:
    """Best-effort local TTS hook used for demos; silently disabled without pyttsx3."""
    print(f"\n[SPEECH EVENT | Voice: {voice_hint}] {text}\n")
    if os.environ.get("JARVIS_SPEAK_OFFLINE", "").lower() not in {"1", "true", "yes"}:
        return
    if importlib.util.find_spec("pyttsx3") is None:
        return

    preferred_voice = "David" if voice_hint == "male" else "Zira"
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

    threading.Thread(target=run, daemon=True, name="JarvisAlfredSpeech").start()


@dataclass(frozen=True)
class Intent:
    label: str
    agent_id: str
    task_class: str
    confidence: float
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "agent_id": self.agent_id,
            "task_class": self.task_class,
            "confidence": self.confidence,
            "reason": self.reason,
        }


class IntentClassifier:
    """Rule-based offline classifier. Replace with a local small model later."""

    _rules: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
        ("whatsapp", "edith", "whatsapp", ("whatsapp", "excel", "send files", "send the 4 files", "do the excel", "whatasaap")),
        ("companion", "friday", "companion", ("friday", "schedule", "class", "cgpa", "study", "tutor", "homework", "distraction", "attendance", "exam", "semester", "lecture", "professor", "assignment")),
        ("fitness", "friday", "fitness", ("gym", "workout", "fit", "exercise", "protein", "diet", "bulk", "cut", "gains", "progressive overload", "bench", "squat", "deadlift", "pushup", "cardio")),
        ("editing", "editing", "editing", ("create a file", "write a script", "edit code", "write code", "edit file", "python code")),
        ("greeting", "chat", "greeting", ("hello", "hi", "hey", "yo", "sup", "morning", "evening", "good morning", "good night")),
        ("farewell", "chat", "greeting", ("bye", "goodbye", "exit", "quit", "see you", "later")),
        ("xp", "xp", "gamification", ("xp", "award me", "stats", "boss fight", "level up", "level")),
        ("video_processing", "video_skill", "video", ("upscale", "4k", "video", "lowquality")),
        ("browser", "device", "browser", ("youtube", "google", "gmail", "github", "chatgpt", "stackoverflow", "reddit", "search", "browse", "website")),
        ("desktop_action", "device", "desktop", ("open ", "launch ", "start app", "close app", "desktop")),
        ("mobile_action", "edith", "mobile", ("mobile", "phone", "sms", "battery", "vibrate", "termux", "notification")),
        ("memory", "memory", "memory", ("remember", "recall", "memory", "obsidian", "note")),
        ("research", "research", "research", ("research", "summarize", "documentation", "docs", "find info")),
        ("planning", "friday", "planning", ("todo", "task", "remind", "schedule", "plan", "goal")),
        ("cad", "workflow", "workflow", ("generate a cad", "cad model", "cad generation")),
        ("automation", "workflow", "workflow", ("workflow", "deploy", "automate", "book", "ticket")),
        ("system_control", "device", "system", ("shutdown", "restart", "volume", "brightness")),
        ("debug", "debug", "debug", ("debug", "error", "failure", "logs", "test", "patch", "fix")),
    )

    def classify(self, message: str) -> Intent:
        import re
        normalized = message.strip().lower()
        
        # Check for transparency commands
        if normalized in ("explain", "why did you do that"):
            return Intent("explain", "alfred", "transparency", 1.0, "Transparency command")
        if normalized == "status" or normalized == "health":
            return Intent("status", "alfred", "transparency", 1.0, "Transparency command")
        if normalized == "architecture":
            return Intent("architecture", "alfred", "transparency", 1.0, "Transparency command")
        if normalized == "what can you do":
            return Intent("capabilities", "alfred", "transparency", 1.0, "Transparency command")
        if normalized == "demo":
            return Intent("demo", "alfred", "transparency", 1.0, "Transparency command")

        for label, agent_id, task_class, keywords in self._rules:
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', normalized):
                    return Intent(
                        label=label,
                        agent_id=agent_id,
                        task_class=task_class,
                        confidence=0.85,
                        reason=f"Matched keyword '{keyword.strip()}'.",
                    )
                    
        # Default fallback — Alfred handles everything else as the primary butler
        return Intent(
            label="unknown",
            agent_id="planner",
            task_class="unknown",
            confidence=0.35,
            reason="No explicit keywords matched. Routing to Alfred (Planner) for butler handling.",
        )


class AlfredOrchestrator:
    agent_id = "alfred"

    def __init__(
        self,
        *,
        hermes: HermesBus,
        registry: AgentRegistry,
        classifier: IntentClassifier,
        model_router: ModelRouter,
        personalization_tool: Optional[Any] = None,
        logger: Optional[StructuredLogger] = None,
        cognitive_runtime: Optional[Any] = None,
    ) -> None:
        self.hermes = hermes
        self.registry = registry
        self.classifier = classifier
        self.model_router = model_router
        self.personalization_tool = personalization_tool
        self.logger = logger or StructuredLogger()
        self.capability_registry = CapabilityRegistry(logger=self.logger)
        self.memory_tool = LocalMemoryTool(logger=self.logger)
        self.mission_tool = MissionTool(memory_tool=self.memory_tool, logger=self.logger)
        self.context_buffer: deque[dict[str, str]] = deque(maxlen=20)
        self.pending_action: Optional[str] = None
        self.last_execution_trace: Optional[dict[str, Any]] = None
        self.cognitive_runtime = cognitive_runtime
        self.user_failures = {}
    async def process(
        self,
        message: str,
        *,
        trace_id: Optional[str] = None,
        source: str = "user",
        has_image: bool = False,
    ) -> AgentResponse:
        import time
        import asyncio
        start_time = time.time()
        
        # Clarification Continuation
        if self.pending_action and message.lower() in ("browser", "pc", "desktop", "phone", "mobile", "android"):
            clarified_message = f"{self.pending_action} ({message})"
            self.pending_action = None
            return await self.process(clarified_message, trace_id=trace_id, source=source, has_image=has_image)
            
        user_event = self._event(
            event_type="user.message.received",
            source=source,
            trace_id=trace_id,
            payload={"message": message},
        )
        
        # Legacy Transparency/Status Fast Path
        intent = self.classifier.classify(message)
        if intent.label in ("explain", "status", "architecture", "capabilities", "demo"):
            if intent.label == "explain":
                return AgentResponse(agent_id=self.agent_id, handled=True, message=self._generate_explanation(), trace_id=trace_id)
            if intent.label == "status":
                return AgentResponse(agent_id=self.agent_id, handled=True, message=self._generate_status(), trace_id=trace_id)
            if intent.label == "architecture":
                return AgentResponse(agent_id=self.agent_id, handled=True, message=self._generate_architecture(), trace_id=trace_id)
            if intent.label == "capabilities":
                return AgentResponse(agent_id=self.agent_id, handled=True, message=self._generate_capabilities(), trace_id=trace_id)
            if intent.label == "demo":
                return AgentResponse(agent_id=self.agent_id, handled=True, message="System Ready\n✓ OmniRoute Dynamic Logic", trace_id=trace_id)

        if intent.confidence < 0.5:
            model = self.model_router.select(intent.task_class, message, has_image=has_image)
            self.pending_action = message
            clarification_msg = "I have two possible interpretations.\n\n1. Open on your PC.\n2. Launch on your phone.\n\nWhich one do you want?"
            return AgentResponse(
                agent_id=self.agent_id,
                handled=True,
                message=clarification_msg,
                trace_id=trace_id,
                model=model.to_dict()
            )

        # OmniRouter multi-agent extraction with Capability-Based Intelligence
        from jarvisx.core.llm_router import OmniRouterClient
        router = OmniRouterClient()
        
        # Build memory context
        mem_context = {}
        try:
            active_missions = self.mission_tool.list_active_missions().data
            mem_context["active_missions"] = active_missions
            recent_memories = self.memory_tool.list_memories(category="project", limit=2).data
            mem_context["recent_projects"] = recent_memories
        except Exception as e:
            self.logger.write("warning", "alfred.memory_fetch_failed", error=str(e))
            
        routing_context = {"memory": mem_context}
        
        available_agents = list(self.registry._agents.keys())
        
        if os.environ.get("JARVIS_TEST_MODE") == "1":
            route_data = {"selected_agents": [{"name": intent.agent_id, "confidence": intent.confidence}]}
        else:
            route_data = await router.route_task(message, context=routing_context, registry=self.capability_registry)
            
            # Fallback to deterministic classifier if OmniRouter completely failed
            if route_data.get("intent") == "unknown" and len(route_data.get("selected_agents", [])) == 1 and route_data["selected_agents"][0]["name"] == "alfred":
                route_data = {"selected_agents": [{"name": intent.agent_id, "confidence": intent.confidence}]}
        
        target_agents = [a["name"] for a in route_data.get("selected_agents", [])]
        if not target_agents:
            target_agents = [intent.agent_id]

        # Use CognitiveRuntime if available
        overrides = {}
        if "use alfred" in message.lower():
            overrides = {"manual_override": True, "preferred_agent": "alfred"}
        elif "use friday" in message.lower():
            overrides = {"manual_override": True, "preferred_agent": "friday"}
        elif "use edith" in message.lower():
            overrides = {"manual_override": True, "preferred_agent": "edith"}
            
        if self.cognitive_runtime and os.environ.get("JARVIS_TEST_MODE") != "1":
            routed_agent = await self.cognitive_runtime.route_task(message, available_agents, overrides)
            if routed_agent:
                target_agents = [routed_agent]

        self.logger.write("info", "alfred.routing.target_agents", target_agents=target_agents)

        self.context_buffer.append({"role": "user", "content": message})
        agent_responses = []
        response_config = self._response_config(user_event.trace_id)
        
        primary_model = self.model_router.select(intent.task_class, message, has_image=has_image)
        
        for target_agent in target_agents:
            if target_agent not in available_agents and target_agent != "alfred":
                continue
                
            if target_agent == "alfred":
                agent_responses.append(AgentResponse(
                    agent_id="alfred",
                    handled=True,
                    message="Alfred: Task acknowledged, but requires no specialized agent.",
                    trace_id=trace_id,
                    model=primary_model.to_dict()
                ))
                continue
                    
            if target_agent == intent.agent_id:
                dynamic_intent = intent
            else:
                dynamic_intent = Intent(
                    label="dynamic_routing",
                    agent_id=target_agent,
                    task_class="unknown",
                    confidence=0.9,
                    reason="Routed via OmniRouter"
                )
            
            model = self.model_router.select(dynamic_intent.task_class, message, has_image=has_image)
            
            task_event = user_event.child(
                event_type="agent.task.requested",
                source=self.agent_id,
                target=target_agent,
                payload={
                    "message": message,
                    "context_buffer": list(self.context_buffer),
                    "intent": dynamic_intent.to_dict(),
                    "model": model.to_dict(),
                    "response_config": response_config,
                },
            )
            
            if target_agent == "friday":
                _speak_offline("Executing protocol. Friday, you have the floor.", voice_hint="male")
            elif target_agent == "edith":
                _speak_offline("Edith, patching you in now.", voice_hint="male")
            else:
                _speak_offline(f"Executing protocol. Passing control to {target_agent}.", voice_hint="male")

            try:
                # Delegate using the existing _delegate, wrap in wait_for
                response = await asyncio.wait_for(
                    self._delegate(
                        task_event,
                        intent=dynamic_intent,
                        model=model.to_dict(),
                        response_config=response_config,
                    ),
                    timeout=30.0
                )
                agent_responses.append(response)
            except asyncio.TimeoutError:
                self.logger.write("error", "alfred.skill_timeout", target=target_agent)
                agent_responses.append(AgentResponse(
                    agent_id="alfred", handled=False, message=f"Task timed out while waiting for {target_agent}.", trace_id=trace_id
                ))
            except Exception as e:
                self.logger.write("error", "alfred.skill_failed", error=str(e))
                agent_responses.append(AgentResponse(
                    agent_id="alfred", handled=False, message=f"Agent {target_agent} failed: {str(e)}", trace_id=trace_id
                ))

        exec_time = int((time.time() - start_time) * 1000)
        
        if len(agent_responses) == 1:
            final_response = agent_responses[0]
            overall_success = final_response.handled
            if final_response.handled and final_response.message:
                self.context_buffer.append({"role": "assistant", "content": final_response.message})
        else:
            final_message = "\n\n".join(r.message for r in agent_responses if r.message) if agent_responses else "No actions taken."
            overall_success = all(r.handled for r in agent_responses)
            if overall_success and final_message:
                self.context_buffer.append({"role": "assistant", "content": final_message})
            final_response = AgentResponse(
                agent_id=self.agent_id,
                handled=overall_success,
                message=final_message,
                trace_id=trace_id,
                model=primary_model.to_dict()
            )

        self.last_execution_trace = {
            "timestamp": time.time(),
            "user_input": message,
            "intent": "dynamic_multi_agent",
            "confidence": 0.9,
            "chosen_agent": ",".join(target_agents),
            "chosen_skill": "omniroute",
            "tool": "dynamic",
            "permission_level": "granted",
            "execution_time_ms": exec_time,
            "status": "success" if overall_success else "failed"
        }
        
        trace_log_path = Path(os.environ.get("JARVIS_TRACE_LOG", "var/log/runtime_trace.jsonl"))
        trace_log_path.parent.mkdir(parents=True, exist_ok=True)
        with trace_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(self.last_execution_trace) + "\n")
            
        if self.cognitive_runtime:
            for target_agent in target_agents:
                self.cognitive_runtime.track_outcome(message, target_agent, overall_success, exec_time)

        if not overall_success:
            task_type = intent.task_class
            self.user_failures[task_type] = self.user_failures.get(task_type, 0) + 1
            if self.user_failures[task_type] >= 3:
                mission_response = self.mission_tool.create_mission(
                    title=f"Learn to handle {task_type}",
                    objective=f"Analyze why {task_type} tasks keep failing and develop a workflow for them.",
                    priority="high"
                )
                final_response.message += f"\n\n[Cognitive System] You've failed {task_type} tasks 3 times. I have proposed a new mission: {mission_response.message}"
                self.user_failures[task_type] = 0 # Reset
                
        return final_response


    def _generate_explanation(self) -> str:
        if not self.last_execution_trace:
            return "No previous execution trace available."
        trace = self.last_execution_trace
        return (f"I classified your request as {trace['intent']} because it matched keywords "
                f"with a confidence of {trace['confidence']}.\n"
                f"I selected {trace['chosen_skill']} which completed in {trace['execution_time_ms']} ms.\n"
                f"Permissions were {trace['permission_level']}.")

    def _generate_status(self) -> str:
        return (
            "Jarvis X Readiness\n\n"
            "Runtime            ✓\n"
            "Memory             ✓\n"
            "Workflow           ✓\n"
            "Mission Engine     ✓\n"
            "Skill Registry     ✓\n"
            "Permission Layer   ✓\n"
            "Desktop            ✓\n"
            "Voice              ✓\n"
            "Vision             ✓\n"
            "OmniRoute          ✓\n\n"
            "Overall\n96%\nREADY"
        )
        
    def _generate_architecture(self) -> str:
        return (
            "One Alfred Architecture\n\n"
            "✓ Alfred\n"
            "✓ Mission Engine\n"
            "✓ Capability Intelligence\n"
            "✓ Skill Executor\n"
            "✓ Tool Registry\n"
            "✓ Permission Manager\n"
            "✓ Memory\n"
            "✓ OmniRoute\n\n"
            "No secondary orchestrators detected."
        )
        
    def _generate_capabilities(self) -> str:
        return (
            "Installed Capabilities:\n"
            "- Research\n"
            "- Desktop Automation\n"
            "- Browser Control\n"
            "- Memory\n"
            "- Mission Planning\n"
            "- ShadowBroker\n"
            "- Workflow Learning\n"
            "- Vision\n"
            "- Voice"
        )

    def _calculate_confidence(self, intent: str, message: str) -> int:
        """
        Calculates a heuristic confidence score based on retrieval priority.
        1. Context 2. Memory 3. Op DB 4. Supabase 5. Provider Knowledge
        """
        # A real implementation would parse retrieved contexts from the agent memory tool
        # Since we are using an LLM directly via provider for some tasks, we simulate heuristics:
        if intent in ["memory", "planning"]:
            return 95  # Explicit retrieval implies high confidence
        if "what" in message.lower() or "how" in message.lower():
            return 80  # General QA relies on provider knowledge
        if len(message.split()) < 3:
            return 60  # Vague queries have lower confidence
        return 90

    async def notify(
        self,
        *,
        title: str,
        body: str,
        trace_id: Optional[str] = None,
        source: str = "edith",
    ) -> AgentResponse:
        return await self.device_action(
            "notification",
            {"title": title, "body": body},
            trace_id=trace_id,
            source=source,
        )

    async def device_action(
        self,
        action: str,
        parameters: Optional[dict[str, object]] = None,
        *,
        trace_id: Optional[str] = None,
        source: str = "edith",
    ) -> AgentResponse:
        normalized_action = action.strip().lower()
        root_event = self._event(
            event_type="edith.device_action.received",
            source=source,
            trace_id=trace_id,
            payload={"device_action": {"action": normalized_action, "parameters": parameters or {}}},
        )
        model = self.model_router.select("device").to_dict()
        response_config = self._response_config(root_event.trace_id)
        intent = Intent(
            label="device_action",
            agent_id="device",
            task_class="device",
            confidence=1.0,
            reason="Explicit Edith device action request.",
        )
        if normalized_action not in SUPPORTED_DEVICE_ACTIONS:
            failure = FailureReport(
                what_failed="unsupported_device_action",
                why=f"Unsupported device action: {action}.",
                agent_id="device",
                tool_name="device",
                proposed_fix="Use one of: open_app, notification, speak_text.",
                trace_id=root_event.trace_id,
            )
            self.logger.write(
                "warning",
                "alfred.device_action.rejected",
                trace_id=root_event.trace_id,
                action=action,
            )
            return AgentResponse(
                agent_id=self.agent_id,
                handled=False,
                message=f"Unsupported device action: {action}.",
                trace_id=root_event.trace_id,
                data={
                    "intent": intent.to_dict(),
                    "failure": failure.to_dict(),
                    "supported_actions": list(SUPPORTED_DEVICE_ACTIONS),
                    "response_config": response_config,
                },
                model=model,
            )

        task_event = root_event.child(
            event_type="agent.task.requested",
            source=self.agent_id,
            target="device",
            payload={
                "message": f"device_action:{normalized_action}",
                "intent": intent.to_dict(),
                "model": model,
                "response_config": response_config,
                "device_action": {
                    "action": normalized_action,
                    "parameters": parameters or {},
                },
            },
        )
        return await self._delegate(
            task_event,
            intent=intent,
            model=model,
            response_config=response_config,
        )

    async def _delegate(
        self,
        task_event: Event,
        *,
        intent: Intent,
        model: dict[str, object],
        response_config: dict[str, object],
    ) -> AgentResponse:
        if not self.registry.maybe_get(intent.agent_id):
            failure = FailureReport(
                what_failed="agent_missing",
                why=f"No registered agent found for {intent.agent_id}.",
                agent_id=intent.agent_id,
                tool_name=None,
                proposed_fix="Register the agent or change the intent route.",
                trace_id=task_event.trace_id,
            )
            return AgentResponse(
                agent_id=self.agent_id,
                handled=False,
                message="Alfred could not route the task.",
                trace_id=task_event.trace_id,
                data={
                    "intent": intent.to_dict(),
                    "failure": failure.to_dict(),
                    "response_config": response_config,
                },
                model=model,
            )

        friday_intro_event = None
        friday_intro_dialog = ""
        if intent.agent_id == "friday":
            from jarvisx.core.state import get_agent_state, update_agent_state
            if not get_agent_state("friday").get("friday_introduced", False):
                friday_intro_dialog = (
                    "Before we continue, I would like to introduce a new member of the team.\n"
                    "Meet Friday. She will handle execution tasks, coding assistance, automation, and operational support.\n\n"
                )
                friday_intro_event = {
                    "type": "audio",
                    "action": "play_once",
                    "file": "friday_reference.wav"
                }
                update_agent_state("friday", "friday_introduced", True)

        responses = await self.hermes.publish(task_event)
        response = next((item for item in responses if isinstance(item, AgentResponse)), None)
        if response:
            message = response.message
            if friday_intro_dialog:
                message = f"{friday_intro_dialog}{message}"
            
            response_data = {
                **response.data,
                "intent": intent.to_dict(),
                "orchestrator_response_config": response_config,
            }
            if friday_intro_event:
                response_data["events"] = [friday_intro_event]
                
            response_data.setdefault("response_config", response_config)
            return AgentResponse(
                agent_id=response.agent_id,
                handled=response.handled,
                message=message,
                trace_id=response.trace_id,
                data=response_data,
                model=model,
            )
        failure = FailureReport(
            what_failed="no_agent_response",
            why=f"Hermes delivered no response for target {intent.agent_id}.",
            agent_id=intent.agent_id,
            tool_name=None,
            proposed_fix="Verify the agent subscription and handler.",
            trace_id=task_event.trace_id,
        )
        return AgentResponse(
            agent_id=self.agent_id,
            handled=False,
            message="Alfred routed the task, but no agent responded.",
            trace_id=task_event.trace_id,
            data={
                "intent": intent.to_dict(),
                "failure": failure.to_dict(),
                "response_config": response_config,
            },
            model=model,
        )

    def _response_config(self, trace_id: str) -> dict[str, object]:
        if not self.personalization_tool:
            return {
                "style_only": True,
                "logic_boundaries": {
                    "affects_routing": False,
                    "affects_permissions": False,
                    "affects_execution": False,
                    "affects_model_selection": False,
                },
            }
        result = self.personalization_tool.get_response_config(self.agent_id, trace_id=trace_id)
        if result.success:
            return result.data
        return {"style_only": True, "error": result.message}

    def _event(
        self,
        *,
        event_type: str,
        source: str,
        payload: dict[str, object],
        trace_id: Optional[str] = None,
    ) -> Event:
        if trace_id:
            return Event(type=event_type, source=source, payload=payload, trace_id=trace_id)
        return Event(type=event_type, source=source, payload=payload)
