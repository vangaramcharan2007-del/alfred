"""UI Element Matcher for Phase 93 Computer Use & Vision Layer."""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.vision.ui_state import UIElement, UIState


class UIElementMatcher:
    """Matches semantic natural language queries to target UI elements in the current UIState."""

    def find_target_element(self, query: str, state: UIState) -> Optional[UIElement]:
        """Find the UIElement matching the target description."""
        q_lower = query.lower().strip()

        # 1. Exact or Substring Label Match
        for el in state.elements:
            if q_lower in el.label.lower():
                return el

        # 2. Semantic Token Overlap Match
        q_tokens = set(q_lower.replace("_", " ").split())
        best_match: Optional[UIElement] = None
        best_score = 0.0

        for el in state.elements:
            label_tokens = set(el.label.lower().replace("_", " ").split())
            type_tokens = set(el.type.lower().split())
            overlap = len(q_tokens.intersection(label_tokens | type_tokens))
            if overlap > best_score:
                best_score = float(overlap)
                best_match = el

        if best_match and best_score > 0:
            return best_match

        # 3. Check Windows Titles
        for w in state.windows:
            if any(t in w.title.lower() for t in q_tokens):
                return UIElement(
                    type="window",
                    label=w.title,
                    confidence=0.90,
                    bounding_box=(w.position[0], w.position[1], w.position[0] + w.size[0], w.position[1] + w.size[1]),
                    center_coordinates=(w.position[0] + (w.size[0] // 2), w.position[1] + 20),
                    is_clickable=True
                )

        return None
