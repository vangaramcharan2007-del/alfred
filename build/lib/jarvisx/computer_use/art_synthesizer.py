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

    @staticmethod
    def generate_luffy_vs_zoro_strokes(cx: int, cy: int) -> List[Dict[str, Any]]:
        """Generate high-intensity dual character clash vector strokes for Luffy vs Zoro in MS Paint."""
        strokes = []
        d = 0.035

        # -----------------------------------------------------------
        # 1. LEFT FIGHTER: MONKEY D. LUFFY (STRAW HAT PIRATE)
        # -----------------------------------------------------------
        lx = cx - 260
        ly = cy

        # Straw Hat
        strokes.append({"start": [lx - 110, ly - 90], "end": [lx + 90, ly - 90], "duration": d}) # Hat Brim
        strokes.append({"start": [lx - 70, ly - 90], "end": [lx - 60, ly - 150], "duration": d}) # Hat Left Crown
        strokes.append({"start": [lx + 50, ly - 90], "end": [lx + 40, ly - 150], "duration": d}) # Hat Right Crown
        strokes.append({"start": [lx - 60, ly - 150], "end": [lx + 40, ly - 150], "duration": d}) # Hat Top
        strokes.append({"start": [lx - 65, ly - 110], "end": [lx + 45, ly - 110], "duration": d}) # Red Ribbon Band

        # Luffy Spiky Hair
        strokes.append({"start": [lx - 80, ly - 85], "end": [lx - 105, ly - 50], "duration": d})
        strokes.append({"start": [lx - 105, ly - 50], "end": [lx - 70, ly - 40], "duration": d})
        strokes.append({"start": [lx + 60, ly - 85], "end": [lx + 85, ly - 50], "duration": d})
        strokes.append({"start": [lx + 85, ly - 50], "end": [lx + 50, ly - 40], "duration": d})

        # Luffy Face & Jaw
        strokes.append({"start": [lx - 70, ly - 40], "end": [lx - 40, ly + 50], "duration": d})
        strokes.append({"start": [lx + 50, ly - 40], "end": [lx + 20, ly + 50], "duration": d})
        strokes.append({"start": [lx - 40, ly + 50], "end": [lx - 10, ly + 70], "duration": d})
        strokes.append({"start": [lx + 20, ly + 50], "end": [lx - 10, ly + 70], "duration": d})

        # Luffy Eyes & Iconic Under-Eye Stitch Scar
        strokes.append({"start": [lx - 50, ly - 20], "end": [lx - 20, ly - 20], "duration": d}) # Left Eye
        strokes.append({"start": [lx - 40, ly - 10], "end": [lx - 30, ly - 10], "duration": d})
        strokes.append({"start": [lx - 45, ly - 5], "end": [lx - 25, ly - 5], "duration": d}) # Eye Scar Line
        strokes.append({"start": [lx - 35, ly - 8], "end": [lx - 35, ly - 2], "duration": d}) # Stitch tick
        strokes.append({"start": [lx + 10, ly - 20], "end": [lx + 40, ly - 20], "duration": d}) # Right Eye
        strokes.append({"start": [lx + 20, ly - 10], "end": [lx + 30, ly - 10], "duration": d})

        # Luffy Massive Grin
        strokes.append({"start": [lx - 40, ly + 15], "end": [lx + 20, ly + 15], "duration": d})
        strokes.append({"start": [lx - 40, ly + 15], "end": [lx - 10, ly + 35], "duration": d})
        strokes.append({"start": [lx + 20, ly + 15], "end": [lx - 10, ly + 35], "duration": d})

        # Luffy Arm & Gomu Gomu Pistol Fist Clashing Toward Center
        strokes.append({"start": [lx + 30, ly + 30], "end": [cx - 60, ly + 10], "duration": d}) # Arm Top
        strokes.append({"start": [lx + 30, ly + 60], "end": [cx - 60, ly + 40], "duration": d}) # Arm Bottom
        # Giant Fist Knuckles
        strokes.append({"start": [cx - 60, ly - 15], "end": [cx - 15, ly - 15], "duration": d})
        strokes.append({"start": [cx - 15, ly - 15], "end": [cx - 10, ly + 45], "duration": d})
        strokes.append({"start": [cx - 10, ly + 45], "end": [cx - 60, ly + 45], "duration": d})
        strokes.append({"start": [cx - 60, ly + 45], "end": [cx - 60, ly - 15], "duration": d})

        # -----------------------------------------------------------
        # 2. RIGHT FIGHTER: RORONOA ZORO (PIRATE HUNTER & SAMURAI)
        # -----------------------------------------------------------
        zx = cx + 260
        zy = cy

        # Zoro Bandana
        strokes.append({"start": [zx - 90, zy - 90], "end": [zx + 90, zy - 90], "duration": d})
        strokes.append({"start": [zx - 90, zy - 90], "end": [zx - 100, zy - 40], "duration": d})
        strokes.append({"start": [zx + 90, zy - 90], "end": [zx + 100, zy - 40], "duration": d})
        strokes.append({"start": [zx - 100, zy - 40], "end": [zx + 100, zy - 40], "duration": d})
        # Bandana Tails
        strokes.append({"start": [zx + 100, zy - 55], "end": [zx + 160, zy - 20], "duration": d})
        strokes.append({"start": [zx + 100, zy - 45], "end": [zx + 150, zy], "duration": d})

        # Zoro Jaw & Piercing Scowling Face
        strokes.append({"start": [zx - 80, zy - 40], "end": [zx - 50, zy + 50], "duration": d})
        strokes.append({"start": [zx + 80, zy - 40], "end": [zx + 50, zy + 50], "duration": d})
        strokes.append({"start": [zx - 50, zy + 50], "end": [zx, zy + 70], "duration": d})
        strokes.append({"start": [zx + 50, zy + 50], "end": [zx, zy + 70], "duration": d})

        # Zoro Eyes & Vertical Scar
        strokes.append({"start": [zx - 50, zy - 20], "end": [zx - 15, zy - 25], "duration": d}) # Closed Scarred Eye
        strokes.append({"start": [zx - 35, zy - 40], "end": [zx - 30, zy - 5], "duration": d}) # Vertical Slash Scar
        strokes.append({"start": [zx + 15, zy - 25], "end": [zx + 50, zy - 20], "duration": d}) # Sharp Eye
        strokes.append({"start": [zx + 25, zy - 22], "end": [zx + 35, zy - 18], "duration": d})

        # Zoro Santoryu: Mouth Katana (Wado Ichimonji) Clashing Center
        strokes.append({"start": [zx + 80, zy + 25], "end": [cx + 10, zy + 15], "duration": d}) # Mouth Blade
        strokes.append({"start": [zx + 80, zy + 32], "end": [cx + 10, zy + 22], "duration": d})
        strokes.append({"start": [zx + 80, zy + 15], "end": [zx + 80, zy + 42], "duration": d}) # Tsuba
        strokes.append({"start": [zx + 80, zy + 28], "end": [zx + 160, zy + 28], "duration": d}) # Hilt

        # Zoro Santoryu: Dual Overhead Cross Swords (Enma & Kitetsu)
        strokes.append({"start": [zx - 140, zy - 160], "end": [zx + 120, zy + 140], "duration": d})
        strokes.append({"start": [zx + 140, zy - 160], "end": [zx - 120, zy + 140], "duration": d})

        # -----------------------------------------------------------
        # 3. CENTER IMPACT: CONQUEROR'S HAKI & CLASH LIGHTNING
        # -----------------------------------------------------------
        # Impact Starburst / Clash Flash
        strokes.append({"start": [cx, cy - 80], "end": [cx, cy + 80], "duration": d})
        strokes.append({"start": [cx - 80, cy], "end": [cx + 80, cy], "duration": d})
        strokes.append({"start": [cx - 55, cy - 55], "end": [cx + 55, cy + 55], "duration": d})
        strokes.append({"start": [cx + 55, cy - 55], "end": [cx - 55, cy + 55], "duration": d})

        # Conqueror's Haki Jagged Lightning Bolting across Center
        strokes.append({"start": [cx - 10, cy - 100], "end": [cx + 25, cy - 40], "duration": d})
        strokes.append({"start": [cx + 25, cy - 40], "end": [cx - 15, cy + 20], "duration": d})
        strokes.append({"start": [cx - 15, cy + 20], "end": [cx + 30, cy + 90], "duration": d})

        strokes.append({"start": [cx + 20, cy - 110], "end": [cx - 30, cy - 50], "duration": d})
        strokes.append({"start": [cx - 30, cy - 50], "end": [cx + 10, cy + 10], "duration": d})
        strokes.append({"start": [cx + 10, cy + 10], "end": [cx - 25, cy + 100], "duration": d})

        # Top Center "VS" Clash Insignia
        strokes.append({"start": [cx - 30, cy - 180], "end": [cx - 10, cy - 130], "duration": d}) # V
        strokes.append({"start": [cx + 10, cy - 180], "end": [cx - 10, cy - 130], "duration": d})
        strokes.append({"start": [cx + 30, cy - 180], "end": [cx + 15, cy - 165], "duration": d}) # S
        strokes.append({"start": [cx + 15, cy - 165], "end": [cx + 30, cy - 150], "duration": d})
        strokes.append({"start": [cx + 30, cy - 150], "end": [cx + 15, cy - 135], "duration": d})

        return strokes
