"""
Swarm Orchestrator — Parallel Agent Delegation for Jarvis X.
Decomposes complex intents into parallel sub-tasks, executes them
concurrently via asyncio, and merges results.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

MAX_AGENTS = 5
AGENT_TIMEOUT = 30
DEFAULT_MODEL = "qwen2.5-coder:1.5b"


class SwarmOrchestrator:
    """Spawns parallel LLM sub-agents to tackle complex multi-part tasks."""

    _instance = None

    @classmethod
    def get_instance(
        cls,
        model: str = DEFAULT_MODEL,
        max_agents: int = MAX_AGENTS,
        timeout_per_agent: float = AGENT_TIMEOUT,
    ) -> "SwarmOrchestrator":
        if cls._instance is None:
            cls._instance = cls(
                model=model, max_agents=max_agents, timeout_per_agent=timeout_per_agent
            )
        return cls._instance

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        max_agents: int = MAX_AGENTS,
        timeout_per_agent: float = AGENT_TIMEOUT,
    ):
        # These were previously hardcoded on the instance and as module-level
        # constants, so there was no way to run the swarm against a different
        # model, cap fan-out, or shorten the per-agent timeout without editing
        # the source. Callers now supply them; the old constants remain the
        # defaults so existing behaviour is unchanged.
        self.model = model
        # MAX_AGENTS is a ceiling, not a default: each agent is a separate
        # model call, so an uncapped fan-out is a way to spend a request budget
        # by accident. Clamp rather than trust the caller.
        self.max_agents = min(max_agents, MAX_AGENTS)
        self.timeout_per_agent = timeout_per_agent
        # A single shared client rather than importing ollama inside each
        # coroutine. It is also the seam the tests mock: without an attribute
        # to patch, the only way to test decomposition was to stand up a real
        # model server.
        import ollama

        self._client = ollama.AsyncClient()

    async def decompose(self, intent: str) -> List[Dict[str, str]]:
        """Ask LLM to split a complex intent into parallel sub-tasks."""
        prompt = f"""Break this complex request into 2-{self.max_agents} independent sub-tasks that can run in parallel.

Request: "{intent}"

Output ONLY a JSON array of objects, each with:
- "task_id": short identifier
- "description": what this sub-task should accomplish
- "prompt": the exact prompt to send to an LLM agent for this sub-task

Example: [{{"task_id": "research", "description": "Research topic X", "prompt": "Research and summarize..."}}]
Output ONLY the JSON array."""

        res = await self._client.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
        text = res["message"]["content"].strip()

        # Parse JSON
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        try:
            tasks = json.loads(text)
            if isinstance(tasks, list):
                return tasks[:self.max_agents]
        except json.JSONDecodeError:
            logger.warning("[Swarm] Failed to parse decomposition, running as single task")

        return [{"task_id": "main", "description": intent, "prompt": intent}]

    async def _run_agent(self, task: Dict[str, str]) -> Dict[str, Any]:
        """Run a single sub-agent with timeout."""
        task_id = task.get("task_id", "unknown")
        prompt = task.get("prompt", "")
        logger.info(f"[Swarm] Agent '{task_id}' starting...")
        t0 = time.perf_counter()

        try:
            # Await the async client directly. The previous version wrapped a
            # blocking ollama.chat in asyncio.to_thread, which meant every
            # "parallel" sub-agent consumed a real OS thread for its whole
            # lifetime -- the fan-out was bounded by the thread pool, not by
            # max_agents, and the concurrency the swarm exists to provide was
            # largely spent on thread handoff.
            res = await asyncio.wait_for(
                self._client.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                ),
                timeout=self.timeout_per_agent,
            )
            duration = round(time.perf_counter() - t0, 2)
            logger.info(f"[Swarm] Agent '{task_id}' completed in {duration}s")
            return {
                "task_id": task_id,
                "status": "success",
                "result": res["message"]["content"],
                "duration_sec": duration,
            }
        except asyncio.TimeoutError:
            logger.warning(f"[Swarm] Agent '{task_id}' timed out after {self.timeout_per_agent}s")
            return {"task_id": task_id, "status": "timeout", "result": ""}
        except Exception as e:
            logger.error(f"[Swarm] Agent '{task_id}' failed: {e}")
            return {"task_id": task_id, "status": "error", "result": str(e)}

    async def execute_swarm(self, intent: str) -> Dict[str, Any]:
        """Decompose intent, run agents in parallel, merge results."""
        t0 = time.perf_counter()

        tasks = await self.decompose(intent)
        logger.info(f"[Swarm] Decomposed into {len(tasks)} sub-tasks")

        # Run all agents concurrently
        results = await asyncio.gather(*[self._run_agent(t) for t in tasks])

        # Merge
        merged_text = []
        for r in results:
            if r["status"] == "success" and r["result"]:
                merged_text.append(f"### {r['task_id']}\n{r['result']}")

        total_time = round(time.perf_counter() - t0, 2)
        return {
            "status": "success",
            "agents_deployed": len(tasks),
            "agents_succeeded": sum(1 for r in results if r["status"] == "success"),
            "merged_response": "\n\n".join(merged_text),
            "individual_results": results,
            "total_duration_sec": total_time,
        }


def get_swarm_orchestrator(
    model: str = DEFAULT_MODEL,
    max_agents: int = MAX_AGENTS,
    timeout_per_agent: float = AGENT_TIMEOUT,
) -> SwarmOrchestrator:
    return SwarmOrchestrator.get_instance(
        model=model, max_agents=max_agents, timeout_per_agent=timeout_per_agent
    )
