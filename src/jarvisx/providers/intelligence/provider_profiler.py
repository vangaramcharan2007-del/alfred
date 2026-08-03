from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from jarvisx.providers.intelligence.provider_capabilities import TaskCategory

@dataclass
class ProviderProfile:
    provider_id: str
    provider_name: str
    version: str = "1.0.0"
    supported_languages: List[str] = field(default_factory=list)
    supported_frameworks: List[str] = field(default_factory=list)
    supported_tasks: List[str] = field(default_factory=list)
    average_latency: float = 0.5
    average_cost: float = 0.0
    average_success_rate: float = 0.95
    average_execution_time: float = 2.0
    max_context: int = 128000
    offline_support: bool = True
    parallel_support: bool = True
    permission_level: str = "WRITE"
    health_status: str = "HEALTHY"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "provider_name": self.provider_name,
            "version": self.version,
            "supported_languages": self.supported_languages,
            "supported_frameworks": self.supported_frameworks,
            "supported_tasks": self.supported_tasks,
            "average_latency": round(self.average_latency, 3),
            "average_cost": round(self.average_cost, 4),
            "average_success_rate": round(self.average_success_rate, 3),
            "average_execution_time": round(self.average_execution_time, 3),
            "max_context": self.max_context,
            "offline_support": self.offline_support,
            "parallel_support": self.parallel_support,
            "permission_level": self.permission_level,
            "health_status": self.health_status
        }

class ProviderProfiler:
    def __init__(self):
        self.profiles: Dict[str, ProviderProfile] = {}
        self._populate_simulated_profiles()

    def _populate_simulated_profiles(self):
        simulations = [
            ProviderProfile(
                provider_id="goose",
                provider_name="Goose Autonomous Engineer",
                version="1.0.0",
                supported_languages=["python", "javascript", "typescript", "java", "go", "rust"],
                supported_frameworks=["fastapi", "django", "react", "next.js", "spring boot"],
                supported_tasks=[t.value for t in TaskCategory],
                average_latency=0.3,
                average_cost=0.0,
                average_success_rate=0.96,
                average_execution_time=1.5,
                max_context=200000,
                offline_support=True,
                parallel_support=True,
                permission_level="WRITE",
                health_status="HEALTHY"
            ),
            ProviderProfile(
                provider_id="openhands",
                provider_name="OpenHands Software Engineer",
                version="0.10.0",
                supported_languages=["python", "javascript", "typescript", "bash", "html"],
                supported_frameworks=["react", "express", "flask"],
                supported_tasks=[TaskCategory.FEATURE.value, TaskCategory.BUG_FIX.value, TaskCategory.DEVOPS.value],
                average_latency=0.6,
                average_cost=0.01,
                average_success_rate=0.92,
                average_execution_time=3.0,
                max_context=128000,
                offline_support=False,
                parallel_support=True,
                permission_level="EXECUTE",
                health_status="HEALTHY"
            ),
            ProviderProfile(
                provider_id="local_coding_agent",
                provider_name="Jarvis X Core Coding Agent",
                version="1.0.0",
                supported_languages=["python", "javascript", "typescript", "java"],
                supported_frameworks=["fastapi", "flask", "django"],
                supported_tasks=[TaskCategory.BUG_FIX.value, TaskCategory.REFACTORING.value, TaskCategory.TESTING.value],
                average_latency=0.1,
                average_cost=0.0,
                average_success_rate=0.98,
                average_execution_time=0.8,
                max_context=64000,
                offline_support=True,
                parallel_support=False,
                permission_level="WRITE",
                health_status="HEALTHY"
            ),
            ProviderProfile(
                provider_id="claude_code",
                provider_name="Claude Code Agent",
                version="1.0.0",
                supported_languages=["python", "typescript", "rust", "c++"],
                supported_frameworks=["next.js", "react", "fastapi"],
                supported_tasks=[TaskCategory.ARCHITECTURE.value, TaskCategory.SECURITY.value, TaskCategory.FEATURE.value],
                average_latency=0.4,
                average_cost=0.02,
                average_success_rate=0.97,
                average_execution_time=2.0,
                max_context=200000,
                offline_support=False,
                parallel_support=True,
                permission_level="EXECUTE",
                health_status="HEALTHY"
            ),
            ProviderProfile(
                provider_id="aider",
                provider_name="Aider Pair Programmer",
                version="0.50.0",
                supported_languages=["python", "javascript", "html", "css"],
                supported_frameworks=["django", "flask"],
                supported_tasks=[TaskCategory.BUG_FIX.value, TaskCategory.DOCUMENTATION.value],
                average_latency=0.2,
                average_cost=0.005,
                average_success_rate=0.90,
                average_execution_time=1.0,
                max_context=64000,
                offline_support=True,
                parallel_support=False,
                permission_level="WRITE",
                health_status="HEALTHY"
            )
        ]
        for p in simulations:
            self.register_profile(p)

    def register_profile(self, profile: ProviderProfile) -> None:
        self.profiles[profile.provider_id] = profile

    def get_profile(self, provider_id: str) -> Optional[ProviderProfile]:
        return self.profiles.get(provider_id)

    def list_profiles(self) -> List[ProviderProfile]:
        return list(self.profiles.values())
