import pytest
import asyncio
from unittest.mock import patch, MagicMock

from jarvisx.core.llm_router import OmniRouterClient
from jarvisx.core.omniroute_manager import OmniRouteManager
from jarvisx.core.model_policy import ModelPolicy

@pytest.mark.asyncio
async def test_omniroute_manager_health():
    manager = OmniRouteManager()
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response
        
        is_healthy = await manager.check_health()
        assert is_healthy is True

@pytest.mark.asyncio
async def test_omniroute_manager_start():
    manager = OmniRouteManager()
    
    with patch.object(manager, 'detect_installation', return_value=True), \
         patch.object(manager, 'check_health', side_effect=[False, True]), \
         patch("subprocess.Popen") as mock_popen:
         
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        started = await manager.start()
        assert started is True
        mock_popen.assert_called_once()
        
        manager.stop()
        mock_process.terminate.assert_called_once()

@pytest.mark.asyncio
async def test_llm_router_chat_success():
    router = OmniRouterClient()
    messages = [{"role": "user", "content": "Hello"}]
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status = 200
        
        async def mock_json():
            return {"choices": [{"message": {"content": "Hi there!"}}]}
            
        mock_response.json = mock_json
        mock_post.return_value.__aenter__.return_value = mock_response
        
        result = await router.chat(messages=messages)
        assert result == "Hi there!"

@pytest.mark.asyncio
async def test_llm_router_offline_fallback():
    router = OmniRouterClient()
    messages = [{"role": "user", "content": "Hello"}]
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        # First call fails (OmniRoute), second call succeeds (Ollama)
        omniroute_fail = MagicMock()
        omniroute_fail.status = 500
        
        ollama_success = MagicMock()
        ollama_success.status = 200
        async def mock_ollama_json():
            return {"message": {"content": "Ollama fallback text"}}
        ollama_success.json = mock_ollama_json
        
        mock_post.return_value.__aenter__.side_effect = [omniroute_fail, ollama_success]
        
        result = await router.chat(messages=messages)
        assert result == "Ollama fallback text"

def test_model_policy():
    policy = ModelPolicy()
    ctx = policy.evaluate(agent_name="TestAgent", task_description="Write some python code")
    
    # Coding should route to reasoning capability
    assert ctx.metadata["agent"] == "TestAgent"
    assert ctx.metadata["capability"] == "reasoning"
    assert ctx.model == "reasoning-model"

def test_agents_do_not_import_ollama():
    """Verify that agent source files no longer import ollama directly."""
    import os
    agents_dir = "src/jarvisx/agents"
    if not os.path.exists(agents_dir):
        return
        
    for file in os.listdir(agents_dir):
        if file.endswith(".py"):
            with open(os.path.join(agents_dir, file), "r", encoding="utf-8") as f:
                content = f.read()
                assert "import ollama" not in content, f"{file} still imports ollama directly!"

