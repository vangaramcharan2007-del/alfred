"""Memory Classifier for Jarvis X Memory Intelligence Layer (Layer 2 - Memory).

Classifies memories into preference, task, goal, deadline, habit, knowledge, and temporary context.
"""

import re
from typing import Any, Dict, List


class MemoryClassifier:
    """Zero-fluff production memory classifier engine."""

    CATEGORIES = [
        "preference",
        "task",
        "goal",
        "deadline",
        "habit",
        "knowledge",
        "temporary context",
    ]

    def classify_text(self, text: str, context: str = "") -> str:
        """Classify memory text into canonical category based on linguistic patterns and context."""
        t_lower = text.lower() + " " + context.lower()

        if any(w in t_lower for w in ["deadline", "due", "by friday", "by tomorrow", "exam date"]):
            return "deadline"
        elif any(w in t_lower for w in ["prefer", "like", "always use", "favorite", "setting"]):
            return "preference"
        elif any(w in t_lower for w in ["goal", "aim to", "learn", "master", "achieve", "long-term"]):
            return "goal"
        elif any(w in t_lower for w in ["usually", "every day", "at 8 pm", "routine", "habit", "daily"]):
            return "habit"
        elif any(w in t_lower for w in ["todo", "task", "finish", "complete", "assignment", "fix"]):
            return "task"
        elif any(w in t_lower for w in ["concept", "definition", "formula", "theory", "knowledge", "architecture"]):
            return "knowledge"
        else:
            return "temporary context"

    def classify_memory_object(self, value: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Classify structured memory value and context dictionary."""
        val_str = str(value)
        ctx_str = str(context)
        return self.classify_text(val_str, context=ctx_str)
