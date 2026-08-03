from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.meta.capability_graph import CapabilityGraph, CapabilityNode
from jarvisx.meta.capability_reasoner import CapabilityReasoner

class CapabilityIntrospector:
    def __init__(self, registry: Optional[CapabilityRegistry] = None):
        self.registry = registry or CapabilityRegistry()
        self.graph = CapabilityGraph()
        self.reasoner = CapabilityReasoner(capability_graph=self.graph)

    def scan_registered_capabilities(self) -> CapabilityGraph:
        descriptors = self.registry.list_capabilities()

        for desc in descriptors:
            node = CapabilityNode(
                id=desc.id,
                name=desc.name,
                category=desc.category,
                actions=desc.supported_actions,
                dependencies=getattr(desc, "dependencies", [])
            )
            self.graph.add_capability(node)
        return self.graph

    def introspect(self) -> Dict[str, Any]:
        self.scan_registered_capabilities()
        nodes = self.graph.list_nodes()

        categories: Dict[str, int] = {}
        for n in nodes:
            categories[n.category] = categories.get(n.category, 0) + 1

        return {
            "total_capabilities": len(nodes),
            "categories": categories,
            "capabilities": [n.to_dict() for n in nodes]
        }

    def analyze_mission(self, mission_description: str) -> Dict[str, Any]:
        self.scan_registered_capabilities()
        return self.reasoner.evaluate_mission_requirements(mission_description)
