import asyncio
import os
from jarvisx.capabilities.capability_registry import CapabilityRegistry
from jarvisx.capabilities.capability_loader import CapabilityLoader
from jarvisx.capabilities.capability_health import CapabilityHealth
from jarvisx.cognition.decision_engine import DecisionEngine

async def run_demo():
    print("--- JarvisX Capability System Demo ---")
    
    registry = CapabilityRegistry()
    loader = CapabilityLoader(registry)
    health = CapabilityHealth()
    decision_engine = DecisionEngine()
    
    print("\n1. Loading capabilities from manifests...")
    manifests_path = os.path.join(os.path.dirname(__file__), "..", "src", "jarvisx", "capabilities", "manifests")
    await loader.load_local(manifests_path)
    
    github_cap = registry.query("github")
    if github_cap:
        print(f"Loaded {github_cap.manifest.name} capability (version {github_cap.manifest.version})")
    
    print("\n2. User Input: 'Analyze this GitHub repository'")
    print("Cognitive Runtime checking capabilities...")
    
    context = {
        "github_agent": {
            "capability_match": 0.95,
            "capability_reliability": health.get_status("github").reliability_score,
            "health_score": 1.0 if github_cap else 0.0
        },
        "general_agent": {
            "capability_match": 0.2,
            "capability_reliability": 1.0,
            "health_score": 1.0
        }
    }
    
    ranked_agents = decision_engine.rank_agents(["github_agent", "general_agent"], context)
    selected_agent = ranked_agents[0]
    print(f"Decision Engine selected: {selected_agent}")
    
    if selected_agent == "github_agent" and github_cap:
        print("\n3. Execution...")
        try:
            result = await github_cap.execute({"repo": "jarvis-x", "action": "analyze"})
            print(f"Execution result: {result}")
            health.record_call("github", success=True, latency_ms=150.0)
        except Exception as e:
            print(f"Execution failed: {e}")
            health.record_call("github", success=False, latency_ms=50.0)
            
        print("\n4. Health metrics updated")
        status = health.get_status("github")
        print(f"GitHub capability reliability score: {status.reliability_score:.2f}")
    
    print("\nDemo completed.")

if __name__ == "__main__":
    asyncio.run(run_demo())
