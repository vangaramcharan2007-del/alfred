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


class SwarmOrchestrator:
    """Spawns parallel LLM sub-agents to tackle complex multi-part tasks."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "SwarmOrchestrator":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.model = "qwen2.5-coder:1.5b"

    async def decompose(self, intent: str) -> List[Dict[str, str]]:
        """Ask LLM to split a complex intent into parallel sub-tasks."""
        import ollama

        prompt = f"""Break this complex request into 2-{MAX_AGENTS} independent sub-tasks that can run in parallel.

Request: "{intent}"

Output ONLY a JSON array of objects, each with:
- "task_id": short identifier
- "description": what this sub-task should accomplish
- "prompt": the exact prompt to send to an LLM agent for this sub-task

Example: [{{"task_id": "research", "description": "Research topic X", "prompt": "Research and summarize..."}}]
Output ONLY the JSON array."""

        res = ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
        text = res["message"]["content"].strip()

        # Parse JSON
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        try:
            tasks = json.loads(text)
            if isinstance(tasks, list):
                return tasks[:MAX_AGENTS]
        except json.JSONDecodeError:
            logger.warning("[Swarm] Failed to parse decomposition, running as single task")

        return [{"task_id": "main", "description": intent, "prompt": intent}]

    async def _run_agent(self, task: Dict[str, str]) -> Dict[str, Any]:
        """Run a single sub-agent with timeout."""
        import ollama

        task_id = task.get("task_id", "unknown")
        prompt = task.get("prompt", "")
        logger.info(f"[Swarm] Agent '{task_id}' starting...")
        t0 = time.perf_counter()

        try:
            res = await asyncio.wait_for(
                asyncio.to_thread(
                    ollama.chat,
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                ),
                timeout=AGENT_TIMEOUT,
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
            logger.warning(f"[Swarm] Agent '{task_id}' timed out after {AGENT_TIMEOUT}s")
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


def get_swarm_orchestrator() -> SwarmOrchestrator:
    return SwarmOrchestrator.get_instance()
