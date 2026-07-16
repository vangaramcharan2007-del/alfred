import logging
from .recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

class AdaptationEngine:
    """
    Connects reflection insights directly into the Strategic Planner to adapt future behaviors.
    """
    def __init__(self, recommender: RecommendationEngine):
        self.recommender = recommender

    def apply_adaptations_to_plan(self, raw_plan: dict) -> dict:
        """
        Modifies a newly generated DAG plan based on historical recommendations.
        """
        recommendations = self.recommender.generate_recommendations()
        
        # Example heuristic adaptation
        # If we have a recommendation about testing, inject a testing milestone earlier.
        needs_early_testing = any("testing" in r.lower() for r in recommendations)
        
        if needs_early_testing and "milestones" in raw_plan:
            # Shift testing up or inject a mock-testing phase
            raw_plan["milestones"].insert(0, {"name": "Test Driven Development Setup"})
            
        return raw_plan
