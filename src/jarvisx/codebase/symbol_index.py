from __future__ import annotations
import ast
from pathlib import Path
from typing import Dict, Any, List, Optional

class SymbolIndex:
    """
    Indexes functions, classes, and types defined across python source files.
    """
    def index_file(self, file_path: str) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.exists() or not file_path.endswith(".py"):
            return {"classes": [], "functions": []}

        classes = []
        functions = []

        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    functions.append(node.name)
        except Exception:
            pass

        return {
            "file": file_path,
            "classes": classes,
            "functions": functions
        }
