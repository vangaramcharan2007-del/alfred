import asyncio
from jarvisx.core.providers.provider_router import ProviderRouter
from jarvisx.core.tools.tool_registry import ToolRegistry
from jarvisx.core.tools.execution.file_ops import FileOps
from jarvisx.core.tools.execution.command_executor import CommandExecutor
from jarvisx.core.planning.objective_manager import ObjectiveManager

async def test():
    try:
        router = ProviderRouter()
        registry = ToolRegistry.get_instance()
        registry.register(FileOps(), "file_ops")
        registry.register(CommandExecutor(), "command_executor")
        
        manager = ObjectiveManager(router, registry=registry)
        print("Running real objective...")
        res = await manager.execute_objective("Create a file named hello_real.txt containing 'Hello from LLM'")
        print(res)
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    asyncio.run(test())
