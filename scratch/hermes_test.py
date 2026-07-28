import asyncio
from jarvisx.core.events import Event
from jarvisx.core.hermes import HermesBus

async def handler(event):
    await asyncio.sleep(0.1)
    return f"Response to {event.type}"

async def main():
    bus = HermesBus()
    bus.subscribe("test.event", handler, subscriber_id="test_agent")
    
    event = Event(type="test.event", source="alfred", target="test_agent", payload={})
    responses = await bus.publish(event)
    print(f"Got responses: {responses}")

if __name__ == "__main__":
    asyncio.run(main())
