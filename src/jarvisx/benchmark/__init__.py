"""
Alfred Autonomous Mission Benchmark System.
Tests and scores Alfred's real autonomy across core capabilities:
- Mission 001: Python app creation & test execution
- Mission 002: Python project debugging & failure recovery
- Mission 003: Technical research & memory storage
- Mission 004: Academic study plan generation (Friday Engine)
- Mission 005: Desktop workflow automation & safety validation
"""

from jarvisx.benchmark.definitions import get_all_missions, MissionDefinition
from jarvisx.benchmark.runner import BenchmarkRunner
from jarvisx.benchmark.scoring import AutonomyScorer, AutonomyScoreResult
from jarvisx.benchmark.reporter import BenchmarkReporter

__all__ = [
    "get_all_missions",
    "MissionDefinition",
    "BenchmarkRunner",
    "AutonomyScorer",
    "AutonomyScoreResult",
    "BenchmarkReporter"
]
