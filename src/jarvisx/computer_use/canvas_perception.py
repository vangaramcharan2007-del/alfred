"""Canvas Perception & Screen Understanding Engine for Jarvis X.

Provides geometric localization of MS Paint and GUI drawing viewports:
- Detects canvas bounding box (excluding ribbons, toolbars, and taskbars)
- Analyzes visual center, usable canvas dimensions, and coordinate transforms
"""

from __future__ import annotations
import sys
import json
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass

try:
    import pyautogui
    HAVE_PYAUTOGUI = True
except Exception:
    HAVE_PYAUTOGUI = False


@dataclass
class CanvasBoundingBox:
    left: int
    top: int
    right: int
    bottom: int
    width: int
    height: int
    center_x: int
    center_y: int


class CanvasPerceptionEngine:
    """Understands screen geometry and locates interactive canvas regions."""

    @staticmethod
    def locate_paint_canvas(screen_w: int = 1920, screen_h: int = 1080) -> CanvasBoundingBox:
        """Calculate the usable drawing canvas rectangle in MS Paint."""
        # In Windows 11/10 MS Paint:
        # - Top ribbon takes ~145-180px
        # - Left margin ~10-20px
        # - Bottom status bar / taskbar ~70-100px
        # - Right scrollbar margin ~20-30px
        top_offset = 180 if screen_h >= 1080 else 150
        bottom_offset = 80
        left_offset = 30
        right_offset = 30

        canvas_left = left_offset
        canvas_top = top_offset
        canvas_right = max(canvas_left + 400, screen_w - right_offset)
        canvas_bottom = max(canvas_top + 300, screen_h - bottom_offset)

        canvas_w = canvas_right - canvas_left
        canvas_h = canvas_bottom - canvas_top
        cx = canvas_left + (canvas_w // 2)
        cy = canvas_top + (canvas_h // 2)

        return CanvasBoundingBox(
            left=canvas_left,
            top=canvas_top,
            right=canvas_right,
            bottom=canvas_bottom,
            width=canvas_w,
            height=canvas_h,
            center_x=cx,
            center_y=cy
        )

    @staticmethod
    def scale_point_to_canvas(norm_x: float, norm_y: float, bbox: CanvasBoundingBox) -> Tuple[int, int]:
        """Convert normalized [-1.0, 1.0] coordinates to absolute pixel coordinates inside canvas."""
        half_w = bbox.width * 0.4
        half_h = bbox.height * 0.4
        px = int(bbox.center_x + (norm_x * half_w))
        py = int(bbox.center_y + (norm_y * half_h))
        return (px, py)
