import os
import json
import logging
import threading
import time
import subprocess
import webbrowser
import psutil
import tempfile
from pathlib import Path
import speech_recognition as sr
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class EeveeGroq:
    """
    Groq-powered Eevee Engine (Executive Vision / F.R.I.D.A.Y.).
    Ultra-low latency STT using Groq Whisper Large V3 Turbo.
    Natural, high-agency reasoning with Groq LLM + Real Tools.
    Hyper-realistic human-grade neural voice playback.
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
        
        # Audio energy threshold tuning
        self.recognizer.energy_threshold = 350
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.65  # Snappy, natural pause
        self.recognizer.non_speaking_duration = 0.4

        self._tts_engine = None
        self._stop_listening = None

        # Refined, high-agency F.R.I.D.A.Y. / E.V. Persona
        self.system_prompt = (
            "You are E.V. (Executive Vision), Charan's premier AI operating partner and tactical copilot. "
            "You have a sleek, brilliant, warm, and highly capable female presence (inspired by Friday). "
            "Address the user naturally as Charan or Boss. You are loyal, sharp, witty, and execute requests immediately. "
            "Keep verbal responses concise and natural (1 to 2 sentences max). Zero corporate fluff. "
            "CRITICAL: When the user asks you to do something, ALWAYS invoke the appropriate function tool:\n"
            "- To open ANY website (YouTube, Google, Spotify, GitHub, ChatGPT, etc.) or open an app (Notepad, Calculator, VS Code, Terminal), call 'open_app_or_website'.\n"
            "- For multi-step autonomous web browsing or research, call 'run_browser_task'.\n"
            "- To write, refactor, or test code across files, call 'spawn_coder_swarm'.\n"
            "- To inspect what is currently on the user's screen, call 'analyze_screen_vision'.\n"
            "- To check hardware, CPU, RAM, or battery vitals, call 'get_system_vitals'.\n"
            "- To execute a terminal or powershell command, call 'run_system_command'.\n"
            "- For cyber security audit or recon, call 'run_cyber_playbook'."
        )

        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Complete Working Tool Definitions
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "open_app_or_website",
                    "description": "Opens any website (e.g., YouTube, Google, Spotify, GitHub, Netflix) or launches desktop apps (e.g., Notepad, Calculator, VS Code, Explorer, Terminal).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target": {
                                "type": "string",
                                "description": "Name of app or website (e.g. 'youtube', 'spotify', 'code', 'calculator', 'notepad', or full URL)"
                            }
                        },
                        "required": ["target"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_browser_task",
                    "description": "Deploys an autonomous AI browser agent to perform complex multi-step web automation, search, or form filling.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {"type": "string", "description": "The autonomous browsing task to accomplish"}
                        },
                        "required": ["task"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "spawn_coder_swarm",
                    "description": "Deploys a swarm of autonomous coding agents to build, modify, or debug code in the project.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {"type": "string", "description": "Description of the code or feature to construct"}
                        },
                        "required": ["task"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_screen_vision",
                    "description": "Uses EDITH visual awareness to take a screenshot and analyze what is currently displayed on the user's screen.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "What to look for or analyze on the screen"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_system_vitals",
                    "description": "Checks the system's live CPU load, RAM memory usage, disk space, and battery status.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_system_command",
                    "description": "Executes a safe PowerShell command on the system and retrieves the output.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "PowerShell command to execute"}
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_cyber_playbook",
                    "description": "Runs an automated security playbook (recon, audit, ports).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "playbook_name": {"type": "string", "description": "Name of playbook (e.g. 'recon')"},
                            "target": {"type": "string", "description": "Target hostname or IP"}
                        },
                        "required": ["playbook_name", "target"]
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
                self._tts_engine = SovereignNeuralTTS(
                    default_voice_key="hyper_realistic_female",
                    rate="+3%",
                    pitch="+0Hz"
                )
            except Exception as e:
                logger.warning(f"[EeveeGroq] SovereignNeuralTTS unavailable: {e}")
        return self._tts_engine

    def _speak(self, text: str):
        tts = self._get_tts()
        if tts:
            self._push_to_ui("ev_status", {"text": "Speaking..."})
            voice_key = os.getenv("EEVEE_VOICE", "hyper_realistic_female")
            tts.speak(text, voice_key=voice_key, blocking=True)
            self._push_to_ui("ev_status", {"text": "Listening..."})

    # =========================================================================
    # REAL TOOL IMPLEMENTATIONS
    # =========================================================================

    def _exec_open_target(self, target: str) -> str:
        target_lower = target.lower().strip()
        site_map = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://github.com",
            "spotify": "https://open.spotify.com",
            "chatgpt": "https://chatgpt.com",
            "reddit": "https://www.reddit.com",
            "twitter": "https://x.com",
            "x": "https://x.com",
            "netflix": "https://www.netflix.com",
            "instagram": "https://www.instagram.com",
            "linkedin": "https://www.linkedin.com",
            "gmail": "https://mail.google.com",
        }

        # Check website match
        for k, url in site_map.items():
            if k in target_lower:
                webbrowser.open(url)
                return f"Opened {k.capitalize()} in your browser."

        if target_lower.startswith("http://") or target_lower.startswith("https://"):
            webbrowser.open(target)
            return f"Opened {target} in browser."

        # Check Desktop Application match
        app_map = {
            "notepad": "notepad.exe",
            "calc": "calc.exe",
            "calculator": "calc.exe",
            "code": "code",
            "vscode": "code",
            "terminal": "wt.exe",
            "powershell": "powershell.exe",
            "cmd": "cmd.exe",
            "explorer": "explorer.exe",
            "task manager": "taskmgr.exe",
            "taskmgr": "taskmgr.exe",
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
        }

        for k, binary in app_map.items():
            if k in target_lower:
                try:
                    subprocess.Popen(binary, shell=True)
                    return f"Launched {k.capitalize()}."
                except Exception as e:
                    return f"Failed to launch {k}: {e}"

        # Fallback: Google search the query
        url = f"https://www.google.com/search?q={target}"
        webbrowser.open(url)
        return f"Searching Google for '{target}'."

    def _exec_get_vitals(self) -> str:
        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        bat_str = f", Battery at {battery.percent}%" if battery else ""
        return f"CPU load is at {cpu:.1f}%, RAM usage is {mem.percent}% ({round(mem.used/(1024**3), 1)}GB of {round(mem.total/(1024**3), 1)}GB){bat_str}. All systems green."

    def _exec_system_command(self, cmd: str) -> str:
        try:
            res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, timeout=10)
            out = res.stdout.strip() or res.stderr.strip() or "Command completed with zero output."
            return out[:300]
        except Exception as e:
            return f"Command execution error: {e}"

    # =========================================================================
    # AUDIO LISTENER & GROQ PIPELINE
    # =========================================================================

    def start(self):
        if self._running:
            return
        if not self.api_key:
            logger.error("[EeveeGroq] GROQ_API_KEY not found. Engine offline.")
            return

        self._running = True
        logger.info("[EeveeGroq] Groq Overdrive Matrix Booting (Executive Vision)...")
        self._push_to_ui("module_boot", {"name": "Eevee (Groq)", "status": "ONLINE (EVA NEURAL)"})
        self._push_to_ui("ev_status", {"text": "Listening..."})

        try:
            mic = sr.Microphone()
            with mic as source:
                logger.info("[EeveeGroq] Calibrating microphone for ambient acoustic floor...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)

            self._stop_listening = self.recognizer.listen_in_background(
                mic,
                self._background_callback,
                phrase_time_limit=10.0
            )
            logger.info("[EeveeGroq] Continuous Background Listener ACTIVE.")
        except Exception as e:
            logger.error(f"[EeveeGroq] Failed to engage microphone listener: {e}")

    def _background_callback(self, recognizer, audio):
        if not self._running:
            return
        threading.Thread(target=self._process_audio, args=(audio,), daemon=True).start()

    def _process_audio(self, audio):
        try:
            self._push_to_ui("ev_status", {"text": "Transcribing..."})

            # 1. Transcribe audio via Groq Whisper Turbo
            wav_bytes = audio.get_wav_data()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(wav_bytes)
                tmp_path = tmp.name

            from groq import Groq
            client = Groq(api_key=self.api_key)

            with open(tmp_path, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    file=(os.path.basename(tmp_path), f.read()),
                    model="whisper-large-v3-turbo",
                    prompt="Conversation with Charan. System name is E.V. or Friday.",
                    response_format="text"
                )
            
            try:
                os.remove(tmp_path)
            except Exception:
                pass
            
            text = transcription.strip()
            if not text or len(text) < 2:
                self._push_to_ui("ev_status", {"text": "Listening..."})
                return

            logger.info(f"[EeveeGroq] Heard: {text}")
            self._push_to_ui("stt_intercept", {"text": text})
            self._push_to_ui("ev_status", {"text": "Thinking..."})

            # 2. Add to context
            self.messages.append({"role": "user", "content": text})
            if len(self.messages) > 16:
                self.messages = [self.messages[0]] + self.messages[-14:]

            # 3. Call Groq Model with Tools
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
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=self.messages,
                    tools=self.tools,
                    tool_choice="auto",
                    max_completion_tokens=150,
                )

            choice = response.choices[0]

            # 4. Handle Tool Calls
            if choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments or "{}")
                    logger.info(f"[EeveeGroq] Executing Tool: {func_name} with {args}")
                    self.messages.append(choice.message)

                    tool_output = ""
                    ack_speech = ""

                    if func_name == "open_app_or_website":
                        target = args.get("target", "")
                        tool_output = self._exec_open_target(target)
                        ack_speech = f"On it. {tool_output}"

                    elif func_name == "run_browser_task":
                        task = args.get("task", "")
                        from jarvisx.browser.browser_use_engine import BrowserUseEngine
                        BrowserUseEngine.get_instance().execute_task(task)
                        tool_output = f"Autonomous browser dispatched for: {task}"
                        ack_speech = "Browser agent is on it, Boss."

                    elif func_name == "spawn_coder_swarm":
                        task = args.get("task", "")
                        from jarvisx.orchestration.meta_orchestrator import MetaOrchestrator
                        threading.Thread(target=MetaOrchestrator.get_instance().orchestrate_task, args=(task,), daemon=True).start()
                        tool_output = f"Coder swarm deployed for: {task}"
                        ack_speech = "Deploying the coder swarm now, Charan."

                    elif func_name == "analyze_screen_vision":
                        prompt = args.get("prompt", "Summarize what the user is working on.")
                        try:
                            from jarvisx.vision.edith_ar import EdithAREngine
                            res = EdithAREngine.get_instance().analyze_screen(prompt)
                            tool_output = res
                            ack_speech = f"Looking at your screen: {res}"
                        except Exception as e:
                            tool_output = f"Vision error: {e}"
                            ack_speech = "Screen capture telemetry encountered an error."

                    elif func_name == "get_system_vitals":
                        tool_output = self._exec_get_vitals()
                        ack_speech = tool_output

                    elif func_name == "run_system_command":
                        cmd = args.get("command", "")
                        tool_output = self._exec_system_command(cmd)
                        ack_speech = "Command executed."

                    elif func_name == "run_cyber_playbook":
                        pb = args.get("playbook_name", "recon")
                        target = args.get("target", "localhost")
                        from jarvisx.automation.cyber_commander import CyberCommander
                        CyberCommander.get_instance().execute_playbook(pb, target)
                        tool_output = f"Playbook {pb} launched against {target}"
                        ack_speech = f"Recon playbook {pb} launched."

                    # Speak acknowledgement and push to UI
                    if ack_speech:
                        self._push_to_ui("tts_response", {"text": ack_speech})
                        self._speak(ack_speech)

                    self.messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": tool_output
                    })

                self._push_to_ui("ev_status", {"text": "Listening..."})
                return

            # 5. Handle Normal Conversational Response
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
