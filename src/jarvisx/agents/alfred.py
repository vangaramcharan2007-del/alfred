from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from jarvisx.agents.base import AgentResponse
from jarvisx.agents.registry import AgentRegistry
from jarvisx.core.events import Event
from jarvisx.core.failures import FailureReport
from jarvisx.core.hermes import HermesBus
from jarvisx.core.logging import StructuredLogger
from jarvisx.models.router import ModelRouter
from jarvisx.tools.device import SUPPORTED_DEVICE_ACTIONS


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
        ("device_control", "device", "device", ("open ", "launch ", "start app", "youtube", "android")),
        ("memory", "memory", "memory", ("remember", "recall", "memory", "obsidian", "note")),
        ("research", "research", "research", ("research", "summarize", "documentation", "docs", "find info")),
        (
            "planning",
            "planner",
            "planning",
            ("schedule", "remind", "todo", "task", "goal", "mission", "quest", "boss", "xp", "streak"),
        ),
        ("editing", "editing", "editing", ("create a file", "write a script", "edit code", "write code", "edit file")),
        ("cad", "cad", "cad", ("cad", "stl", "3d model", "manufacturing", "dimension")),
        ("shadowbroker", "shadowbroker", "shadowbroker", ("osint", "threat", "security", "trend monitoring")),
        ("debug", "debug", "debug", ("debug", "error", "failure", "logs", "test", "patch", "fix")),
        ("edith_mobile", "edith", "device", ("voice", "notification", "mobile companion")),
    )

    def classify(self, message: str) -> Intent:
        normalized = f" {message.strip().lower()} "
        for label, agent_id, task_class, keywords in self._rules:
            for keyword in keywords:
                if keyword in normalized:
                    return Intent(
                        label=label,
                        agent_id=agent_id,
                        task_class=task_class,
                        confidence=0.82,
                        reason=f"Matched keyword '{keyword.strip()}'.",
                    )
        return Intent(
            label="planning",
            agent_id="planner",
            task_class="planning",
            confidence=0.35,
            reason="No specialist keyword matched; using Planner as a safe clarification path.",
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
    ) -> None:
        self.hermes = hermes
        self.registry = registry
        self.classifier = classifier
        self.model_router = model_router
        self.personalization_tool = personalization_tool
        self.logger = logger or StructuredLogger()

    async def process(
        self,
        message: str,
        *,
        trace_id: Optional[str] = None,
        source: str = "user",
        has_image: bool = False,
    ) -> AgentResponse:
        user_event = self._event(
            event_type="user.message.received",
            source=source,
            trace_id=trace_id,
            payload={"message": message},
        )
        intent = self.classifier.classify(message)
        model = self.model_router.select(intent.task_class, message, has_image=has_image)
        self.logger.write(
            "info",
            "alfred.intent.selected",
            trace_id=user_event.trace_id,
            intent=intent.to_dict(),
            model=model.to_dict(),
        )
        response_config = self._response_config(user_event.trace_id)

        task_event = user_event.child(
            event_type="agent.task.requested",
            source=self.agent_id,
            target=intent.agent_id,
            payload={
                "message": message,
                "intent": intent.to_dict(),
                "model": model.to_dict(),
                "response_config": response_config,
            },
        )
        return await self._delegate(
            task_event,
            intent=intent,
            model=model.to_dict(),
            response_config=response_config,
        )

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

        responses = await self.hermes.publish(task_event)
        response = next((item for item in responses if isinstance(item, AgentResponse)), None)
        if response:
            response_data = {
                **response.data,
                "intent": intent.to_dict(),
                "orchestrator_response_config": response_config,
            }
            response_data.setdefault("response_config", response_config)
            return AgentResponse(
                agent_id=response.agent_id,
                handled=response.handled,
                message=response.message,
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
