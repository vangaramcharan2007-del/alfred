import asyncio
from jarvisx.agents.friday import FridayAgent
from jarvisx.tools.memory import LocalMemoryTool
from jarvisx.core.logging import StructuredLogger
from jarvisx.agents.base import Event

async def test_friday_memory():
    logger = StructuredLogger()
    memory_tool = LocalMemoryTool(logger=logger)
    
    friday = FridayAgent(tools={"memory": memory_tool}, logger=logger)
    
    event = Event(
        type="message",
        source="user",
        payload={
            "intent": "companion",
            "message": "Hey Friday, I just spent $15 on a coffee and pastry. Also, I finished my physics assignment."
        }
    )
    
    response = await friday.handle(event)
    print("Friday said:", response.message)

if __name__ == "__main__":
    asyncio.run(test_friday_memory())
