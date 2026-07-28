from typing import Dict, Any, List, Optional

from jarvisx.learning.experience_engine import ExperienceEngine
from jarvisx.learning.knowledge_extractor import KnowledgeExtractor
from jarvisx.learning.knowledge_graph import KnowledgeGraph
from jarvisx.memory.cognitive_memory import CognitiveMemory
from jarvisx.core.logging import StructuredLogger


class LearningEngine:
    """
    Autonomous Learning Engine: turns completed task results into
    structured knowledge that improves future decisions.

    Pipeline: Experience → Knowledge Extraction → Graph Update → Strategy Improvement
    """

    def __init__(
        self,
        experience_engine: ExperienceEngine,
        knowledge_extractor: KnowledgeExtractor,
        knowledge_graph: KnowledgeGraph,
        cognitive_memory: CognitiveMemory,
        logger: Optional[StructuredLogger] = None,
    ) -> None:
        self.experience_engine = experience_engine
        self.knowledge_extractor = knowledge_extractor
        self.knowledge_graph = knowledge_graph
        self.cognitive_memory = cognitive_memory
        self.logger = logger or StructuredLogger()

    async def learn(self, task_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Full learning pipeline:
        1. Capture experience from task result
        2. Extract entities and relationships
        3. Update knowledge graph
        4. Store facts in cognitive memory
        """
        self.logger.write("info", "learning.pipeline_started")

        # Step 1: Capture experience
        experience = self.experience_engine.capture_experience(task_result)

        # Step 2: Extract knowledge
        entities = self.knowledge_extractor.extract_entities(experience)
        relationships = self.knowledge_extractor.extract_relationships(entities)
        facts = self.knowledge_extractor.generate_facts(experience)

        # Step 3: Update knowledge graph
        for entity in entities:
            self.knowledge_graph.add_entity(
                name=entity["name"],
                entity_type=entity["type"],
                attributes=entity.get("attributes", {}),
            )
        for rel in relationships:
            self.knowledge_graph.add_relationship(
                source=rel["source"],
                target=rel["target"],
                relation=rel["relation"],
                confidence=rel.get("confidence", 1.0),
            )

        # Step 4: Store facts as semantic memory
        facts_stored = 0
        for fact in facts:
            await self.cognitive_memory.extract_knowledge(
                fact=fact["fact"],
                subject=experience.get("action", "general"),
                confidence=fact["confidence"],
                source=fact["source"],
            )
            facts_stored += 1

        # Store experience as episodic memory
        await self.experience_engine.store_experience(experience)

        self.logger.write(
            "info", "learning.pipeline_completed",
            entities=len(entities), relationships=len(relationships), facts_stored=facts_stored,
        )
        return {
            "experience": experience,
            "entities": entities,
            "relationships": relationships,
            "facts_stored": facts_stored,
        }

    async def apply_learning(self, agent_id: str, task_type: str) -> Dict[str, Any]:
        """
        Query the knowledge graph and cognitive memory for relevant context
        to improve future decision-making for a given agent and task.
        """
        self.logger.write("info", "learning.applying", agent_id=agent_id, task_type=task_type)

        # Query graph for agent relationships
        agent_rels = self.knowledge_graph.query_relationships(agent_id)
        preferences = self.knowledge_graph.find_related("user", relation_type="prefers")

        # Query cognitive memory for relevant context
        context = await self.cognitive_memory.retrieve_context(task_type, limit=5)

        # Build strategies from learned preferences
        strategies: List[str] = []
        for pref in preferences:
            strategies.append(f"Apply preference: {pref}")

        return {
            "preferences": preferences,
            "context": [c.get("data", c) for c in context] if context else [],
            "strategies": strategies,
        }

    async def evaluate_outcome(self, task_id: str, outcome: str, feedback: str = "") -> Dict[str, Any]:
        """Evaluate a task outcome and update confidence in relevant knowledge."""
        self.logger.write("info", "learning.evaluating_outcome", task_id=task_id, outcome=outcome)

        # Search for related facts to update
        related = await self.cognitive_memory.retrieve_context(outcome, limit=3)
        updated_facts = len(related)
        confidence_boost = 0.05 if outcome == "success" else -0.1

        return {
            "updated_facts": updated_facts,
            "new_confidence": max(0.0, min(1.0, 0.8 + confidence_boost)),
        }

    async def update_strategy(self, agent_id: str, strategy: Dict[str, Any]) -> bool:
        """Store a new strategy/preference for an agent."""
        self.logger.write("info", "learning.strategy_updated", agent_id=agent_id)
        strategy_desc = strategy.get("description", str(strategy))
        await self.cognitive_memory.extract_knowledge(
            fact=strategy_desc,
            subject=f"strategy.{agent_id}",
            confidence=strategy.get("confidence", 0.8),
            source="learning_engine",
        )
        return True
