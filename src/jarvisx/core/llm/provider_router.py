import logging
from .confidence_estimator import ConfidenceEstimator
from .escalation_engine import EscalationEngine
from .cost_tracker import CostTracker
from .token_budget_manager import TokenBudgetManager

logger = logging.getLogger(__name__)

class ProviderRouter:
    """
    Tiered intelligence routing:
    Tier 1 - Local Inference (Ollama)
    Tier 2 - Medium Complexity (Gemini)
    Tier 3 - Premium Intelligence (OpenAI / Claude)
    """
    def __init__(self):
        self.confidence_estimator = ConfidenceEstimator()
        self.escalation = EscalationEngine(threshold=0.7)
        self.cost = CostTracker()
        self.budget = TokenBudgetManager()

    def route_request(self, prompt: str) -> str:
        """
        Routes the prompt to the appropriate tier based on confidence and complexity.
        """
        optimized_prompt = self.budget.optimize_context(prompt)
        confidence = self.confidence_estimator.estimate(optimized_prompt)
        
        # Simulated token count
        estimated_tokens = len(optimized_prompt) // 4
        self.budget.add_tokens(estimated_tokens)

        if not self.escalation.requires_escalation(confidence):
            logger.info("Routing to Tier 1 (Ollama).")
            return f"[Ollama] Handled locally with high confidence ({confidence:.2f})"
            
        elif confidence >= 0.4:
            logger.info("Routing to Tier 2 (Gemini).")
            self.cost.track_cost("Gemini", estimated_tokens)
            return f"[Gemini] Handled in cloud due to medium complexity ({confidence:.2f})"
            
        else:
            logger.info("Routing to Tier 3 (OpenAI/Claude).")
            self.cost.track_cost("OpenAI", estimated_tokens)
            return f"[OpenAI] Handled by premium model due to high complexity ({confidence:.2f})"
