import asyncio
import unittest
from unittest.mock import MagicMock

from jarvisx.agents.edith import EdithAgent
from jarvisx.core.events import Event
from jarvisx.tools.base import ToolResult
from jarvisx.tools.termux import TermuxTool


class TestEdithAgent(unittest.TestCase):

    def setUp(self) -> None:
        self.termux = MagicMock(spec=TermuxTool)
        self.termux.battery_status.return_value = ToolResult(success=True, message="Battery at 100%", data={"output": "100%"})
        self.termux.vibrate.return_value = ToolResult(success=True, message="Vibrated")
        self.termux.trigger_macrodroid.return_value = ToolResult(success=True, message="Macro triggered")
        
        self.agent = EdithAgent(tools={"termux": self.termux})

    def test_edith_termux_battery(self) -> None:
        event = Event(source="test", type="request", payload={"message": "check my battery"})
        response = asyncio.run(self.agent.handle(event))
        
        self.assertTrue(response.handled)
        self.assertIn("battery", response.data)
        self.termux.battery_status.assert_called_once()

    def test_edith_termux_vibrate(self) -> None:
        event = Event(source="test", type="request", payload={"message": "vibrate the phone"})
        response = asyncio.run(self.agent.handle(event))
        
        self.assertTrue(response.handled)
        self.termux.vibrate.assert_called_once()

    def test_edith_termux_macro(self) -> None:
        event = Event(source="test", type="request", payload={"message": "run macro"})
        response = asyncio.run(self.agent.handle(event))
        
        self.assertTrue(response.handled)
        self.termux.trigger_macrodroid.assert_called_once_with("default_macro_id")


if __name__ == "__main__":
    unittest.main()
