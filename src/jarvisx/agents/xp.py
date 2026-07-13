from typing import Mapping
from jarvisx.agents.base import BaseAgent, AgentResponse
from jarvisx.core.events import Event


def _message(event: Event) -> str:
    return str(event.payload.get("message", "")) if isinstance(event.payload, Mapping) else str(event.payload)


class XPAgent(BaseAgent):
    agent_id = "xp"
    role = "Gamification and progress tracker"
    expertise = ("xp", "levels", "streaks", "rewards")
    tone = "encouraging and enthusiastic"
    personality = "game master"
    capabilities = ("xp.award", "xp.stats")

    async def handle(self, event: Event) -> AgentResponse:
        xp_tool = self.tools.get("xp")
        if not xp_tool:
            return self._response(
                event,
                handled=False,
                message="XPAgent requires the 'xp' tool to operate."
            )

        text = _message(event).lower()
        
        if "award" in text or "complete" in text or "finish" in text:
            # Simple heuristic for mission type
            mission_type = "daily_mission"
            if "boss" in text:
                mission_type = "boss_fight"
            elif "main" in text:
                mission_type = "main_quest"
            elif "side" in text:
                mission_type = "side_quest"
                
            result = xp_tool.award_xp(mission_type, trace_id=event.trace_id)
            if not result.success:
                return self._response(event, handled=False, message="Failed to award XP.")
                
            data = result.data
            msg = f"Awesome! You completed a {mission_type} and earned {data['gained']} XP. Total: {data['new_total']} XP."
            if data["leveled_up"]:
                msg += f" 🎉 LEVEL UP! You are now Level {data['level']}!"
                
            return self._response(event, handled=True, message=msg, data=data)
            
        elif "stats" in text or "level" in text or "xp" in text:
            result = xp_tool.get_stats(trace_id=event.trace_id)
            if not result.success:
                return self._response(event, handled=False, message="Could not retrieve XP stats.")
                
            data = result.data
            msg = f"You are currently Level {data.get('level', 1)} with {data.get('xp', 0)} XP and {data.get('credits', 0)} credits. Streak: {data.get('streak', 0)} days."
            return self._response(event, handled=True, message=msg, data=data)

        return self._response(
            event,
            handled=False,
            message="I can track your XP stats and award points for completed missions."
        )
