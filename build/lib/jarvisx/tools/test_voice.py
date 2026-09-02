"""Interactive Diagnostic & Testing Tool for Jarvis X Voice STT & TTS."""

from __future__ import annotations
import time
from jarvisx.interface.voice_duplex_engine import get_voice_duplex_engine

def test_voice_system():
    print("=" * 60)
    print("  JARVIS X: VOICE SYSTEM DIAGNOSTICS & HARDWARE TEST")
    print("=" * 60)
    
    engine = get_voice_duplex_engine()
    
    print("\n[1/2] Testing Text-To-Speech (Speakers)...")
    engine.speak("Hello Charan! Voice synthesis is active and functional.", sync=True)
    print("  -> If you heard the audio through your speakers, TTS is 100% working!")
    
    print("\n[2/2] Testing Speech-To-Text (Microphone)...")
    print("  -> Please speak a sentence into your microphone right now.")
    transcript = engine.listen_and_transcribe()
    print(f"\n[RESULT] Captured Transcript: '{transcript}'")
    
    print("\n" + "=" * 60)
    print("  VOICE TEST COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    test_voice_system()
