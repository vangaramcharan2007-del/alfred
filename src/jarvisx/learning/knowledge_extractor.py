from typing import Dict, Any, List, Optional
from jarvisx.core.logging import StructuredLogger
from jarvisx.memory.cognitive_memory import CognitiveMemory


class KnowledgeExtractor:
    """
    Converts experiences into structured knowledge: entities, relationships, and facts.
    """

    def __init__(self, cognitive_memory: CognitiveMemory, logger: Optional[StructuredLogger] = None) -> None:
        self.memory = cognitive_memory
        self.logger = logger or StructuredLogger()

    def extract_entities(self, experience: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract entities like {name, type, attributes} from an experience."""
        entities: List[Dict[str, Any]] = []

        agent = experience.get("agent")
        if agent:
            entities.append({"name": agent, "type": "agent", "attributes": {}})

        action = experience.get("action")
        if action and action != "unknown":
            entities.append({"name": action, "type": "action", "attributes": {}})

        for pref in experience.get("preferences_detected", []):
            entities.append({"name": pref, "type": "preference", "attributes": {}})

        exp_type = experience.get("type")
        if exp_type and exp_type not in ("unknown", "general_task"):
            entities.append({"name": exp_type, "type": "task_type", "attributes": {}})

        self.logger.write("info", "knowledge.entities_extracted", count=len(entities))
        return entities

    def extract_relationships(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relationships between entities."""
        relationships: List[Dict[str, Any]] = []
        agents = [e for e in entities if e["type"] == "agent"]
        actions = [e for e in entities if e["type"] == "action"]
        preferences = [e for e in entities if e["type"] == "preference"]

        for agent in agents:
            for action in actions:
                relationships.append({
                    "source": agent["name"],
                    "target": action["name"],
                    "relation": "performed",
                    "confidence": 1.0,
                })
            for pref in preferences:
                relationships.append({
                    "source": "user",
                    "target": pref["name"],
                    "relation": "prefers",
                    "confidence": 0.85,
                })

        self.logger.write("info", "knowledge.relationships_extracted", count=len(relationships))
        return relationships

    def generate_facts(self, experience: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fact dicts with {fact, confidence, source}."""
        facts: List[Dict[str, Any]] = []
        agent = experience.get("agent", "unknown")
        action = experience.get("action", "unknown")
        result = experience.get("result", "unknown")

        if agent != "unknown" and action != "unknown":
            facts.append({
                "fact": f"{agent} performed {action} with result: {result}",
                "confidence": self.calculate_confidence("task_completion", 1),
                "source": "experience",
            })

        for pref in experience.get("preferences_detected", []):
            facts.append({
                "fact": f"User prefers {pref}",
                "confidence": self.calculate_confidence("preference", 1),
                "source": "feedback",
            })

        self.logger.write("info", "knowledge.facts_generated", count=len(facts))
        return facts

    def calculate_confidence(self, source: str, repetitions: int) -> float:
        """Calculate confidence based on source type and repetition count."""
        base_map = {
            "task_completion": 0.9,
            "preference": 0.75,
            "feedback": 0.8,
            "inference": 0.6,
        }
        base = base_map.get(source, 0.5)
        boost = min(0.2, repetitions * 0.05)
        return min(1.0, base + boost)
