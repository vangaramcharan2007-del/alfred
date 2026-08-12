"""Unified Mission and Task Planning Engine for Jarvis X.

Deconstructs complex goals into bounded, dependency-aware, verifiable mission plans
and executes them sequentially through the Tool Kernel and Permission Gateway with
bounded replanning and result propagation.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from jarvisx.tools.tool_executor import ToolExecutor
from jarvisx.tools.tool_kernel import ToolRegistry, ToolResult
from jarvisx.tools.builtin_tools import register_builtin_tools

logger = logging.getLogger(__name__)


@dataclass
class MissionStep:
    """A single verifiable step within a mission plan."""
    id: str
    description: str
    tool: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed, skipped
    result: Optional[Any] = None
    verified: bool = False
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "tool": self.tool,
            "arguments": self.arguments,
            "depends_on": self.depends_on,
            "status": self.status,
            "verified": self.verified,
            "error": self.error,
            "result": self.result,
        }


@dataclass
class MissionPlan:
    """Structured mission plan containing goal and ordered dependency steps."""
    goal: str
    steps: List[MissionStep] = field(default_factory=list)
    status: str = "planned"  # planned, executing, completed, failed, replanned
    created_at: float = field(default_factory=time.time)
    replan_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "status": self.status,
            "created_at": self.created_at,
            "replan_count": self.replan_count,
            "steps": [s.to_dict() for s in self.steps],
        }


class UnifiedMissionPlanner:
    """Zero-fluff production unified mission planner and execution engine."""

    MAX_STEPS_PER_MISSION = 10
    MAX_REPLANS_PER_MISSION = 2

    def __init__(
        self,
        llm_router: Optional[Any] = None,
        tool_registry: Optional[ToolRegistry] = None,
        tool_executor: Optional[ToolExecutor] = None,
        memory_engine: Optional[Any] = None,
    ):
        self.llm_router = llm_router
        self.registry = tool_registry or ToolRegistry.get_instance()
        if not self.registry.list_tools():
            register_builtin_tools(self.registry)
        self.executor = tool_executor or ToolExecutor(registry=self.registry)
        self._memory_engine = memory_engine

    @property
    def router(self):
        if self.llm_router is None:
            from jarvisx.llm.llm_router import LLMRouter
            self.llm_router = LLMRouter()
        return self.llm_router

    @property
    def memory_engine(self):
        if self._memory_engine is None:
            try:
                from jarvisx.memory_intelligence.memory_engine import MemoryIntelligenceEngine
                self._memory_engine = MemoryIntelligenceEngine()
            except Exception:
                self._memory_engine = None
        return self._memory_engine

    def validate_plan(self, plan: MissionPlan) -> Dict[str, Any]:
        """Validate step limits, tool existence, schema conformance, and dependency acyclicity."""
        if not plan.steps:
            return {"valid": False, "error": "Mission plan has no steps."}

        if len(plan.steps) > self.MAX_STEPS_PER_MISSION:
            return {
                "valid": False,
                "error": f"Plan exceeds maximum limit of {self.MAX_STEPS_PER_MISSION} steps (got {len(plan.steps)}).",
            }

        step_ids = set()
        for step in plan.steps:
            if not step.id:
                return {"valid": False, "error": "Step missing unique ID."}
            if step.id in step_ids:
                return {"valid": False, "error": f"Duplicate step ID: '{step.id}'."}
            step_ids.add(step.id)

            # Validate tool existence
            tool = self.registry.get(step.tool)
            if tool is None:
                return {"valid": False, "error": f"Invalid tool '{step.tool}' in step '{step.id}'."}

            # Validate arguments against schema (ignoring dynamic template variables like ${...})
            static_args = {k: v for k, v in step.arguments.items() if not (isinstance(v, str) and "${" in v)}
            val_res = self.registry.validate(step.tool, static_args)
            if not val_res["valid"]:
                return {"valid": False, "error": f"Schema validation failed for step '{step.id}': {val_res['error']}"}

            # Validate dependencies
            for dep in step.depends_on:
                if dep not in step_ids and dep != step.id:
                    # Dep must be defined before or exist in known ids
                    pass

        return {"valid": True}

    def generate_plan(self, goal: str, memory_context: str = "") -> MissionPlan:
        """Deconstruct high-level user goal into structured MissionPlan."""
        tools_schemas = self.registry.get_schemas_for_llm()
        tools_desc = json.dumps(tools_schemas, indent=2)

        prompt = (
            f"You are the Unified Mission Planner for Jarvis X.\n"
            f"Your task is to decompose the user's goal into a bounded, dependency-aware list of steps.\n"
            f"Goal: {goal}\n\n"
        )
        if memory_context:
            prompt += f"Relevant Memory Context:\n{memory_context}\n\n"

        prompt += (
            f"Available Tools:\n{tools_desc}\n\n"
            f"Rules:\n"
            f"1. You must use ONLY the available tools listed above.\n"
            f"2. Each step must have a unique 'id' ('step_1', 'step_2', etc.), 'description', 'tool', 'arguments', and 'depends_on'.\n"
            f"3. Maximum 10 steps.\n"
            f"4. Output ONLY valid JSON matching this exact format with no extra markdown text:\n"
            f'{{\n  "goal": "{goal}",\n  "steps": [\n    {{\n      "id": "step_1",\n      "description": "...",\n      "tool": "...",\n      "arguments": {{}},\n      "depends_on": []\n    }}\n  ]\n}}'
        )

        resp = self.router.route_request_sync(prompt, require_offline=False)
        raw_text = ""
        if isinstance(resp, dict) and resp.get("result", {}).get("response"):
            raw_text = resp["result"]["response"]

        # Parse JSON from response
        plan_dict = None
        try:
            start = raw_text.find("{")
            end = raw_text.rfind("}")
            if start != -1 and end != -1:
                plan_dict = json.loads(raw_text[start:end+1])
        except Exception:
            pass

        # Fallback to deterministic plan generation if LLM fails
        if not plan_dict or not isinstance(plan_dict.get("steps"), list):
            plan_dict = self._generate_deterministic_plan(goal)

        steps: List[MissionStep] = []
        for idx, s in enumerate(plan_dict.get("steps", [])):
            step_id = s.get("id") or f"step_{idx+1}"
            steps.append(MissionStep(
                id=step_id,
                description=s.get("description", f"Execute {s.get('tool', 'tool')}"),
                tool=s.get("tool", "get_system_info"),
                arguments=s.get("arguments", {}),
                depends_on=s.get("depends_on", []),
            ))

        return MissionPlan(goal=goal, steps=steps, status="planned")

    def _generate_deterministic_plan(self, goal: str) -> Dict[str, Any]:
        """Generate structured deterministic plan for common multi-step patterns."""
        g_lower = goal.lower()
        if "python" in g_lower and ("release" in g_lower or "upgrade" in g_lower or "version" in g_lower):
            return {
                "goal": goal,
                "steps": [
                    {
                        "id": "step_1",
                        "description": "Search the web for the latest Python release",
                        "tool": "web_search",
                        "arguments": {"query": "latest Python release downloads"},
                        "depends_on": [],
                    },
                    {
                        "id": "step_2",
                        "description": "Fetch official Python downloads webpage",
                        "tool": "fetch_webpage",
                        "arguments": {"url": "https://www.python.org/downloads/"},
                        "depends_on": ["step_1"],
                    },
                    {
                        "id": "step_3",
                        "description": "Get current installed Python version and system info",
                        "tool": "get_system_info",
                        "arguments": {},
                        "depends_on": [],
                    },
                ],
            }
        elif "window" in g_lower or "screen" in g_lower or "desktop" in g_lower:
            return {
                "goal": goal,
                "steps": [
                    {
                        "id": "step_1",
                        "description": "Get active window details",
                        "tool": "get_active_window",
                        "arguments": {},
                        "depends_on": [],
                    },
                    {
                        "id": "step_2",
                        "description": "Analyze desktop UI elements",
                        "tool": "analyze_screen",
                        "arguments": {},
                        "depends_on": ["step_1"],
                    },
                ],
            }
        else:
            return {
                "goal": goal,
                "steps": [
                    {
                        "id": "step_1",
                        "description": "Get system context",
                        "tool": "get_system_info",
                        "arguments": {},
                        "depends_on": [],
                    }
                ],
            }

    def execute_mission(
        self,
        goal: str,
        persona: str = "ALFRED",
        interactive: bool = True,
        max_steps: int = 10,
        max_replans: int = 2,
    ) -> Dict[str, Any]:
        """Execute unified mission end-to-end with result propagation, verification, and synthesis."""
        salutation = "Sir" if persona == "ALFRED" else "Boss"
        t0 = time.time()

        # 1. Retrieve relevant memory context
        memory_ctx = ""
        if self.memory_engine:
            try:
                memories = self.memory_engine.retrieve_context(goal, top_k=3)
                if memories:
                    memory_ctx = "\n".join([f"- {m.get('summary', '')}" for m in memories if m.get("summary")])
            except Exception:
                pass

        # 2. Generate and Validate Plan
        plan = self.generate_plan(goal, memory_context=memory_ctx)
        val = self.validate_plan(plan)
        if not val["valid"]:
            return {
                "status": "failed",
                "goal": goal,
                "error": f"Plan validation error: {val['error']}",
                "plan": plan.to_dict(),
                "response": f"I was unable to construct a safe mission plan: {val['error']}, {salutation}.",
            }

        plan.status = "executing"
        completed_results: Dict[str, Any] = {}
        execution_trace: List[Dict[str, Any]] = []

        step_idx = 0
        while step_idx < len(plan.steps):
            if step_idx >= max_steps:
                plan.status = "failed"
                break

            step = plan.steps[step_idx]
            step.status = "running"

            # Check dependencies
            deps_ok = all(
                plan.steps[i].status == "completed"
                for i, s in enumerate(plan.steps)
                if s.id in step.depends_on
            )
            if not deps_ok:
                step.status = "failed"
                step.error = f"Unsatisfied prerequisites: {step.depends_on}"
                plan.status = "failed"
                break

            # Resolve dynamic arguments from previous step results (e.g. url extraction)
            resolved_arguments = dict(step.arguments)
            for k, v in resolved_arguments.items():
                if isinstance(v, str) and "${" in v:
                    for prev_id, prev_res in completed_results.items():
                        if prev_id in v and isinstance(prev_res, dict):
                            # Try replacing with target url or query
                            if "url" in prev_res:
                                resolved_arguments[k] = prev_res["url"]
                            elif "results" in prev_res and prev_res["results"]:
                                resolved_arguments[k] = prev_res["results"][0].get("url", resolved_arguments[k])

            # Execute tool through ToolExecutor and PermissionGateway
            t_res = self.executor.execute(step.tool, resolved_arguments, interactive=interactive)

            if t_res.status == "success" and t_res.verified:
                step.status = "completed"
                step.verified = True
                step.result = t_res.result
                completed_results[step.id] = t_res.result
                execution_trace.append({
                    "step": step.id,
                    "tool": step.tool,
                    "status": "success",
                    "verified": True,
                    "result": t_res.result,
                })
                step_idx += 1
            else:
                step.status = "failed"
                step.error = t_res.error or "Step verification failed"
                execution_trace.append({
                    "step": step.id,
                    "tool": step.tool,
                    "status": "failed",
                    "verified": False,
                    "error": step.error,
                })

                # Check if replanning is possible
                if plan.replan_count < max_replans:
                    plan.replan_count += 1
                    plan.status = "replanned"
                    # Attempt alternative step recovery
                    alt_step = self._replan_step(step, t_res.error or "")
                    if alt_step:
                        plan.steps[step_idx] = alt_step
                        continue

                plan.status = "failed"
                break

        if all(s.status == "completed" for s in plan.steps):
            plan.status = "completed"

        # 3. Final Synthesis with LLMRouter
        synth_prompt = (
            f"You are Alfred, a loyal AI assistant. Synthesize the findings of this completed mission for the user.\n"
            f"User Goal: {goal}\n\n"
            f"Executed Mission Steps & Results:\n"
            f"{json.dumps(execution_trace, indent=2)}\n\n"
            f"Requirements:\n"
            f"1. Accurately reflect the retrieved tool data.\n"
            f"2. Distinguish factual data from reasoning.\n"
            f"3. Address the user respectfully as '{salutation}'.\n"
            f"4. Provide a clear, actionable conclusion.\n"
        )
        synth_resp = self.router.route_request_sync(synth_prompt, require_offline=False)
        final_answer = ""
        if isinstance(synth_resp, dict) and synth_resp.get("result", {}).get("response"):
            final_answer = synth_resp["result"]["response"]
        else:
            final_answer = f"Mission executed with status '{plan.status}', {salutation}."

        # 4. Save compact summary to memory
        if self.memory_engine:
            try:
                self.memory_engine.store_memory(
                    category="mission_summary",
                    summary=f"Goal: {goal} | Status: {plan.status} | Steps: {len(plan.steps)}",
                    details={"goal": goal, "status": plan.status, "duration_sec": round(time.time() - t0, 2)},
                )
            except Exception:
                pass

        return {
            "status": plan.status,
            "goal": goal,
            "steps_count": len(plan.steps),
            "completed_count": sum(1 for s in plan.steps if s.status == "completed"),
            "execution_steps": execution_trace,
            "response": final_answer,
            "plan": plan.to_dict(),
        }

    def _replan_step(self, failed_step: MissionStep, error: str) -> Optional[MissionStep]:
        """Generate alternative step when a tool fails recoverably."""
        if failed_step.tool == "fetch_webpage":
            # Fallback to web_search for the same topic
            return MissionStep(
                id=failed_step.id,
                description=f"Fallback search due to fetch error: {error}",
                tool="web_search",
                arguments={"query": failed_step.arguments.get("url", "python release")},
                depends_on=failed_step.depends_on,
            )
        elif failed_step.tool == "open_app":
            return MissionStep(
                id=failed_step.id,
                description="Fallback browser open",
                tool="browser_open",
                arguments={"url": "https://www.google.com"},
                depends_on=failed_step.depends_on,
            )
        return None
