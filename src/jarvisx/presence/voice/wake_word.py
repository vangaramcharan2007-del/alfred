from __future__ import annotations
from typing import Tuple

class WakeWordDetector:
    """
    Detects wake-word 'Alfred' in text or audio stream.
    """
    WAKE_WORD = "alfred"

    def detect(self, input_text: str) -> Tuple[bool, str]:
        text_lower = input_text.lower().strip()
        if self.WAKE_WORD in text_lower:
            # Extract command after wake word
            idx = text_lower.find(self.WAKE_WORD)
            remainder = input_text[idx + len(self.WAKE_WORD):].strip(",. ")
            return True, remainder
        return False, ""
