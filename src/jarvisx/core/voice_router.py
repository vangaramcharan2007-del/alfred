import asyncio
import uuid
import logging
from .planner_engine import PlannerEngine

logger = logging.getLogger(__name__)

class VoiceRouter:
    def __init__(self):
        self.planner = PlannerEngine()

    async def process_voice_command(self, text: str) -> str:
        """
        Receives text from STT, routes to Alfred (Planner), and returns 
        the synthesized TTS response string.
        """
        logger.info(f"Voice Router processing: {text}")
        
        goal_id = str(uuid.uuid4())[:8]
        plan = self.planner.generate_plan(goal_id, text)
        
        if any(task.get("type") == "sw_engineering" for task in plan):
            return "I have planned the implementation and routed it to the workforce. The backend and testing agents are now running."
        else:
            return "I will handle that immediately."
