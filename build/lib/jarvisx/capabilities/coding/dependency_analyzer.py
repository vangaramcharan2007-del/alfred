from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from jarvisx.capabilities.coding.code_graph import CodeGraph

@dataclass
class ImpactReport:
    affected_files: List[str]
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    affected_modules: List[str]
    recommended_tests: List[str]
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "affected_files": self.affected_files,
            "risk_level": self.risk_level,
            "affected_modules": self.affected_modules,
            "recommended_tests": self.recommended_tests,
            "details": self.details
        }

class DependencyAnalyzer:
    def __init__(self, code_graph: Optional[CodeGraph] = None):
        self.graph = code_graph or CodeGraph()

    def analyze_impact(self, target_files: List[str], repo_path: Optional[str] = None) -> ImpactReport:
        if repo_path and len(self.graph.nodes) == 0:
            self.graph.build_from_repository(repo_path)

        affected_files_set: Set[str] = set(target_files)
        affected_modules_set: Set[str] = set()
        recommended_tests_set: Set[str] = set()

        for tf in target_files:
            node_id = f"file:{tf}"
            # Extract module name from file path
            mod_name = Path(tf).stem
            affected_modules_set.add(mod_name)

            # Find files dependent on tf
            dependents = self.graph.get_dependents(node_id)
            for dep in dependents:
                if dep.node_type == "file":
                    affected_files_set.add(dep.path)
                    affected_modules_set.add(Path(dep.path).stem)
                    if "test" in dep.path.lower():
                        recommended_tests_set.add(dep.path)

        # Default recommended tests if none found in graph
        if not recommended_tests_set:
            recommended_tests_set.add("pytest")

        # Determine risk level heuristic
        total_affected = len(affected_files_set)
        is_core_mod = any(
            any(keyword in f.lower() for keyword in ["auth", "db", "security", "core", "schema", "api"])
            for f in affected_files_set
        )

        if total_affected >= 5 or (is_core_mod and total_affected >= 2):
            risk_level = "HIGH"
        elif total_affected >= 2 or is_core_mod:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return ImpactReport(
            affected_files=sorted(list(affected_files_set)),
            risk_level=risk_level,
            affected_modules=sorted(list(affected_modules_set)),
            recommended_tests=sorted(list(recommended_tests_set)),
            details={
                "total_affected_count": total_affected,
                "is_core_module_affected": is_core_mod
            }
        )
