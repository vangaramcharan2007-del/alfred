from __future__ import annotations

import asyncio
from typing import Dict, Any

from jarvisx.agents.plugins import Plugin
from jarvisx.agents.base import BaseAgent, AgentResponse
from jarvisx.core.events import Event


class IntelligenceAgent(BaseAgent):
    agent_id = "intelligence"
    role = "Strategic analyst and intelligence aggregator"
    expertise = ("timeline analysis", "contextual awareness", "trend monitoring")
    tone = "analytical"
    personality = "sharp intelligence officer"
    capabilities = ("intelligence.analyze_timeline", "intelligence.get_recommendations")

    async def handle(self, event: Event) -> AgentResponse:
        message = str(event.payload.get("message", "")).lower()
        
        # Stub response for intelligence layer
        if "timeline" in message:
            return self._response(
                event,
                handled=True,
                message="Intelligence Agent analyzed the timeline.",
                data={"timeline": "Timeline indicates high productivity early in the week."}
            )
            
        return self._response(
            event,
            handled=True,
            message="Intelligence Agent provided strategic recommendations.",
            data={"recommendations": ["Focus on the core Jarvis X deployment", "Minimize distractions"]}
        )


class IntelligencePlugin(Plugin):
    """
    Optional intelligence plugin. Disabled by default.
    Provides timeline analysis, contextual awareness, and strategic recommendations.
    """
    
    @property
    def id(self) -> str:
        return "intelligence"
        
    @property
    def name(self) -> str:
        return "Intelligence Module"
        
    @property
    def version(self) -> str:
        return "0.1.0"
        
    @property
    def enabled_by_default(self) -> bool:
        return False
        
    def setup(self) -> None:
        pass
        
    def get_agents(self) -> list[BaseAgent]:
        return [IntelligenceAgent()]
        
    def get_tools(self) -> dict[str, Any]:
        return {}
