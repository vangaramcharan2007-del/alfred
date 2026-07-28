import pytest
import json
from unittest.mock import AsyncMock, patch

from jarvisx.core.llm_router import OmniRouterClient
from jarvisx.agents.capability_registry import CapabilityRegistry

@pytest.mark.asyncio
async def test_route_task_valid_json():
    router = OmniRouterClient()
    mock_json = """```json
{
 "intent": "productivity",
 "required_capabilities": ["planning", "reminders"],
 "selected_agents": [
   {"name": "friday", "confidence": 0.95}
 ]
}
```"""
    
    with patch.object(router, 'chat', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = mock_json
        
        result = await router.route_task("Help me plan my day")
        assert result["intent"] == "productivity"
        assert "planning" in result["required_capabilities"]
        assert result["selected_agents"][0]["name"] == "friday"

@pytest.mark.asyncio
async def test_route_task_fallback_on_invalid_schema():
    router = OmniRouterClient()
    # Invalid JSON schema
    mock_text = "I think you should use Friday."
    
    with patch.object(router, 'chat', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = mock_text
        
        result = await router.route_task("Do something")
        # Should fallback to existing alfred routing gracefully
        assert result["intent"] == "unknown"
        assert result["selected_agents"][0]["name"] == "alfred"

@pytest.mark.asyncio
async def test_route_task_with_registry():
    router = OmniRouterClient()
    registry = CapabilityRegistry()
    
    mock_json = """{
 "intent": "visual_analysis",
 "required_capabilities": ["vision", "image_analysis"],
 "selected_agents": []
}"""
    
    with patch.object(router, 'chat', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = mock_json
        
        # When passed a registry, it should auto-discover Vision agent
        result = await router.route_task("What is in this image?", registry=registry)
        selected = [a["name"] for a in result["selected_agents"]]
        assert "vision" in selected
