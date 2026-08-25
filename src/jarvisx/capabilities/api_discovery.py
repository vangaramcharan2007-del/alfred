"""
Semantic & Keyword API Discovery Engine for Jarvis X.
Allows Alfred to answer: "Find me an API tool capable of doing X."
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from jarvisx.capabilities.registry import APIEndpointSpec, PublicAPICapabilityRegistry


class APIDiscoveryEngine:
    """Discovers matching public APIs based on natural language intent or category."""

    def __init__(self, registry: Optional[PublicAPICapabilityRegistry] = None):
        self.registry = registry or PublicAPICapabilityRegistry()

    def discover_apis_for_query(
        self,
        query: str,
        category: Optional[str] = None,
        max_results: int = 5,
    ) -> List[Tuple[APIEndpointSpec, float]]:
        """
        Discovers and ranks APIs matching the query terms.
        Returns list of (APIEndpointSpec, relevance_score).
        """
        tokens = set(re.findall(r"\w+", query.lower()))
        if not tokens:
            return []

        scored_apis: List[Tuple[APIEndpointSpec, float]] = []

        for spec in self.registry.list_all_apis():
            if category and spec.category.lower() != category.lower():
                continue

            score = 0.0

            # Match against name
            name_tokens = set(re.findall(r"\w+", spec.name.lower()))
            score += len(tokens.intersection(name_tokens)) * 4.0

            # Match against category
            cat_tokens = set(re.findall(r"\w+", spec.category.lower()))
            score += len(tokens.intersection(cat_tokens)) * 3.0

            # Match against tags
            tag_tokens = set(spec.tags)
            score += len(tokens.intersection(tag_tokens)) * 5.0

            # Match against description
            desc_tokens = set(re.findall(r"\w+", spec.description.lower()))
            score += len(tokens.intersection(desc_tokens)) * 1.5

            if score > 0.0:
                scored_apis.append((spec, score))

        # Sort by highest score first
        scored_apis.sort(key=lambda x: x[1], reverse=True)
        return scored_apis[:max_results]
