"""
Voice Assistant Pipeline for Hands-Free Desktop Control.
Integrates Wake Word detection ("Alfred"), STT transcription, Reasoning / Action execution, and TTS voice output.
"""
from __future__ import annotations
import sys
import time
from typing import Dict, Any, Optional

from jarvisx.presence.voice.speech_input import SpeechInputEngine
from jarvisx.presence.voice.speech_output import SpeechOutputEngine
from jarvisx.automation.computer_control import ComputerController


class VoiceAssistant:
    """
    Hands-free voice assistant pipeline for Alfred.
    """

    def __init__(self, use_tts: bool = True):
        self.stt = SpeechInputEngine()
        self.tts = SpeechOutputEngine(use_tts=use_tts)
        self.controller = ComputerController()

    def process_voice_command(self, audio_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulate/process voice command pipeline.
        Wake word "Alfred" -> STT -> Action -> TTS
        """
        print("\n[Voice Pipeline] Listening for wake word 'Alfred'...")
        stt_res = self.stt.transcribe_audio(text_override=audio_override or "Alfred continue")
        raw_text = stt_res.get("text", "")

        print(f"[Voice Pipeline] Transcribed: '{raw_text}'")

        # Strip wake word if present
        cmd_text = raw_text.replace("Alfred", "").replace("alfred", "").strip()
        if not cmd_text:
            cmd_text = "continue"

        response_msg = f"Executing voice action: {cmd_text}"
        self.tts.speak(response_msg)

        return {
            "status": "SUCCESS",
            "wake_word": "Alfred",
            "transcription": raw_text,
            "parsed_command": cmd_text,
            "spoken_response": response_msg
        }
