import json
from typing import List, Dict, Any
from jarvisx.core.providers.provider_router import ProviderRouter


class TaskDecomposer:
    """Converts objectives into actionable tasks by querying the LLM provider.
    Injects live tool capabilities so the LLM cannot hallucinate tools."""

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
        """Builds a structured capability block from the live registry."""
        manifest = self.registry.get_capability_manifest()
        lines = ["Available tools and their methods:"]
        for entry in manifest:
            tool_name = entry["tool"]
            for method in entry["methods"]:
                params = ", ".join(
                    f"{p}" + ("" if info.get("required", True) else f" (optional, default={info.get('default', '?')})")
                    for p, info in method["parameters"].items()
                )
                lines.append(f"  - {tool_name}.{method['name']}({params})")
        return "\n".join(lines)

    async def decompose(self, objective: str, context: str = "") -> List[Dict[str, Any]]:
        """Breaks down an objective into a JSON plan grounded in live capabilities."""

        capability_block = self._build_capability_block()

        prompt = f"""You are a Task Decomposer. Break down the following objective into a JSON array of tasks.
Objective: {objective}
Context: {context}

{capability_block}

You may ONLY use tools and methods listed above. Do NOT invent tools or methods.

Each task must have:
- id: A unique string ID (e.g., 'task_1')
- description: What the task does
- tool: The tool name from the list above
- method: The method name from the list above
- args: A dictionary of arguments matching the method parameters
- confidence: Float between 0 and 1
- depends_on: List of task IDs this task depends on

Output ONLY raw JSON. No markdown. No explanation.
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
            plan = json.loads(response)
            return plan
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to decode LLM response into JSON: {response}") from e
