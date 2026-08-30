"""
Dynamic Autonomous Agent Factory for Alfred OS / Jarvis X.
Allows the user to create, configure, instantiate, and deploy custom AI agents on the fly
using Gemini 3.6 Flash.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvisx.agents.factory")

CONFIG_PATH = Path("config/custom_agents.json")


@dataclass
class CustomAgentSpec:
    """Specification for a dynamically created AI agent."""
    name: str
    role: str
    description: str
    system_prompt: str
    tools: List[str]
    created_at: float = field(default_factory=time.time)
    tasks_executed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DynamicAgentFactory:
    """Creates, registers, and runs specialized AI agents on demand."""

    _instance: Optional["DynamicAgentFactory"] = None

    def __init__(self, config_file: Optional[str] = None):
        self.config_path = Path(config_file or CONFIG_PATH)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.agents: Dict[str, CustomAgentSpec] = {}
        self._load_agents()

    @classmethod
    def get_instance(cls) -> "DynamicAgentFactory":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_agents(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        self.agents[k] = CustomAgentSpec(**v)
            except Exception as e:
                logger.warning(f"Could not load custom agents: {e}")

    def _save_agents(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                data = {k: v.to_dict() for k, v in self.agents.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save custom agents: {e}")

    async def create_agent_from_prompt_async(self, user_goal: str) -> CustomAgentSpec:
        """
        Uses Gemini 3.6 Flash to design a complete agent spec from a prompt.
        """
        from jarvisx.llm.llm_router import LLMRouter
        router = LLMRouter()

        design_prompt = f"""You are the Master AI Agent Architect for Alfred OS.
The user wants to create a new specialized autonomous AI agent.

User Request: "{user_goal}"

Available Tools:
- get_system_info, get_current_time, list_directory, read_file, create_file
- optimize_game_settings, reduce_heat_and_ram_usage, clear_space, web_search, fetch_webpage

Design the optimal agent spec.
Respond ONLY with valid JSON in this exact schema:
{{
  "name": "CamelCaseAgentName",
  "role": "Short 3-5 word role description",
  "description": "Comprehensive explanation of what this agent specializes in",
  "system_prompt": "Detailed system instructions for how this agent reasons and acts",
  "tools": ["tool1", "tool2"]
}}
"""
        res = await router.route_request(design_prompt)
        raw_text = res.get("result", {}).get("response", "")

        # Clean JSON
        clean = raw_text.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        if clean.endswith("```"):
            clean = clean[:-3]

        try:
            data = json.loads(clean.strip())
            name = data.get("name", "CustomSpecialistAgent")
            spec = CustomAgentSpec(
                name=name,
                role=data.get("role", "Specialized Task Agent"),
                description=data.get("description", user_goal),
                system_prompt=data.get("system_prompt", "You are an autonomous specialist agent."),
                tools=data.get("tools", ["get_system_info", "web_search"])
            )
        except Exception as ex:
            logger.warning(f"Agent JSON parse fallback: {ex}")
            name = "SpecialistAgent"
            spec = CustomAgentSpec(
                name=name,
                role="Specialist Agent",
                description=user_goal,
                system_prompt=f"Specialized agent created for: {user_goal}",
                tools=["get_system_info", "web_search"]
            )

        self.agents[spec.name] = spec
        self._save_agents()
        return spec

    async def execute_agent_task_async(self, agent_name: str, task: str) -> Dict[str, Any]:
        """Runs a task through the specified custom agent."""
        spec = self.agents.get(agent_name)
        if not spec:
            return {"status": "error", "error": f"Agent '{agent_name}' not found."}

        from jarvisx.llm.llm_router import LLMRouter
        router = LLMRouter()

        prompt = f"""[AGENT IDENTITY: {spec.name} - {spec.role}]
{spec.system_prompt}

Task to execute: "{task}"
Available tools: {spec.tools}

Execute this task and provide a concise, high-intelligence resolution."""

        res = await router.route_request(prompt)
        output = res.get("result", {}).get("response", "Task completed.")
        spec.tasks_executed += 1
        self._save_agents()

        return {
            "status": "success",
            "agent_name": spec.name,
            "role": spec.role,
            "result": output
        }

    def list_all_agents(self) -> List[Dict[str, Any]]:
        return [v.to_dict() for v in self.agents.values()]


def get_agent_factory() -> DynamicAgentFactory:
    return DynamicAgentFactory.get_instance()
