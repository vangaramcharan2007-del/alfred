import logging
from typing import Dict, Any, List, Optional
from .context_retriever import ContextRetriever
from .decision_engine import DecisionEngine
from .outcome_tracker import OutcomeTracker
from .confidence_manager import ConfidenceManager
from .learning_explanation import LearningExplanation
from .metrics import metrics
from .decision_record import DecisionRecord

from jarvisx.core.logging import StructuredLogger

logger = StructuredLogger()

class CognitiveRuntime:
    def __init__(self, config_path: str = None):
        self.context_retriever = ContextRetriever()
        self.decision_engine = DecisionEngine(config_path)
        self.outcome_tracker = OutcomeTracker(metrics)
        self.confidence_manager = ConfidenceManager()
        self.explanation_generator = LearningExplanation()
        self.metrics = metrics
        
    async def route_task(self, task: str, capable_agents: List[str], overrides: Dict[str, Any] = None) -> str:
        if overrides and overrides.get("manual_override"):
            logger.write("info", "Manual override specified. Bypassing cognitive routing.", event="cognitive_runtime.manual_override")
            return overrides.get("preferred_agent", capable_agents[0] if capable_agents else None)
            
        context = await self.context_retriever.retrieve(task)
        ranked = self.decision_engine.rank_agents(capable_agents, context)
        
        if not ranked:
            return None
            
        selected = ranked[0]
        reasons = [f"highest capability match in context"]
        explanation = self.explanation_generator.generate(selected, reasons)
        
        record = DecisionRecord(
            task=task,
            selected_agent=selected,
            alternatives=ranked[1:],
            reasons=reasons,
            confidence=self.confidence_manager.get_confidence(selected)
        )
        
        logger.write("info", f"Routed task to {selected}: {explanation}", event="cognitive_runtime.routed_task", selected=selected, explanation=explanation)
        return selected

    def track_outcome(self, task: str, agent: str, success: bool, duration: float):
        self.outcome_tracker.record_outcome(task, agent, success, duration)
        self.confidence_manager.update_confidence(agent, success)
