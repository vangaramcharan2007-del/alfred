"""
Streaming Voice Activity Detector (VAD) & Energy Monitor for Jarvis X.
Processes real-time 20ms PCM audio frames to detect speech onset and offset in < 30ms.
Enables instant barge-in triggering when user begins speaking.
"""

from __future__ import annotations

import math
import struct
import time
from dataclasses import dataclass
from typing import Callable, List, Optional


@dataclass
class VADFrameResult:
    timestamp: float
    is_speech: bool
    rms_energy: float
    speech_probability: float
    state_transition: Optional[str] = None  # "SPEECH_START", "SPEECH_END", or None


class StreamingVADEngine:
    """Fast real-time Voice Activity Detector with adaptive noise floor."""

    def __init__(
        self,
        energy_threshold: float = 0.025,
        speech_hold_frames: int = 3,
        on_speech_start: Optional[Callable[[], None]] = None,
        on_speech_end: Optional[Callable[[], None]] = None,
    ):
        self.energy_threshold = energy_threshold
        self.speech_hold_frames = speech_hold_frames
        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end

        self._in_speech = False
        self._consecutive_speech_frames = 0
        self._consecutive_silence_frames = 0
        self._noise_floor = 0.005

    def compute_rms(self, pcm_bytes: bytes) -> float:
        """Calculates RMS amplitude of 16-bit mono PCM bytes."""
        if not pcm_bytes:
            return 0.0
        num_samples = len(pcm_bytes) // 2
        if num_samples == 0:
            return 0.0
        try:
            samples = struct.unpack(f"<{num_samples}h", pcm_bytes)
            sum_sq = sum((s / 32768.0) ** 2 for s in samples)
            return math.sqrt(sum_sq / num_samples)
        except Exception:
            return 0.0

    def process_frame(self, pcm_bytes: bytes, timestamp: Optional[float] = None) -> VADFrameResult:
        """
        Processes a single audio chunk (e.g. 20ms - 50ms) and returns VAD state.
        """
        t = timestamp or time.time()
        rms = self.compute_rms(pcm_bytes)

        # Dynamic noise floor tracking
        if not self._in_speech and rms < self.energy_threshold:
            self._noise_floor = (self._noise_floor * 0.95) + (rms * 0.05)

        is_frame_loud = rms > (self.energy_threshold + self._noise_floor)
        prob = min(1.0, max(0.0, (rms - self._noise_floor) / (self.energy_threshold * 2)))

        transition: Optional[str] = None

        if is_frame_loud:
            self._consecutive_speech_frames += 1
            self._consecutive_silence_frames = 0

            if not self._in_speech and self._consecutive_speech_frames >= 2:
                self._in_speech = True
                transition = "SPEECH_START"
                if self.on_speech_start:
                    self.on_speech_start()
        else:
            self._consecutive_silence_frames += 1
            self._consecutive_speech_frames = 0

            if self._in_speech and self._consecutive_silence_frames >= self.speech_hold_frames:
                self._in_speech = False
                transition = "SPEECH_END"
                if self.on_speech_end:
                    self.on_speech_end()

        return VADFrameResult(
            timestamp=t,
            is_speech=self._in_speech,
            rms_energy=round(rms, 4),
            speech_probability=round(prob, 2),
            state_transition=transition,
        )
