"""
Multi-Model Router — Intelligent model selection for Jarvis X.
Routes tasks to the optimal LLM based on complexity, speed requirements, and task type.
"""

import logging
import time
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    TRIVIAL = "trivial"      # time/date, greetings
    SIMPLE = "simple"        # open app, quick search
    MODERATE = "moderate"    # code gen, analysis
    COMPLEX = "complex"      # multi-step reasoning, planning


class ModelTier:
    def __init__(self, name: str, model_id: str, max_tokens: int, speed: str):
        self.name = name
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.speed = speed


# Model registry — add/remove models here
MODEL_TIERS: Dict[str, ModelTier] = {
    "fast": ModelTier("Fast", "qwen2.5-coder:1.5b", 2048, "fast"),
    "balanced": ModelTier("Balanced", "qwen2.5-coder:7b", 4096, "medium"),
    "heavy": ModelTier("Heavy", "llama3", 8192, "slow"),
}

# Complexity keywords
TRIVIAL_KEYWORDS = [
    "time", "date", "hello", "hi", "hey", "thanks", "bye", "good morning",
    "good night", "what day", "weather",
]

SIMPLE_KEYWORDS = [
    "open", "launch", "close", "start", "stop", "volume", "brightness",
    "screenshot", "battery", "ram", "cpu", "system",
]

COMPLEX_KEYWORDS = [
    "explain", "analyze", "compare", "design", "architect", "refactor",
    "debug", "optimize", "plan", "strategy", "research", "write essay",
    "multi-step", "create a full", "build me",
]


class MultiModelRouter:
    """Routes prompts to optimal model based on task complexity."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "MultiModelRouter":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.stats: Dict[str, Dict[str, float]] = {}
        self._override: Optional[str] = None

    def set_override(self, tier: Optional[str]):
        """Force a specific model tier. None to auto-select."""
        self._override = tier

    def classify_complexity(self, prompt: str) -> TaskComplexity:
        """Zero-LLM complexity classifier."""
        p = prompt.lower().strip()
        word_count = len(p.split())

        # Trivial: very short + trivial keywords
        if word_count <= 5:
            for kw in TRIVIAL_KEYWORDS:
                if kw in p:
                    return TaskComplexity.TRIVIAL

        # Complex: specific keywords or long prompts
        for kw in COMPLEX_KEYWORDS:
            if kw in p:
                return TaskComplexity.COMPLEX

        # Simple: action keywords
        for kw in SIMPLE_KEYWORDS:
            if kw in p:
                return TaskComplexity.SIMPLE

        # Default by length
        if word_count > 30:
            return TaskComplexity.COMPLEX
        elif word_count > 10:
            return TaskComplexity.MODERATE
        return TaskComplexity.SIMPLE

    def select_model(self, prompt: str) -> ModelTier:
        """Select the best model for the given prompt."""
        if self._override and self._override in MODEL_TIERS:
            return MODEL_TIERS[self._override]

        complexity = self.classify_complexity(prompt)

        if complexity == TaskComplexity.TRIVIAL:
            tier = MODEL_TIERS["fast"]
        elif complexity == TaskComplexity.SIMPLE:
            tier = MODEL_TIERS["fast"]
        elif complexity == TaskComplexity.MODERATE:
            tier = MODEL_TIERS.get("balanced", MODEL_TIERS["fast"])
        else:
            tier = MODEL_TIERS.get("heavy", MODEL_TIERS["fast"])

        logger.info(f"[ModelRouter] '{prompt[:30]}...' -> {complexity.value} -> {tier.name} ({tier.model_id})")
        return tier

    def route_and_call(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """Select model, call it, and return result with metadata."""
        import ollama

        tier = self.select_model(prompt)
        t0 = time.perf_counter()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            res = ollama.chat(model=tier.model_id, messages=messages)
            duration = round(time.perf_counter() - t0, 2)

            # Track stats
            if tier.name not in self.stats:
                self.stats[tier.name] = {"calls": 0, "total_time": 0}
            self.stats[tier.name]["calls"] += 1
            self.stats[tier.name]["total_time"] += duration

            return {
                "status": "success",
                "model": tier.model_id,
                "tier": tier.name,
                "response": res["message"]["content"],
                "duration_sec": duration,
            }
        except Exception as e:
            logger.error(f"[ModelRouter] Call failed: {e}")
            return {"status": "failed", "error": str(e), "model": tier.model_id}

    def get_stats(self) -> Dict[str, Any]:
        return self.stats
