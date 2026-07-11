from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.runtime import create_default_runtime


class AlfredRoutingTests(unittest.TestCase):
    def test_open_youtube_routes_to_device_agent(self) -> None:
        runtime = create_default_runtime()
        response = asyncio.run(runtime.alfred.process("Open YouTube"))
        self.assertTrue(response.handled)
        self.assertEqual(response.agent_id, "device")
        self.assertEqual(response.data["intent"]["agent_id"], "device")
        self.assertEqual(
            response.data["result"]["data"]["package_hint"],
            "com.google.android.youtube",
        )

    def test_remember_routes_to_memory_agent(self) -> None:
        runtime = create_default_runtime()
        response = asyncio.run(runtime.alfred.process("remember Jarvis X stays modular"))
        self.assertTrue(response.handled)
        self.assertEqual(response.agent_id, "memory")
        self.assertEqual(response.data["intent"]["task_class"], "memory")

    def test_debug_routes_to_debug_agent_without_deploying(self) -> None:
        runtime = create_default_runtime()
        response = asyncio.run(runtime.alfred.process("debug this failure in the logs"))
        self.assertTrue(response.handled)
        self.assertEqual(response.agent_id, "debug")
        self.assertIn("will not deploy", response.message.lower())


if __name__ == "__main__":
    unittest.main()
