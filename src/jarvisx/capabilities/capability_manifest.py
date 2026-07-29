from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class CapabilityManifest:
    name: str
    version: str
    api_version: str
    description: str
    category: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    confidence: float = 1.0
