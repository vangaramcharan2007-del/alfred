from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple

class CommandParser:
    COMMANDS = {
        "status": "Show system health, active agents, models, memory, evolution level",
        "mission": "Run autonomous mission (usage: jarvis mission \"description\")",
        "plan": "Show planned execution without running (usage: jarvis plan \"description\")",
        "execute": "Execute an approved plan (usage: jarvis execute <plan_id>)",
        "explain": "Explain why decisions were made (usage: jarvis explain <mission_id>)",
        "replay": "Replay previous mission state (usage: jarvis replay <mission_id>)",
        "assistant": "Launch persistent multimodal desktop assistant mode",
        "evaluate": "Run human evaluation mode for a mission (usage: jarvis evaluate \"task\")",
        "history": "Show previous persisted missions",

        "evolve": "Trigger self-improvement analysis",
        "health": "Run full health check",
        "help": "Show available commands",
    }




    def parse(self, raw_input: str) -> Tuple[str, str]:
        parts = raw_input.strip().split(maxsplit=1)
        command = parts[0].lower() if parts else "help"
        args = parts[1].strip('"').strip("'") if len(parts) > 1 else ""
        return command, args

    def list_commands(self) -> Dict[str, str]:
        return dict(self.COMMANDS)
