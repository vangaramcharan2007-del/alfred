import logging
from .initiative_store import InitiativeStore
from .priority_evaluator import PriorityEvaluator

logger = logging.getLogger(__name__)

class ProactiveTaskGenerator:
    """
    Transforms observations into formal recommendations and tasks.
    """
    def __init__(self, store: InitiativeStore, evaluator: PriorityEvaluator):
        self.store = store
        self.evaluator = evaluator

    def generate_task_from_observation(self, obs_id: str, category: str, details: dict):
        if category == "opportunity" and "days_stalled" in details:
            # High priority
            priority = self.evaluator.evaluate(impact=0.8, confidence=0.9)
            rec = "Authentication deployment is blocked by testing failures. Recommendation: Assign additional testing workers and prioritize testing tasks."
            self.store.add_recommendation(obs_id, rec, priority)
            logger.info(f"Generated task recommendation for stalled objective.")
            
        elif category == "risk" and "deadline_risk" in details.get("risk_type", ""):
            priority = self.evaluator.evaluate(impact=0.9, confidence=0.8)
            rec = details.get("reason", "High risk detected. Allocate more resources.")
            self.store.add_recommendation(obs_id, rec, priority)
