from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class Component:
    name: str
    responsibility: str
    dependencies: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "responsibility": self.responsibility,
            "dependencies": self.dependencies,
            "interfaces": self.interfaces
        }

@dataclass
class ArchitectureDecision:
    decision: str
    alternatives_considered: List[str] = field(default_factory=list)
    reasoning: str = ""
    tradeoffs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "alternatives_considered": self.alternatives_considered,
            "reasoning": self.reasoning,
            "tradeoffs": self.tradeoffs
        }

@dataclass
class SystemArchitecture:
    project_name: str
    requirements: List[str] = field(default_factory=list)
    components: List[Component] = field(default_factory=list)
    technology_stack: Dict[str, str] = field(default_factory=dict)
    data_flow: List[str] = field(default_factory=list)
    api_design: List[Dict[str, Any]] = field(default_factory=list)
    database_design: List[Dict[str, Any]] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    decisions: List[ArchitectureDecision] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "requirements": self.requirements,
            "components": [c.to_dict() for c in self.components],
            "technology_stack": self.technology_stack,
            "data_flow": self.data_flow,
            "api_design": self.api_design,
            "database_design": self.database_design,
            "risks": self.risks,
            "decisions": [d.to_dict() for d in self.decisions]
        }
