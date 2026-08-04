import pytest
from jarvisx.llm.llm_manager import LLMManager

@pytest.mark.asyncio
async def test_integration_llm_fallback():
    manager = LLMManager()
    res = await manager.execute_gateway_action("generate", prompt="Unit test query", require_offline=True)
    assert res["status"] in ("SUCCESS", "FALLBACK")
    assert "response" in res
