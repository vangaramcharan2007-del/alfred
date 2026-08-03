import time
import uuid
from typing import Dict, Any, List, Optional
from jarvisx.core.logging import StructuredLogger
from jarvisx.memory.providers.memory_provider import MemoryProvider

class CognitiveMemory:
    """
    Transforms raw memory into structured knowledge.
    Supports Episodic, Semantic, and Procedural memory storage and retrieval.
    """
    def __init__(self, provider: MemoryProvider, logger: Optional[StructuredLogger] = None):
        self.provider = provider
        self.logger = logger or StructuredLogger()

    def _generate_id(self, memory_type: str) -> str:
        return f"mem_{memory_type}_{uuid.uuid4().hex[:8]}"

    async def store_experience(self, fact: str, confidence: float = 1.0, source: str = "observation") -> str:
        """Store episodic memory (what happened)."""
        mem_id = self._generate_id("episodic")
        record = {
            "type": "episodic",
            "fact": fact,
            "confidence": confidence,
            "source": source
        }
        await self.provider.save(mem_id, record)
        self.logger.write("info", "cognitive_memory.stored", type="episodic", fact=fact)
        return mem_id

    async def extract_knowledge(self, fact: str, subject: str, confidence: float = 1.0, source: str = "inference") -> str:
        """Store semantic memory (what is known, preferences, facts)."""
        mem_id = self._generate_id("semantic")
        record = {
            "type": "semantic",
            "subject": subject,
            "fact": fact,
            "confidence": confidence,
            "source": source
        }
        await self.provider.save(mem_id, record)
        self.logger.write("info", "cognitive_memory.stored", type="semantic", subject=subject)
        return mem_id
        
    async def build_relationships(self, workflow: str, steps: List[str], confidence: float = 1.0) -> str:
        """Store procedural memory (how to do something)."""
        mem_id = self._generate_id("procedural")
        record = {
            "type": "procedural",
            "workflow": workflow,
            "steps": steps,
            "confidence": confidence,
            "source": "observation"
        }
        await self.provider.save(mem_id, record)
        self.logger.write("info", "cognitive_memory.stored", type="procedural", workflow=workflow)
        return mem_id

    async def retrieve_context(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search across all memory categories for relevant context."""
        results = await self.provider.search(query, limit=limit)
        self.logger.write("debug", "cognitive_memory.retrieved", query=query, count=len(results))
        return results

    async def forget_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        success = await self.provider.delete(memory_id)
        if success:
            self.logger.write("info", "cognitive_memory.forgotten", memory_id=memory_id)
        return success

    async def store_coding_experience(self, framework: str, task: str, solution_pattern: str) -> str:
        """Store coding procedural experience for ExperienceEngine and coding capability."""
        return await self.build_relationships(
            workflow=f"coding_pattern_{framework}",
            steps=[task, solution_pattern],
            confidence=1.0
        )

    async def query_framework_patterns(self, framework: str) -> List[Dict[str, Any]]:
        """Retrieve stored coding patterns for a given framework."""
        return await self.retrieve_context(f"coding_pattern_{framework}")

    async def store_repair_experience(self, error_type: str, failing_code: str, fix_applied: str) -> str:
        """Store automated self-repair experience for future debugging sessions."""
        return await self.build_relationships(
            workflow=f"repair_pattern_{error_type}",
            steps=[failing_code, fix_applied],
            confidence=1.0
        )

    async def query_repair_patterns(self, error_type: str) -> List[Dict[str, Any]]:
        """Retrieve stored repair patterns for a given error type."""
        return await self.retrieve_context(f"repair_pattern_{error_type}")


