from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.interface.command_parser import CommandParser
from jarvisx.kernel.runtime_kernel import RuntimeKernel

class JarvisCLI:
    def __init__(self, kernel: Optional[RuntimeKernel] = None):
        self.kernel = kernel or RuntimeKernel()
        self.parser = CommandParser()

    def handle_command(self, raw_input: str) -> Dict[str, Any]:
        command, args = self.parser.parse(raw_input)

        if command == "status":
            return self.kernel.status()
        elif command == "health":
            return self.kernel.health_check()
        elif command == "help":
            return {"commands": self.parser.list_commands()}
        elif command == "mission":
            return {"action": "mission", "description": args, "note": "Use async create_and_execute_mission for runtime execution."}
        elif command == "evolve":
            return {"action": "evolve", "note": "Use async evolution engine for runtime execution."}

        return {"error": f"Unknown command: '{command}'. Type 'help' for available commands."}
