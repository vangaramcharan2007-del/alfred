from __future__ import annotations
from typing import Dict, Any, List, Optional

class TaskReasoner:
    """
    Decomposes requirements into technical tasks with dependency ordering and complexity estimation.
    """
    def decompose(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        raw = requirements.get("raw_request", "").lower()
        tasks = [
            {
                "task_id": "task_1_arch",
                "name": "Architecture Design & Blueprint",
                "depends_on": [],
                "complexity": "LOW"
            },
            {
                "task_id": "task_2_scaffold",
                "name": "Workspace & File Structure Setup",
                "depends_on": ["task_1_arch"],
                "complexity": "LOW"
            },
            {
                "task_id": "task_3_implementation",
                "name": "Core Application Logic Implementation",
                "depends_on": ["task_2_scaffold"],
                "complexity": requirements.get("complexity", "MEDIUM")
            },
            {
                "task_id": "task_4_testing",
                "name": "Pytest Sandbox Test Suite Generation & Execution",
                "depends_on": ["task_3_implementation"],
                "complexity": "MEDIUM"
            },
            {
                "task_id": "task_5_git",
                "name": "Local Version Control Commit & Report Generation",
                "depends_on": ["task_4_testing"],
                "complexity": "LOW"
            }
        ]

        return tasks
