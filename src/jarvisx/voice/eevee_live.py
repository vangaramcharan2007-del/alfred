import os
import asyncio
import logging
import threading
import queue
import pyaudio
from google import genai
from google.genai import types
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Audio configuration required by Gemini Live
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE_IN = 16000
RATE_OUT = 24000
CHUNK = 1024

class EeveeLive:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread = None
        
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        self.system_prompt = (
            "You are Tony Stark (Mr. Stark). The user is Peter Parker ('kid'). "
            "You are his brilliant, sarcastic, protective mentor. "
            "CRITICAL RULES: "
            "1. Call the user 'kid'. "
            "2. Keep responses short, punchy, and witty. "
            "3. Be sarcastic but ultimately supportive. "
            "4. If they ask for code, tell them you're deploying the Coder Swarm."
        )

        self.p = None
        self.stream_in = None
        self.stream_out = None
        self.audio_out_queue = queue.Queue()

    def _push_to_ui(self, event_type: str, data: dict):
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_async_loop, daemon=True, name="EeveeLive")
        self._thread.start()

    def stop(self):
        self._running = False

    def _run_async_loop(self):
        if not self.api_key:
            logger.error("[EeveeLive] GEMINI_API_KEY not found. Eevee Live cannot start.")
            return

        asyncio.run(self._live_session())

    async def _live_session(self):
        logger.info("[EeveeLive] Initializing audio streams...")
        self.p = pyaudio.PyAudio()
        
        try:
            self.stream_in = self.p.open(format=FORMAT,
                                         channels=CHANNELS,
                                         rate=RATE_IN,
                                         input=True,
                                         frames_per_buffer=CHUNK)
            
            self.stream_out = self.p.open(format=FORMAT,
                                          channels=CHANNELS,
                                          rate=RATE_OUT,
                                          output=True)
        except Exception as e:
            logger.error(f"[EeveeLive] PyAudio failed to open streams: {e}")
            return

        # Start background thread to play audio chunks from the queue
        threading.Thread(target=self._audio_player_worker, daemon=True).start()

        client = genai.Client(api_key=self.api_key)
        
        # Define native tools
        run_cyber_tool = {
            "name": "run_cyber_playbook", 
            "description": "Executes a cybersecurity MITRE ATT&CK playbook against a target.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "playbook_name": {"type": "STRING", "description": "e.g. recon, exfiltration, xss"},
                    "target": {"type": "STRING", "description": "e.g. localhost, 192.168.1.5"}
                },
                "required": ["playbook_name", "target"]
            }
        }
        
        spawn_coder_tool = {
            "name": "spawn_coder_swarm",
            "description": "Deploys a swarm of AI agents to write code or modify files.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "task": {"type": "STRING", "description": "Description of the code to write"}
                },
                "required": ["task"]
            }
        }
        
        tools = [{"function_declarations": [run_cyber_tool, spawn_coder_tool]}]
        
        config = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            system_instruction=types.Content(
                parts=[types.Part(text=self.system_prompt)]
            ),
            tools=tools
        )

        logger.info("[EeveeLive] Connecting to gemini-3.1-flash-live-preview WebSocket...")
        self._push_to_ui("ev_status", {"text": "Connecting Live Audio Matrix..."})
        
        try:
            async with client.aio.live.connect(model="gemini-3.1-flash-live-preview", config=config) as session:
                logger.info("[EeveeLive] Live connection established. Full duplex streaming active.")
                self._push_to_ui("module_boot", {"name": "EeveeLive", "status": "ONLINE"})
                self._push_to_ui("ev_status", {"text": "Live Stream Active. Speak naturally."})

                send_task = asyncio.create_task(self._send_mic_data(session))
                video_task = asyncio.create_task(self._send_video_data(session))
                receive_task = asyncio.create_task(self._receive_events(session))
                
                await asyncio.gather(send_task, video_task, receive_task)
        except Exception as e:
            logger.error(f"[EeveeLive] WebSocket session failed: {e}")
        finally:
            self._cleanup()

    async def _send_video_data(self, session):
        loop = asyncio.get_running_loop()
        while self._running:
            try:
                def capture_screen():
                    import io
                    from PIL import ImageGrab
                    img = ImageGrab.grab()
                    # Resize to 720p or similar for bandwidth limits
                    img.thumbnail((1024, 1024))
                    buf = io.BytesIO()
                    img.save(buf, format='JPEG', quality=70)
                    return buf.getvalue()
                    
                frame_bytes = await loop.run_in_executor(None, capture_screen)
                await session.send_realtime_input(
                    video=types.Blob(data=frame_bytes, mime_type="image/jpeg")
                )
            except Exception as e:
                logger.warning(f"[EeveeLive] Video capture error: {e}")
            await asyncio.sleep(1.0)  # 1 FPS to prevent bandwidth saturation

    async def _send_mic_data(self, session):
        loop = asyncio.get_running_loop()
        while self._running:
            try:
                # Read mic without blocking the event loop
                data = await loop.run_in_executor(None, self.stream_in.read, CHUNK, False)
                await session.send_realtime_input(
                    audio=types.Blob(data=data, mime_type="audio/pcm;rate=16000")
                )
            except Exception as e:
                logger.warning(f"[EeveeLive] Mic read error: {e}")
                await asyncio.sleep(0.1)

    async def _receive_events(self, session):
        async for response in session.receive():
            if response.tool_call:
                logger.info("[EeveeLive] Function call intercepted from Gemini.")
                function_responses = []
                for fc in response.tool_call.function_calls:
                    if fc.name == "run_cyber_playbook":
                        # Execute logic
                        args = fc.args if hasattr(fc, 'args') else {}
                        pb = args.get("playbook_name", "recon")
                        target = args.get("target", "localhost")
                        logger.info(f"[EeveeLive] Executing {pb} on {target}")
                        try:
                            from jarvisx.automation.cyber_commander import CyberCommander
                            CyberCommander.get_instance().execute_playbook(pb, target)
                            res_text = "Playbook dispatched successfully."
                        except Exception as e:
                            res_text = f"Failed to dispatch: {e}"
                        
                        function_responses.append(types.FunctionResponse(
                            id=fc.id,
                            name=fc.name,
                            response={"result": res_text}
                        ))
                    elif fc.name == "spawn_coder_swarm":
                        args = fc.args if hasattr(fc, 'args') else {}
                        task_desc = args.get("task", "")
                        logger.info(f"[EeveeLive] Spawning coder swarm for: {task_desc}")
                        try:
                            from jarvisx.orchestration.meta_orchestrator import MetaOrchestrator
                            import threading
                            threading.Thread(target=MetaOrchestrator.get_instance().orchestrate_task, args=(task_desc,), daemon=True).start()
                            res_text = "Coder swarm successfully deployed in the background."
                        except Exception as e:
                            res_text = f"Failed to deploy swarm: {e}"
                            
                        function_responses.append(types.FunctionResponse(
                            id=fc.id,
                            name=fc.name,
                            response={"result": res_text}
                        ))
                        
                if function_responses:
                    await session.send_tool_response(function_responses=function_responses)

            content = response.server_content
            if content:
                # Handle Interruption (VAD)
                if content.interrupted:
                    logger.info("[EeveeLive] Interruption detected! Flushing audio queues.")
                    self._push_to_ui("ev_status", {"text": "Listening..."})
                    # Flush output queue
                    with self.audio_out_queue.mutex:
                        self.audio_out_queue.queue.clear()

                # Handle Audio
                if content.model_turn:
                    self._push_to_ui("ev_status", {"text": "Speaking..."})
                    for part in content.model_turn.parts:
                        if part.inline_data:
                            # Queue audio bytes to be played
                            self.audio_out_queue.put(part.inline_data.data)

                # Handle Text Transcripts (optional)
                if content.input_transcription:
                    self._push_to_ui("stt_intercept", {"text": content.input_transcription.text})
                if content.output_transcription:
                    self._push_to_ui("tts_response", {"text": content.output_transcription.text})

    def _audio_player_worker(self):
        """Dedicated thread to play audio chunks to prevent blocking."""
        while self._running:
            try:
                chunk = self.audio_out_queue.get(timeout=0.5)
                if self.stream_out and chunk:
                    self.stream_out.write(chunk)
            except queue.Empty:
                continue
            except Exception as e:
                logger.warning(f"[EeveeLive] Audio playback error: {e}")

    def _cleanup(self):
        self._running = False
        if self.stream_in:
            self.stream_in.stop_stream()
            self.stream_in.close()
        if self.stream_out:
            self.stream_out.stop_stream()
            self.stream_out.close()
        if self.p:
            self.p.terminate()
        logger.info("[EeveeLive] Audio matrix disconnected.")
