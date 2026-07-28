import asyncio
from jarvisx.agents.alfred import AlfredOrchestrator, IntentClassifier
from jarvisx.agents.friday import FridayAgent
from jarvisx.agents.edith import EdithAgent
from jarvisx.core.events import Event
from jarvisx.core.hermes import HermesBus
from jarvisx.core.logging import StructuredLogger
from jarvisx.models.router import ModelRouter

class MockAgentRegistry:
    def __init__(self):
        self.friday = FridayAgent()
        self.edith = EdithAgent()
        
    def maybe_get(self, agent_id: str):
        if agent_id == "friday":
            return self.friday
        elif agent_id == "edith":
            return self.edith
        return None

async def test_omega_demonstration():
    logger = StructuredLogger()
    hermes = HermesBus()
    classifier = IntentClassifier()
    model_router = ModelRouter()
    registry = MockAgentRegistry()
    
    alfred = AlfredOrchestrator(
        hermes=hermes,
        registry=registry,
        classifier=classifier,
        model_router=model_router,
        logger=logger
    )
    
    print("\n--- PHASE OMEGA: SWARM HANDOFF (BUDGET) ---")
    await alfred.process("Friday, I want to buy a new mechanical keyboard for $150.")
    await asyncio.sleep(3)
    
    print("\n--- PHASE OMEGA: SWARM HANDOFF (MOBILE / WHATSAPP) ---")
    await alfred.process("Edith, prepare the WhatsApp automation for the employee files.")
    await asyncio.sleep(3)
    
    print("\n--- PHASE OMEGA: CONTINUOUS VISION & POMODORO (STUDY) ---")
    await alfred.process("I have my physics exam tomorrow. Time to study.")
    await asyncio.sleep(3)
    
    print("\n--- PHASE OMEGA DEMONSTRATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test_omega_demonstration())
