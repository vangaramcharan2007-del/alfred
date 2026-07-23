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
        text = _message(event).lower()
        
        # Stub implementation mapping keywords to mock results simulating Friday's logic
        action_taken = "Prepared a plan to execute tasks as Friday."
        
        if "array basics" in text:
            action_taken = "Opening Visual Studio Code...\nCreating array_basics.py...\nWriting the programs..."
            if file_system:
                try:
                    code = (
                        "# array_basics.py\n"
                        "# Array Basics in Python\n\n"
                        "# 1. Creating an array (list in Python)\n"
                        "my_array = [10, 20, 30, 40, 50]\n\n"
                        "# 2. Accessing elements\n"
                        "print('First element:', my_array[0])\n"
                        "print('Last element:', my_array[-1])\n\n"
                        "# 3. Modifying elements\n"
                        "my_array[1] = 25\n"
                        "print('Modified array:', my_array)\n\n"
                        "# 4. Adding elements\n"
                        "my_array.append(60)\n"
                        "print('After append:', my_array)\n"
                    )
                    file_system.write_file("array_basics.py", code)
                    action_taken += "\n\nFile array_basics.py has been created. Let me know if you would like me to run it."
                except Exception as e:
                    action_taken = f"I encountered an error: {str(e)}"
            else:
                action_taken = "I need file system tools to do that, Alfred."
        elif "write a script" in text or "create a file" in text or "write code" in text:
            # Simulate a write action
            if file_system:
                try:
                    file_system.write_file("stub.txt", "Stub content by Friday")
                    action_taken = "Creating 'stub.txt'."
                except Exception as e:
                    action_taken = f"I encountered an error: {str(e)}"
            else:
                action_taken = "I need file system tools to do that, Alfred."
                
        return self._response(
            event,
            handled=True,
            message=action_taken,
            data={"workflow_request": _message(event), "system_prompt": self.system_prompt},
        )
