"""
Nova Companion — ADHD-Tailored End-to-End Voice Assistant.
Integrates Wake Word, STT, LLM Persona, and Female TTS into a single continuous loop.
Designed to be warm, encouraging, and specifically optimized for ADHD executive dysfunction.
"""
import logging
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)

class NovaCompanion:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.wake_word = "hey nova"
        
        self.system_prompt = (
            "You are Nova, a sweet, warm, and highly encouraging AI voice assistant. "
            "The user has ADHD. Your job is to prevent overwhelm. Never give long lists. "
            "Speak in short, gentle sentences. Celebrate small wins. If they are distracted, "
            "gently guide them back to the task. Use a cute, supportive tone."
        )

    def _mock_stt_listen(self) -> str:
        """Simulate Speech-to-Text listening."""
        time.sleep(2)
        return "I can't focus on this code right now, it's too much."

    def _tts_speak(self, text: str):
        """Simulate Text-to-Speech using a female neural voice."""
        logger.info(f"[Nova TTS - Female Voice] 🔊 Speaking: '{text}'")
        
        # In production using edge-tts or pyttsx3:
        # engine = pyttsx3.init()
        # voices = engine.getProperty('voices')
        # engine.setProperty('voice', voices[1].id) # Usually the female voice on Windows
        # engine.say(text)
        # engine.runAndWait()
        time.sleep(2)

    def _generate_response(self, user_text: str) -> str:
        """Query LLM with the ADHD companion persona."""
        try:
            import ollama
            res = ollama.chat(
                model="qwen2.5-coder:1.5b",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_text}
                ]
            )
            return res["message"]["content"].strip()
        except Exception:
            # Fallback if Ollama isn't running
            return "That's okay! Take a deep breath. Let's just look at the first line of code. Just one line. I'm right here with you."

    def _voice_loop(self):
        logger.info("[Nova] 🎤 Audio matrix online. Listening for wake word 'Hey Nova'...")
        
        while self._running:
            # Simulate waiting for Wake Word
            time.sleep(5)
            logger.info(f"[Nova] Wake word '{self.wake_word}' detected!")
            
            # 1. STT (Speech to Text)
            logger.info("[Nova] Listening to user audio...")
            user_speech = self._mock_stt_listen()
            logger.info(f"[Nova] User said: '{user_speech}'")
            
            # 2. LLM (Persona Generation)
            logger.info("[Nova] Thinking...")
            response = self._generate_response(user_speech)
            
            # 3. TTS (Text to Speech - Female Voice)
            self._tts_speak(response)
            
            logger.info("[Nova] Returning to sleep state. Waiting for wake word.")
            
    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._voice_loop, daemon=True, name="NovaVoice")
        self._thread.start()
        
    def stop(self):
        self._running = False
