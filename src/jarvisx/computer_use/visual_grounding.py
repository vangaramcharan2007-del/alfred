"""
Semantic Visual Grounding Matcher for Jarvis X Computer Use.
Maps natural language user intents ("Search bar", "Start button", "Editor", "Close")
to exact screen coordinates and interactive UIA elements.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from jarvisx.computer_use.screen_perception import ScreenPerceptionEngine, UIElementNode


@dataclass
class GroundingMatchResult:
    target_query: str
    element: Optional[UIElementNode]
    center_coords: Tuple[int, int]
    confidence: float
    matched_by: str


class VisualGroundingMatcher:
    """Matches natural language descriptions to real spatial UI coordinates on screen."""

    def __init__(self, perception_engine: Optional[ScreenPerceptionEngine] = None):
        self.perception = perception_engine or ScreenPerceptionEngine()

    def ground_element(
        self,
        target_description: str,
        elements: Optional[List[UIElementNode]] = None,
    ) -> GroundingMatchResult:
        """
        Finds the highest confidence spatial match on screen for the requested target.
        """
        if elements is None:
            snapshot = self.perception.perceive_screen(save_screenshot=False)
            elements = snapshot.elements

        w, h = self.perception.get_screen_resolution()
        query_lower = target_description.lower().strip()
        tokens = set(re.findall(r"\w+", query_lower))

        best_match: Optional[UIElementNode] = None
        best_score = 0.0
        match_strategy = "heuristic_fallback"

        # 1. Exact or Fuzzy Name & Class Match
        for el in elements:
            score = 0.0
            el_name_lower = el.name.lower()
            el_type_lower = el.control_type.lower()
            el_class_lower = el.class_name.lower()

            # Exact name match
            if query_lower in el_name_lower:
                score += 10.0
            
            # Token overlap with name
            name_tokens = set(re.findall(r"\w+", el_name_lower))
            overlap = len(tokens.intersection(name_tokens))
            score += overlap * 4.0

            # Control type match (e.g. user asks for "button")
            if any(t in el_type_lower for t in tokens):
                score += 3.0

            # Class match
            if any(t in el_class_lower for t in tokens):
                score += 2.0

            if score > best_score:
                best_score = score
                best_match = el
                match_strategy = "uia_semantic_match"

        if best_match and best_score >= 3.0:
            conf = min(1.0, best_score / 15.0)
            return GroundingMatchResult(
                target_query=target_description,
                element=best_match,
                center_coords=best_match.center,
                confidence=conf,
                matched_by=match_strategy,
            )

        # 2. Known Spatial Heuristic Anchor (e.g. Start Button, System Tray, Window Center)
        if "start" in query_lower:
            # Windows 11 / 10 Start button location (bottom left or bottom center)
            coords = (w // 2 if w > 1920 else 30, h - 25)
            return GroundingMatchResult(
                target_query=target_description,
                element=None,
                center_coords=coords,
                confidence=0.85,
                matched_by="spatial_anchor_start",
            )
        elif "close" in query_lower or "exit" in query_lower:
            # Top right close button of active window
            coords = (w - 25, 15)
            return GroundingMatchResult(
                target_query=target_description,
                element=None,
                center_coords=coords,
                confidence=0.80,
                matched_by="spatial_anchor_close",
            )
        elif "center" in query_lower or "screen" in query_lower:
            coords = (w // 2, h // 2)
            return GroundingMatchResult(
                target_query=target_description,
                element=None,
                center_coords=coords,
                confidence=0.75,
                matched_by="spatial_anchor_center",
            )

        # Default fallback to center of active screen
        fallback_coords = (w // 2, h // 2)
        return GroundingMatchResult(
            target_query=target_description,
            element=None,
            center_coords=fallback_coords,
            confidence=0.50,
            matched_by="screen_center_fallback",
        )
