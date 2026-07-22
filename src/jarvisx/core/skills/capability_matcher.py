import re
from typing import List, Dict, Any

# We assume OmniRouterClient is available for LLM classification if needed
from jarvisx.core.llm_router import OmniRouterClient
from jarvisx.core.model_policy import ModelPolicy

class CapabilityMatcher:
    """
    Evaluates mission intent against available skills to find candidates.
    Uses a hybrid approach: rules -> tags -> LLM fallback.
    """
    def __init__(self, context):
        self.context = context
        self.router = OmniRouterClient()
        self.policy = ModelPolicy()
        
    async def match(self, task_description: str, task_type: str = "") -> List[Dict[str, Any]]:
        """
        Returns a list of candidate skills that might fulfill the task_description.
        Each candidate has {'metadata': {...}, 'relevance_score': float, 'match_reason': str}
        """
        candidates = []
        skills_metadata = self.context.get_available_skills_metadata()
        
        task_lower = task_description.lower()
        
        for meta in skills_metadata:
            candidate = {
                "metadata": meta,
                "relevance_score": 0.0,
                "match_reason": "none"
            }
            
            name = meta["name"].lower()
            category = meta["category"].lower()
            tags = [t.lower() for t in meta.get("tags", [])]
            
            # 1. Rule / Keyword matching (High confidence)
            if name in task_lower or any(word in task_lower for word in name.split()):
                candidate["relevance_score"] = max(candidate["relevance_score"], 0.9)
                candidate["match_reason"] = "Name keyword match"
                
            # 2. Tag / Category matching (Medium confidence)
            matched_tags = [t for t in tags if t in task_lower]
            if matched_tags:
                candidate["relevance_score"] = max(candidate["relevance_score"], 0.7 + (0.05 * len(matched_tags)))
                candidate["match_reason"] = f"Tag match: {', '.join(matched_tags)}"
            elif category in task_lower:
                candidate["relevance_score"] = max(candidate["relevance_score"], 0.6)
                candidate["match_reason"] = f"Category match: {category}"
                
            # 3. Workflow history matching
            # If this skill was previously successful for this task type
            # (We rely on historical success rate built into the metadata from context)
            if meta.get("historical_success_rate", 0) > 0.8 and task_type and task_type.lower() == category:
                candidate["relevance_score"] = max(candidate["relevance_score"], 0.85)
                candidate["match_reason"] = "Strong historical success for task type"

            candidates.append(candidate)
            
        # 4. LLM Fallback
        # If the best candidate is below a confidence threshold, use LLM
        best_candidate = max(candidates, key=lambda x: x["relevance_score"]) if candidates else None
        
        if not best_candidate or best_candidate["relevance_score"] < 0.6:
            # LLM Classification
            skill_descriptions = "\n".join([f"- {m['name']}: {m['description']} (Tags: {', '.join(m.get('tags', []))})" for m in skills_metadata])
            
            prompt = (
                "You are an intelligent capability selector. "
                "Analyze the following task and select the best skill from the available list.\n"
                f"Task: {task_description}\n\n"
                f"Available Skills:\n{skill_descriptions}\n\n"
                "Return only the exact name of the selected skill."
            )
            
            try:
                response = await self.router.execute(
                    prompt=prompt,
                    policy=self.policy
                )
                llm_skill = response.strip()
                
                # Find the matched skill in candidates
                for c in candidates:
                    if c["metadata"]["name"].lower() == llm_skill.lower():
                        c["relevance_score"] = 0.8  # LLM confident match
                        c["match_reason"] = "LLM selected capability"
            except Exception:
                pass # Fallback to existing rules if LLM fails

        # Filter out 0 relevance
        valid_candidates = [c for c in candidates if c["relevance_score"] > 0]
        return valid_candidates
