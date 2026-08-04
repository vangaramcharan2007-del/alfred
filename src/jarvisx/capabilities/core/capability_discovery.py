"""
Capability Discovery System for Alfred & Friday.
Dynamically discovers, ranks, and matches available tools and capabilities for any unknown task.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from jarvisx.automation.action_registry import ActionRegistry
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry


@dataclass
class MatchResult:
    capability_id: str
    name: str
    category: str
    action_name: str
    score: float
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "category": self.category,
            "action_name": self.action_name,
            "score": round(self.score, 2),
            "reason": self.reason
        }


class CapabilityDiscoverySystem:
    """Discovers available capabilities dynamically based on natural language task descriptions."""

    def __init__(
        self,
        capability_registry: Optional[CapabilityRegistry] = None,
        action_registry: Optional[ActionRegistry] = None
    ):
        self.cap_registry = capability_registry or CapabilityRegistry()
        self.action_registry = action_registry or ActionRegistry.get_instance()
        self._registered_tools: List[Dict[str, Any]] = self._populate_tool_catalog()

    def _populate_tool_catalog(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "tool.file_system",
                "name": "File System Operator",
                "category": "file_ops",
                "actions": ["read_file", "write_file", "create_directory", "list_files", "organize_files"],
                "keywords": ["file", "create", "write", "read", "folder", "directory", "app.py", "pdf", "txt", "code", "organize"]
            },
            {
                "id": "tool.python_executor",
                "name": "Python Code Sandbox Executor",
                "category": "code_execution",
                "actions": ["execute_python", "run_pytest", "run_script"],
                "keywords": ["python", "run", "execute", "pytest", "test", "app", "script", "code", "debug"]
            },
            {
                "id": "tool.memory",
                "name": "Cognitive Local Memory Tool",
                "category": "memory",
                "actions": ["save_memory", "search_memory", "get_daily_note"],
                "keywords": ["memory", "remember", "store", "save", "search", "note", "knowledge", "obsidian", "recall"]
            },
            {
                "id": "tool.academic_engine",
                "name": "Friday 10 CGPA Academic Engine",
                "category": "academic",
                "actions": ["get_war_strategy", "generate_study_plan", "get_schedule"],
                "keywords": ["study", "plan", "academic", "cgpa", "exam", "subject", "revision", "operating systems", "timetable", "schedule"]
            },
            {
                "id": "tool.desktop_operator",
                "name": "Desktop Operator & Process Manager",
                "category": "desktop",
                "actions": ["open_app", "disk_usage", "compress", "screenshot", "windows"],
                "keywords": ["desktop", "open", "app", "compress", "disk", "screenshot", "process", "window", "browser"]
            },
            {
                "id": "tool.ocr_vision",
                "name": "OCR Vision & PDF Document Parser",
                "category": "vision_docs",
                "actions": ["read_pdf", "ocr_image", "extract_text"],
                "keywords": ["pdf", "ocr", "read pdf", "image", "document", "extract", "scan"]
            }
        ]

    def discover_best_capability(self, task_description: str) -> MatchResult:
        candidates = self.rank_capabilities(task_description)
        if candidates:
            return candidates[0]
        
        # Fallback default capability
        return MatchResult(
            capability_id="tool.python_executor",
            name="Python Code Sandbox Executor",
            category="code_execution",
            action_name="execute_python",
            score=0.5,
            reason="Fallback code executor for general task requirements"
        )

    def rank_capabilities(self, task_description: str) -> List[MatchResult]:
        task_lower = task_description.lower()
        tokens = set(re.findall(r"\w+", task_lower))
        matches: List[MatchResult] = []

        for tool in self._registered_tools:
            score = 0.0
            matched_keywords = []

            for kw in tool["keywords"]:
                if kw in task_lower or any(t == kw for t in tokens):
                    score += 1.5
                    matched_keywords.append(kw)

            # Bonus score for specific action matches
            matched_action = tool["actions"][0]
            for act in tool["actions"]:
                act_words = act.split("_")
                if any(aw in task_lower for aw in act_words):
                    score += 2.0
                    matched_action = act
                    break

            if score > 0:
                normalized_score = min(1.0, score / 5.0)
                reason = f"Matched keywords: {', '.join(matched_keywords[:3])}" if matched_keywords else "Category match"
                matches.append(MatchResult(
                    capability_id=tool["id"],
                    name=tool["name"],
                    category=tool["category"],
                    action_name=matched_action,
                    score=normalized_score,
                    reason=reason
                ))

        matches.sort(key=lambda m: m.score, reverse=True)
        return matches
