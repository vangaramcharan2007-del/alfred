import pytest
from jarvisx.llm.llm_router import LLMRouter

@pytest.mark.asyncio
async def test_llm_router_selection_and_routing():
    router = LLMRouter()

    profile, score = router.select_model("Refactor fast API authentication endpoints", require_offline=True)
    assert profile is not None
    assert profile.provider_id == "ollama.local"
    assert score > 0.70

    res = await router.route_request("Refactor fast API authentication endpoints", require_offline=True)
    assert res["status"] == "success"
    assert "selected_model" in res
    assert "result" in res

    fallback_p, fallback_s = router.fallback_model(profile.model_name, "Refactor fast API")
    assert fallback_p.model_name != profile.model_name

    rankings = router.compare_models("Complex reasoning problem", count=3)
    assert len(rankings) <= 3
