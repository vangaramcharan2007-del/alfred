import asyncio
import os
import shutil
import unittest
from pathlib import Path

from jarvisx.runtime import create_default_runtime
from jarvisx.tools.file_system import FileSystem


class EditingAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sandbox_dir = Path("./jarvis_workspace")
        if self.sandbox_dir.exists():
            shutil.rmtree(self.sandbox_dir)

    def tearDown(self) -> None:
        if self.sandbox_dir.exists():
            shutil.rmtree(self.sandbox_dir)

    def test_sandbox_read_write(self) -> None:
        fs = FileSystem()
        
        # Write file in sandbox
        fs.write_file("test_script.py", "print('hello world')")
        self.assertTrue((self.sandbox_dir / "test_script.py").exists())
        
        # Read file
        content = fs.read_file("test_script.py")
        self.assertEqual(content, "print('hello world')")
        
        # Edit file
        fs.edit_file("test_script.py", "hello world", "goodbye world")
        content = fs.read_file("test_script.py")
        self.assertEqual(content, "print('goodbye world')")

    def test_sandbox_violation_raises_error(self) -> None:
        fs = FileSystem()
        
        # Attempt to write outside sandbox
        with self.assertRaises(PermissionError):
            fs.write_file("../malicious_script.py", "print('hacked')")
            
        # Attempt to read outside sandbox (assuming a file exists)
        with self.assertRaises(PermissionError):
            fs.read_file("../README.md")
            
        # Attempt to use absolute path outside sandbox
        with self.assertRaises(PermissionError):
            fs.write_file(os.path.abspath("../another_malicious.txt"), "hacked")

    def test_editing_agent_routing_and_execution(self) -> None:
        runtime = create_default_runtime()
        # Prompt should route to editing agent
        response = asyncio.run(runtime.alfred.process("Please write a script that says hello"))
        self.assertTrue(response.handled)
        self.assertEqual(response.agent_id, "editing")
        self.assertIn("stub.txt", response.message)
        
        # Verify the agent actually wrote the file via the tool
        self.assertTrue((self.sandbox_dir / "stub.txt").exists())


if __name__ == "__main__":
    unittest.main()
