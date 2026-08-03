from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.meta.failure_memory import FailureMemory, FailureRecord

class FailureAnalyzer:
    def __init__(self, failure_memory: Optional[FailureMemory] = None):
        self.memory = failure_memory or FailureMemory()

    def analyze_patterns(self) -> List[Dict[str, Any]]:

        patterns = []
        by_provider: Dict[str, int] = {}
        for f in self.memory.failures:
            by_provider[f.provider_id] = by_provider.get(f.provider_id, 0) + 1

        for prov, count in by_provider.items():
            if count >= 1:
                patterns.append({
                    "provider_id": prov,
                    "failure_count": count,
                    "insight": f"Provider '{prov}' has encountered {count} failure(s). Consider rerouting tasks to alternative providers."
                })
        return patterns

    def get_proven_fix(self, task_keyword: str) -> Optional[str]:
        matches = self.memory.find_similar_failures(task_keyword)
        for m in matches:
            if m.successful_fix:
                return m.successful_fix
        return None
