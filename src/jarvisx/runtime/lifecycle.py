"""Daemon Lifecycle & Graceful Shutdown Handler for Jarvis X."""

from __future__ import annotations
import logging
import signal
import sys
from typing import Callable, List, Optional
from jarvisx.runtime.pid_lock import PIDLockManager
from jarvisx.runtime.state import RuntimeStateManager

logger = logging.getLogger("jarvisx.lifecycle")


class DaemonLifecycleManager:
    """Coordinates clean startup and graceful shutdown hooks."""

    def __init__(self, pid_manager: PIDLockManager, state_manager: RuntimeStateManager):
        self.pid_manager = pid_manager
        self.state_manager = state_manager
        self._shutdown_hooks: List[Callable[[], None]] = []
        self._is_shutting_down = False

    def register_shutdown_hook(self, hook: Callable[[], None]):
        """Register a callback to run during graceful shutdown."""
        self._shutdown_hooks.append(hook)

    def install_signal_handlers(self, on_signal_callback: Optional[Callable[[], None]] = None):
        """Bind SIGINT and SIGTERM handlers."""
        def handle_signal(sig, frame):
            logger.info(f"Received shutdown signal {sig}. Initiating graceful shutdown...")
            if on_signal_callback:
                on_signal_callback()
            self.shutdown()

        try:
            signal.signal(signal.SIGINT, handle_signal)
            signal.signal(signal.SIGTERM, handle_signal)
        except Exception:
            pass  # Some signals cannot be bound in child threads or certain environments

    def shutdown(self):
        """Execute all registered shutdown hooks, release PID lock, and mark state as OFFLINE."""
        if self._is_shutting_down:
            return
        self._is_shutting_down = True

        self.state_manager.update_state(status="STOPPING")

        for hook in reversed(self._shutdown_hooks):
            try:
                hook()
            except Exception as e:
                logger.error(f"Error during shutdown hook: {e}")

        self.pid_manager.release()
        self.state_manager.clear()
        logger.info("Jarvis X Daemon shutdown complete.")
