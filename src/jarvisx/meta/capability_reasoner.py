from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.meta.capability_graph import CapabilityGraph

class CapabilityReasoner:
    def __init__(self, capability_graph: Optional[CapabilityGraph] = None):
        self.graph = capability_graph or CapabilityGraph()

    def evaluate_mission_requirements(self, mission_description: str) -> Dict[str, Any]:
        d = mission_description.lower()

        required_caps: List[str] = ["architecture.agent", "coding.agent"]
        missing_caps: List[str] = []
        recommendations: List[str] = []

        if "mobile" in d or "ios" in d or "android" in d or "appium" in d:
            required_caps.append("mobile.testing")
            if "mobile.testing" not in self.graph.nodes:
                missing_caps.append("mobile.testing")
                recommendations.append("Integrate Appium MCP server for end-to-end mobile app testing.")

        if "kubernetes" in d or "k8s" in d or "helm" in d:
            required_caps.append("k8s.orchestration")
            if "k8s.orchestration" not in self.graph.nodes:
                missing_caps.append("k8s.orchestration")
                recommendations.append("Integrate Kubernetes / Helm MCP server for cluster deployment management.")

        if "database" in d or "postgres" in d or "sql" in d:
            required_caps.append("database.ops")
            if "database.ops" not in self.graph.nodes:
                missing_caps.append("database.ops")
                recommendations.append("Integrate Postgres MCP server for schema introspection and migrations.")

        present_count = len([c for c in required_caps if c in self.graph.nodes])
        sufficiency_score = round(present_count / len(required_caps), 2) if required_caps else 1.0

        return {
            "mission": mission_description,
            "required_capabilities": required_caps,
            "available_capabilities": [c for c in required_caps if c in self.graph.nodes],
            "missing_capabilities": missing_caps,
            "recommendations": recommendations,
            "sufficiency_score": sufficiency_score
        }
