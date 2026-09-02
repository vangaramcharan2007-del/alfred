"""Visual Memory and Spatial Landmark Cache for Phase 93."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


class VisualMemory:
    """Caches UI spatial coordinates and landmark locations across sessions."""

    def __init__(self, memory_file: str = "var/vision/visual_landmarks.json"):
        self.memory_file = Path(memory_file)
        self.landmarks: Dict[str, Dict[str, Any]] = {}
        self.load_landmarks()

    def load_landmarks(self) -> None:
        if self.memory_file.exists():
            try:
                self.landmarks = json.loads(self.memory_file.read_text(encoding="utf-8"))
            except Exception:
                self.landmarks = {}
        else:
            self.landmarks = {
                "vs_code_icon": {"coordinates": [40, 40], "confidence": 0.98},
                "notepad_icon": {"coordinates": [40, 100], "confidence": 0.95},
                "search_bar": {"coordinates": [190, 1057], "confidence": 0.99},
            }

    def save_landmarks(self) -> None:
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.memory_file.write_text(json.dumps(self.landmarks, indent=2), encoding="utf-8")

    def get_landmark_coordinates(self, label: str) -> Optional[Tuple[int, int]]:
        rec = self.landmarks.get(label.lower().replace(" ", "_"))
        if rec and "coordinates" in rec:
            return (rec["coordinates"][0], rec["coordinates"][1])
        return None

    def store_landmark(self, label: str, coordinates: Tuple[int, int], confidence: float = 0.95) -> None:
        self.landmarks[label.lower().replace(" ", "_")] = {
            "coordinates": list(coordinates),
            "confidence": confidence,
        }
        self.save_graph() if hasattr(self, 'save_graph') else self.save_landmarks()
