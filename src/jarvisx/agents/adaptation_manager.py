from typing import Dict, Any, List, Optional

from jarvisx.memory.cognitive_memory import CognitiveMemory
from jarvisx.memory.knowledge_graph import PersonalKnowledgeGraph as KnowledgeGraph
from jarvisx.core.logging import StructuredLogger


class AdaptationManager:
    """
    Allows agents to improve behavior without modifying source code.
    Maintains per-agent adaptation profiles built from learned preferences and feedback.
    """

    def __init__(
        self,
        cognitive_memory: CognitiveMemory,
        knowledge_graph: KnowledgeGraph,
        logger: Optional[StructuredLogger] = None,
    ) -> None:
        self.cognitive_memory = cognitive_memory
        self.knowledge_graph = knowledge_graph
        self.logger = logger or StructuredLogger()
        self._agent_profiles: Dict[str, Dict[str, Any]] = {}

    def _ensure_profile(self, agent_id: str) -> Dict[str, Any]:
        """Get or create an agent profile."""
        if agent_id not in self._agent_profiles:
            self._agent_profiles[agent_id] = {
                "agent_id": agent_id,
                "preferences": {},
                "learned_behaviors": [],
                "adaptation_score": 0.0,
            }
        return self._agent_profiles[agent_id]

    async def adapt_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Query cognitive memory and knowledge graph for preferences related to this agent.
        Build an adaptation profile.
        """
        profile = self._ensure_profile(agent_id)

        # Query knowledge graph for agent relationships
        relationships = self.knowledge_graph.query_relationships(agent_id)
        user_prefs = self.knowledge_graph.find_related("user", relation_type="prefers")

        # Query cognitive memory for agent-specific context
        context = await self.cognitive_memory.retrieve_context(agent_id, limit=5)

        # Build learned behaviors from graph data
        for rel in relationships:
            behavior = f"{rel['relation']}: {rel['target']}" if rel["source"] == agent_id else f"{rel['relation']}: {rel['source']}"
            if behavior not in profile["learned_behaviors"]:
                profile["learned_behaviors"].append(behavior)

        # Apply user preferences
        for pref in user_prefs:
            profile["preferences"][pref] = True

        # Update adaptation score
        profile["adaptation_score"] = min(1.0, len(profile["learned_behaviors"]) * 0.1 + len(profile["preferences"]) * 0.15)

        self.logger.write("info", "adaptation.agent_adapted", agent_id=agent_id, score=profile["adaptation_score"])
        return profile

    async def update_preferences(self, agent_id: str, preference_key: str, preference_value: Any) -> bool:
        """Store a preference for an agent."""
        profile = self._ensure_profile(agent_id)
        profile["preferences"][preference_key] = preference_value
        self.logger.write("info", "adaptation.preference_updated", agent_id=agent_id, key=preference_key)
        return True

    async def apply_feedback(self, agent_id: str, feedback: Dict[str, Any]) -> bool:
        """Apply a feedback result to the agent's profile."""
        profile = self._ensure_profile(agent_id)
        if feedback.get("type") in ("preference", "correction"):
            profile["learned_behaviors"].append(feedback.get("preference", feedback.get("raw", "")))
            profile["adaptation_score"] = min(1.0, profile["adaptation_score"] + 0.1)
            self.logger.write("info", "adaptation.feedback_applied", agent_id=agent_id)
        return True

    async def evaluate_agent(self, agent_id: str) -> Dict[str, Any]:
        """Return performance metrics and adaptation status for an agent."""
        profile = self.get_agent_context(agent_id)
        return {
            "agent_id": agent_id,
            "adaptation_score": profile["adaptation_score"],
            "total_preferences": len(profile["preferences"]),
            "total_behaviors": len(profile["learned_behaviors"]),
            "profile": profile,
        }

    def get_agent_context(self, agent_id: str) -> Dict[str, Any]:
        """Synchronous: returns the current adaptation profile for prompt injection."""
        return self._agent_profiles.get(agent_id, {
            "agent_id": agent_id,
            "preferences": {},
            "learned_behaviors": [],
            "adaptation_score": 0.0,
        })
