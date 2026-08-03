from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.codebase.dependency_graph import DependencyGraphBuilder

class ChangeImpactAnalyzer:
    """
    Analyzes potential impact of mutating or refactoring specific source files before changes occur.
    """
    def __init__(self, dep_graph_builder: Optional[DependencyGraphBuilder] = None):
        self.dep_graph_builder = dep_graph_builder or DependencyGraphBuilder()

    def analyze_impact(self, target_files: List[str]) -> Dict[str, Any]:
        graph = self.dep_graph_builder.build_graph()
        impacted_dependents = []

        for target in target_files:
            mod_name = target.replace("/", ".").replace(".py", "")
            for f, imports in graph.items():
                if any(mod_name in imp for imp in imports):
                    impacted_dependents.append(f)

        return {
            "target_files": target_files,
            "impacted_dependents": list(set(impacted_dependents)),
            "impact_level": "HIGH" if len(impacted_dependents) > 3 else "LOW"
        }
