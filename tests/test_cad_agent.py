import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from jarvisx.agents.specialists import CADAgent
from jarvisx.core.events import Event
from jarvisx.tools.cad import CADTool


class TestCADAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name) / "cad_workspace"
        self.cad_tool = CADTool(workspace_dir=str(self.workspace))
        self.agent = CADAgent(tools={"cad": self.cad_tool})

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_cad_box_generation(self) -> None:
        event = Event(source="test", type="request", payload={"message": "generate a 10x10 cube"})
        response = asyncio.run(self.agent.handle(event))
        
        self.assertTrue(response.handled)
        self.assertIn("cad", response.data["tool"])
        
        # Verify the file was created
        expected_file = self.workspace / "generated_cube.scad"
        self.assertTrue(expected_file.exists())
        
        # Verify content
        with open(expected_file, "r") as f:
            content = f.read()
        self.assertIn("cube([10, 10, 10], center=true);", content)

    def test_cad_outside_workspace(self) -> None:
        # If we try to write outside the workspace, it should fail.
        # This isn't strictly driven by the agent's intent right now, but tests the tool.
        result = self.cad_tool.generate_scad("../sneaky.scad", "cube();")
        self.assertFalse(result.success)
        self.assertIn("Permission denied", result.message)


if __name__ == "__main__":
    unittest.main()
