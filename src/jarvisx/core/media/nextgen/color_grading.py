from typing import Dict, Any

class CinematicPresets:
    """
    Reusable color grading presets utilizing MLT 'color' and 'lift_gamma_gain' filters.
    """
    PRESETS = {
        "Travel Documentary": {
            "saturation": "1.2",
            "contrast": "1.1",
            "lift_r": "0.01", "lift_g": "0.01", "lift_b": "-0.01",
            "gamma_r": "1.0", "gamma_g": "1.0", "gamma_b": "1.1",
            "gain_r": "1.05", "gain_g": "1.0", "gain_b": "0.95"  # Subtle warm pop
        },
        "Temple Pilgrimage": {
            "saturation": "1.1",
            "contrast": "1.2",
            "lift_r": "0.02", "lift_g": "0.0", "lift_b": "-0.02",
            "gamma_r": "1.05", "gamma_g": "1.0", "gamma_b": "0.95",
            "gain_r": "1.1", "gain_g": "0.95", "gain_b": "0.9"   # Ethereal warm golden look
        },
        "Golden Hour": {
            "saturation": "1.3",
            "contrast": "1.15",
            "lift_r": "0.03", "lift_g": "0.0", "lift_b": "-0.05",
            "gamma_r": "1.1", "gamma_g": "0.95", "gamma_b": "0.85",
            "gain_r": "1.2", "gain_g": "1.0", "gain_b": "0.8"    # Extreme warm sunset wash
        },
        "Family Memories": {
            "saturation": "1.1",
            "contrast": "1.05",
            "lift_r": "0.0", "lift_g": "0.0", "lift_b": "0.0",
            "gamma_r": "1.0", "gamma_g": "1.0", "gamma_b": "1.0",
            "gain_r": "1.0", "gain_g": "1.0", "gain_b": "1.0"    # Very neutral, just slight sat
        }
    }

    @classmethod
    def get_preset(cls, name: str) -> Dict[str, str]:
        return cls.PRESETS.get(name, cls.PRESETS["Family Memories"])
