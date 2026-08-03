import pytest
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.providers.intelligence.provider_selector import ProviderSelector

@pytest.mark.asyncio
async def test_provider_selector_selection_and_fallback():
    selector = ProviderSelector()
    registry = CapabilityRegistry()
    await selector.register(registry)

    profile, score = await selector.select_provider(
        task_description="Fix FastAPI JWT authentication bug",
        language="Python",
        framework="FastAPI"
    )

    assert profile is not None
    assert score > 0.70

    fallback_p, fallback_score = await selector.fallback_provider(
        current_provider_id=profile.provider_id,
        task_description="Fix FastAPI JWT authentication bug",
        language="Python",
        framework="FastAPI"
    )

    assert fallback_p.provider_id != profile.provider_id

    # Test registry action execution
    res = await registry.execute(
        "provider.intelligence",
        "provider.selection",
        task_description="Refactor React dashboard component",
        language="TypeScript",
        framework="React"
    )

    assert "selected_provider" in res
    assert "score" in res
