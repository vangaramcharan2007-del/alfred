from __future__ import annotations
import asyncio
from typing import Dict, Any, Optional

from jarvisx.runtime.bootstrap import BootstrapManager
from jarvisx.runtime.shutdown import ShutdownManager
from jarvisx.runtime.state import RuntimeState
from jarvisx.kernel.runtime_kernel import RuntimeKernel
from jarvisx.interface.cli import JarvisCLI

class JarvisRuntime:
    def __init__(self, config_path: Optional[str] = None):
        self.bootstrap = BootstrapManager(config_path=config_path)
        self.kernel = RuntimeKernel()
        self.shutdown_mgr: Optional[ShutdownManager] = None
        self.cli: Optional[JarvisCLI] = None

    async def start(self, print_banner: bool = True) -> RuntimeState:
        state = await self.bootstrap.initialize()
        await self.kernel.boot()
        self.shutdown_mgr = ShutdownManager(state)
        self.cli = JarvisCLI(
            kernel=self.kernel,
            mission_manager=self.bootstrap.mission_mgr,
            evolution_engine=None
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
