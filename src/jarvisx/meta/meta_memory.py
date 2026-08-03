from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from jarvisx.memory.cognitive_memory import CognitiveMemory
from jarvisx.capabilities.coding.architecture_memory import ArchitectureMemory
from jarvisx.providers.intelligence.provider_history import ProviderHistoryManager
from jarvisx.llm.llm_history import LLMHistoryManager

@dataclass
class EvolutionSnapshot:
    timestamp: float = field(default_factory=time.time)
    registered_capabilities_count: int = 0
    system_confidence: float = 0.95
    milestone: str = ""

class MetaMemory:
    def __init__(
        self,
        cognitive_memory: Optional[CognitiveMemory] = None,
        architecture_memory: Optional[ArchitectureMemory] = None,
        provider_history: Optional[ProviderHistoryManager] = None,
        llm_history: Optional[LLMHistoryManager] = None
    ):
        self.cognitive = cognitive_memory

        self.architecture = architecture_memory or ArchitectureMemory()
        self.provider_history = provider_history or ProviderHistoryManager()
        self.llm_history = llm_history or LLMHistoryManager()
        self.evolution_timeline: List[EvolutionSnapshot] = []

    def record_evolution_step(self, milestone: str, capability_count: int, confidence: float = 0.95) -> EvolutionSnapshot:
        snap = EvolutionSnapshot(
            timestamp=time.time(),
            registered_capabilities_count=capability_count,
            system_confidence=confidence,
            milestone=milestone
        )
        self.evolution_timeline.append(snap)
        return snap

    def get_evolution_summary(self) -> Dict[str, Any]:
        return {
            "total_snapshots": len(self.evolution_timeline),
            "timeline": [
                {
                    "milestone": s.milestone,
                    "capabilities": s.registered_capabilities_count,
                    "confidence": s.system_confidence,
                    "timestamp": s.timestamp
                }
                for s in self.evolution_timeline
            ]
        }
