import logging
import asyncio
import io
import wave
import time

try:
    import pyaudio
    from faster_whisper import WhisperModel
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

logger = logging.getLogger(__name__)

class STTEngine:
    def __init__(self, confidence_threshold: float = 0.50):
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.audio = None

    def initialize(self):
        if not HAS_WHISPER:
            logger.warning("faster-whisper or pyaudio missing. STT Engine disabled.")
            return

        try:
            # Load a fast, lightweight model for local execution
            self.model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
            self.audio = pyaudio.PyAudio()
            logger.info("STTEngine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize STTEngine: {e}")

    async def listen_and_transcribe(self, silence_threshold: int = 500, silence_duration: float = 1.5) -> str:
        """
        Records audio until silence is detected, then transcribes.
        """
        if not self.model or not self.audio:
            logger.warning("STT Engine not fully initialized.")
            return ""

        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )

        logger.info("STT listening...")
        frames = []
        silent_chunks = 0
        is_speaking = False
        start_time = time.time()
        max_duration = 15.0 # Stop after 15 seconds max

        while True:
            # Read block
            data = stream.read(1024, exception_on_overflow=False)
            frames.append(data)
            
            # Simple volume/silence detection
            # In a real app, use WebRTC VAD
            audio_data = memoryview(data).cast('h')
            rms = sum(abs(s) for s in audio_data) / len(audio_data)

            if rms > silence_threshold:
                is_speaking = True
                silent_chunks = 0
            elif is_speaking:
                silent_chunks += 1
                
            # If we've been silent for `silence_duration` seconds, stop.
            if is_speaking and silent_chunks > (16000 / 1024 * silence_duration):
                break
                
            if time.time() - start_time > max_duration:
                break
                
            await asyncio.sleep(0.01)

        stream.stop_stream()
        stream.close()

        if not is_speaking:
            return ""

        # Transcribe
        logger.info("Transcribing...")
        audio_bytes = b''.join(frames)
        
        # Save to a temporary memory buffer as a WAV file
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(audio_bytes)
        
        wav_io.seek(0)
        
        # Run transcription in a thread to not block asyncio
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, self._transcribe_sync, wav_io)
        return text

    def _transcribe_sync(self, audio_io):
        segments, info = self.model.transcribe(audio_io, beam_size=1, language="en")
        text = "".join(segment.text for segment in segments).strip()
        
        # Check confidence (faster-whisper provides no prob per word out of the box easily, 
        # but info.language_probability works as a rough proxy, or segment.no_speech_prob)
        # We'll just return text for this MVP.
        return text

    def cleanup(self):
        if self.audio:
            self.audio.terminate()
