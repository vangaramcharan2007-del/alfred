"""Architecture Validation Engine.

Performs static AST analysis across the codebase to enforce structural boundaries,
detect forbidden import patterns, identify layer inversion, and uncover circular import cycles.
"""

import ast
import os
from dataclasses import dataclass, field
from typing import Dict, List, Set

from jarvisx.architecture.contracts import ArchitectureContract
from jarvisx.architecture.layers import get_layer_for_module


@dataclass
class Violation:
    file_path: str
    source_module: str
    target_module: str
    violation_type: str  # 'FORBIDDEN_IMPORT', 'LAYER_VIOLATION', 'CIRCULAR_DEPENDENCY'
    description: str


@dataclass
class ValidationResult:
    valid: bool
    violations: List[Violation] = field(default_factory=list)
    scanned_files: int = 0
    import_graph: Dict[str, Set[str]] = field(default_factory=dict)

    def summary_text(self) -> str:
        if self.valid:
            return f"PASSED: Scanned {self.scanned_files} files with 0 architecture violations."
        lines = [f"FAILED: Scanned {self.scanned_files} files, found {len(self.violations)} violations:"]
        for v in self.violations:
            lines.append(f"  [{v.violation_type}] {v.source_module} -> {v.target_module}: {v.description}")
        return "\n".join(lines)


class ArchitectureValidator:
    """AST-backed validator that verifies code alignment with the Jarvis X 6-layer architecture."""

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        self.import_graph: Dict[str, Set[str]] = {}
        self.violations: List[Violation] = []
        self.scanned_files: int = 0

    def validate(self) -> ValidationResult:
        self._scan_repository()
        self._check_forbidden_imports()
        self._check_layer_violations()
        self._detect_circular_dependencies()

        valid = len(self.violations) == 0
        return ValidationResult(
            valid=valid,
            violations=self.violations,
            scanned_files=self.scanned_files,
            import_graph=self.import_graph,
        )

    def _scan_repository(self) -> None:
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.root_dir)
                    mod_name = os.path.splitext(rel_path)[0].replace(os.sep, ".")
                    if mod_name.endswith(".__init__"):
                        mod_name = mod_name[:-9]

                    self.scanned_files += 1
                    imports = self._extract_imports_from_file(file_path, mod_name)
                    self.import_graph[mod_name] = imports

    def _extract_imports_from_file(self, file_path: str, current_module: str) -> Set[str]:
        imports: Set[str] = set()
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source_content = f.read()
            tree = ast.parse(source_content, filename=file_path)
        except Exception:
            return imports

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("jarvisx.") or alias.name == "jarvisx":
                        imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and (node.module.startswith("jarvisx.") or node.module == "jarvisx"):
                    imports.add(node.module)
                elif node.level > 0:
                    parts = current_module.split(".")
                    if len(parts) >= node.level:
                        parent = ".".join(parts[:-node.level])
                        full_mod = (
                            f"jarvisx.{parent}.{node.module}".lstrip(".")
                            if node.module
                            else f"jarvisx.{parent}".lstrip(".")
                        )
                        if not full_mod.startswith("jarvisx"):
                            full_mod = f"jarvisx.{full_mod}".lstrip(".")
                        imports.add(full_mod)

        return imports

    def _check_forbidden_imports(self) -> None:
        for source_mod, targets in self.import_graph.items():
            src_parts = source_mod.split(".")
            src_package = src_parts[0] if src_parts else ""

            for target_mod in targets:
                target_parts = target_mod.split(".")
                target_package = (
                    target_parts[1] if len(target_parts) > 1 and target_parts[0] == "jarvisx" else target_parts[0]
                )

                for rule in ArchitectureContract.FORBIDDEN_IMPORTS:
                    if src_package == rule["source"] and target_package == rule["target"]:
                        self.violations.append(
                            Violation(
                                file_path=source_mod,
                                source_module=src_package,
                                target_module=target_package,
                                violation_type="FORBIDDEN_IMPORT",
                                description=rule["reason"],
                            )
                        )

    def _check_layer_violations(self) -> None:
        for source_mod, targets in self.import_graph.items():
            src_layer = get_layer_for_module(source_mod)
            if not src_layer:
                continue

            for target_mod in targets:
                target_layer = get_layer_for_module(target_mod)
                if not target_layer or target_layer == src_layer:
                    continue

                if not ArchitectureContract.is_valid_layer_dependency(src_layer, target_layer):
                    self.violations.append(
                        Violation(
                            file_path=source_mod,
                            source_module=f"{source_mod} ({src_layer})",
                            target_module=f"{target_mod} ({target_layer})",
                            violation_type="LAYER_VIOLATION",
                            description=(
                                f"Layer inversion: '{src_layer}' is forbidden from depending directly on"
                                f" '{target_layer}'."
                            ),
                        )
                    )

    def _detect_circular_dependencies(self) -> None:
        graph: Dict[str, Set[str]] = {}
        for mod, imports in self.import_graph.items():
            graph[mod] = set()
            for imp in imports:
                target = imp[8:] if imp.startswith("jarvisx.") else imp
                if target in self.import_graph and target != mod:
                    graph[mod].add(target)

        visited: Set[str] = set()
        stack: List[str] = []
        stack_set: Set[str] = set()

        def dfs(node: str) -> None:
            visited.add(node)
            stack.append(node)
            stack_set.add(node)
            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in stack_set:
                    cycle = stack[stack.index(neighbor) :] + [neighbor]
                    cycle_str = " -> ".join(cycle)
                    self.violations.append(
                        Violation(
                            file_path=node,
                            source_module=node,
                            target_module=neighbor,
                            violation_type="CIRCULAR_DEPENDENCY",
                            description=f"Module import cycle detected: {cycle_str}",
                        )
                    )
            stack.pop()
            stack_set.remove(node)

        for mod in list(graph.keys()):
            if mod not in visited:
                dfs(mod)
