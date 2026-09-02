from __future__ import annotations
import asyncio
from typing import Dict, Any, Optional

from jarvisx.runtime.bootstrap import BootstrapManager
from jarvisx.runtime.context import RuntimeContext
from jarvisx.runtime.daemon import JarvisDaemon
from jarvisx.runtime.shutdown import ShutdownManager
from jarvisx.runtime.state import RuntimeState
from jarvisx.kernel.runtime_kernel import RuntimeKernel
from jarvisx.interface.cli import JarvisCLI

class JarvisRuntime:
    def __init__(self, config_path: Optional[str] = None, context: Optional[RuntimeContext] = None):
        self.context = context or RuntimeContext.create(config_path)
        self.bootstrap = BootstrapManager(config_path=config_path, context=self.context)
        self.kernel = RuntimeKernel(context=self.context)
        self.daemon = JarvisDaemon(context=self.context)
        # Compatibility aliases for legacy callers that accessed runtime internals.
        self.config = self.context.config
        self.bus = self.context.event_bus
        self.registry = self.context.capability_registry
        self.memory = self.context.memory
        self.security = self.context.security
        self.health_manager = self.context.health_manager
        self.shutdown_mgr: Optional[ShutdownManager] = None
        self.cli: Optional[JarvisCLI] = None
        self.alfred = None

    async def start(self, print_banner: bool = True) -> RuntimeState:
        self.context.bind_event_loop()
        state = await self.bootstrap.initialize()
        await self.kernel.boot()
        self.shutdown_mgr = ShutdownManager(state)
        self.alfred = self.bootstrap.brain
        self.cli = JarvisCLI(
            kernel=self.kernel,
            mission_manager=getattr(self.bootstrap, "mission_mgr", None),
            evolution_engine=None,
            runtime_context=self.context,
            daemon=self.daemon,
        )

        if print_banner:
            self.bootstrap.print_startup_banner()
        return state

    async def process_task(self, user_request: str) -> Dict[str, Any]:
        if not self.cli:
            await self.start(print_banner=False)
        return await self.cli.handle_command_async(f'mission "{user_request}"')

    async def stop(self) -> Dict[str, Any]:
        await self.kernel.shutdown()
        if self.shutdown_mgr:
            return await self.shutdown_mgr.graceful_shutdown()
        return {"status": "STOPPED"}

    def shutdown(self) -> None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.stop())
            else:
                loop.run_until_complete(self.stop())
        except Exception:
            pass


def create_default_runtime(*args, **kwargs) -> JarvisRuntime:
    """Legacy factory retained as the single RuntimeContext construction path."""
    return JarvisRuntime(*args, **kwargs)
