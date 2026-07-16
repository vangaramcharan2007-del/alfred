import asyncio
import logging
from jarvisx.core.planning.planning_engine import PlanningEngine
from jarvisx.core.reflection.reflection_engine import ReflectionEngine
from jarvisx.core.initiative.initiative_engine import InitiativeEngine
from jarvisx.core.memory import ConversationStore, TaskMemory, ContextRebuilder, ContinuityEngine
from jarvisx.core.voice.intent_router import IntentRouter
from jarvisx.core.voice.command_dispatcher import CommandDispatcher

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
        
        self.intent_router = IntentRouter()
        self.command_dispatcher = CommandDispatcher()

    async def process_voice_command(self, text: str) -> str:
        """
        Receives transcribed text, delegates to the low-latency IntentRouter, 
        and routes execution to the appropriate subsystem or OS bridge.
        """
        logger.info(f"Voice Router processing: {text}")
        
        intent_category = self.intent_router.route_intent(text)
        logger.debug(f"Resolved intent category: {intent_category}")
        
        # New Voice-First OS/Control Intents
        if intent_category == "os_control":
            return await self.command_dispatcher.execute_os_command(text)
            
        elif intent_category == "development":
            return await self.command_dispatcher.execute_dev_command(text)
            
        elif intent_category == "browser":
            return await self.command_dispatcher.execute_browser_command(text)
            
        elif intent_category == "interruption":
            return "Command interrupted."
            
        elif intent_category == "handoff":
            return "Handing off to secondary device."

        # Legacy Context / Intelligence Routing
        if intent_category == "continuity":
            if self.continuity_engine.is_resume_intent(text):
                return self.continuity_engine.process_resume()
            return "Resuming context."
            
        elif intent_category == "initiative":
            return self.initiative.process_voice_intent(text)
            
        elif intent_category == "reflection":
            return self.reflection.process_voice_intent(text)
        
        # Default to heavy DAG Planner
        return self.planner.process_voice_intent(text)
