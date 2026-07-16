import asyncio
import uuid
import logging
from jarvisx.core.planning.planning_engine import PlanningEngine
from jarvisx.core.memory import ConversationStore, TaskMemory, ContextRebuilder, ContinuityEngine

logger = logging.getLogger(__name__)

class VoiceRouter:
    def __init__(self):
        self.planner = PlanningEngine()
        self.conv_store = ConversationStore()
        self.task_memory = TaskMemory()
        self.context_rebuilder = ContextRebuilder(self.conv_store, self.task_memory)
        self.continuity_engine = ContinuityEngine(self.context_rebuilder)

    async def process_voice_command(self, text: str) -> str:
        """
        Receives text from STT, routes to PlanningEngine or ContinuityEngine, 
        and returns the synthesized TTS response string.
        """
        logger.info(f"Voice Router processing: {text}")
        
        # Check Continuity Intents first
        if self.continuity_engine.is_resume_intent(text):
            return self.continuity_engine.process_resume()
        
        # Route to Planning Engine for all other intents
        return self.planner.process_voice_intent(text)
