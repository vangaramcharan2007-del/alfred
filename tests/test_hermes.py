from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.core.events import Event
from jarvisx.core.hermes import HermesBus


class HermesTests(unittest.TestCase):
    def test_targeted_events_only_reach_target_subscriber(self) -> None:
        bus = HermesBus()
        seen: list[str] = []

        async def handler_one(event: Event) -> str:
            seen.append(f"one:{event.payload['value']}")
            return "one"

        async def handler_two(event: Event) -> str:
            seen.append(f"two:{event.payload['value']}")
            return "two"

        bus.subscribe("agent.task.requested", handler_one, subscriber_id="one")
        bus.subscribe("agent.task.requested", handler_two, subscriber_id="two")
        responses = asyncio.run(
            bus.publish(
                Event(
                    type="agent.task.requested",
                    source="test",
                    target="two",
                    payload={"value": "ok"},
                )
            )
        )

        self.assertEqual(responses, ["two"])
        self.assertEqual(seen, ["two:ok"])


if __name__ == "__main__":
    unittest.main()
