import asyncio
from jarvisx.cognition.cognitive_runtime import CognitiveRuntime
from jarvisx.agents.alfred import AlfredOrchestrator

async def demo():
    print("--- Jarvis X Cognitive Runtime Demo ---")
    runtime = CognitiveRuntime()
    
    # 1. Ask for something
    print("\nUser: Teach me Python decorators")
    agent = await runtime.route_task("Teach me Python decorators", ["friday", "edith", "alfred"])
    print(f"Cognitive Routing chose: {agent}")
    
    # 2. Execution and Feedback
    print(f"Executing task with {agent}...")
    # Simulate execution success
    runtime.track_outcome("Teach me Python decorators", agent, True, 1.2)
    print(f"Feedback loop: Outcome tracked for {agent}")
    
    # 3. Preference Learning - Second Request
    print("\nUser: Teach me Python decorators (again)")
    agent2 = await runtime.route_task("Teach me Python decorators", ["friday", "edith", "alfred"])
    print(f"Cognitive Routing chose: {agent2}")
    print(f"Confidence score for {agent2}: {runtime.confidence_manager.get_confidence(agent2)}")

if __name__ == "__main__":
    asyncio.run(demo())
