"""UI State Representation for Phase 93 Computer Use & Vision Layer."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Window:
    """Represents an active or background application window."""
    title: str
    position: Tuple[int, int]  # (x, y)
    size: Tuple[int, int]      # (width, height)
    is_active: bool = False
    process_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "position": self.position,
            "size": self.size,
            "is_active": self.is_active,
            "process_name": self.process_name,
        }


@dataclass
class UIElement:
    """Represents a detectable UI element (button, icon, input field, menu item)."""
    type: str  # button, icon, input, window, tab, text
    label: str
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # (left, top, right, bottom)
    center_coordinates: Tuple[int, int]      # (x, y)
    is_clickable: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "label": self.label,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box,
            "center_coordinates": self.center_coordinates,
            "is_clickable": self.is_clickable,
            "metadata": self.metadata,
        }


@dataclass
class UIState:
    """Complete snapshot of the desktop UI state at a specific timestamp."""
    windows: List[Window] = field(default_factory=list)
    elements: List[UIElement] = field(default_factory=list)
    timestamp: float = 0.0
    screen_resolution: Tuple[int, int] = (1920, 1080)
    focused_window: Optional[str] = None

    def find_element_by_label(self, label: str) -> Optional[UIElement]:
        """Find element matching label (case-insensitive substring)."""
        target = label.lower().strip()
        for el in self.elements:
            if target in el.label.lower():
                return el
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "screen_resolution": self.screen_resolution,
            "focused_window": self.focused_window,
            "window_count": len(self.windows),
            "element_count": len(self.elements),
            "windows": [w.to_dict() for w in self.windows],
            "elements": [e.to_dict() for e in self.elements],
        }
