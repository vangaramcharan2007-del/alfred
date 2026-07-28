from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from jarvisx.core.logging import StructuredLogger

@dataclass
class AgentManifest:
    id: str
    name: str
    role: str
    capabilities: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    input_types: List[str] = field(default_factory=list)
    output_types: List[str] = field(default_factory=list)
    priority: int = 0
    resource_requirements: Dict[str, bool] = field(default_factory=dict)
    status: str = "active"

class CapabilityRegistry:
    """
    Higher intelligence layer that sits above AgentRegistry.
    Answers: "Which agent can solve this problem?" based on capabilities.
    """
    
    def __init__(self, logger: Optional[StructuredLogger] = None):
        self._manifests: Dict[str, AgentManifest] = {}
        self.logger = logger or StructuredLogger()
        self._load_manifests()
        
    def _load_manifests(self) -> None:
        """Automatically load agent manifests from src/jarvisx/agents/manifests/"""
        manifests_dir = Path(__file__).parent / "manifests"
        if not manifests_dir.exists():
            return
            
        for file in manifests_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    manifest = AgentManifest(**data)
                    self.register_agent(manifest)
            except Exception as e:
                self.logger.write("warning", "capability.manifest_load_failed", file=str(file), error=str(e))

    def register_agent(self, manifest: AgentManifest) -> None:
        """Register a new agent capability manifest."""
        self._manifests[manifest.id] = manifest
        self.logger.write("info", "capability.agent_registered", agent_id=manifest.id)

    def unregister_agent(self, agent_id: str) -> None:
        """Remove an agent from the capability registry."""
        if agent_id in self._manifests:
            del self._manifests[agent_id]
            self.logger.write("info", "capability.agent_unregistered", agent_id=agent_id)

    def discover_capability(self, required_capabilities: List[str]) -> List[Dict[str, Any]]:
        """
        Given a list of required capabilities, discover agents that match.
        Returns a list of dicts with agent ids and confidence scores.
        """
        results = []
        for agent_id, manifest in self._manifests.items():
            if manifest.status != "active":
                continue
                
            match_count = sum(1 for cap in required_capabilities if cap.lower() in [c.lower() for c in manifest.capabilities])
            if match_count > 0:
                # Basic confidence score: percentage of required capabilities met + small priority bump
                base_confidence = match_count / len(required_capabilities)
                priority_bump = min(0.05, manifest.priority * 0.005)
                confidence = min(0.99, base_confidence + priority_bump)
                
                results.append({
                    "agent": agent_id,
                    "confidence": round(confidence, 2)
                })
                
        return sorted(results, key=lambda x: x["confidence"], reverse=True)

    def rank_agents(self, required_capabilities: List[str]) -> List[str]:
        """Returns just a ranked list of agent IDs based on capabilities."""
        discovered = self.discover_capability(required_capabilities)
        return [res["agent"] for res in discovered]

    def list_agents(self) -> List[AgentManifest]:
        """List all known agent manifests."""
        return list(self._manifests.values())

    def update_capabilities(self, agent_id: str, new_capabilities: List[str]) -> None:
        """Dynamically update an agent's capabilities in memory."""
        if agent_id in self._manifests:
            self._manifests[agent_id].capabilities = new_capabilities
            self.logger.write("info", "capability.agent_updated", agent_id=agent_id)
