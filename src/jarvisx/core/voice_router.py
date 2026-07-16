import asyncio
import uuid
import logging
from jarvisx.core.planning.planning_engine import PlanningEngine
from jarvisx.core.reflection.reflection_engine import ReflectionEngine
from jarvisx.core.memory import ConversationStore, TaskMemory, ContextRebuilder, ContinuityEngine

logger = logging.getLogger(__name__)

class VoiceRouter:
    def __init__(self):
        self.planner = PlanningEngine()
        self.reflection = ReflectionEngine()
        self.conv_store = ConversationStore()
        self.task_memory = TaskMemory()
        self.context_rebuilder = ContextRebuilder(self.conv_store, self.task_memory)
        self.continuity_engine = ContinuityEngine(self.context_rebuilder)

    async def process_voice_command(self, text: str) -> str:
        """
        Receives text from STT, routes to PlanningEngine, ReflectionEngine, or ContinuityEngine, 
        and returns the synthesized TTS response string.
        """
        logger.info(f"Voice Router processing: {text}")
        
        # Check Continuity Intents first
        if self.continuity_engine.is_resume_intent(text):
            return self.continuity_engine.process_resume()
            
        # Check Reflection Intents
        intent_lower = text.lower()
        reflection_triggers = ["learn", "fail", "optimization", "improve", "performs best"]
        if any(trigger in intent_lower for trigger in reflection_triggers):
            return self.reflection.process_voice_intent(text)
        
        # Route to Planning Engine for all other intents
        return self.planner.process_voice_intent(text)
