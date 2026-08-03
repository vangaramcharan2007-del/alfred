import pytest
from jarvisx.llm.llm_history import LLMHistoryManager

def test_llm_history_outcomes():
    mgr = LLMHistoryManager()
    mgr.record_outcome("ollama.local", "qwen2.5-coder:7b", "coding", success=True, latency=0.2)
    mgr.record_outcome("ollama.local", "qwen2.5-coder:7b", "coding", success=True, latency=0.25)
    mgr.record_outcome("omniroute.gateway", "gemini-1.5-pro", "architecture", success=False, latency=1.0)

    assert mgr.get_success_rate("ollama.local", "qwen2.5-coder:7b") == 1.0
    assert mgr.get_success_rate("omniroute.gateway", "gemini-1.5-pro") == 0.0
    assert mgr.get_preferred_model_for_task("coding") == "qwen2.5-coder:7b"
