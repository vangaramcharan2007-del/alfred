from __future__ import annotations
from typing import Dict, Any, List

class ModelTrace:
    """
    Logs LLM generation details: model name, prompt size, response size, latency (ms), token count, and fallbacks.
    """
    def __init__(self):
        self.generation_logs: List[Dict[str, Any]] = []

    def record_generation(
        self,
        model: str,
        prompt_size: int,
        response_size: int,
        latency_ms: float,
        token_count: int,
        fallback_used: bool = False
    ) -> Dict[str, Any]:
        entry = {
            "model": model,
            "prompt_size_chars": prompt_size,
            "response_size_chars": response_size,
            "latency_ms": latency_ms,
            "tokens": token_count,
            "fallback_used": fallback_used
        }
        self.generation_logs.append(entry)
        return entry
