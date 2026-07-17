import asyncio
import os
import sys
from pathlib import Path

# Setup Python path to find jarvisx module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from jarvisx.core.providers.fallback_manager import FallbackManager
from jarvisx.core.providers.provider_router import ProviderRouter
from jarvisx.core.planning.objective_manager import ObjectiveManager
from jarvisx.core.providers.provider_registry import BaseProvider, ProviderCapability, ProviderRegistry

# We need a native OpenAI provider implementation that actually returns valid JSON
# Because the mocked implementations don't fulfill the 'No simulated success' rule
from jarvisx.clients.openai_client import OpenAIClient

class NativeOpenAIProvider(BaseProvider):
    def __init__(self):
        self.client = OpenAIClient()
        
    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("planning", "NativeOpenAI", 20, False)
        
    async def check_health(self) -> bool:
        return self.client.is_configured
        
    async def benchmark(self) -> float:
        return 150.0

    async def generate(self, prompt: str) -> str:
        """Native minimal urllib JSON generation call."""
        if not self.client.is_configured:
            raise RuntimeError("OPENAI_API_KEY is not set.")
            
        import urllib.request
        import urllib.error
        import json
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.client.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a specialized agent generating JSON plans based on instructions. Only return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }
        
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {e}")

async def run_scenario(manager: ObjectiveManager, name: str, objective: str):
    print(f"\\n{'='*50}")
    print(f"Running Scenario: {name}")
    print(f"Objective: {objective}")
    print(f"{'='*50}\\n")
    
    result = await manager.execute_objective(objective)
    
    print(f"\\nResult: {'SUCCESS' if result['success'] else 'FAILED'}")
    print(f"State: {result['tracker']['state']}")
    print(f"Completed Tasks: {result['tracker']['completed_tasks']}")
    print(f"Failed Tasks: {result['tracker']['failed_tasks']}")
    print(f"Retries: {result['tracker']['retries']}")
    print(f"Elapsed Time: {result['tracker']['elapsed_time']}s")
    
    return result

async def main():
    # Setup Provider Router with Native implementation
    native_provider = NativeOpenAIProvider()
    registry = ProviderRegistry()
    registry.register(native_provider)
    fallback_manager = FallbackManager(registry)
    # Mocking internal state of FallbackManager since we don't have the full app startup sequence
    fallback_manager.active_providers["planning"] = native_provider
    
    router = ProviderRouter(fallback_manager)
    manager = ObjectiveManager(router)
    
    # Scenario 1: Happy Path
    await run_scenario(
        manager,
        "Scenario 1 - Happy Path",
        "Create a python file named hello.py in the current directory that prints 'Hello World!', then execute it."
    )
    
    # Scenario 2: Failure Recovery
    await run_scenario(
        manager,
        "Scenario 2 - Failure Recovery",
        "Execute a python file named nonexistent_script.py using python_executor. This file definitely does not exist."
    )
    
    # Scenario 3: Parallel Execution
    await run_scenario(
        manager,
        "Scenario 3 - Parallel Execution",
        "Create three completely independent text files: file_a.txt, file_b.txt, and file_c.txt. Do not make them depend on each other."
    )

if __name__ == "__main__":
    asyncio.run(main())
