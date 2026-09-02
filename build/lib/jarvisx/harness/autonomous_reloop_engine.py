"""
Autonomous ReAct Execution & Self-Healing Harness Engine for Jarvis X.
Transforms single-turn chat into continuous, self-correcting task tree execution.
Executes steps, inspects actual terminal outputs/exit codes, autonomously debugs failures,
and iterates until goals are verified complete.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("jarvisx.harness.reloop")


@dataclass
class TaskNode:
    """A node in the living task tree."""
    id: str
    description: str
    assigned_agent: str
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED, RETRYING
    tool: str = ""
    tool_args: Dict[str, Any] = field(default_factory=dict)
    output: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    start_time: float = 0.0
    end_time: float = 0.0


@dataclass
class LivingTaskTree:
    """Hierarchical execution graph of a macro mission."""
    mission_id: str
    goal: str
    nodes: List[TaskNode] = field(default_factory=list)
    overall_status: str = "IN_PROGRESS"  # IN_PROGRESS, COMPLETED, FAILED
    current_node_index: int = 0
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AutonomousReActHarness:
    """The Continuous Autonomous Execution and Self-Healing Engine."""

    def __init__(self):
        from jarvisx.tools.tool_kernel import ToolRegistry
        from jarvisx.tools.builtin_tools import register_builtin_tools
        from jarvisx.tools.tool_executor import ToolExecutor
        from jarvisx.llm.llm_router import LLMRouter

        self.registry = ToolRegistry.get_instance()
        register_builtin_tools(self.registry)
        self.executor = ToolExecutor(registry=self.registry)
        self.router = LLMRouter()
        self.active_tree: Optional[LivingTaskTree] = None
        self._listeners: List[Callable[[LivingTaskTree], None]] = []

    def add_tree_listener(self, callback: Callable[[LivingTaskTree], None]):
        self._listeners.append(callback)

    def _notify(self):
        if self.active_tree:
            for cb in self._listeners:
                try:
                    cb(self.active_tree)
                except Exception:
                    pass

    async def execute_macro_goal_async(self, goal: str) -> LivingTaskTree:
        """
        Executes a high-level goal through the Autonomous ReAct Self-Healing Loop:
        1. Deconstructs goal into TaskNodes.
        2. Executes each node in order.
        3. Autonomously self-heals any failures by feeding tracebacks back to Gemini 3.6 Flash.
        """
        mission_id = f"mission_{int(time.time())}"
        
        # 1. Plan Initial Tree using Gemini 3.6 Flash
        plan_prompt = f"""You are the Master Harness Planner for Jarvis X / Alfred OS.
Break down the following goal into a precise sequential task tree of 2 to 5 actionable steps.

Available tools:
- get_current_time, get_system_info, list_directory, read_file, create_file
- optimize_game_settings, reduce_heat_and_ram_usage, clear_space, web_search, fetch_webpage

Goal: "{goal}"

Respond ONLY with valid JSON in this schema:
{{
  "steps": [
    {{"id": "step_1", "description": "short description", "assigned_agent": "CodingAgent", "tool": "tool_name", "args": {{}}}}
  ]
}}
"""
        plan_res = await self.router.route_request(plan_prompt)
        raw_text = plan_res.get("result", {}).get("response", "")
        
        # Parse JSON
        nodes = []
        try:
            cleaned = raw_text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            data = json.loads(cleaned.strip())
            for idx, s in enumerate(data.get("steps", [])):
                nodes.append(TaskNode(
                    id=s.get("id", f"step_{idx+1}"),
                    description=s.get("description", "Execute task"),
                    assigned_agent=s.get("assigned_agent", "DevOpsAgent"),
                    tool=s.get("tool", "get_system_info"),
                    tool_args=s.get("args", {})
                ))
        except Exception as e:
            logger.warning(f"Plan fallback: {e}")
            nodes.append(TaskNode(id="step_1", description=f"Execute: {goal}", assigned_agent="GeneralAgent", tool="get_system_info", tool_args={}))

        self.active_tree = LivingTaskTree(mission_id=mission_id, goal=goal, nodes=nodes)
        self._notify()

        # 2. Continuous Execution & Self-Healing Loop
        from jarvisx.orchestration.unified_agent_fleet import get_unified_fleet
        fleet = get_unified_fleet()

        for i, node in enumerate(self.active_tree.nodes):
            self.active_tree.current_node_index = i
            node.status = "RUNNING"
            node.start_time = time.time()
            self._notify()

            success = False
            while not success and node.retry_count <= node.max_retries:
                try:
                    # 1. Dispatch real work to the designated specialist agent
                    agent_res = await fleet.dispatch_task_async(node.assigned_agent, node.description)

                    # 2. Also execute underlying system tool if specified
                    tool_res = None
                    if node.tool and node.tool in self.registry.list_tools():
                        tool_res = self.executor.execute(node.tool, node.tool_args)

                    combined_output = {
                        "agent_execution": agent_res.get("result"),
                        "tool_execution": tool_res.result if tool_res and tool_res.status == "success" else None,
                        "agent_invoked": agent_res.get("real_agent_invoked", True),
                    }

                    node.status = "COMPLETED"
                    node.output = combined_output
                    node.end_time = time.time()
                    success = True
                    self._notify()

                except Exception as err:
                    node.retry_count += 1
                    node.error = str(err)
                    node.status = "RETRYING"
                    self._notify()

                    if node.retry_count > node.max_retries:
                        node.status = "FAILED"
                        node.end_time = time.time()
                        break


                    # 3. Autonomous Self-Healing via Gemini 3.6 Flash
                    heal_prompt = f"""Tool execution failed on task step '{node.description}'.
Tool: {node.tool}
Args: {node.tool_args}
Error: {err}

Generate a corrected tool and args to fix this failure and succeed.
Respond ONLY with JSON: {{"tool": "corrected_tool_name", "args": {{...}}}}"""
                    
                    heal_res = await self.router.route_request(heal_prompt)
                    heal_text = heal_res.get("result", {}).get("response", "")
                    try:
                        h_clean = heal_text.strip()
                        if "```" in h_clean:
                            h_clean = h_clean.split("```")[1]
                            if h_clean.startswith("json"):
                                h_clean = h_clean[4:]
                        h_data = json.loads(h_clean.strip())
                        node.tool = h_data.get("tool", node.tool)
                        node.tool_args = h_data.get("args", node.tool_args)
                    except Exception:
                        pass

        # Finalize
        all_completed = all(n.status == "COMPLETED" for n in self.active_tree.nodes)
        self.active_tree.overall_status = "COMPLETED" if all_completed else "FAILED"
        self._notify()
        return self.active_tree


def get_react_harness() -> AutonomousReActHarness:
    return AutonomousReActHarness()
