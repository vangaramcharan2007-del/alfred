from __future__ import annotations
import os
import ast
from pathlib import Path
from typing import Dict, Any, List, Optional

class RepositoryScanner:
    """
    Scans codebase directories, lists files, and parses AST imports for python source files.
    """
    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = Path(root_dir or ".")

    def scan_directory(self, target_dir: Optional[str] = None) -> Dict[str, Any]:
        p = Path(target_dir or self.root_dir)
        files = []
        py_files = []

        for root, dirs, filenames in os.walk(p):
            # Skip hidden and cache dirs
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", ".venv", "node_modules", "archive", "jarvis_workspace", "workspace")]
            for fn in filenames:
                fp = Path(root) / fn
                rel_p = str(fp.relative_to(p))
                files.append(rel_p)
                if fn.endswith(".py"):
                    py_files.append(rel_p)

        return {
            "root": str(p),
            "total_files": len(files),
            "python_files_count": len(py_files),
            "files": files[:100],
            "python_files": py_files[:50]
        }

    def parse_imports(self, file_path: str) -> List[str]:
        p = Path(file_path)
        if not p.exists() or not file_path.endswith(".py"):
            return []

        imports = []
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception:
            pass

        return imports
