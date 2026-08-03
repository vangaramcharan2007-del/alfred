from __future__ import annotations
import shutil
import importlib
from typing import Dict, Any, List

class DependencyChecker:
    """
    Checks for the actual existence of Python packages and system binaries on PATH.
    """
    REQUIRED_PACKAGES = ["pytest", "yaml", "fastapi", "httpx", "pyttsx3"]
    REQUIRED_BINARIES = ["git", "python"]

    def check_python_packages(self) -> Dict[str, bool]:
        results = {}
        for pkg in self.REQUIRED_PACKAGES:
            try:
                importlib.import_module(pkg)
                results[pkg] = True
            except ImportError:
                results[pkg] = False
        return results

    def check_system_binaries(self) -> Dict[str, bool]:
        results = {}
        for b in self.REQUIRED_BINARIES:
            results[b] = shutil.which(b) is not None
        results["ollama"] = shutil.which("ollama") is not None
        return results

    def run_full_check(self) -> Dict[str, Any]:
        pkgs = self.check_python_packages()
        bins = self.check_system_binaries()
        return {
            "packages": pkgs,
            "binaries": bins,
            "all_critical_available": bins.get("git", False) and bins.get("python", False)
        }
