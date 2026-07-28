from typing import Dict, Any, Optional

from jarvisx.memory.cognitive_memory import CognitiveMemory
from jarvisx.learning.knowledge_graph import KnowledgeGraph
from jarvisx.core.logging import StructuredLogger


class FeedbackEngine:
    """
    Learns from user corrections and preferences.
    Classifies feedback, extracts preferences, and stores them in cognitive memory.
    """

    CORRECTION_KEYWORDS = ("no", "wrong", "not", "instead", "actually", "correct")
    PREFERENCE_KEYWORDS = ("prefer", "like", "want", "love", "style", "shorter", "longer", "examples")
    POSITIVE_KEYWORDS = ("good", "great", "perfect", "thanks", "excellent", "nice")
    NEGATIVE_KEYWORDS = ("bad", "terrible", "hate", "awful", "slow", "worse")

    def __init__(
        self,
        cognitive_memory: CognitiveMemory,
        knowledge_graph: KnowledgeGraph,
        logger: Optional[StructuredLogger] = None,
    ) -> None:
        self.cognitive_memory = cognitive_memory
        self.knowledge_graph = knowledge_graph
        self.logger = logger or StructuredLogger()

    def classify_feedback(self, feedback_text: str) -> str:
        """Classify feedback into: 'correction', 'preference', 'positive', 'negative', or 'unknown'."""
        text = feedback_text.lower()
        if any(kw in text for kw in self.CORRECTION_KEYWORDS):
            return "correction"
        if any(kw in text for kw in self.PREFERENCE_KEYWORDS):
            return "preference"
        if any(kw in text for kw in self.POSITIVE_KEYWORDS):
            return "positive"
        if any(kw in text for kw in self.NEGATIVE_KEYWORDS):
            return "negative"
        return "unknown"

    async def capture_feedback(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze user feedback text and extract preferences."""
        feedback_type = self.classify_feedback(user_input)
        preference = ""
        confidence = 0.7

        if feedback_type == "correction":
            preference = user_input
            confidence = 0.9
        elif feedback_type == "preference":
            preference = user_input
            confidence = 0.85
        elif feedback_type == "positive":
            confidence = 0.6
        elif feedback_type == "negative":
            preference = user_input
            confidence = 0.8

        result = {
            "type": feedback_type,
            "preference": preference,
            "confidence": confidence,
            "raw": user_input,
        }
        self.logger.write("info", "feedback.captured", feedback_type=feedback_type)
        return result

    async def update_memory(self, feedback: Dict[str, Any]) -> str:
        """Store classified feedback as semantic memory. Returns memory ID."""
        preference = feedback.get("preference", feedback.get("raw", ""))
        feedback_type = feedback.get("type", "unknown")
        confidence = feedback.get("confidence", 0.7)

        mem_id = await self.cognitive_memory.extract_knowledge(
            fact=preference,
            subject=f"user.feedback.{feedback_type}",
            confidence=confidence,
            source="feedback",
        )

        # Also store in knowledge graph if it's actionable
        if feedback_type in ("correction", "preference"):
            self.knowledge_graph.add_entity("user", "user")
            self.knowledge_graph.add_entity(preference, "preference")
            self.knowledge_graph.add_relationship("user", preference, "prefers", confidence)

        self.logger.write("info", "feedback.stored", memory_id=mem_id, feedback_type=feedback_type)
        return mem_id
