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
        message = str(event.payload.get("message", "")).lower()
        notification = self.tools.get("notification")
        termux = self.tools.get("termux")
        personalization = self.tools.get("personalization")
        
        data = {"requested_message": message}
        
        if personalization:
            style = personalization.get_response_config(self.agent_id, trace_id=event.trace_id)
            if style.success:
                data["response_config"] = style.data
                
        # Termux Mobile Execution
        if termux:
            if "battery" in message:
                battery_res = termux.battery_status()
                data["battery"] = battery_res.to_dict()
            if "vibrate" in message:
                termux.vibrate()
            if "macro" in message:
                termux.trigger_macrodroid("default_macro_id")
                
        # Fallback to desktop notification if requested
        if notification and "notification" in message:
            result = notification.prepare_notification("Jarvis X", message)
            data["notification"] = result.to_dict()
            
        return self._response(
            event,
            handled=True,
            message="Edith prepared the mobile execution handoff.",
            data=data,
        )
