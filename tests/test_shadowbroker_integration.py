import os
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from jarvisx.integrations.shadowbroker.shadowbroker_adapter import ShadowBrokerAdapter, ShadowBrokerTimeout, ShadowBrokerError
from jarvisx.core.skills.installed.shadowbroker_skill import ShadowBrokerOSINT
from jarvisx.core.skills.skill_registry import SkillRegistry

@pytest.fixture
def mock_sb_client_class():
    with patch("jarvisx.integrations.shadowbroker.shadowbroker_adapter._load_sb_client_class") as mock:
        mock_class = MagicMock()
        mock.return_value = mock_class
        yield mock_class

@pytest.mark.asyncio
async def test_adapter_configuration(mock_sb_client_class):
    # Test setting through environment
    os.environ["SHADOWBROKER_URL"] = "http://test:8000"
    os.environ["SHADOWBROKER_HMAC_SECRET"] = "secret123"
    
    adapter = ShadowBrokerAdapter(timeout_sec=5)
    assert adapter.base_url == "http://test:8000"
    assert adapter.hmac_secret == "secret123"
    assert adapter.timeout_sec == 5
    
    # Test explicit override
    adapter_override = ShadowBrokerAdapter(base_url="http://other", hmac_secret="newsec")
    assert adapter_override.base_url == "http://other"
    assert adapter_override.hmac_secret == "newsec"

@pytest.mark.asyncio
async def test_adapter_timeout_handling(mock_sb_client_class):
    mock_instance = mock_sb_client_class.return_value
    mock_instance.channel_status = AsyncMock(side_effect=asyncio.TimeoutError("Timeout"))
    
    adapter = ShadowBrokerAdapter(timeout_sec=1)
    
    with pytest.raises(ShadowBrokerTimeout):
        await adapter.health_check()

@pytest.mark.asyncio
async def test_adapter_graceful_failure(mock_sb_client_class):
    mock_instance = mock_sb_client_class.return_value
    mock_instance.ask = AsyncMock(side_effect=Exception("Connection refused"))
    
    adapter = ShadowBrokerAdapter()
    
    with pytest.raises(ShadowBrokerError):
        await adapter.ask("test query")

@pytest.mark.asyncio
async def test_skill_registration():
    registry = SkillRegistry()
    skill = ShadowBrokerOSINT()
    registry.register(skill)
    
    skills = registry.skills.values()
    assert any(s.name == "ShadowBrokerOSINT" for s in skills)
    assert "network_access" in skill.required_permissions
    assert "shadowbroker_ask" in skill.required_tools

@pytest.mark.asyncio
async def test_skill_permission_boundary():
    skill = ShadowBrokerOSINT()
    # Mock permission manager to deny
    skill.permission_manager.request = MagicMock(return_value=False)
    
    result = await skill.execute("test task", {"operation": "ask"})
    assert "Execution denied" in result
    skill.permission_manager.request.assert_called_once()
    
    # Mock permission manager to allow
    skill.permission_manager.request = MagicMock(return_value=True)
    skill.adapter.ask = AsyncMock(return_value={"ok": True})
    
    result = await skill.execute("test task", {"operation": "ask"})
    assert "ShadowBroker Result" in result
    skill.permission_manager.request.assert_called_once()
