import asyncio
import logging
from typing import Dict, Any, Callable
from jarvisx.core.tools.execution.file_ops import FileOps
from jarvisx.core.tools.execution.command_executor import CommandExecutor
from jarvisx.core.tools.execution.python_executor import PythonExecutor

logger = logging.getLogger(__name__)

class ExecutionMonitor:
    """Dispatches tasks to tools and monitors their execution."""

    def __init__(self):
        # Maps tool strings to actual class/module references
        self.tool_map = {
            "file_ops": FileOps,
            "command_executor": CommandExecutor,
            "python_executor": PythonExecutor,
            # Placeholder for others...
            # "git_ops": GitOps,
            # "browser_manager": BrowserManager,
            # "desktop_controller": DesktopController,
        }

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Runs a single task and returns the result."""
        tool_name = task.get("tool")
        method_name = task.get("method")
        args = task.get("args", {})
        
        logger.info(f"Executing task '{task.get('id')}' using {tool_name}.{method_name}")

        if tool_name not in self.tool_map:
            return {"success": False, "error": f"Tool '{tool_name}' not supported.", "task_id": task.get("id")}
            
        tool_class = self.tool_map[tool_name]
        
        if not hasattr(tool_class, method_name):
            return {"success": False, "error": f"Method '{method_name}' not found in {tool_name}", "task_id": task.get("id")}
            
        method = getattr(tool_class, method_name)
        
        try:
            # Most of our execution tools are currently synchronous static methods
            if asyncio.iscoroutinefunction(method):
                result = await method(**args)
            else:
                # Run sync functions in thread pool
                result = await asyncio.to_thread(method, **args)
                
            return {
                "success": result if isinstance(result, bool) else result.get("success", True),
                "output": result,
                "task_id": task.get("id")
            }
        except Exception as e:
            logger.error(f"Execution failed for {task.get('id')}: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task.get("id")
            }
