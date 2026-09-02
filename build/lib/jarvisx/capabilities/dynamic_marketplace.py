"""
Unified Public API Capability Marketplace & Dynamic Router for Jarvis X.
Coordinates:
1. Intent & Capability Matching.
2. Provider Selection & Fallback Hierarchy.
3. Safe Sandboxed Execution.
4. Response Synthesis for Alfred / Voice HUD.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from jarvisx.capabilities.api_discovery import APIDiscoveryEngine
from jarvisx.capabilities.api_executor import APIExecutionResult, SafeAPIExecutor
from jarvisx.capabilities.api_health import APIHealthMonitor, APISelectorEngine
from jarvisx.capabilities.registry import APIEndpointSpec, PublicAPICapabilityRegistry


@dataclass
class MarketplaceTurnResult:
    query: str
    selected_api: Optional[str]
    category: str
    status: str
    result_summary: str
    raw_data: Any
    latency_ms: float
    audit_hash: str


class DynamicAPIMarketplace:
    """Master orchestrator for autonomous API discovery and tool execution."""

    def __init__(
        self,
        registry: Optional[PublicAPICapabilityRegistry] = None,
        health_monitor: Optional[APIHealthMonitor] = None,
    ):
        self.registry = registry or PublicAPICapabilityRegistry()
        self.health = health_monitor or APIHealthMonitor()
        self.discovery = APIDiscoveryEngine(self.registry)
        self.selector = APISelectorEngine(self.discovery, self.health)
        self.executor = SafeAPIExecutor(self.health)

    def route_and_execute_intent(
        self,
        user_intent: str,
        custom_params: Optional[Dict[str, Any]] = None,
    ) -> MarketplaceTurnResult:
        """
        End-to-end dynamic workflow:
        Query -> Match & Select API -> Execute Safe Call -> Summarize Output.
        """
        spec = self.selector.select_best_api(query=user_intent)
        if not spec:
            return MarketplaceTurnResult(
                query=user_intent,
                selected_api=None,
                category="Unknown",
                status="NO_CAPABILITY_FOUND",
                result_summary="No suitable public API found in the capability registry for this request.",
                raw_data=None,
                latency_ms=0.0,
                audit_hash="0" * 64,
            )

        # Execute selected API
        exec_res = self.executor.execute_api_call(spec=spec, custom_params=custom_params)

        # Synthesize a clean human-readable summary
        summary = self._synthesize_summary(spec, exec_res.data)

        return MarketplaceTurnResult(
            query=user_intent,
            selected_api=spec.name,
            category=spec.category,
            status=exec_res.status,
            result_summary=summary,
            raw_data=exec_res.data,
            latency_ms=exec_res.latency_ms,
            audit_hash=exec_res.audit_hash,
        )

    def _synthesize_summary(self, spec: APIEndpointSpec, data: Any) -> str:
        """Transforms raw API JSON responses into concise natural summaries."""
        if not data:
            return f"Executed {spec.name}, but received empty response."

        try:
            if spec.api_id == "open_meteo_weather" and isinstance(data, dict):
                cw = data.get("current_weather", {})
                temp = cw.get("temperature", "N/A")
                wind = cw.get("windspeed", "N/A")
                return f"Weather report from {spec.name}: Current temperature is {temp}°C with wind speed {wind} km/h."
            
            elif spec.api_id == "frankfurter_currency" and isinstance(data, dict):
                rates = data.get("rates", {})
                rates_str = ", ".join(f"{k}: {v}" for k, v in rates.items())
                return f"Foreign exchange rates from {spec.name} (Base {data.get('base', 'USD')}): {rates_str}"
            
            elif spec.api_id == "coingecko_crypto" and isinstance(data, dict):
                entries = []
                for coin, prices in data.items():
                    usd = prices.get("usd", "N/A")
                    entries.append(f"{coin.title()}: ${usd}")
                return f"Live crypto prices from {spec.name}: " + ", ".join(entries)
            
            elif spec.api_id == "open_geocoding" and isinstance(data, dict):
                results = data.get("results", [])
                if results:
                    first = results[0]
                    return f"Geocoding match: {first.get('name')}, {first.get('country')} (Lat: {first.get('latitude')}, Lon: {first.get('longitude')})"
            
            elif spec.api_id == "useless_facts" and isinstance(data, dict):
                return f"Fact: {data.get('text', '')}"
        except Exception:
            pass

        return f"Successfully received live data from {spec.name} ({spec.category})."
