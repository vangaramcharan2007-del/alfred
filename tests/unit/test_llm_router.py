import pytest
from jarvisx.llm.llm_router import LLMRouter

def test_unit_llm_router_profiles():
    router = LLMRouter()
    assert len(router.profiles) > 0
    assert any("qwen" in p.model_name for p in router.profiles)
