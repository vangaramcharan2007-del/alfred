from __future__ import annotations

import re
from typing import Any

from jarvisx.agents.base import BaseAgent, AgentResponse
from jarvisx.core.events import Event
from jarvisx.core.failures import FailureReport


def _message(event: Event) -> str:
    return str(event.payload.get("message", "")).strip()


class MemoryAgent(BaseAgent):
    agent_id = "memory"
    role = "Long-term and project memory manager"
    expertise = ("Obsidian", "structured memory", "knowledge graph")
    tone = "precise"
    personality = "careful archivist"
    capabilities = (
        "memory.save_memory",
        "memory.search_memory",
        "memory.append_daily_note",
        "memory.get_daily_note",
        "memory.list_memories",
    )

    async def handle(self, event: Event) -> AgentResponse:
        memory = self.tools["memory"]
        text = _message(event)
        lowered = text.lower()
        if lowered.startswith("remember"):
            content = re.sub(r"^remember\s*", "", text, flags=re.IGNORECASE).strip()
            result = memory.save_memory(content, "general", trace_id=event.trace_id)
        elif lowered.startswith("daily"):
            content = re.sub(r"^daily\s*", "", text, flags=re.IGNORECASE).strip()
            if content:
                result = memory.append_daily_note(content, trace_id=event.trace_id)
            else:
                result = memory.get_daily_note(trace_id=event.trace_id)
        elif lowered.startswith("list memory"):
            category = re.sub(r"^list memory\s*", "", text, flags=re.IGNORECASE).strip()
            result = memory.list_memories(category or "general", trace_id=event.trace_id)
        else:
            query = re.sub(r"^(recall|memory|find memory)\s*", "", text, flags=re.IGNORECASE).strip()
            result = memory.search_memory(query, trace_id=event.trace_id)
        return self._response(
            event,
            handled=result.success,
            message=result.message,
            data={"tool": "memory", "result": result.to_dict()},
        )


class DeviceAgent(BaseAgent):
    agent_id = "device"
    role = "Android automation and device control"
    expertise = ("app launching", "notifications", "device actions")
    tone = "direct"
    personality = "efficient operator"
    capabilities = ("device.open_app", "device.notification", "device.speak_text")

    async def handle(self, event: Event) -> AgentResponse:
        device = self.tools["device"]
        device_action = event.payload.get("device_action")
        if isinstance(device_action, dict):
            action = str(device_action.get("action", ""))
            parameters = device_action.get("parameters", {})
            if not isinstance(parameters, dict):
                parameters = {}
            result = device.prepare_device_action(action, parameters, trace_id=event.trace_id)
            return self._response(
                event,
                handled=result.success,
                message=result.message,
                data={"tool": "device", "result": result.to_dict()},
            )

        text = _message(event)
        app_name = _extract_app_name(text)
        result = device.prepare_open_app(app_name, trace_id=event.trace_id)
        return self._response(
            event,
            handled=result.success,
            message=result.message,
            data={"tool": "device", "result": result.to_dict()},
        )


class ResearchAgent(BaseAgent):
    agent_id = "research"
    role = "Information gathering and documentation analysis"
    expertise = ("research", "summarization", "documentation")
    tone = "analytical"
    personality = "methodical researcher"
    capabilities = ("research.summarize_local", "research.prepare_query")

    async def handle(self, event: Event) -> AgentResponse:
        research = self.tools["research"]
        result = research.summarize_local_note(_message(event))
        return self._response(
            event,
            handled=True,
            message="Research Agent prepared an offline research summary.",
            data={"tool": "research", "result": result.to_dict()},
        )


class PlannerAgent(BaseAgent):
    agent_id = "planner"
    role = "Scheduling, tasks, goals, and reminders"
    expertise = ("planning", "scheduling", "goals")
    tone = "organized"
    personality = "steady coordinator"
    capabilities = (
        "planner.capture_task",
        "planner.prepare_reminder",
        "mission.create_mission",
        "mission.complete_mission",
        "mission.list_active_missions",
        "mission.get_next_mission",
        "mission.generate_recovery_mission",
    )

    async def handle(self, event: Event) -> AgentResponse:
        text = _message(event)
        mission = self.tools.get("mission")
        if mission and _looks_like_mission_request(text):
            result = _handle_mission_request(mission, text, event.trace_id)
            return self._response(
                event,
                handled=result.success,
                message=result.message,
                data={"tool": "mission", "result": result.to_dict()},
            )

        data: dict[str, Any] = {"captured_task": text}
        notification = self.tools.get("notification")
        if notification and "remind" in text.lower():
            data["notification"] = notification.prepare_notification("Reminder", text).to_dict()
        return self._response(
            event,
            handled=True,
            message="Planner Agent captured the task for scheduling.",
            data=data,
        )


class EditingAgent(BaseAgent):
    agent_id = "editing"
    role = "Media workflow specialist"
    expertise = ("video editing", "thumbnails", "subtitles")
    tone = "creative and specific"
    personality = "practical editor"
    capabilities = ("editing.plan_workflow", "editing.prepare_assets")

    async def handle(self, event: Event) -> AgentResponse:
        return self._response(
            event,
            handled=True,
            message="Editing Agent prepared a media workflow plan.",
            data={"workflow_request": _message(event), "tools_needed": ["media", "file"]},
        )


class CADAgent(BaseAgent):
    agent_id = "cad"
    role = "CAD analysis and manufacturing support"
    expertise = ("CAD analysis", "model understanding", "manufacturing")
    tone = "technical"
    personality = "careful design reviewer"
    capabilities = ("cad.inspect", "cad.manufacturing_notes")

    async def handle(self, event: Event) -> AgentResponse:
        return self._response(
            event,
            handled=True,
            message="CAD Agent prepared a design-analysis handoff.",
            data={"cad_request": _message(event), "tools_needed": ["cad", "vision"]},
        )


class ShadowBrokerAgent(BaseAgent):
    agent_id = "shadowbroker"
    role = "OSINT and security awareness specialist"
    expertise = ("OSINT", "security awareness", "trend monitoring")
    tone = "cautious"
    personality = "measured intelligence analyst"
    capabilities = ("osint.plan_collection", "security.summarize_trends")

    async def handle(self, event: Event) -> AgentResponse:
        research = self.tools.get("research")
        data: dict[str, Any] = {"collection_request": _message(event)}
        if research:
            data["offline_summary"] = research.summarize_local_note(_message(event)).to_dict()
        return self._response(
            event,
            handled=True,
            message="ShadowBroker Agent prepared an offline intelligence collection plan.",
            data=data,
        )


class DebugAgent(BaseAgent):
    agent_id = "debug"
    role = "Failure analysis and patch suggestion specialist"
    expertise = ("logs", "tests", "patch suggestions")
    tone = "diagnostic"
    personality = "careful debugger"
    capabilities = ("debug.analyze_failure", "debug.suggest_fix")

    async def handle(self, event: Event) -> AgentResponse:
        failure_payload = event.payload.get("failure")
        if isinstance(failure_payload, dict):
            report = failure_payload
        else:
            report = FailureReport(
                what_failed="unknown_failure",
                why=_message(event) or "No failure details supplied.",
                agent_id=self.agent_id,
                tool_name=None,
                proposed_fix="Collect logs, reproduce the failure, then add a targeted regression test.",
                trace_id=event.trace_id,
            ).to_dict()
        return self._response(
            event,
            handled=True,
            message="Debug Agent produced a failure report and proposed fix. It will not deploy changes without approval.",
            data={"failure_report": report},
        )


def _extract_app_name(text: str) -> str:
    lowered = text.lower().strip()
    for prefix in ("open", "launch", "start"):
        if lowered.startswith(prefix):
            return text[len(prefix) :].strip()
    if "youtube" in lowered:
        return "YouTube"
    return text or "requested app"


def _looks_like_mission_request(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in ("mission", "quest", "boss", "xp", "streak"))


def _handle_mission_request(mission: Any, text: str, trace_id: str) -> Any:
    lowered = text.lower().strip()
    if "next" in lowered:
        return mission.get_next_mission(trace_id=trace_id)
    if "recovery" in lowered:
        return mission.generate_recovery_mission(trace_id=trace_id)
    if "list" in lowered or "active" in lowered:
        return mission.list_active_missions(trace_id=trace_id)
    complete_match = re.search(r"complete\s+(?:mission\s+)?([a-f0-9]{8,32})", lowered)
    if complete_match:
        return mission.complete_mission(complete_match.group(1), trace_id=trace_id)

    mission_type = "side_quest"
    if "main quest" in lowered:
        mission_type = "main_quest"
    elif "boss" in lowered:
        mission_type = "boss_fight"
    elif "daily" in lowered:
        mission_type = "daily_mission"
    title = re.sub(
        r"^(create|add|start)?\s*(a\s*)?(main quest|side quest|boss fight|daily mission|mission|quest)\s*",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    return mission.create_mission(title or text, mission_type, trace_id=trace_id)
