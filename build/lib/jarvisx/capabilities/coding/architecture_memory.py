from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from jarvisx.memory.cognitive_memory import CognitiveMemory

class ArchitectureMemory:
    def __init__(self, cognitive_memory: Optional[CognitiveMemory] = None):
        self.cognitive_memory = cognitive_memory
        # Fallback local in-memory store if cognitive memory provider is not wired
        self.local_patterns: Dict[str, Dict[str, Any]] = {}

    async def store_architecture_pattern(self, pattern_name: str, details: Dict[str, Any]) -> str:
        self.local_patterns[pattern_name] = details
        if self.cognitive_memory:
            try:
                fact_str = f"Architecture pattern '{pattern_name}': {details}"
                return await self.cognitive_memory.extract_knowledge(
                    fact=fact_str,
                    subject=f"arch_pattern_{pattern_name}",
                    confidence=1.0,
                    source="architecture_memory"
                )
            except Exception:
                pass
        return f"arch_mem_{pattern_name}"

    async def query_architecture_context(self, query: str) -> List[Dict[str, Any]]:
        results = []
        q_lower = query.lower()

        # Check local pattern store
        for name, details in self.local_patterns.items():
            if q_lower in name.lower() or any(q_lower in str(v).lower() for v in details.values()):
                results.append({
                    "pattern_name": name,
                    "details": details,
                    "source": "local_architecture_memory"
                })

        if self.cognitive_memory:
            try:
                mem_results = await self.cognitive_memory.retrieve_context(f"arch_pattern_{query}")
                for r in mem_results:
                    results.append({
                        "pattern_name": r.get("subject", query),
                        "details": r,
                        "source": "cognitive_memory"
                    })
            except Exception:
                pass

        return results
