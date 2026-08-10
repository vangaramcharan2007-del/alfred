from __future__ import annotations
from typing import Any

from jarvisx.runtime.edge_quantization_manager import EdgeQuantizationManager
from jarvisx.runtime.sovereign_release_manager import SovereignReleaseManager
from jarvisx.runtime.grand_finale_release import GrandFinaleReleaseEngine

__all__ = [
    "JarvisRuntime",
    "create_default_runtime",
    "RuntimeState",
    "RuntimeContext",
    "BootstrapManager",
    "ShutdownManager",
    "MissionRuntime",
    "MissionState",
    "MissionStatus",
    "TaskItem",
    "AgentDispatcher",
    "RecoveryManager",
    "MissionExecutor",
    "EdgeQuantizationManager",
    "SovereignReleaseManager",
    "GrandFinaleReleaseEngine",
]

def __getattr__(name: str) -> Any:
    if name in ("JarvisRuntime", "create_default_runtime"):
        from jarvisx.runtime.runtime import JarvisRuntime, create_default_runtime
        return JarvisRuntime if name == "JarvisRuntime" else create_default_runtime
    elif name == "RuntimeState":
        from jarvisx.runtime.state import RuntimeState
        return RuntimeState
    elif name == "RuntimeContext":
        from jarvisx.runtime.context import RuntimeContext
        return RuntimeContext
    elif name == "BootstrapManager":
        from jarvisx.runtime.bootstrap import BootstrapManager
        return BootstrapManager
    elif name == "ShutdownManager":
        from jarvisx.runtime.shutdown import ShutdownManager
        return ShutdownManager
    elif name in ("MissionState", "MissionStatus", "TaskItem"):
        from jarvisx.runtime.mission_state import MissionState, MissionStatus, TaskItem
        if name == "MissionState":
            return MissionState
        elif name == "MissionStatus":
            return MissionStatus
        return TaskItem
    elif name == "AgentDispatcher":
        from jarvisx.runtime.agent_dispatcher import AgentDispatcher
        return AgentDispatcher
    elif name == "RecoveryManager":
        from jarvisx.runtime.recovery_manager import RecoveryManager
        return RecoveryManager
    elif name in ("MissionRuntime", "MissionExecutor"):
        if name == "MissionExecutor":
            from jarvisx.runtime.mission_executor import MissionExecutor
            return MissionExecutor
        from jarvisx.runtime.mission_runtime import MissionRuntime
        return MissionRuntime
    elif name == "EdgeQuantizationManager":
        from jarvisx.runtime.edge_quantization_manager import EdgeQuantizationManager
        return EdgeQuantizationManager
    elif name == "SovereignReleaseManager":
        from jarvisx.runtime.sovereign_release_manager import SovereignReleaseManager
        return SovereignReleaseManager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
