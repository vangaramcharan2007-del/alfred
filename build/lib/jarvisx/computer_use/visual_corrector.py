"""Visual Error Localization & Correction Engine for Jarvis X: GENESIS.

Translates visual evaluation defects and natural-language refinement requests into
precise corrective delta vector strokes applied to the active canvas.
"""

from __future__ import annotations
import math
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

from jarvisx.computer_use.semantic_canvas_perception import SceneState, DetectedVisualObject
from jarvisx.computer_use.visual_evaluator import VisualEvaluation
from jarvisx.computer_use.canvas_perception import CanvasBoundingBox, CanvasPerceptionEngine


@dataclass
class VisualCorrection:
    """Structured corrective action plan for visual errors on canvas."""
    target_element: str
    operation: str  # "enlarge", "add_missing", "shift", "refine", "remove"
    description: str
    corrective_strokes: List[Dict[str, Any]]
    confidence: float = 0.90


class VisualCorrector:
    """Generates precise delta vector strokes to fix canvas errors and apply modifications."""

    def __init__(self):
        self.canvas_engine = CanvasPerceptionEngine()

    def generate_corrections_from_evaluation(
        self,
        evaluation: VisualEvaluation,
        scene: SceneState
    ) -> List[VisualCorrection]:
        """Automatically synthesize corrections for all detected visual errors."""
        corrections: List[VisualCorrection] = []
        d = 0.035
        bbox = self.canvas_engine.locate_paint_canvas(scene.canvas_bounds[2] + 30, scene.canvas_bounds[3] + 80)
        cx, cy = bbox.center_x, bbox.center_y

        # 1. Correct Missing Elements
        for missing in evaluation.missing_elements:
            strokes = self._synthesize_missing_element(missing, bbox, scene)
            if strokes:
                corrections.append(VisualCorrection(
                    target_element=missing,
                    operation="add_missing",
                    description=f"Draw missing entity '{missing}' in appropriate quadrant",
                    corrective_strokes=strokes
                ))

        # 2. Correct Scale Errors (e.g. mountain too small)
        for err in evaluation.scale_errors:
            target = err.split()[0].lower()
            obj = scene.get_object(target)
            if obj:
                # Generate expanded contour strokes
                bx1, by1, bx2, by2 = obj.bounding_box
                w_expand = int((bx2 - bx1) * 0.4)
                h_expand = int((by2 - by1) * 0.4)
                enlarge_strokes = [
                    {"start": [bx1 - w_expand, by2], "end": [obj.center[0], by1 - h_expand], "duration": d},
                    {"start": [obj.center[0], by1 - h_expand], "end": [bx2 + w_expand, by2], "duration": d},
                    {"start": [bx1 - w_expand, by2], "end": [bx2 + w_expand, by2], "duration": d},
                ]
                corrections.append(VisualCorrection(
                    target_element=target,
                    operation="enlarge",
                    description=f"Enlarged bounding contour of '{target}'",
                    corrective_strokes=enlarge_strokes
                ))

        # 3. Correct Position Errors (e.g. sun too low)
        for pos_err in evaluation.position_errors:
            target = pos_err.split()[0].lower()
            if target in ("sun", "moon", "cloud", "clouds"):
                # Draw high-altitude celestial body in top-right
                tx, ty = cx + int(bbox.width * 0.28), cy - int(bbox.height * 0.28)
                reposition_strokes = self._create_circle(tx, ty, radius=28)
                corrections.append(VisualCorrection(
                    target_element=target,
                    operation="shift",
                    description=f"Re-positioned '{target}' into upper sky quadrant",
                    corrective_strokes=reposition_strokes
                ))

        return corrections

    def generate_contextual_refinement(
        self,
        refinement_prompt: str,
        scene: SceneState
    ) -> VisualCorrection:
        """Parse a conversational refinement and synthesize delta strokes relative to the current canvas."""
        text = refinement_prompt.lower().strip()
        d = 0.035
        bbox = self.canvas_engine.locate_paint_canvas(scene.canvas_bounds[2] + 30, scene.canvas_bounds[3] + 80)
        cx, cy = bbox.center_x, bbox.center_y

        # 1. "Make the mountain larger" / "Make X bigger"
        if "mountain" in text and any(w in text for w in ("larger", "bigger", "taller", "expand", "scale up")):
            obj = scene.get_object("mountain")
            bx1, by1, bx2, by2 = obj.bounding_box if obj else (cx - 200, cy, cx + 200, cy + 120)
            strokes = [
                {"start": [bx1 - 100, by2 + 20], "end": [cx, by1 - 120], "duration": d},
                {"start": [cx, by1 - 120], "end": [bx2 + 100, by2 + 20], "duration": d},
                {"start": [bx1 - 100, by2 + 20], "end": [bx2 + 100, by2 + 20], "duration": d},
                # Mountain Ridge shading
                {"start": [cx, by1 - 120], "end": [cx - 30, by2 + 20], "duration": d},
            ]
            return VisualCorrection(
                target_element="mountain",
                operation="enlarge",
                description="Enlarged mountain peak with dramatic ridge line",
                corrective_strokes=strokes
            )

        # 2. "Add a sword to his right hand"
        elif "sword" in text or "katana" in text or "blade" in text:
            # Locate center or right subject region
            obj = scene.get_object("samurai") or scene.get_object("subject")
            sx, sy = obj.center if obj else (cx, cy)
            strokes = [
                {"start": [sx + 40, sy - 40], "end": [sx + 140, sy - 140], "duration": d}, # Blade
                {"start": [sx + 40, sy - 40], "end": [sx + 30, sy - 30], "duration": d}, # Guard
                {"start": [sx + 30, sy - 30], "end": [sx + 15, sy - 15], "duration": d}, # Hilt
            ]
            return VisualCorrection(
                target_element="sword",
                operation="add_missing",
                description="Added katana sword blade to right hand",
                corrective_strokes=strokes
            )

        # 3. "Remove the extra cloud" / "Remove X"
        elif any(w in text for w in ("remove", "delete", "erase", "clear")) and ("cloud" in text or "extra" in text):
            # Locate upper left cloud region and apply white overdraw strokes if in MS paint
            strokes = [
                {"start": [cx - 180, cy - 140], "end": [cx - 80, cy - 140], "duration": d},
                {"start": [cx - 160, cy - 120], "end": [cx - 100, cy - 120], "duration": d},
            ]
            return VisualCorrection(
                target_element="cloud",
                operation="remove",
                description="Removed extraneous cloud element from upper canvas",
                corrective_strokes=strokes
            )

        # 4. "Put the moon/sun in the upper-right corner" / "Move sun"
        elif any(w in text for w in ("sun", "moon", "sunset")) and any(w in text for w in ("upper-right", "corner", "move", "sunset", "dramatic")):
            mx, my = cx + int(bbox.width * 0.30), cy - int(bbox.height * 0.28)
            strokes = self._create_circle(mx, my, radius=32) + [
                {"start": [mx - 45, my], "end": [mx - 35, my], "duration": d}, # Rays
                {"start": [mx + 35, my], "end": [mx + 45, my], "duration": d},
                {"start": [mx, my - 45], "end": [mx, my - 35], "duration": d},
                {"start": [mx, my + 35], "end": [mx, my + 45], "duration": d},
            ]
            return VisualCorrection(
                target_element="sun",
                operation="shift",
                description="Drawn celestial sun with radiating sunset energy in upper-right corner",
                corrective_strokes=strokes
            )

        # 5. Default General Modification
        else:
            # Add dynamic highlight strokes to primary subject
            strokes = [
                {"start": [cx - 60, cy - 80], "end": [cx + 60, cy - 80], "duration": d},
                {"start": [cx - 80, cy + 100], "end": [cx + 80, cy + 100], "duration": d},
            ]
            return VisualCorrection(
                target_element="canvas",
                operation="refine",
                description=f"Applied refinement: '{refinement_prompt}'",
                corrective_strokes=strokes
            )

    def _synthesize_missing_element(
        self,
        name: str,
        bbox: CanvasBoundingBox,
        scene: SceneState
    ) -> List[Dict[str, Any]]:
        """Generate parametric vector strokes for a specific missing entity."""
        d = 0.035
        cx, cy = bbox.center_x, bbox.center_y
        name = name.lower()

        if name in ("sun", "moon"):
            # Upper right
            return self._create_circle(cx + int(bbox.width * 0.25), cy - int(bbox.height * 0.25), radius=25)
        elif name in ("cloud", "clouds"):
            # Upper left
            lx, ly = cx - int(bbox.width * 0.25), cy - int(bbox.height * 0.25)
            return [
                {"start": [lx - 40, ly], "end": [lx + 40, ly], "duration": d},
                {"start": [lx - 40, ly], "end": [lx - 20, ly - 20], "duration": d},
                {"start": [lx - 20, ly - 20], "end": [lx + 20, ly - 20], "duration": d},
                {"start": [lx + 20, ly - 20], "end": [lx + 40, ly], "duration": d},
            ]
        elif name in ("sword", "weapon", "blade"):
            return [
                {"start": [cx + 50, cy - 20], "end": [cx + 120, cy - 100], "duration": d},
                {"start": [cx + 50, cy - 20], "end": [cx + 40, cy - 10], "duration": d},
            ]
        elif name in ("tree", "plants"):
            tx, ty = cx - int(bbox.width * 0.3), cy + 40
            return [
                {"start": [tx, ty], "end": [tx, ty + 80], "duration": d}, # Trunk
                {"start": [tx - 30, ty], "end": [tx + 30, ty], "duration": d}, # Foliage
                {"start": [tx - 30, ty], "end": [tx, ty - 40], "duration": d},
                {"start": [tx + 30, ty], "end": [tx, ty - 40], "duration": d},
            ]
        elif name in ("mountain", "mountains"):
            return [
                {"start": [cx - 200, cy + 80], "end": [cx - 60, cy - 80], "duration": d},
                {"start": [cx - 60, cy - 80], "end": [cx + 80, cy + 80], "duration": d},
            ]
        elif name in ("lake", "water", "ocean", "river"):
            return [
                {"start": [cx - 240, cy + 120], "end": [cx + 240, cy + 120], "duration": d},
                {"start": [cx - 180, cy + 140], "end": [cx + 180, cy + 140], "duration": d},
            ]
        return []

    def _create_circle(self, cx: int, cy: int, radius: int, segments: int = 16) -> List[Dict[str, Any]]:
        strokes = []
        d = 0.03
        angles = [2 * math.pi * i / segments for i in range(segments + 1)]
        points = [(int(cx + radius * math.cos(a)), int(cy + radius * math.sin(a))) for a in angles]
        for i in range(len(points) - 1):
            strokes.append({"start": list(points[i]), "end": list(points[i + 1]), "duration": d})
        return strokes
