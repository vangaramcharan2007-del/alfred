from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from jarvisx.agents.base import BaseAgent, AgentResponse
from jarvisx.core.events import Event

def _message(event: Event) -> str:
    return str(event.payload.get("message", "")).strip()


class FridayAgent(BaseAgent):
    agent_id = "friday"
    role = "Execution specialist and coding assistant"
    expertise = ("execution", "coding", "desktop actions", "teaching")
    tone = "friendly, calm, and confident"
    personality = "helpful assistant"
    capabilities = ("file.read", "file.write", "file.edit", "computer.run_command")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        prompt_path = Path("assets/prompts/friday.md")
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return "You are Friday, the execution specialist of Jarvis X."

    async def handle(self, event: Event) -> AgentResponse:
        file_system = self.tools.get("file")
        computer = self.tools.get("computer")
        vscode = self.tools.get("vscode")
        text = _message(event).lower()
        
        from jarvisx.core.state import get_agent_state, update_agent_state
        import asyncio
        import os
        import subprocess
        import json
        
        action_taken = ""
        
        # Check if we need to greet
        greeting = ""
        if not get_agent_state("friday").get("friday_greeted", False):
            greeting = "Hello. I'm Friday. I'm ready to assist.\n\n"
            update_agent_state("friday", "friday_greeted", True)
            
        demo_mode = False
        config_path = os.path.join("config", "demo.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    demo_mode = config.get("demo_mode", False)
            except:
                pass
                
        def maybe_pause(seconds: float):
            # Blocking sleep for simplicity in this synchronous handler path if needed
            # The demo script uses asyncio.sleep, so we can just return text.
            pass

        current_stage = get_agent_state("friday").get("mission_stage", "idle")
        
        if any(kw in text for kw in ["numpy tutorial", "numpy programs", "numpy indexing", "numpy basics", "numpy random package"]):
            update_agent_state("friday", "mission_stage", "typing_code")
            
            action_taken = "On it. Opening Visual Studio Code.\n"
            if demo_mode:
                action_taken += "\nCreating numpy_indexing.py.\nWriting the indexing and slicing examples.\n"
                action_taken += "\nCreating numpy_basics.py.\nWriting the array fundamentals examples.\n"
                action_taken += "\nCreating numpy_random.py.\nWriting the random package examples.\n"
            else:
                action_taken += (
                    "Creating numpy_indexing.py.\n"
                    "Writing the indexing and slicing examples.\n"
                    "Creating numpy_basics.py.\n"
                    "Writing the array fundamentals examples.\n"
                    "Creating numpy_random.py.\n"
                    "Writing the random package examples.\n"
                )
            
            if file_system and vscode:
                try:
                    file_system.write_file("JarvisX_Tutorials/numpy_indexing.py", "")
                    file_system.write_file("JarvisX_Tutorials/numpy_basics.py", "")
                    file_system.write_file("JarvisX_Tutorials/numpy_random.py", "")
                    
                    target_path = os.path.abspath("jarvis_workspace/JarvisX_Tutorials")
                    vscode.vscode_open_workspace(target_path)
                    
                    # 1. numpy_indexing.py
                    vscode.vscode_open_file(os.path.join(target_path, "numpy_indexing.py"))
                    vscode.vscode_type_code(
                        "# numpy_indexing.py\n"
                        "import numpy as np\n\n"
                        "arr = np.array([10, 20, 30, 40, 50])\n"
                        "print('Array:', arr)\n"
                        "print('First element:', arr[0])\n"
                        "print('Negative indexing (last):', arr[-1])\n"
                        "print('Slicing (1 to 3):', arr[1:4])\n"
                    )
                    vscode.vscode_save()
                    
                    # 2. numpy_basics.py
                    vscode.vscode_open_file(os.path.join(target_path, "numpy_basics.py"))
                    vscode.vscode_type_code(
                        "# numpy_basics.py\n"
                        "import numpy as np\n\n"
                        "arr1d = np.array([1, 2, 3])\n"
                        "arr2d = np.array([[1, 2], [3, 4]])\n"
                        "print('1D Shape:', arr1d.shape, 'Dimensions:', arr1d.ndim, 'Size:', arr1d.size, 'Type:', arr1d.dtype)\n"
                        "print('2D Shape:', arr2d.shape, 'Dimensions:', arr2d.ndim, 'Size:', arr2d.size, 'Type:', arr2d.dtype)\n"
                    )
                    vscode.vscode_save()
                    
                    # 3. numpy_random.py
                    vscode.vscode_open_file(os.path.join(target_path, "numpy_random.py"))
                    vscode.vscode_type_code(
                        "# numpy_random.py\n"
                        "import numpy as np\n\n"
                        "print('Random Integer:', np.random.randint(1, 100))\n"
                        "print('Random Float:', np.random.rand())\n"
                        "print('Random 1D Array:', np.random.rand(3))\n"
                        "print('Random 2D Array:\\n', np.random.rand(2, 2))\n"
                    )
                    vscode.vscode_save()
                    
                    action_taken += "\nThe programs are ready. Shall I run them?"
                    update_agent_state("friday", "mission_stage", "ready_to_execute")
                except Exception as e:
                    action_taken = f"I encountered an error creating the files: {str(e)}"
            else:
                action_taken = "I need file system and vscode tools to do that, Alfred."
                
        elif text.strip() == "yes" and current_stage == "ready_to_execute":
            # Execution Mode
            action_taken = "Running the examples.\n\n"
            if vscode:
                try:
                    vscode.vscode_run_in_terminal("python numpy_indexing.py")
                    vscode.vscode_run_in_terminal("python numpy_basics.py")
                    vscode.vscode_run_in_terminal("python numpy_random.py")
                    
                    action_taken += (
                        "Execution complete.\n"
                        "Would you like me to explain the concepts?"
                    )
                    update_agent_state("friday", "mission_stage", "explaining")
                except Exception as e:
                    action_taken = f"I encountered an error running the programs: {str(e)}"
            else:
                action_taken = "I need VSCodeController to execute programs, Alfred."

        elif text.strip() == "yes" and current_stage == "explaining":
            # Explanation Mode in Notepad
            explanation_text = (
                "Here is your revision summary.\n\n"
                "NumPy Indexing:\n"
                "- Accessing elements\n"
                "- Index positions\n"
                "- Negative indexing\n\n"
                "NumPy Slicing:\n"
                "- Range extraction\n"
                "- Step slicing\n\n"
                "NumPy Basics:\n"
                "- Array creation\n"
                "- Shape\n"
                "- Dimensions\n"
                "- Size\n"
                "- Data types\n\n"
                "NumPy Random:\n"
                "- randint()\n"
                "- rand()\n"
                "- Random arrays\n\n"
                "Revision Summary:\n"
                "1. Use `np.array()` to create arrays.\n"
                "2. Use `.shape`, `.ndim`, `.size`, `.dtype` for array properties.\n"
                "3. Use `np.random` module for generating random data arrays."
            )
            
            action_taken = explanation_text
            
            if computer:
                try:
                    # Open notepad to visibly type the explanation
                    computer.run_command("notepad", _user_approved=True)
                    
                    # Wait for notepad to open
                    import time
                    time.sleep(1.5)
                    
                    # Assuming vscode tool has our type_code helper which just types what we want slowly
                    if vscode:
                        vscode.vscode_type_code(explanation_text)
                except Exception as e:
                    action_taken += f"\n(Failed to type in Notepad: {e})"
            
            update_agent_state("friday", "mission_stage", "idle")

        elif "write a script" in text or "create a file" in text or "write code" in text:
            if file_system:
                try:
                    file_system.write_file("stub.txt", "Stub content by Friday")
                    action_taken = "Creating 'stub.txt'."
                except Exception as e:
                    action_taken = f"I encountered an error: {str(e)}"
            else:
                action_taken = "I need file system tools to do that, Alfred."
        else:
             action_taken = "Prepared a plan to execute tasks as Friday."
                
        return self._response(
            event,
            handled=True,
            message=greeting + action_taken,
            data={"workflow_request": _message(event), "system_prompt": self.system_prompt},
        )
