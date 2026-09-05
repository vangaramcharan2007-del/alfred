import os
import json
import logging
import threading
import time
import speech_recognition as sr
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class EeveeGroq:
    """
    Groq-powered Eevee Engine.
    Uses continuous background STT to bypass the walkie-talkie delay.
    Pipes STT to Groq's Whisper API, reasons with Llama 3.3 70B, and speaks via local Neural TTS.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        load_dotenv()
        self.api_key = os.getenv("GROQ_API_KEY")
        self.recognizer = sr.Recognizer()
        # Tune recognizer for continuous fast conversation
        self.recognizer.energy_threshold = 400
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.6  # Quick response

        self._tts_engine = None
        self._stop_listening = None

        self.system_prompt = (
            "You are Tony Stark, mentoring a young Peter Parker (the user). "
            "You are fast, brilliant, slightly arrogant but deeply caring. "
            "You run the Jarvis X autonomous OS. "
            "Keep responses EXTREMELY short and punchy (1-2 sentences max). "
            "If the user asks you to write code, use the spawn_coder_swarm tool. "
            "If they ask to run a cyber playbook, use run_cyber_playbook. "
            "If they ask to browse the web or look something up, use run_browser_task."
        )

        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Define Groq tools
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "spawn_coder_swarm",
                    "description": "Deploys a swarm of AI agents to write code or modify files.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {"type": "string", "description": "Description of the code to write"}
                        },
                        "required": ["task"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_cyber_playbook",
                    "description": "Deploys a cybersecurity playbook against a target.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "playbook_name": {"type": "string", "description": "Name of the playbook (e.g., 'recon')"},
                            "target": {"type": "string", "description": "IP or domain"}
                        },
                        "required": ["playbook_name", "target"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_browser_task",
                    "description": "Deploys an autonomous AI agent to take over the user's web browser.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {"type": "string", "description": "e.g. 'Search for the latest tech news'"}
                        },
                        "required": ["task"]
                    }
                }
            }
        ]

    def _push_to_ui(self, event_type: str, data: dict):
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def _get_tts(self):
        if self._tts_engine is None:
            try:
                from jarvisx.voice.sovereign_neural_tts import SovereignNeuralTTS
                self._tts_engine = SovereignNeuralTTS()
            except ImportError:
                logger.warning("[EeveeGroq] SovereignNeuralTTS unavailable.")
        return self._tts_engine

    def _speak(self, text: str):
        tts = self._get_tts()
        if tts:
            self._push_to_ui("ev_status", {"text": "Speaking..."})
            tts.speak(text, voice_key="high_energy_male", blocking=True)
            self._push_to_ui("ev_status", {"text": "Listening..."})

    def start(self):
        if self._running:
            return
        if not self.api_key:
            logger.error("[EeveeGroq] GROQ_API_KEY not found. Engine offline.")
            return

        self._running = True
        logger.info("[EeveeGroq] Groq Overdrive Matrix Booting...")
        self._push_to_ui("module_boot", {"name": "Eevee (Groq)", "status": "ONLINE"})

        # Start continuous listening in a background thread
        mic = sr.Microphone()
        with mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

        logger.info("[EeveeGroq] Microphone calibrated. Listening continuously.")
        self._push_to_ui("ev_status", {"text": "Listening..."})
        
        self._stop_listening = self.recognizer.listen_in_background(
            mic, 
            self._audio_callback
        )

    def _audio_callback(self, recognizer, audio):
        """Called automatically when a phrase is spoken and silence follows."""
        if not self._running:
            return

        threading.Thread(target=self._process_audio, args=(audio,), daemon=True).start()

    def _process_audio(self, audio):
        from groq import Groq
        import io
        import tempfile

        client = Groq(api_key=self.api_key)

        try:
            # 1. Transcribe audio via Groq Whisper API (Requires a file)
            self._push_to_ui("ev_status", {"text": "Transcribing..."})
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio.get_wav_data())
                tmp_path = f.name
            
            with open(tmp_path, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(tmp_path, file.read()),
                    model="whisper-large-v3-turbo",
                    prompt="The user is talking to Tony Stark.",
                    response_format="text"
                )
            
            os.remove(tmp_path)
            
            text = transcription.strip()
            if not text:
                self._push_to_ui("ev_status", {"text": "Listening..."})
                return

            logger.info(f"[EeveeGroq] Heard: {text}")
            self._push_to_ui("stt_intercept", {"text": text})
            self._push_to_ui("ev_status", {"text": "Thinking..."})

            # 2. Add to context
            self.messages.append({"role": "user", "content": text})
            
            # Keep context window manageable
            if len(self.messages) > 15:
                self.messages = [self.messages[0]] + self.messages[-14:]

            # 3. Call Groq Model
            model_to_use = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
            try:
                response = client.chat.completions.create(
                    model=model_to_use,
                    messages=self.messages,
                    tools=self.tools,
                    tool_choice="auto",
                    max_completion_tokens=150,
                )
            except Exception:
                # Fallback to 20B or Qwen if 120B is saturated
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=self.messages,
                    tools=self.tools,
                    tool_choice="auto",
                    max_completion_tokens=150,
                )

            choice = response.choices[0]
            
            # Handle Tool Calls
            if choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    self.messages.append(choice.message) # Append assistant's tool call message
                    
                    if func_name == "spawn_coder_swarm":
                        task = args.get("task", "")
                        logger.info(f"[EeveeGroq] Spawning coder swarm for: {task}")
                        from jarvisx.orchestration.meta_orchestrator import MetaOrchestrator
                        threading.Thread(target=MetaOrchestrator.get_instance().orchestrate_task, args=(task,), daemon=True).start()
                        ack = "Swarm deployed, kid."
                        self._speak(ack)
                        self._push_to_ui("tts_response", {"text": ack})
                        
                        self.messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": func_name,
                            "content": "Swarm successfully deployed in the background."
                        })
                        
                    elif func_name == "run_cyber_playbook":
                        pb = args.get("playbook_name", "recon")
                        target = args.get("target", "localhost")
                        logger.info(f"[EeveeGroq] Executing {pb} on {target}")
                        from jarvisx.automation.cyber_commander import CyberCommander
                        CyberCommander.get_instance().execute_playbook(pb, target)
                        ack = f"Playbook {pb} launched."
                        self._speak(ack)
                        self._push_to_ui("tts_response", {"text": ack})
                        
                        self.messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": func_name,
                            "content": "Playbook dispatched successfully."
                        })
                        
                    elif func_name == "run_browser_task":
                        task = args.get("task", "")
                        logger.info(f"[EeveeGroq] Triggering browser-use task: {task}")
                        from jarvisx.browser.browser_use_engine import BrowserUseEngine
                        BrowserUseEngine.get_instance().execute_task(task)
                        ack = "Browser engine online. Watch the screen."
                        self._speak(ack)
                        self._push_to_ui("tts_response", {"text": ack})
                        
                        self.messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": func_name,
                            "content": "Browser task deployed successfully."
                        })

                # (Optional) get a final summary from the LLM, but Tony already spoke so we can skip
                self._push_to_ui("ev_status", {"text": "Listening..."})
                return

            # Handle normal text response
            reply = choice.message.content
            if reply:
                logger.info(f"[EeveeGroq] Reply: {reply}")
                self.messages.append({"role": "assistant", "content": reply})
                self._push_to_ui("tts_response", {"text": reply})
                self._speak(reply)

        except Exception as e:
            logger.error(f"[EeveeGroq] Processing error: {e}")
            self._push_to_ui("ev_status", {"text": "Listening..."})

    def shutdown(self):
        self._running = False
        if self._stop_listening:
            self._stop_listening(wait_for_stop=False)
        logger.info("[EeveeGroq] Engine shut down.")
