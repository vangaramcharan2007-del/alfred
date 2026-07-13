import asyncio
import tempfile
import os
import shutil
import sys
import unittest
from pathlib import Path

from jarvisx.runtime import create_default_runtime


class PluginAndXPTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_op.db"
        self.plugins_dir = Path(__file__).resolve().parents[1] / "src" / "jarvisx" / "plugins"
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        # Create a dummy plugin
        self.dummy_plugin_path = self.plugins_dir / "dummy_agent.py"
        self.dummy_plugin_path.write_text(
            "from jarvisx.agents.base import BaseAgent, AgentResponse\n"
            "from jarvisx.core.events import Event\n"
            "class DummyPluginAgent(BaseAgent):\n"
            "    agent_id = 'dummy_plugin'\n"
            "    role = 'Dummy'\n"
            "    async def handle(self, event: Event) -> AgentResponse:\n"
            "        return self._response(event, handled=True, message='Dummy handled it')\n"
        )
        
        # Fresh runtime picks up the plugin dynamically
        self.runtime = create_default_runtime(op_db_path=self.db_path)

    def tearDown(self) -> None:
        if self.dummy_plugin_path.exists():
            self.dummy_plugin_path.unlink()
        self.temp_dir.cleanup()

    def test_dynamic_plugin_loaded(self) -> None:
        # Check if dummy_plugin was registered
        agent = self.runtime.registry.maybe_get("dummy_plugin")
        self.assertIsNotNone(agent)
        self.assertEqual(agent.role, "Dummy")

    def test_xp_routing(self) -> None:
        response = asyncio.run(self.runtime.alfred.process("show my xp stats"))
        self.assertTrue(response.handled)
        self.assertEqual(response.agent_id, "xp")
        self.assertIn("Level", response.message)
        self.assertIn("XP", response.message)

    def test_xp_awarding(self) -> None:
        response = asyncio.run(self.runtime.alfred.process("award me for a boss fight"))
        self.assertTrue(response.handled)
        self.assertEqual(response.agent_id, "xp")
        self.assertIn("500 XP", response.message)
        self.assertTrue(response.data["leveled_up"])
        self.assertEqual(response.data["level"], 6)  # (500 // 100) + 1 = 6


if __name__ == "__main__":
    unittest.main()
