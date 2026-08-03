import pytest
from jarvisx.llm.llm_profile import LLMProfile
from jarvisx.llm.llm_scoring import HardwareMonitor, LLMTaskClassifier, LLMScorer

def test_hardware_monitor_and_task_classifier():
    hw = HardwareMonitor.get_hardware_specs()
    assert hw.cpu_cores > 0
    assert hw.ram_gb > 0

    assert LLMTaskClassifier.classify_request("Write Python function") == "coding"
    assert LLMTaskClassifier.classify_request("Fix null pointer error") == "debugging"
    assert LLMTaskClassifier.classify_request("Summarize text") == "summarization"

def test_llm_scorer_evaluation():
    scorer = LLMScorer()
    profile = LLMProfile(
        provider_id="ollama.local",
        model_name="qwen2.5-coder:7b",
        coding_score=0.97,
        cost=0.0,
        offline_support=True
    )

    score = scorer.compute_score(
        profile=profile,
        prompt="Fix critical memory leak bug",
        require_offline=True
    )

    assert score >= 0.70
