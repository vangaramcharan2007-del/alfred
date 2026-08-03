from __future__ import annotations
from enum import Enum
from typing import Dict, Any, List

class TaskCategory(str, Enum):
    BUG_FIX = "Bug Fix"
    FEATURE = "Feature"
    ARCHITECTURE = "Architecture"
    SECURITY = "Security"
    PERFORMANCE = "Performance"
    DOCUMENTATION = "Documentation"
    TESTING = "Testing"
    REFACTORING = "Refactoring"
    MIGRATION = "Migration"
    DEVOPS = "DevOps"

class TaskClassifier:
    @staticmethod
    def classify_task(description: str) -> TaskCategory:
        d = description.lower()
        if any(w in d for w in ["bug", "fix", "error", "exception", "crash", "issue"]):
            return TaskCategory.BUG_FIX
        if any(w in d for w in ["security", "auth", "vulnerability", "secret", "token"]):
            return TaskCategory.SECURITY
        if any(w in d for w in ["architecture", "design", "system", "diagram", "component"]):
            return TaskCategory.ARCHITECTURE
        if any(w in d for w in ["refactor", "clean", "rewrite", "structure"]):
            return TaskCategory.REFACTORING
        if any(w in d for w in ["test", "pytest", "unit", "coverage"]):
            return TaskCategory.TESTING
        if any(w in d for w in ["perf", "performance", "latency", "speed", "optimize"]):
            return TaskCategory.PERFORMANCE
        if any(w in d for w in ["doc", "documentation", "readme", "comment"]):
            return TaskCategory.DOCUMENTATION
        if any(w in d for w in ["migrate", "migration", "upgrade"]):
            return TaskCategory.MIGRATION
        if any(w in d for w in ["docker", "k8s", "deploy", "ci", "cd", "pipeline", "devops"]):
            return TaskCategory.DEVOPS
        return TaskCategory.FEATURE
