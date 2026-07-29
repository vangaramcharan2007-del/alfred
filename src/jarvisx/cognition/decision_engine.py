import yaml
from pathlib import Path
from typing import Dict, Any, List

class DecisionEngine:
    def __init__(self, weights_path: str = None):
        self.weights = {
            "capability_match": 0.30,
            "historical_success": 0.20,
            "preference_match": 0.15,
            "task_similarity": 0.10,
            "confidence_score": 0.05,
            "capability_reliability": 0.10,
            "health_score": 0.10
        }
        if weights_path:
            self._load_weights(weights_path)
    
    def _load_weights(self, weights_path: str):
        try:
            with open(weights_path, 'r') as f:
                loaded = yaml.safe_load(f)
                if loaded and "routing_weights" in loaded:
                    self.weights.update(loaded["routing_weights"])
        except Exception:
            pass
            
    def evaluate(self, agent_id: str, context: Dict[str, Any]) -> float:
        # Calculate agent score based on weights and context
        cap = context.get("capability_match", 0.0) * self.weights["capability_match"]
        hist = context.get("historical_success", 0.0) * self.weights["historical_success"]
        pref = context.get("preference_match", 0.0) * self.weights["preference_match"]
        sim = context.get("task_similarity", 0.0) * self.weights["task_similarity"]
        conf = context.get("confidence_score", 0.0) * self.weights["confidence_score"]
        
        cap_rel = context.get("capability_reliability", 0.0) * self.weights.get("capability_reliability", 0.10)
        health = context.get("health_score", 0.0) * self.weights.get("health_score", 0.10)
        
        return cap + hist + pref + sim + conf + cap_rel + health

    def rank_agents(self, capable_agents: List[str], context: Dict[str, Any]) -> List[str]:
        scored = [(agent, self.evaluate(agent, context.get(agent, {}))) for agent in capable_agents]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [agent for agent, score in scored]
