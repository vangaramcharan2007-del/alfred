from __future__ import annotations
from typing import Any

__all__ = [
    "ProjectIntelligence",
    "RepositoryInfo",
    "ImpactAnalyzer",
    "ImpactReport",
    "ArchitectureReasoner",
    "EngineeringPlan",
    "DynamicToolSelector",
    "EngineeringTool",
    "ToolExecutionResult",
    "DebugLoopEngine",
    "DebugAttempt",
    "DebugResult",
    "ChangeVerifier",
    "ChangeReport",
    "EngineeringMemory",
    "MemoryEntry",
    "AdaptiveEngineeringAgent",
    "WorkflowExecutionReport",
]

def __getattr__(name: str) -> Any:
    if name in ("ProjectIntelligence", "RepositoryInfo"):
        from jarvisx.engineering.intelligence import ProjectIntelligence, RepositoryInfo
        return ProjectIntelligence if name == "ProjectIntelligence" else RepositoryInfo
    elif name in ("ImpactAnalyzer", "ImpactReport"):
        from jarvisx.engineering.impact_analyzer import ImpactAnalyzer, ImpactReport
        return ImpactAnalyzer if name == "ImpactAnalyzer" else ImpactReport
    elif name in ("ArchitectureReasoner", "EngineeringPlan"):
        from jarvisx.engineering.planning import ArchitectureReasoner, EngineeringPlan
        return ArchitectureReasoner if name == "ArchitectureReasoner" else EngineeringPlan
    elif name in ("DynamicToolSelector", "EngineeringTool", "ToolExecutionResult"):
        from jarvisx.engineering.tooling import DynamicToolSelector, EngineeringTool, ToolExecutionResult
        if name == "DynamicToolSelector": return DynamicToolSelector
        elif name == "EngineeringTool": return EngineeringTool
        else: return ToolExecutionResult
    elif name in ("DebugLoopEngine", "DebugAttempt", "DebugResult"):
        from jarvisx.engineering.debug_loop import DebugLoopEngine, DebugAttempt, DebugResult
        if name == "DebugLoopEngine": return DebugLoopEngine
        elif name == "DebugAttempt": return DebugAttempt
        else: return DebugResult
    elif name in ("ChangeVerifier", "ChangeReport"):
        from jarvisx.engineering.verification import ChangeVerifier, ChangeReport
        return ChangeVerifier if name == "ChangeVerifier" else ChangeReport
    elif name in ("EngineeringMemory", "MemoryEntry"):
        from jarvisx.engineering.memory import EngineeringMemory, MemoryEntry
        return EngineeringMemory if name == "EngineeringMemory" else MemoryEntry
    elif name in ("AdaptiveEngineeringAgent", "WorkflowExecutionReport"):
        from jarvisx.engineering.workflow import AdaptiveEngineeringAgent, WorkflowExecutionReport
        return AdaptiveEngineeringAgent if name == "AdaptiveEngineeringAgent" else WorkflowExecutionReport
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
