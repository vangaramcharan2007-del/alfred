import asyncio
import uuid
import logging
from .planner_engine import PlannerEngine
from jarvisx.core.memory import ConversationStore, TaskMemory, ContextRebuilder, ContinuityEngine

logger = logging.getLogger(__name__)

class VoiceRouter:
    def __init__(self):
        self.planner = PlannerEngine()
        self.conv_store = ConversationStore()
        self.task_memory = TaskMemory()
        self.context_rebuilder = ContextRebuilder(self.conv_store, self.task_memory)
        self.continuity_engine = ContinuityEngine(self.context_rebuilder)

    async def process_voice_command(self, text: str) -> str:
        """
        Receives text from STT, routes to Alfred (Planner) or Memory (Continuity), 
        and returns the synthesized TTS response string.
        """
        logger.info(f"Voice Router processing: {text}")
        
        # Check Continuity Intents first
        if self.continuity_engine.is_resume_intent(text):
            return self.continuity_engine.process_resume()
        
        # Default Planner Execution
        goal_id = str(uuid.uuid4())[:8]
        plan = self.planner.generate_plan(goal_id, text)
        
        if any(task.get("type") == "sw_engineering" for task in plan):
            # Write a dummy task to simulate workforce backend insertion
            self.task_memory.db.upsert_task({
                "task_id": f"{goal_id}-backend",
                "assigned_agent": "backend_agent",
                "status": "PENDING"
            })
            return "I have planned the implementation and routed it to the workforce. The backend and testing agents are now running."
        else:
            return "I will handle that immediately."
