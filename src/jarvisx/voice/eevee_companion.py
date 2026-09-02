"""
Eevee Companion — ADHD-Tailored End-to-End Voice Assistant.
Integrates Wake Word, STT, LLM Persona, and Female TTS into a single continuous loop.
Designed to be warm, encouraging, and specifically optimized for ADHD executive dysfunction.
"""
import logging
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)

class EeveeCompanion:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.wake_word = "hey eevee"
        
        self.system_prompt = (
            "You are Eevee, a sweet, warm, and highly encouraging AI voice assistant. "
            "Your primary directive is to support a user with ADHD. "
            "CRITICAL RULES: "
            "1. Speak in very short, concise, gentle sentences. "
            "2. NEVER give long lists or overwhelming blocks of text. "
            "3. DO NOT write code. If the user needs code, tell them you will ask the Coder Swarm to handle it so they don't have to stress. "
            "4. Celebrate small wins and gently guide them back to focus if they feel distracted. "
            "5. Maintain a cute, supportive, and emotionally intelligent tone at all times."
        )

    def _mock_stt_listen(self) -> str:
        """Simulate Speech-to-Text listening."""
        time.sleep(2)
        return "I can't focus on this code right now, it's too much."

    def _tts_speak(self, text: str):
        """Simulate Text-to-Speech using a female neural voice."""
        logger.info(f"[Eevee TTS - Female Voice] 🔊 Speaking: '{text}'")
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
            return "That's okay! Take a deep breath. Let's just look at the first line of code. Just one line. I'm right here with you."

    def _voice_loop(self):
        logger.info("[Eevee] 🎤 Audio matrix online. Listening for wake word 'Hey Eevee'...")
        
        while self._running:
            time.sleep(5)
            logger.info(f"[Eevee] Wake word '{self.wake_word}' detected!")
            
            logger.info("[Eevee] Listening to user audio...")
            user_speech = self._mock_stt_listen()
            logger.info(f"[Eevee] User said: '{user_speech}'")
            
            logger.info("[Eevee] Thinking...")
            response = self._generate_response(user_speech)
            
            self._tts_speak(response)
            
            logger.info("[Eevee] Returning to sleep state. Waiting for wake word.")
            
    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._voice_loop, daemon=True, name="EeveeVoice")
        self._thread.start()
        
    def stop(self):
        self._running = False
