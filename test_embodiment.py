import asyncio
import os
import json
import time

from jarvisx.core.tools.tool_registry import ToolRegistry
from jarvisx.core.planning.objective_manager import ObjectiveManager
from jarvisx.core.providers.provider_router import ProviderRouter
from jarvisx.core.providers.fallback_manager import FallbackManager
from jarvisx.core.providers.provider_registry import BaseProvider
from unittest.mock import AsyncMock

objective_str = (
    "Open Windows Notepad. Wait until Notepad is visible. "
    "Type exactly: Jarvis embodiment integration successful. "
    "Save the file as: jarvis_embodiment_test.txt Close Notepad."
)

plan = [
    {"id": "step1", "description": "Open Notepad", "tool": "desktop_ops", "method": "open_application", "args": {"app_name": "notepad.exe"}, "depends_on": []},
    {"id": "step2", "description": "Type text", "tool": "desktop_ops", "method": "type_text", "args": {"text": "Jarvis embodiment integration successful."}, "depends_on": ["step1"]},
    {"id": "step3", "description": "Save file hotkey", "tool": "desktop_ops", "method": "press_key", "args": {"key": "ctrl+shift+s"}, "depends_on": ["step2"]},
    {"id": "step4", "description": "Type filename", "tool": "desktop_ops", "method": "type_text", "args": {"text": os.path.abspath("jarvis_embodiment_test.txt")}, "depends_on": ["step3"]},
    {"id": "step5", "description": "Press enter", "tool": "desktop_ops", "method": "press_key", "args": {"key": "enter"}, "depends_on": ["step4"]},
    {"id": "step_wait", "description": "Wait for save", "tool": "command_executor", "method": "execute", "args": {"command": "powershell -Command \"Start-Sleep -Seconds 2\""}, "depends_on": ["step5"]},
    {"id": "step6", "description": "Close Notepad", "tool": "desktop_ops", "method": "close_application", "args": {"app_name": "notepad.exe"}, "depends_on": ["step_wait"]}
]

async def run_integration_test():
    print("========== 1. REGISTRY CHECK ==========")
    registry = ToolRegistry.get_instance()
    tools = registry.list_tools()
    print("Registered tools:", tools)
    if "desktop_ops" not in tools:
        print("desktop_ops not registered!")
        return False
        
    print("\n========== 2. INTEGRATION TEST ==========")
    # Remove file if exists
    if os.path.exists("jarvis_embodiment_test.txt"):
        os.remove("jarvis_embodiment_test.txt")
        
    mock_router = ProviderRouter(fallback_manager=None)
    mock_router.route_with_failover = AsyncMock(return_value=json.dumps(plan))
    
    manager = ObjectiveManager(mock_router, registry=registry)
    
    print("Executing deterministic integration plan...")
    res = await manager.execute_objective(objective_str)
    
    print("Integration Test Success:", res.get("success"))
    print("Evidence generated:")
    print(json.dumps(res.get("evidence", {}), indent=2))
    
    if os.path.exists("jarvis_embodiment_test.txt"):
        print("File exists! Integration test passed.")
        # Clean up for E2E
        os.remove("jarvis_embodiment_test.txt")
    else:
        print("File not found! Integration test failed.")

class MockLLMProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self.name = "MockLLM"
        self.category = "LLM"
        self.priority = 1
        
    async def initialize(self) -> bool:
        return True
        
    async def shutdown(self):
        pass
        
    async def is_healthy(self) -> bool:
        return True
        
    async def generate(self, *args, **kwargs) -> str:
        print(f"MockLLMProvider: Generating plan via LLM interface...")
        return json.dumps(plan)
        
    async def get_metrics(self) -> dict:
        return {}
        
    async def benchmark(self) -> dict:
        return {}
        
    def capability(self, feature: str) -> bool:
        return True
        
    async def check_health(self) -> bool:
        return True

async def run_e2e_test():
    print("\n========== 3. END-TO-END TEST ==========")
    # Setup FallbackManager with our mock provider
    registry = ToolRegistry.get_instance()
    from jarvisx.core.providers.provider_registry import ProviderRegistry
    provider_registry = ProviderRegistry()
    fallback = FallbackManager(provider_registry)
    
    mock_llm = MockLLMProvider()
    provider_registry.register_provider(mock_llm)
    fallback.active_providers["LLM"] = mock_llm
    
    real_router = ProviderRouter(fallback_manager=fallback)
    manager = ObjectiveManager(real_router, registry=registry)
    
    print("Executing E2E test through provider_router.route_with_failover()...")
    res = await manager.execute_objective(objective_str)
    
    print("E2E Test Success:", res.get("success"))
    print("Evidence generated:")
    print(json.dumps(res.get("evidence", {}), indent=2))
    
    if os.path.exists("jarvis_embodiment_test.txt"):
        print("File exists! E2E test passed.")
    else:
        print("File not found! E2E test failed.")

if __name__ == "__main__":
    asyncio.run(run_integration_test())
    time.sleep(2)
    asyncio.run(run_e2e_test())
