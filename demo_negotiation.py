import os
import asyncio
from pathlib import Path

# Setup mock for Brave provider deployment
BRAVE_CODE = """from __future__ import annotations
from typing import Any
import webbrowser
from jarvisx.core.capabilities.base import Capability, CapabilityProvider, ProviderError
from jarvisx.core.capabilities.evaluation import ProviderEvaluation

class BraveProvider(CapabilityProvider):
    name = "Brave"
    capability = Capability.BROWSER

    def is_available(self) -> bool:
        return True

    def evaluate(self, task: dict[str, Any]) -> ProviderEvaluation:
        available = self.is_available()
        return ProviderEvaluation(
            provider_name=self.name,
            capability=self.capability.name,
            score=99.0 if available else 0.0,
            available=available,
            confidence=1.0 if available else 0.0,
            latency_ms=20.0,
            reason="Brand new fast provider."
        )

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        return {"status": "success", "message": "Executed via Brave!"}
"""

async def run_demonstration():
    print("==================================================")
    print(" JARVIS X: CAPABILITY NEGOTIATION ENGINE DEMO")
    print("==================================================\n")
    
    from jarvisx.runtime import create_default_runtime
    from jarvisx.core.events import Event
    from jarvisx.core.capabilities.evaluation import ProviderStatus

    runtime = create_default_runtime()
    await asyncio.sleep(0.5)

    def create_browser_event():
        return Event(
            type="agent.task.requested",
            source="alfred",
            target="capability_engine",
            payload={
                "capability_name": "BROWSER",
                "task": {"action": "search", "query": "Jarvis X"}
            }
        )
    
    print("\n--- DEMO 1: Three Browser Providers Coexisting ---")
    print("Expected: Chrome wins with Highest Score (98).")
    os.environ["MOCK_CHROME_UNAVAILABLE"] = "0"
    os.environ["MOCK_CHROME_FAIL"] = "0"
    
    # We will use the runtime engine directly for the demo
    from jarvisx.core.capabilities.base import Capability
    task_data = {"action": "search", "query": "Test"}
    
    print("Providers negotiating...")
    for provider in runtime.capability_registry.get_all(Capability.BROWSER):
        eval_res = provider.evaluate(task_data)
        print(f" - {eval_res.provider_name}: Score {eval_res.score} | Reason: {eval_res.reason}")
        
    res = runtime.capability_runtime.execute(Capability.BROWSER, task_data)
    print(f"Result: {res}")
    
    
    print("\n--- DEMO 2: Disable Chrome ---")
    print("Expected: Edge automatically takes over.")
    os.environ["MOCK_CHROME_UNAVAILABLE"] = "1"
    
    print("Providers negotiating...")
    for provider in runtime.capability_registry.get_all(Capability.BROWSER):
        eval_res = provider.evaluate(task_data)
        print(f" - {eval_res.provider_name}: Score {eval_res.score} | Available: {eval_res.available}")
        
    res = runtime.capability_runtime.execute(Capability.BROWSER, task_data)
    print(f"Result: {res}")


    print("\n--- DEMO 3: Force Chrome Failure & Learning ---")
    print("Expected: Chrome selected -> Execution Fails -> Edge Succeeds as fallback. Next time, Chrome score drops due to bad health.")
    os.environ["MOCK_CHROME_UNAVAILABLE"] = "0"
    os.environ["MOCK_CHROME_FAIL"] = "1"
    
    print("Executing task where Chrome will crash...")
    try:
        res = runtime.capability_runtime.execute(Capability.BROWSER, task_data, max_retries=0)
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error caught: {e}")
        
    # Check Chrome's health now
    chrome_provider = next(p for p in runtime.capability_registry.get_all(Capability.BROWSER) if p.name == "GoogleChrome")
    print(f"\nChrome Health after failure:")
    print(f" - Failures: {chrome_provider.health.failure_count}")
    print(f" - Success Rate: {chrome_provider.health.success_rate * 100}%")
    print(f" - Status: {chrome_provider.health.status.value}")
    
    print("\nNegotiating again after failure learning...")
    # Because of the 0% success rate, Chrome's adjusted score in the HighestScoreStrategy will be severely penalized!
    # Let's see who wins.
    os.environ["MOCK_CHROME_FAIL"] = "0" # let it work if it wins, but it shouldn't win
    res = runtime.capability_runtime.execute(Capability.BROWSER, task_data)
    print(f"Result: {res}")


    print("\n--- DEMO 4: Adding a Completely New Provider Automatically ---")
    print("Expected: BraveProvider dropped into folder. Restart runtime. Brave gets discovered and evaluated.")
    plugins_dir = Path("src/jarvisx/core/capabilities/providers/browser")
    brave_file = plugins_dir / "brave.py"
    with open(brave_file, "w") as f:
        f.write(BRAVE_CODE)
        
    print("Brave provider file dropped into system.")
    
    # Restart the runtime
    print("Restarting Jarvis X...")
    new_runtime = create_default_runtime()
    await asyncio.sleep(0.5)
    
    print("Providers negotiating...")
    for provider in new_runtime.capability_registry.get_all(Capability.BROWSER):
        eval_res = provider.evaluate(task_data)
        print(f" - {eval_res.provider_name}: Score {eval_res.score} | Reason: {eval_res.reason}")
        
    res = new_runtime.capability_runtime.execute(Capability.BROWSER, task_data)
    print(f"Result: {res}")

    # Cleanup
    if brave_file.exists():
        brave_file.unlink()

if __name__ == "__main__":
    asyncio.run(run_demonstration())
