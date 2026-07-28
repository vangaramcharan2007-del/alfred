import time
from typing import Dict, Any, List, Optional
from jarvisx.core.logging import StructuredLogger
from jarvisx.memory.cognitive_memory import CognitiveMemory


class ExperienceEngine:
    """
    Converts completed tasks into structured experiences.
    Sources: completed tasks, agent results, user feedback, failures, recovery events.
    """

    def __init__(self, cognitive_memory: CognitiveMemory, logger: Optional[StructuredLogger] = None) -> None:
        self.memory = cognitive_memory
        self.logger = logger or StructuredLogger()

    def capture_experience(self, task_result: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a completed task result into a structured experience."""
        experience = {
            "type": task_result.get("type", "general_task"),
            "action": task_result.get("action", "unknown"),
            "result": task_result.get("result", "unknown"),
            "agent": task_result.get("agent", "system"),
            "preferences_detected": task_result.get("preferences_detected", []),
            "timestamp": time.time(),
        }
        self.logger.write("info", "experience.captured", agent=experience["agent"], action=experience["action"])
        return experience

    def summarize_experience(self, experience: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the experience."""
        agent = experience.get("agent", "unknown")
        action = experience.get("action", "unknown")
        result = experience.get("result", "unknown")
        prefs = experience.get("preferences_detected", [])
        summary = f"Agent '{agent}' performed '{action}' with result: {result}."
        if prefs:
            summary += f" Detected preferences: {', '.join(prefs)}."
        return summary

    def extract_patterns(self, experiences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find patterns across multiple experiences (e.g. repeated preferences)."""
        preference_counts: Dict[str, int] = {}
        action_counts: Dict[str, int] = {}

        for exp in experiences:
            for pref in exp.get("preferences_detected", []):
                preference_counts[pref] = preference_counts.get(pref, 0) + 1
            action = exp.get("action")
            if action:
                action_counts[action] = action_counts.get(action, 0) + 1

        patterns: List[Dict[str, Any]] = []
        for pref, count in preference_counts.items():
            if count > 1:
                patterns.append({
                    "pattern_type": "repeated_preference",
                    "value": pref,
                    "occurrences": count,
                    "confidence": min(1.0, 0.5 + count * 0.15),
                })
        for action, count in action_counts.items():
            if count > 1:
                patterns.append({
                    "pattern_type": "frequent_action",
                    "value": action,
                    "occurrences": count,
                    "confidence": min(1.0, 0.4 + count * 0.1),
                })

        self.logger.write("info", "experience.patterns_extracted", count=len(patterns))
        return patterns

    async def store_experience(self, experience: Dict[str, Any]) -> str:
        """Store experience into CognitiveMemory as episodic memory."""
        summary = self.summarize_experience(experience)
        mem_id = await self.memory.store_experience(
            fact=summary,
            confidence=1.0,
            source="experience_engine",
        )
        self.logger.write("info", "experience.stored", memory_id=mem_id)
        return mem_id
