"""Jarvis X: 24/7 Background Wake-Word Detection Engine.

Listens continuously for hotwords ("hey jarvis", "hey alfred", "alfred", "jarvis", "nani")
using sounddevice hardware audio stream and triggers autonomous voice callbacks.
"""

from __future__ import annotations
import os
import sys
from typing import Callable, Optional

from jarvisx.voice.sovereign_wake_word_engine import SovereignWakeWordEngine


class WakeWordListener:
    """Continuous low-CPU wake-word listener for 'Hey Jarvis' / 'Hey Alfred'."""

    WAKE_WORDS = ["hey jarvis", "jarvis", "nani", "alfred", "hey alfred", "wake up"]

    def __init__(self, on_wake_callback: Optional[Callable[[], None]] = None):
        self.callback = on_wake_callback
        self.engine = SovereignWakeWordEngine(on_command_callback=self._handle_wake)

    def _handle_wake(self, text: str):
        if self.callback:
            self.callback()

    def check_phrase_for_wakeword(self, phrase: str) -> bool:
        return self.engine.is_wake_phrase(phrase)

    def start_listening_thread(self, callback: Optional[Callable[[], None]] = None):
        if callback:
            self.callback = callback
        self.engine.start_listening(self._handle_wake)
        return self.engine._thread

    def stop(self):
        self.engine.stop_listening()
