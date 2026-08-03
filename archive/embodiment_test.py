import asyncio
import os
import json
from jarvisx.core.providers.provider_router import ProviderRouter
from jarvisx.core.tools.tool_registry import ToolRegistry
from jarvisx.core.tools.execution.file_ops import FileOps
from jarvisx.core.tools.execution.command_executor import CommandExecutor
from jarvisx.core.planning.objective_manager import ObjectiveManager

async def run_embodiment_test():
    registry = ToolRegistry.get_instance()
    # Register the existing tools
    registry.register(FileOps(), "file_ops")
    registry.register(CommandExecutor(), "command_executor")

    print("=== REGISTRY LOOKUP ===")
    print("Available Tools in Registry:")
    for tool in registry.list_tools():
        print(f"- {tool}")
    print()

    # The real router to attempt dynamic planning
    # Note: We need a real API key or the LLM won't work. But this is just to show the attempt.
    router = ProviderRouter(fallback_manager=None)
    
    manager = ObjectiveManager(router, registry=registry)
    
    objective = (
        "Open Windows Notepad. Type exactly: 'Jarvis embodiment test successful.' "
        "Save the file as: jarvis_embodiment_test.txt Close Notepad."
    )
    print("=== STARTING OBJECTIVE ===")
    print(objective)
    print()

    # Since we know DesktopOps is not registered, we will intercept the planner to show what it would do
    try:
        plan_data = await manager.planner.create_plan(objective, "")
        print("=== GENERATED PLAN ===")
        print(json.dumps(plan_data, indent=2))
        
        # Now validate it using our PlanValidator
        from jarvisx.core.planning.plan_validator import PlanValidator
        validator = PlanValidator(registry=registry)
        valid, err = validator.validate(plan_data.get("steps", []))
        if not valid:
            print("\n=== PLAN VALIDATION FAILED ===")
            print(err)
    except Exception as e:
        print("\n=== PLANNING FAILED ===")
        print(str(e))

if __name__ == "__main__":
    asyncio.run(run_embodiment_test())
