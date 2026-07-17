import json
from typing import List, Dict, Any, Set
from jarvisx.core.providers.provider_router import ProviderRouter


class Replanner:
    """Generates corrective plans after task failures while preserving completed state."""

    def __init__(self, provider_router: ProviderRouter, registry=None):
        self.router = provider_router
        self._registry = registry

    @property
    def registry(self):
        if self._registry is None:
            from jarvisx.core.tools.tool_registry import ToolRegistry
            self._registry = ToolRegistry.get_instance()
        return self._registry

    def _build_capability_block(self) -> str:
        manifest = self.registry.get_capability_manifest()
        lines = ["Available tools and their methods:"]
        for entry in manifest:
            tool_name = entry["tool"]
            for method in entry["methods"]:
                params = ", ".join(
                    f"{p}" + ("" if info.get("required", True) else " (optional)")
                    for p, info in method["parameters"].items()
                )
                lines.append(f"  - {tool_name}.{method['name']}({params})")
        return "\n".join(lines)

    async def generate_correction(
        self,
        objective: str,
        failed_task: Dict[str, Any],
        error_msg: str,
        completed_task_ids: Set[str],
        remaining_tasks: List[Dict[str, Any]],
        logs: str = ""
    ) -> List[Dict[str, Any]]:
        """Generates a corrective plan for only the failed and downstream tasks.
        Completed tasks are NOT regenerated."""

        capability_block = self._build_capability_block()

        completed_str = ", ".join(sorted(completed_task_ids)) if completed_task_ids else "none"
        remaining_str = json.dumps([{"id": t["id"], "description": t.get("description", "")} for t in remaining_tasks], indent=2)

        prompt = f"""You are a Replanner. A failure occurred during execution. Generate a corrective JSON plan.

Original Objective: {objective}
Failed Task: {failed_task.get('description', 'Unknown')} (id: {failed_task.get('id', '?')})
Error Message: {error_msg}
Execution Logs: {logs}

Already completed tasks (DO NOT regenerate these): [{completed_str}]
Remaining tasks that still need completion:
{remaining_str}

{capability_block}

You may ONLY use tools and methods listed above.

Generate ONLY the corrective and remaining tasks. Do NOT include already-completed tasks.
Each task must have: id, description, tool, method, args, confidence, depends_on.
Output ONLY raw JSON.
"""

        response = await self.router.route_with_failover(
            category="planning",
            action="generate",
            prompt=prompt
        )

        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to decode LLM corrective plan: {response}") from e
