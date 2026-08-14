"""Complex Vector Art Synthesizer for UACC & MS Paint in Jarvis X.

Generates precise geometric stroke sequences for iconic character illustrations:
- Zoro (Anime Samurai with Three Swords & Bandana)
- Iron Man (Mark 85 Helmet & Arc Reactor)
- Batman / Dark Knight Emblem
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple


class ArtSynthesizer:
    """Parametric vector art generator for UACC computer-use stroke execution."""

    @staticmethod
    def generate_zoro_strokes(cx: int, cy: int) -> List[Dict[str, Any]]:
        """Generate high-detail vector strokes for Roronoa Zoro in MS Paint."""
        strokes = []
        d = 0.04  # Fast, crisp stroke speed

        # 1. Bandana / Head Outline
        strokes.append({"start": [cx - 120, cy - 80], "end": [cx + 120, cy - 80], "duration": d})
        strokes.append({"start": [cx - 120, cy - 80], "end": [cx - 140, cy - 40], "duration": d})
        strokes.append({"start": [cx + 120, cy - 80], "end": [cx + 140, cy - 40], "duration": d})
        strokes.append({"start": [cx - 140, cy - 40], "end": [cx + 140, cy - 40], "duration": d}) # Bandana bottom line
        # Bandana knot ties on left
        strokes.append({"start": [cx - 140, cy - 60], "end": [cx - 200, cy - 30], "duration": d})
        strokes.append({"start": [cx - 140, cy - 50], "end": [cx - 190, cy - 10], "duration": d})

        # 2. Jawline & Chin
        strokes.append({"start": [cx - 110, cy - 40], "end": [cx - 80, cy + 60], "duration": d})
        strokes.append({"start": [cx + 110, cy - 40], "end": [cx + 80, cy + 60], "duration": d})
        strokes.append({"start": [cx - 80, cy + 60], "end": [cx, cy + 90], "duration": d})
        strokes.append({"start": [cx + 80, cy + 60], "end": [cx, cy + 90], "duration": d})

        # 3. Fierce Anime Eyes & Iconic Left Eye Scar
        # Left Eye (Scared closed eye)
        strokes.append({"start": [cx - 70, cy - 25], "end": [cx - 25, cy - 20], "duration": d})
        # Vertical Eye Scar across left eye
        strokes.append({"start": [cx - 50, cy - 45], "end": [cx - 45, cy - 5], "duration": d})
        # Right Eye (Sharp piercing gaze)
        strokes.append({"start": [cx + 25, cy - 20], "end": [cx + 70, cy - 25], "duration": d})
        strokes.append({"start": [cx + 35, cy - 15], "end": [cx + 60, cy - 15], "duration": d}) # Under eye
        strokes.append({"start": [cx + 45, cy - 22], "end": [cx + 50, cy - 16], "duration": d}) # Pupil

        # 4. Nose & Fierce Expression
        strokes.append({"start": [cx, cy - 15], "end": [cx - 5, cy + 15], "duration": d})
        strokes.append({"start": [cx - 5, cy + 15], "end": [cx + 5, cy + 15], "duration": d})

        # 5. Katana 1: Wado Ichimonji (Held in Teeth/Mouth)
        # Blade extending horizontally across canvas
        strokes.append({"start": [cx - 280, cy + 35], "end": [cx + 280, cy + 35], "duration": d})
        strokes.append({"start": [cx - 280, cy + 42], "end": [cx + 280, cy + 42], "duration": d})
        # Tsuba (Sword Guard) & Hilt on Right
        strokes.append({"start": [cx + 120, cy + 25], "end": [cx + 120, cy + 52], "duration": d})
        strokes.append({"start": [cx + 120, cy + 38], "end": [cx + 240, cy + 38], "duration": d})

        # 6. Katana 2 & 3: Cross Swords (X-Blade Silhouette in Background)
        # Katana Left diagonal (Sandai Kitetsu)
        strokes.append({"start": [cx - 220, cy - 180], "end": [cx + 180, cy + 220], "duration": d})
        strokes.append({"start": [cx - 215, cy - 180], "end": [cx + 185, cy + 220], "duration": d})
        # Katana Right diagonal (Enma)
        strokes.append({"start": [cx + 220, cy - 180], "end": [cx - 180, cy + 220], "duration": d})
        strokes.append({"start": [cx + 215, cy - 180], "end": [cx - 185, cy + 220], "duration": d})

        # 7. Neck & Kimono Collar
        strokes.append({"start": [cx - 60, cy + 80], "end": [cx - 90, cy + 180], "duration": d})
        strokes.append({"start": [cx + 60, cy + 80], "end": [cx + 90, cy + 180], "duration": d})
        strokes.append({"start": [cx - 90, cy + 180], "end": [cx, cy + 230], "duration": d})
        strokes.append({"start": [cx + 90, cy + 180], "end": [cx, cy + 230], "duration": d})

        return strokes

    @staticmethod
    def generate_ironman_strokes(cx: int, cy: int) -> List[Dict[str, Any]]:
        """Generate vector strokes for Iron Man MK-85 Helmet in MS Paint."""
        strokes = []
        d = 0.04

        # 1. Outer Helmet Contour
        strokes.append({"start": [cx - 100, cy - 120], "end": [cx + 100, cy - 120], "duration": d})
        strokes.append({"start": [cx - 100, cy - 120], "end": [cx - 130, cy - 30], "duration": d})
        strokes.append({"start": [cx + 100, cy - 120], "end": [cx + 130, cy - 30], "duration": d})
        strokes.append({"start": [cx - 130, cy - 30], "end": [cx - 90, cy + 100], "duration": d})
        strokes.append({"start": [cx + 130, cy - 30], "end": [cx + 90, cy + 100], "duration": d})
        strokes.append({"start": [cx - 90, cy + 100], "end": [cx, cy + 130], "duration": d})
        strokes.append({"start": [cx + 90, cy + 100], "end": [cx, cy + 130], "duration": d})

        # 2. Faceplate Seams & Forehead Plate
        strokes.append({"start": [cx - 70, cy - 80], "end": [cx + 70, cy - 80], "duration": d})
        strokes.append({"start": [cx - 70, cy - 80], "end": [cx - 80, cy], "duration": d})
        strokes.append({"start": [cx + 70, cy - 80], "end": [cx + 80, cy], "duration": d})

        # 3. Glowing Angular Optical Slits
        strokes.append({"start": [cx - 65, cy - 10], "end": [cx - 20, cy - 10], "duration": d})
        strokes.append({"start": [cx - 65, cy - 10], "end": [cx - 30, cy], "duration": d})
        strokes.append({"start": [cx - 20, cy - 10], "end": [cx - 30, cy], "duration": d})

        strokes.append({"start": [cx + 20, cy - 10], "end": [cx + 65, cy - 10], "duration": d})
        strokes.append({"start": [cx + 20, cy - 10], "end": [cx + 30, cy], "duration": d})
        strokes.append({"start": [cx + 65, cy - 10], "end": [cx + 30, cy], "duration": d})

        # 4. Jawplate & Mouth Grille
        strokes.append({"start": [cx - 40, cy + 50], "end": [cx + 40, cy + 50], "duration": d})
        strokes.append({"start": [cx - 30, cy + 70], "end": [cx + 30, cy + 70], "duration": d})

        # 5. Arc Reactor Core (Below helmet)
        strokes.append({"start": [cx - 40, cy + 190], "end": [cx + 40, cy + 190], "duration": d})
        strokes.append({"start": [cx + 40, cy + 190], "end": [cx + 40, cy + 250], "duration": d})
        strokes.append({"start": [cx + 40, cy + 250], "end": [cx - 40, cy + 250], "duration": d})
        strokes.append({"start": [cx - 40, cy + 250], "end": [cx - 40, cy + 190], "duration": d})
        # Internal Arc Core Triangle
        strokes.append({"start": [cx, cy + 200], "end": [cx + 25, cy + 240], "duration": d})
        strokes.append({"start": [cx + 25, cy + 240], "end": [cx - 25, cy + 240], "duration": d})
        strokes.append({"start": [cx - 25, cy + 240], "end": [cx, cy + 200], "duration": d})

        return strokes
