from __future__ import annotations
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

@dataclass
class Node:
    id: str
    name: str
    node_type: str  # "file", "class", "function", "module"
    path: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "node_type": self.node_type,
            "path": self.path,
            "metadata": self.metadata
        }

@dataclass
class Relationship:
    source_id: str
    target_id: str
    rel_type: str  # "imports", "inherits", "calls", "depends_on"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "rel_type": self.rel_type,
            "metadata": self.metadata
        }

class CodeGraph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.relationships: List[Relationship] = []

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node

    def add_relationship(self, rel: Relationship) -> None:
        # Avoid duplicate identical relationships
        for r in self.relationships:
            if r.source_id == rel.source_id and r.target_id == rel.target_id and r.rel_type == rel.rel_type:
                return
        self.relationships.append(rel)

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def get_dependencies(self, node_id: str) -> List[Node]:
        """Find target nodes that node_id depends on / imports."""
        target_ids = [r.target_id for r in self.relationships if r.source_id == node_id]
        return [self.nodes[tid] for tid in target_ids if tid in self.nodes]

    def get_dependents(self, node_id: str) -> List[Node]:
        """Find source nodes that depend on / import node_id."""
        source_ids = [r.source_id for r in self.relationships if r.target_id == node_id]
        return [self.nodes[sid] for sid in source_ids if sid in self.nodes]

    def search(self, query: str) -> List[Node]:
        q_lower = query.lower()
        results = []
        for n in self.nodes.values():
            if q_lower in n.name.lower() or q_lower in n.path.lower() or q_lower in n.node_type.lower():
                results.append(n)
        return results

    def build_from_repository(self, repo_path: str) -> None:
        p = Path(repo_path)
        if not p.exists() or not p.is_dir():
            return

        file_nodes: Dict[str, str] = {}  # rel_path -> node_id

        for f in p.rglob("*"):
            if f.is_file() and not any(part.startswith(".") or part in ["__pycache__", "node_modules", "venv", "dist", "build"] for part in f.parts):
                rel_path = str(f.relative_to(p))
                file_id = f"file:{rel_path}"
                file_nodes[rel_path] = file_id
                
                self.add_node(Node(
                    id=file_id,
                    name=f.name,
                    node_type="file",
                    path=rel_path,
                    metadata={"extension": f.suffix}
                ))

                # Parse file content for imports, classes, functions
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    self._parse_file_content(rel_path, file_id, content)
                except Exception:
                    pass

        # Resolve inter-file import relationships
        for rel_path, file_id in file_nodes.items():
            f_node = self.nodes.get(file_id)
            if not f_node:
                continue
            imports = f_node.metadata.get("imports", [])
            for imp in imports:
                for target_rel_path, target_id in file_nodes.items():
                    target_stem = Path(target_rel_path).stem
                    if imp in target_rel_path or imp == target_stem:
                        self.add_relationship(Relationship(
                            source_id=file_id,
                            target_id=target_id,
                            rel_type="imports"
                        ))

    def _parse_file_content(self, rel_path: str, file_id: str, content: str) -> None:
        imports: List[str] = []
        lines = content.splitlines()

        for line in lines:
            # Python imports
            py_imp_match = re.match(r'^(?:from|import)\s+([a-zA-Z0-9_\.]+)', line.strip())
            if py_imp_match:
                imports.append(py_imp_match.group(1).split(".")[0])
            
            # JS/TS imports
            js_imp_match = re.match(r'^import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]', line.strip())
            if js_imp_match:
                imports.append(Path(js_imp_match.group(1)).name)

            # Class definitions
            cls_match = re.match(r'^\s*class\s+([a-zA-Z0-9_]+)', line)
            if cls_match:
                cls_name = cls_match.group(1)
                cls_id = f"class:{rel_path}:{cls_name}"
                self.add_node(Node(
                    id=cls_id,
                    name=cls_name,
                    node_type="class",
                    path=rel_path
                ))
                self.add_relationship(Relationship(
                    source_id=file_id,
                    target_id=cls_id,
                    rel_type="contains"
                ))

            # Function definitions
            fn_match = re.match(r'^\s*(?:def|function)\s+([a-zA-Z0-9_]+)', line)
            if fn_match:
                fn_name = fn_match.group(1)
                fn_id = f"function:{rel_path}:{fn_name}"
                self.add_node(Node(
                    id=fn_id,
                    name=fn_name,
                    node_type="function",
                    path=rel_path
                ))
                self.add_relationship(Relationship(
                    source_id=file_id,
                    target_id=fn_id,
                    rel_type="contains"
                ))

        if file_id in self.nodes:
            self.nodes[file_id].metadata["imports"] = imports

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_nodes": len(self.nodes),
            "total_relationships": len(self.relationships),
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "relationships": [r.to_dict() for r in self.relationships]
        }
