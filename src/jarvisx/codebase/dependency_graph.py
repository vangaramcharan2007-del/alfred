from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.codebase.repo_scanner import RepositoryScanner

class DependencyGraphBuilder:
    """
    Builds module dependency graphs and import mappings across codebase files.
    """
    def __init__(self, scanner: Optional[RepositoryScanner] = None):
        self.scanner = scanner or RepositoryScanner()

    def build_graph(self, target_dir: Optional[str] = None) -> Dict[str, List[str]]:
        scan_res = self.scanner.scan_directory(target_dir)
        graph = {}
        for py_file in scan_res["python_files"]:
            full_path = str(self.scanner.root_dir / py_file)
            imports = self.scanner.parse_imports(full_path)
            graph[py_file] = imports

        return graph
