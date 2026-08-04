from __future__ import annotations

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set

from jarvisx.engineering.intelligence import ProjectIntelligence, RepositoryInfo


@dataclass
class ImpactReport:
    target_file: str
    importing_modules: List[str] = field(default_factory=list)
    dependent_tests: List[str] = field(default_factory=list)
    public_apis_affected: List[str] = field(default_factory=list)
    breaking_change_risk: str = "LOW"
    estimated_regression_risk: str = "LOW"
    supporting_evidence: List[str] = field(default_factory=list)

    def generate_report(self) -> str:
        lines: List[str] = []
        lines.append("IMPACT ANALYSIS REPORT")
        lines.append(f"Target File: {self.target_file}")
        lines.append(f"Importing Modules: {', '.join(self.importing_modules) if self.importing_modules else 'None detected'}")
        lines.append(f"Dependent Tests: {', '.join(self.dependent_tests) if self.dependent_tests else 'None detected'}")
        lines.append(f"Public APIs Affected: {', '.join(self.public_apis_affected) if self.public_apis_affected else 'None detected'}")
        lines.append(f"Breaking-Change Risk: {self.breaking_change_risk}")
        lines.append(f"Estimated Regression Risk: {self.estimated_regression_risk}")
        lines.append("Supporting Evidence:")
        for ev in self.supporting_evidence:
            lines.append(f"  - {ev}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_file": self.target_file,
            "importing_modules": self.importing_modules,
            "dependent_tests": self.dependent_tests,
            "public_apis_affected": self.public_apis_affected,
            "breaking_change_risk": self.breaking_change_risk,
            "estimated_regression_risk": self.estimated_regression_risk,
            "supporting_evidence": self.supporting_evidence,
        }


class ImpactAnalyzer:
    """
    Evaluates module coupling, public API surface area, and downstream test dependencies
    to assess architectural regression risks before executing code modifications.
    """

    def __init__(self, repo_path: str | Path, intel_report: RepositoryInfo | None = None):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise FileNotFoundError(f"Repository path not found: {self.repo_path}")
        if intel_report is None:
            self.intel_report = ProjectIntelligence(self.repo_path).analyze()
        else:
            self.intel_report = intel_report

    def analyze_file(self, file_path: str | Path) -> ImpactReport:
        target = Path(file_path)
        if not target.is_absolute():
            target = (self.repo_path / target).resolve()
        
        rel_str = str(target)
        try:
            rel_str = str(target.relative_to(self.repo_path)).replace("\\", "/")
        except ValueError:
            pass

        report = ImpactReport(target_file=rel_str)
        
        # 1. Convert relative file path to python module namespace prefix
        # e.g., src/jarvisx/tools/db_bridge.py -> jarvisx.tools.db_bridge or db_bridge
        mod_name = rel_str.replace(".py", "").replace("/", ".").replace("\\", ".")
        if mod_name.startswith("src."):
            mod_name = mod_name[4:]
        short_name = Path(rel_str).stem

        importing_mods: Set[str] = set()
        dep_tests: Set[str] = set()

        # Scan repository dependency graph and files for imports
        for mod, deps in self.intel_report.dependency_graph.items():
            if mod == rel_str:
                continue
            matches = any(mod_name in d or short_name in d for d in deps)
            if matches:
                if "tests/" in mod or "test_" in Path(mod).name:
                    dep_tests.add(mod)
                else:
                    importing_mods.add(mod)
                    
        # Verify by direct AST inspection across all python files if needed
        for py_rel, deps in self.intel_report.dependency_graph.items():
            if py_rel == rel_str:
                continue
            if py_rel in importing_mods or py_rel in dep_tests:
                continue
            fpath = self.repo_path / py_rel
            if fpath.exists() and fpath.suffix == ".py":
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    if mod_name in content or short_name in content:
                        if "tests/" in py_rel or "test_" in fpath.name:
                            dep_tests.add(py_rel)
                        else:
                            importing_mods.add(py_rel)
                except Exception:
                    pass

        report.importing_modules = sorted(list(importing_mods))
        report.dependent_tests = sorted(list(dep_tests))

        # 2. Extract public APIs via AST
        public_apis: List[str] = []
        if target.exists() and target.suffix == ".py":
            try:
                content = target.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=str(target))
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                        public_apis.append(f"Function: {node.name}()")
                    elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                        public_apis.append(f"Class: {node.name}")
                    elif isinstance(node, ast.Assign):
                        for targets_node in node.targets:
                            if isinstance(targets_node, ast.Name) and targets_node.id == "__all__":
                                public_apis.append(f"Export Manifest: __all__")
                            elif isinstance(targets_node, ast.Name) and targets_node.id.isupper():
                                public_apis.append(f"Constant: {targets_node.id}")
            except Exception:
                pass

        report.public_apis_affected = public_apis

        # 3. Assess Risk Level (LOW, MEDIUM, HIGH)
        evidence: List[str] = []
        mod_count = len(report.importing_modules)
        test_count = len(report.dependent_tests)
        api_count = len(report.public_apis_affected)
        is_core = any(c in rel_str for c in ["runtime.py", "alfred.py", "__main__.py", "base.py", "core/"])

        if is_core or mod_count >= 4 or test_count >= 4:
            risk_level = "HIGH"
            evidence.append(f"HIGH risk: Module is a central architectural component imported by {mod_count} downstream modules and {test_count} automated tests.")
            if is_core:
                evidence.append("Target file resides within core runtime kernel or primary orchestration layer.")
            if api_count > 0:
                evidence.append(f"Modification risks exposing breaking changes across {api_count} documented public endpoints.")
        elif mod_count >= 1 or test_count >= 1 or api_count >= 3:
            risk_level = "MEDIUM"
            evidence.append(f"MEDIUM risk: Moderate coupling detected with {mod_count} dependent modules and {test_count} tests.")
            if api_count > 0:
                evidence.append(f"Contains {api_count} public APIs that require backward-compatible signature maintenance.")
        else:
            risk_level = "LOW"
            evidence.append("LOW risk: Leaf module or isolated script with no direct upstream runtime dependencies detected.")
            evidence.append("Modifications carry negligible systemic regression probability.")

        report.breaking_change_risk = risk_level
        report.estimated_regression_risk = risk_level
        report.supporting_evidence = evidence

        return report
