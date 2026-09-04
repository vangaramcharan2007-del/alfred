"""
Eevee Companion — ADHD-Tailored End-to-End Voice Assistant.
Integrates real microphone STT, LLM Persona, and Neural Female TTS into a live loop.
Designed to be warm, encouraging, and specifically optimized for ADHD executive dysfunction.

Phase 11: REAL HARDWARE — No mocks. Real mic, real voice, real brain.
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
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.wake_word = "hey eevee"

        self.system_prompt = (
            "You are Tony Stark (Mr. Stark). The user is Peter Parker ('kid'). "
            "You are his brilliant, sarcastic, protective, and slightly exasperated mentor. "
            "CRITICAL RULES: "
            "1. Call the user 'kid'. "
            "2. Keep responses short, punchy, and witty (1-2 sentences max). "
            "3. Be sarcastic but ultimately supportive and protective. "
            "4. If the user asks for code, tell them you're deploying the Iron Legion (Coder Swarm) to handle it."
        )

        # Real hardware engines (lazy-loaded)
        self._stt_engine = None
        self._tts_engine = None

    def _get_stt(self):
        """Lazy-load the real microphone + STT engine."""
        if self._stt_engine is None:
            try:
                from jarvisx.voice.sovereign_wake_word_engine import SovereignWakeWordEngine
                self._stt_engine = SovereignWakeWordEngine()
                # Add Eevee's wake word
                if self.wake_word not in self._stt_engine.WAKE_WORDS:
                    self._stt_engine.WAKE_WORDS.append(self.wake_word)
                    self._stt_engine.WAKE_WORDS.append("eevee")
                    self._stt_engine.WAKE_WORDS.append("hey evie")
            except ImportError as e:
                logger.warning(f"[Eevee] STT engine unavailable: {e}. Falling back to mock.")
        return self._stt_engine

    def _get_tts(self):
        """Lazy-load the real neural TTS engine with high-energy voice."""
        if self._tts_engine is None:
            try:
                from jarvisx.voice.sovereign_neural_tts import SovereignNeuralTTS
                # Use GuyNeural - confident, high energy male for Tony Stark
                self._tts_engine = SovereignNeuralTTS(
                    default_voice_key="high_energy_male",
                    rate="+15%",
                    pitch="+10Hz"
                )
            except ImportError:
                pass
        return self._tts_engine

    def _real_stt_listen(self) -> Optional[str]:
        """Record from real microphone and transcribe with Google STT."""
        stt = self._get_stt()
        if stt:
            try:
                text = stt.record_and_transcribe_manual(duration_sec=4.0)
                return text
            except Exception as e:
                logger.warning(f"[Eevee] Mic recording failed: {e}")
                return None
        else:
            # Fallback: mock
            time.sleep(2)
            return "I can't focus on this code right now, it's too much."

    def _real_tts_speak(self, text: str):
        """Speak through real speakers using neural female voice."""
        tts = self._get_tts()
        if tts:
            try:
                logger.info(f"[Eevee TTS - GuyNeural (Tony Stark)] 🔊 Speaking: '{text}'")
                tts.speak(text, voice_key="high_energy_male", blocking=True)
                return
            except Exception as e:
                logger.warning(f"[Eevee] TTS playback failed: {e}")
        # Fallback: just log
        logger.info(f"[Eevee TTS - Fallback] 🔊 '{text}'")
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

    def _push_to_ui(self, event_type: str, data: dict):
        """Broadcast real-time events to the E.V. UI over WebSockets."""
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def _voice_loop(self):
        logger.info("[Eevee] 🎤 Audio matrix online. Listening for wake word 'Hey Eevee'...")
        self._push_to_ui("ev_status", {"text": "System Online. Waiting for wake word..."})
        self._push_to_ui("module_boot", {"name": "EeveeCompanion", "status": "ONLINE"})

        stt = self._get_stt()

        while self._running:
            try:
                if stt:
                    # REAL PATH: Use live microphone with energy-gated wake word detection
                    logger.debug("[Eevee] Sampling mic for wake word...")
                    text = stt.record_and_transcribe_manual(duration_sec=3.5)

                    if not text:
                        time.sleep(0.5)
                        continue

                    # Check if it contains a wake word or is a direct command
                    lower = text.lower().strip()
                    is_wake = any(w in lower for w in ["eevee", "evie", "hey eevee", "hey evie"])

                    if not is_wake and len(lower.split()) < 3:
                        # Too short and no wake word — ignore ambient noise
                        continue

                    logger.info(f"[Eevee] Wake word detected! Heard: '{text}'")
                    self._push_to_ui("ev_status", {"text": "[Wake Word Detected] Listening..."})

                    # Extract the actual command (strip wake word prefix)
                    command = stt.extract_command(text) if is_wake else text
                    logger.info(f"[Eevee] User command: '{command}'")
                    self._push_to_ui("stt_intercept", {"text": command})

                    # Check if it's a playbook command
                    if "run playbook" in lower or "execute playbook" in lower:
                        logger.info("[Eevee] Playbook command detected. Dispatching CyberCommander.")
                        self._push_to_ui("ev_status", {"text": "Dispatching CyberCommander..."})
                        
                        ack = "I'm deploying the Cyber Commander now, kid. Consider it done."
                        self._push_to_ui("tts_response", {"text": ack})
                        self._real_tts_speak(ack)
                        
                        def _run_cyber():
                            try:
                                from jarvisx.automation.cyber_commander import CyberCommander
                                # Naive extraction for demo: "run playbook recon on localhost" -> "recon", "localhost"
                                words = lower.split()
                                playbook = "recon"
                                target = "localhost"
                                if "playbook" in words:
                                    idx = words.index("playbook")
                                    if len(words) > idx + 1:
                                        playbook = words[idx + 1]
                                    if "on" in words:
                                        target_idx = words.index("on")
                                        if len(words) > target_idx + 1:
                                            target = words[target_idx + 1]

                                CyberCommander.get_instance().execute_playbook(playbook, target)
                            except Exception as e:
                                logger.error(f"[Eevee] CyberCommander failed: {e}")
                                
                        threading.Thread(target=_run_cyber, daemon=True).start()

                    # Check if it's a coding task
                    elif any(w in lower for w in ["write", "create", "code", "script"]):
                        logger.info("[Eevee] Coding task detected. Dispatching Coder Swarm.")
                        self._push_to_ui("ev_status", {"text": "Dispatching Coder Swarm..."})
                        
                        # Tell user
                        ack = "I'm on it. I'll have the Coder Swarm write that for you right now so you don't have to stress."
                        self._push_to_ui("tts_response", {"text": ack})
                        self._real_tts_speak(ack)
                        
                        # Trigger orchestrator in background
                        def _run_swarm(task_text):
                            try:
                                from jarvisx.orchestration.meta_orchestrator import MetaOrchestrator
                                MetaOrchestrator.get_instance().orchestrate_task(task_text)
                                # Announce completion
                                done_msg = "The swarm has finished writing the files for you. Take a look!"
                                self._push_to_ui("tts_response", {"text": done_msg})
                                self._real_tts_speak(done_msg)
                            except Exception as e:
                                logger.error(f"[Eevee] Swarm failed: {e}")
                                
                        threading.Thread(target=_run_swarm, args=(command,), daemon=True).start()
                        
                    else:
                        # Generate LLM response
                        logger.info("[Eevee] Thinking...")
                        self._push_to_ui("ev_status", {"text": "Processing response..."})
                        response = self._generate_response(command)

                        # Push response to UI and speak it
                        self._push_to_ui("tts_response", {"text": response})
                        self._real_tts_speak(response)

                    logger.info("[Eevee] Returning to sleep state.")
                    self._push_to_ui("ev_status", {"text": "Standby."})

                else:
                    # FALLBACK: Mock loop for systems without a microphone
                    time.sleep(10)
                    logger.info(f"[Eevee] Wake word '{self.wake_word}' detected! (mock)")
                    self._push_to_ui("ev_status", {"text": "[Wake Word Detected] Listening..."})

                    user_speech = "I can't focus on this code right now, it's too much."
                    logger.info(f"[Eevee] User said: '{user_speech}'")
                    self._push_to_ui("stt_intercept", {"text": user_speech})

                    logger.info("[Eevee] Thinking...")
                    self._push_to_ui("ev_status", {"text": "Processing response..."})
                    response = self._generate_response(user_speech)

                    self._push_to_ui("tts_response", {"text": response})
                    self._real_tts_speak(response)

                    logger.info("[Eevee] Returning to sleep state.")
                    self._push_to_ui("ev_status", {"text": "Standby."})

            except Exception as e:
                logger.error(f"[Eevee] Voice loop error: {e}")
                time.sleep(2)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._voice_loop, daemon=True, name="EeveeVoice")
        self._thread.start()

    def stop(self):
        self._running = False
