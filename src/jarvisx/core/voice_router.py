import asyncio
import uuid
import logging
from jarvisx.core.planning.planning_engine import PlanningEngine
from jarvisx.core.reflection.reflection_engine import ReflectionEngine
from jarvisx.core.initiative.initiative_engine import InitiativeEngine
from jarvisx.core.memory import ConversationStore, TaskMemory, ContextRebuilder, ContinuityEngine

logger = logging.getLogger(__name__)

class VoiceRouter:
    def __init__(self):
        self.planner = PlanningEngine()
        self.reflection = ReflectionEngine()
        self.initiative = InitiativeEngine()
        self.conv_store = ConversationStore()
        self.task_memory = TaskMemory()
        self.context_rebuilder = ContextRebuilder(self.conv_store, self.task_memory)
        self.continuity_engine = ContinuityEngine(self.context_rebuilder)

    async def process_voice_command(self, text: str) -> str:
        """
        Receives text from STT, routes to PlanningEngine, ReflectionEngine, InitiativeEngine, or ContinuityEngine.
        """
        logger.info(f"Voice Router processing: {text}")
        
        # Check Continuity Intents first
        if self.continuity_engine.is_resume_intent(text):
            return self.continuity_engine.process_resume()
            
        intent_lower = text.lower()
        
        # Check Initiative Intents
        initiative_triggers = ["focus on", "attention", "risks", "recommendations", "pending initiatives"]
        if any(trigger in intent_lower for trigger in initiative_triggers):
            return self.initiative.process_voice_intent(text)
            
        # Check Reflection Intents
        reflection_triggers = ["learn", "fail", "optimization", "improve", "performs best"]
        if any(trigger in intent_lower for trigger in reflection_triggers):
            return self.reflection.process_voice_intent(text)
        
        # Route to Planning Engine for all other intents
        return self.planner.process_voice_intent(text)
