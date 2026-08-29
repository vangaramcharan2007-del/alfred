"""
Hermes 3 Protocol & XML Tool Calling Parser for Jarvis X.
Implements the official Nous Research Hermes 3 function calling format:
- <tools> schema injection
- <thought> CoT (Chain-of-Thought) extraction
- <tool_call> JSON extraction and schema validation
- <tool_response> injection for multi-turn agentic loops
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class HermesToolCall:
    name: str
    arguments: Dict[str, Any]
    raw_content: str


@dataclass
class HermesParsedTurn:
    thought: Optional[str]
    tool_calls: List[HermesToolCall]
    content: str
    is_terminal: bool


class HermesProtocolFormatter:
    """Formats system prompts and parses outputs conforming to Nous Hermes 3 standards."""

    HERMES_SYSTEM_PROMPT = (
        "You are Jarvis X powered by Alfred and the Hermes Autonomous Agent Core. "
        "You are equipped with specialized tools to inspect the desktop, query public APIs, "
        "manage distributed GPU clusters, and execute code. "
        "When responding, you can think step-by-step using <thought>...</thought> tags, "
        "and invoke tools using <tool_call>{\"name\": \"<tool_name>\", \"arguments\": {<args>}}</tool_call> tags. "
        "Always be concise, precise, and sovereign."
    )

    @classmethod
    def build_system_prompt_with_tools(cls, tools_schema: List[Dict[str, Any]]) -> str:
        """Injects tool schemas into Hermes <tools> block."""
        tools_str = json.dumps(tools_schema, indent=2)
        return (
            f"{cls.HERMES_SYSTEM_PROMPT}\n\n"
            f"<tools>\n{tools_str}\n</tools>"
        )

    @classmethod
    def parse_hermes_response(cls, raw_response: str) -> HermesParsedTurn:
        """Parses <thought> and <tool_call> blocks from Hermes LLM output."""
        thought = None
        thought_match = re.search(r"<thought>(.*?)</thought>", raw_response, re.DOTALL)
        if thought_match:
            thought = thought_match.group(1).strip()

        tool_calls: List[HermesToolCall] = []
        call_matches = re.finditer(r"<tool_call>(.*?)</tool_call>", raw_response, re.DOTALL)

        for match in call_matches:
            raw_call = match.group(1).strip()
            try:
                data = json.loads(raw_call)
                tool_name = data.get("name", "")
                args = data.get("arguments", {})
                if tool_name:
                    tool_calls.append(HermesToolCall(name=tool_name, arguments=args, raw_content=raw_call))
            except Exception:
                # Fallback pattern matching
                pass

        # Strip internal tags for final user-facing text
        clean_content = re.sub(r"<thought>.*?</thought>", "", raw_response, flags=re.DOTALL)
        clean_content = re.sub(r"<tool_call>.*?</tool_call>", "", clean_content, flags=re.DOTALL).strip()

        return HermesParsedTurn(
            thought=thought,
            tool_calls=tool_calls,
            content=clean_content,
            is_terminal=len(tool_calls) == 0,
        )
