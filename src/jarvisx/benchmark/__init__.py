from __future__ import annotations
from typing import Any

__all__ = [
    "get_all_missions",
    "MissionDefinition",
    "BenchmarkRunner",
    "AutonomyScorer",
    "AutonomyScoreResult",
    "BenchmarkReporter",
]

def __getattr__(name: str) -> Any:
    if name in ("get_all_missions", "MissionDefinition"):
        from jarvisx.benchmark.definitions import get_all_missions, MissionDefinition
        return get_all_missions if name == "get_all_missions" else MissionDefinition
    elif name == "BenchmarkRunner":
        from jarvisx.benchmark.runner import BenchmarkRunner
        return BenchmarkRunner
    elif name in ("AutonomyScorer", "AutonomyScoreResult"):
        from jarvisx.benchmark.scoring import AutonomyScorer, AutonomyScoreResult
        return AutonomyScorer if name == "AutonomyScorer" else AutonomyScoreResult
    elif name == "BenchmarkReporter":
        from jarvisx.benchmark.reporter import BenchmarkReporter
        return BenchmarkReporter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
