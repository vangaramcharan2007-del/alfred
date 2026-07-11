from __future__ import annotations

from jarvisx.agents.base import BaseAgent, AgentResponse
from jarvisx.core.events import Event


class EdithAgent(BaseAgent):
    agent_id = "edith"
    role = "Mobile companion and Android execution layer"
    expertise = ("voice interface", "notifications", "device actions")
    tone = "brief and practical"
    personality = "calm mobile operator"
    capabilities = ("voice", "notifications", "android handoff")

    async def handle(self, event: Event) -> AgentResponse:
        message = str(event.payload.get("message", ""))
        notification = self.tools.get("notification")
        data = {"requested_message": message}
        if notification and "notification" in message.lower():
            result = notification.prepare_notification("Jarvis X", message)
            data["notification"] = result.to_dict()
        return self._response(
            event,
            handled=True,
            message="Edith prepared the mobile execution handoff.",
            data=data,
        )
