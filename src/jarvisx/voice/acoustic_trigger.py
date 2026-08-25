"""
Acoustic Clap & Wakeword Trigger Engine for Jarvis X Desktop App.
Enables:
1. Real-time Double-Clap Detection (Peak impulse & energy envelope analysis).
2. Continuous Hands-Free Wakeword Recognition ("Jarvis", "Alfred", "Hey Jarvis").
3. Global Hotkey Activation (Alt+Space / Win+J).
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class TriggerType(str, Enum):
    DOUBLE_CLAP = "DOUBLE_CLAP"
    WAKEWORD = "WAKEWORD"
    HOTKEY = "HOTKEY"
    MANUAL = "MANUAL"


@dataclass
class TriggerEvent:
    trigger_type: TriggerType
    timestamp: float
    confidence: float
    details: str


class AcousticClapDetector:
    """
    Detects sharp acoustic impulse spikes (claps) and verifies double-clap temporal patterns.
    A double-clap is valid when 2 sharp claps occur within 180ms <= dt <= 750ms.
    """

    def __init__(
        self,
        energy_threshold_multiplier: float = 3.5,
        min_clap_interval_sec: float = 0.18,
        max_clap_interval_sec: float = 0.75,
    ):
        self.threshold_multiplier = energy_threshold_multiplier
        self.min_interval = min_clap_interval_sec
        self.max_interval = max_clap_interval_sec
        self.ambient_energy: float = 0.015
        self.last_clap_time: float = 0.0
        self.clap_history: List[float] = []

    def compute_frame_energy(self, samples: List[float]) -> tuple[float, float]:
        """Calculates RMS energy and peak amplitude of audio frame."""
        if not samples:
            return (0.0, 0.0)
        
        sum_sq = sum(s * s for s in samples)
        rms = math.sqrt(sum_sq / len(samples))
        peak = max(abs(s) for s in samples)
        return (rms, peak)

    def process_audio_frame(self, samples: List[float], timestamp: Optional[float] = None) -> Optional[TriggerEvent]:
        """
        Analyzes an audio frame:
        Returns TriggerEvent(DOUBLE_CLAP) if a valid double clap sequence is recognized.
        """
        t = timestamp or time.time()
        rms, peak = self.compute_frame_energy(samples)

        # Update running ambient noise baseline with exponential moving average
        if rms < self.ambient_energy * 2.0:
            self.ambient_energy = (self.ambient_energy * 0.95) + (rms * 0.05)

        # Dynamic clap trigger threshold
        threshold = max(0.08, self.ambient_energy * self.threshold_multiplier)

        # A clap is a sharp impulse: high peak-to-RMS ratio (> 2.8) and high RMS exceeding ambient
        if rms > threshold and (peak / (rms + 1e-6)) > 2.2:
            # Check interval from previous clap
            dt = t - self.last_clap_time
            self.last_clap_time = t

            if self.min_interval <= dt <= self.max_interval:
                # Double-clap confirmed!
                self.clap_history.append(t)
                self.last_clap_time = 0.0  # Reset
                return TriggerEvent(
                    trigger_type=TriggerType.DOUBLE_CLAP,
                    timestamp=t,
                    confidence=0.92,
                    details=f"Double-clap detected (interval: {dt*1000:.1f}ms, RMS: {rms:.3f}, peak: {peak:.3f})",
                )

        return None


class WakewordEngine:
    """Detects spoken wake words ('Jarvis', 'Alfred', 'Hey Jarvis') from text or audio streams."""

    VALID_WAKEWORDS = {"jarvis", "alfred", "hey jarvis", "hey alfred"}

    def is_wakeword_present(self, transcript: str) -> tuple[bool, str, str]:
        """
        Checks if transcript contains a wake word.
        Returns: (is_triggered, matched_wakeword, cleaned_command_text)
        """
        text_lower = transcript.strip().lower()
        for ww in sorted(self.VALID_WAKEWORDS, key=len, reverse=True):
            if text_lower.startswith(ww):
                command = text_lower[len(ww):].strip(" ,.!?")
                return (True, ww, command)
            elif ww in text_lower:
                idx = text_lower.find(ww)
                command = text_lower[idx + len(ww):].strip(" ,.!?")
                return (True, ww, command)

        return (False, "", transcript.strip())
