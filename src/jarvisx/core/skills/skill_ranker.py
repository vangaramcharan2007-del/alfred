import datetime
from typing import List, Dict, Any

class SkillRanker:
    """
    Ranks candidate skills based on relevance, success history, permissions, cost, and cooldown.
    """
    def __init__(self):
        # Weights
        self.w_relevance = 0.40
        self.w_history = 0.30
        self.w_permissions = 0.20
        self.w_cost = 0.10

    def rank(self, candidates: List[Dict[str, Any]], available_permissions: List[str]) -> List[Dict[str, Any]]:
        """
        Ranks candidate skills and adds a total score and reasoning.
        """
        ranked = []
        now = datetime.datetime.utcnow()

        for candidate in candidates:
            metadata = candidate["metadata"]
            relevance_score = candidate.get("relevance_score", 0.5)
            
            # History score: heavily rely on historical success rate, fallback to base
            history_score = metadata.get("historical_success_rate", metadata.get("base_success_rate", 0.5))
            
            # Permission score: penalty if we lack required permissions
            req_perms = metadata.get("required_permissions", [])
            has_all_perms = all(p in available_permissions for p in req_perms)
            permission_score = 1.0 if has_all_perms else 0.0
            
            # Cost score: inverse of cost ('low' = 1.0, 'medium' = 0.5, 'high' = 0.1)
            cost_mapping = {"low": 1.0, "medium": 0.5, "high": 0.1}
            cost_score = cost_mapping.get(metadata.get("cost", "medium"), 0.5)
            
            # Cooldown penalty: If used recently, slightly reduce score to avoid loops
            cooldown_penalty = 0.0
            last_used_str = metadata.get("last_used")
            if last_used_str:
                try:
                    # Depending on how sqlite returns datetime. 
                    # If it's a string from CURRENT_TIMESTAMP, it might be 'YYYY-MM-DD HH:MM:SS'
                    # ISO format handles many cases
                    if isinstance(last_used_str, str):
                        last_used = datetime.datetime.fromisoformat(last_used_str.replace(" ", "T"))
                        diff = (now - last_used).total_seconds()
                        if diff < 60: # Used within last minute
                            cooldown_penalty = 0.2
                        elif diff < 300: # Used within last 5 minutes
                            cooldown_penalty = 0.1
                except Exception:
                    pass

            total_score = (
                (relevance_score * self.w_relevance) +
                (history_score * self.w_history) +
                (permission_score * self.w_permissions) +
                (cost_score * self.w_cost)
            ) - cooldown_penalty
            
            # Ensure score is within 0-1
            total_score = max(0.0, min(1.0, total_score))
            
            reason = (
                f"Relevance: {relevance_score:.2f}, History: {history_score:.2f}, "
                f"Perms: {permission_score:.2f}, Cost: {cost_score:.2f}"
            )
            if cooldown_penalty > 0:
                reason += f", Cooldown Penalty: -{cooldown_penalty:.2f}"

            candidate_copy = dict(candidate)
            candidate_copy["score"] = total_score
            candidate_copy["reason"] = reason
            ranked.append(candidate_copy)

        # Sort descending by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked
