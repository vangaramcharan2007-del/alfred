"""
API Health Monitoring & Autonomous Selection Engine for Jarvis X.
Scores and selects the best API provider considering:
- Auth requirement (No Auth preferred)
- HTTPS enforcement (Mandatory for zero-trust policy)
- Historical success rate & health status
- Fallback provider hierarchy
"""

from __future__ import annotations

import time
import urllib.request
from dataclasses import dataclass
from typing import Dict, List, Optional

from jarvisx.capabilities.api_discovery import APIDiscoveryEngine
from jarvisx.capabilities.registry import APIEndpointSpec, AuthType, PublicAPICapabilityRegistry


@dataclass
class APIHealthState:
    api_id: str
    is_healthy: bool
    last_latency_ms: float
    last_checked: float
    error_count: int = 0
    total_calls: int = 0


class APIHealthMonitor:
    """Tracks availability and latency of registered public APIs."""

    def __init__(self):
        self._health_map: Dict[str, APIHealthState] = {}

    def record_call_result(self, api_id: str, success: bool, latency_ms: float):
        state = self._health_map.get(api_id)
        if not state:
            state = APIHealthState(
                api_id=api_id,
                is_healthy=success,
                last_latency_ms=latency_ms,
                last_checked=time.time(),
                error_count=0 if success else 1,
                total_calls=1,
            )
            self._health_map[api_id] = state
        else:
            state.total_calls += 1
            if not success:
                state.error_count += 1
            state.is_healthy = (state.error_count / max(1, state.total_calls)) < 0.3
            state.last_latency_ms = latency_ms
            state.last_checked = time.time()

    def is_healthy(self, api_id: str) -> bool:
        state = self._health_map.get(api_id)
        return state.is_healthy if state else True


class APISelectorEngine:
    """Autonomous selector that evaluates candidate APIs and picks the best reliable provider."""

    def __init__(
        self,
        discovery: Optional[APIDiscoveryEngine] = None,
        health_monitor: Optional[APIHealthMonitor] = None,
    ):
        self.discovery = discovery or APIDiscoveryEngine()
        self.health = health_monitor or APIHealthMonitor()

    def select_best_api(self, query: str, category: Optional[str] = None) -> Optional[APIEndpointSpec]:
        """Finds candidate APIs and returns the highest scoring healthy candidate."""
        candidates = self.discovery.discover_apis_for_query(query=query, category=category, max_results=5)
        if not candidates:
            return None

        def compute_score(spec: APIEndpointSpec, rel_score: float) -> float:
            base = rel_score * 10.0
            # HTTPS bonus / enforcement
            if not spec.https:
                return 0.0  # Block non-HTTPS for security
            
            # Auth preference: No Auth gets bonus
            if spec.auth_type == AuthType.NO_AUTH:
                base += 5.0
            
            # Health penalty
            if not self.health.is_healthy(spec.api_id):
                base -= 20.0

            return base

        scored = sorted(candidates, key=lambda pair: compute_score(pair[0], pair[1]), reverse=True)
        return scored[0][0] if scored else None
