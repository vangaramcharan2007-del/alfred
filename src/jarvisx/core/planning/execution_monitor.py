import asyncio
import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ExecutionMonitor:
    """Dispatches tasks to tools via ToolRegistry. No hardcoded dispatch chains."""

    def __init__(self, registry=None):
        self._registry = registry

    @property
    def registry(self):
        if self._registry is None:
            from jarvisx.core.tools.tool_registry import ToolRegistry
            self._registry = ToolRegistry.get_instance()
        return self._registry

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Runs a single task via the registry and returns evidence-backed results."""
        tool_name = task.get("tool")
        method_name = task.get("method")
        args = task.get("args", {})
        task_id = task.get("id", "unknown")

        logger.info(f"Executing task '{task_id}' using {tool_name}.{method_name}")

        if not self.registry.has_tool(tool_name):
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not registered in ToolRegistry",
                "task_id": task_id,
                "evidence": {}
            }

        if not self.registry.has_method(tool_name, method_name):
            return {
                "success": False,
                "error": f"Method '{method_name}' not found on tool '{tool_name}'",
                "task_id": task_id,
                "evidence": {}
            }

        result = await self.registry.execute(tool_name, method_name, args)

        return {
            "success": result.get("success", False),
            "error": result.get("error"),
            "task_id": task_id,
            "evidence": result.get("evidence", {})
        }
