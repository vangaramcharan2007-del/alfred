from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class LLMProfile:
    provider_id: str
    model_name: str
    context_window: int = 128000
    latency: float = 0.3
    cost: float = 0.0
    coding_score: float = 0.95
    reasoning_score: float = 0.90
    tool_support: bool = True
    streaming_support: bool = True
    vision_support: bool = False
    offline_support: bool = True
    privacy_level: str = "HIGH"  # HIGH (local), MEDIUM (encrypted API), LOW
    hardware_requirements: Dict[str, Any] = field(default_factory=lambda: {"ram_gb": 8, "vram_gb": 4})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "model_name": self.model_name,
            "context_window": self.context_window,
            "latency": round(self.latency, 3),
            "cost": round(self.cost, 4),
            "coding_score": round(self.coding_score, 2),
            "reasoning_score": round(self.reasoning_score, 2),
            "tool_support": self.tool_support,
            "streaming_support": self.streaming_support,
            "vision_support": self.vision_support,
            "offline_support": self.offline_support,
            "privacy_level": self.privacy_level,
            "hardware_requirements": self.hardware_requirements
        }
