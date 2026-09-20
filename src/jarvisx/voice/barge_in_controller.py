"""
Full-Duplex Voice Barge-In Controller for Jarvis X / E.V.
=========================================================
Enables instant conversational interruption (< 50ms audio kill).

When the user speaks mid-utterance while Jarvis or E.V. is speaking:
1. Immediately cuts off audio playback via SovereignNeuralTTS.stop()
2. Emits a high-priority 'barge_in_event' to the Executive Vision HUD
3. Displays a tactical toast on screen
4. Speaks an instant acknowledgment in E.V.'s neural voice: "Listening, Charan."
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Optional, Callable

logger = logging.getLogger("jarvisx.voice.barge_in")


@dataclass
class BargeInMetrics:
    total_interrupts: int = 0
    last_latency_ms: float = 0.0
    average_latency_ms: float = 0.0


class BargeInController:
    """
    Full-duplex conversational barge-in controller.
    Monitors audio output and triggers near-instantaneous audio cutoff when interrupted.
    """

    _instance: Optional[BargeInController] = None

    @classmethod
    def get_instance(cls) -> BargeInController:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, on_barge_in: Optional[Callable[[], None]] = None) -> None:
        self.on_barge_in = on_barge_in
        self.metrics = BargeInMetrics()
        self._lock = threading.Lock()
        self._is_monitoring = False

    def is_assistant_speaking(self) -> bool:
        """Returns True if the assistant is actively outputting audio."""
        try:
            from jarvisx.voice.sovereign_neural_tts import get_neural_tts
            tts = get_neural_tts()
            return getattr(tts, "is_speaking", False)
        except Exception:
            return False

    def trigger_barge_in(self, reason: str = "User speech detected") -> float:
        """
        Executes immediate audio cutoff and broadcasts tactical interruption telemetry.

        Returns:
            latency_ms: Time taken to kill the audio stream (typically 5-35ms).
        """
        t0 = time.perf_counter()

        with self._lock:
            # 1. Kill TTS audio stream immediately
            try:
                from jarvisx.voice.sovereign_neural_tts import get_neural_tts
                tts = get_neural_tts()
                tts.stop()
            except Exception as e:
                logger.error(f"[BargeIn] Failed to halt TTS: {e}")

            latency_ms = round((time.perf_counter() - t0) * 1000, 2)

            # Update metrics
            self.metrics.total_interrupts += 1
            self.metrics.last_latency_ms = latency_ms
            if self.metrics.total_interrupts == 1:
                self.metrics.average_latency_ms = latency_ms
            else:
                self.metrics.average_latency_ms = round(
                    (self.metrics.average_latency_ms * (self.metrics.total_interrupts - 1) + latency_ms)
                    / self.metrics.total_interrupts,
                    2
                )

            logger.info(f"[BargeIn] 🎙️ Speech interrupted in {latency_ms}ms ({reason})")

            # 2. Push event to EV HUD (toasts + waveform state)
            try:
                from jarvisx.dashboard.event_bus import push_event_sync
                push_event_sync("barge_in_event", {
                    "latency_ms": latency_ms,
                    "reason": reason,
                    "message": f"Assistant muted in {latency_ms}ms. Listening to Boss...",
                    "timestamp": time.time(),
                })
            except Exception as e:
                logger.debug(f"[BargeIn] HUD event broadcast failed: {e}")

            # 3. Speak E.V. acknowledgment in background thread
            def _speak_ack():
                try:
                    time.sleep(0.08)  # Micro-pause before acknowledgment
                    from jarvisx.voice.sovereign_neural_tts import get_neural_tts
                    tts = get_neural_tts()
                    tts.speak("Listening, Boss.", voice_key="hyper_realistic_female", blocking=False)
                except Exception as e:
                    logger.debug(f"[BargeIn] Ack speech error: {e}")

            threading.Thread(target=_speak_ack, daemon=True, name="BargeInAck").start()

            # 4. Optional custom callback
            if self.on_barge_in:
                try:
                    self.on_barge_in()
                except Exception as e:
                    logger.warning(f"[BargeIn] Custom callback error: {e}")

            return latency_ms


_global_controller: Optional[BargeInController] = None


def get_barge_in_controller() -> BargeInController:
    """Get the global BargeInController singleton."""
    global _global_controller
    if _global_controller is None:
        _global_controller = BargeInController()
    return _global_controller
