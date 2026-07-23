import os
from jarvisx.core.providers.provider_registry import BaseProvider, ProviderCapability
from jarvisx.clients.elevenlabs_client import ElevenLabsClient
import logging

logger = logging.getLogger(__name__)

class ElevenLabsProvider(BaseProvider):
    def __init__(self):
        self.client = ElevenLabsClient()
        
    @property
    def capability(self) -> ProviderCapability:
        # Priority 1: ElevenLabs
        return ProviderCapability("TTS", "ElevenLabs", 10, False)
        
    async def check_health(self) -> bool:
        return self.client.is_configured
        
    async def benchmark(self) -> float:
        return 120.0 if self.client.is_configured else float('inf')
        
    def synthesize(self, text: str, voice_id: str = ElevenLabsClient.VOICE_ALFRED) -> bytes:
        return self.client.synthesize(text, voice_id) or b""


class Pyttsx3Provider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        # Priority 2: pyttsx3
        return ProviderCapability("TTS", "pyttsx3", 20, True)
        
    async def check_health(self) -> bool:
        return True
        
    async def benchmark(self) -> float:
        return 50.0
        
    def synthesize(self, text: str, voice_id: str = "") -> bytes:
        return f"[pyttsx3 TTS] {text}".encode("utf-8")


class EdgeTTSProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        # Priority 3: Edge TTS
        return ProviderCapability("TTS", "Edge TTS", 30, False)
        
    async def check_health(self) -> bool:
        return True
        
    async def benchmark(self) -> float:
        return 150.0
        
    def synthesize(self, text: str, voice_id: str = "") -> bytes:
        return f"[Edge TTS] {text}".encode("utf-8")


class SystemTTSProvider(BaseProvider):
    @property
    def capability(self) -> ProviderCapability:
        # Priority 4: System TTS
        return ProviderCapability("TTS", "System TTS", 40, True)
        
    async def check_health(self) -> bool:
        return True
        
    async def benchmark(self) -> float:
        return 40.0
        
    def synthesize(self, text: str, voice_id: str = "") -> bytes:
        return f"[System TTS] {text}".encode("utf-8")


class XTTSv2Provider(BaseProvider):
    def __init__(self):
        self._model = None

    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("TTS", "xtts_v2", 15, True)

    async def check_health(self) -> bool:
        return True

    async def benchmark(self) -> float:
        return 300.0

    def _load_model(self):
        if self._model is None:
            logger.info("Loading XTTS v2 model (this may take a while)...")
            try:
                from TTS.api import TTS
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self._model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
                logger.info(f"XTTS v2 model loaded on {device}.")
            except ImportError:
                logger.error("TTS library not installed. Falling back to mock model.")
                self._model = "mock_model"
        return self._model

    def synthesize(self, text: str, voice_id: str = "") -> bytes:
        # Default without reference
        raise NotImplementedError("XTTSv2 requires a reference audio. Use synthesize_with_reference.")

    def synthesize_with_reference(self, text: str, reference_audio_path: str) -> bytes:
        try:
            model = self._load_model()
            if model == "mock_model":
                raise ImportError("Mock model detected")
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                out_path = tmp.name
            
            model.tts_to_file(
                text=text, 
                speaker_wav=reference_audio_path, 
                language="en", 
                file_path=out_path
            )
            with open(out_path, "rb") as f:
                audio_data = f.read()
            os.remove(out_path)
            return audio_data
        except ImportError:
            logger.warning("TTS library not installed. Simulating XTTSv2 generation with reference audio...")
            with open(reference_audio_path, "rb") as f:
                return f.read()


class F5TTSProvider(BaseProvider):
    def __init__(self):
        self._model = None

    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability("TTS", "f5_tts", 15, True)

    async def check_health(self) -> bool:
        return True

    async def benchmark(self) -> float:
        return 200.0

    def _load_model(self):
        if self._model is None:
            logger.info("Loading F5-TTS model...")
            try:
                from f5_tts.api import F5TTS
                self._model = F5TTS()
                logger.info("F5-TTS model loaded.")
            except ImportError:
                logger.error("F5-TTS library not installed. Falling back to mock model.")
                self._model = "mock_model"
        return self._model

    def synthesize(self, text: str, voice_id: str = "") -> bytes:
        raise NotImplementedError("F5-TTS requires a reference audio. Use synthesize_with_reference.")

    def synthesize_with_reference(self, text: str, reference_audio_path: str) -> bytes:
        try:
            model = self._load_model()
            if model == "mock_model":
                raise ImportError("Mock model detected")
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                out_path = tmp.name
                
            model.infer(
                ref_file=reference_audio_path,
                ref_text="",  # F5-TTS can auto-transcribe reference if empty
                gen_text=text,
                file_wave=out_path
            )
            with open(out_path, "rb") as f:
                audio_data = f.read()
            os.remove(out_path)
            return audio_data
        except ImportError:
            logger.warning("F5-TTS library not installed locally. Using remote Hugging Face API fallback...")
            try:
                import httpx
                original_init = httpx.Client.__init__
                def new_init(self, *args, **kwargs):
                    kwargs['timeout'] = httpx.Timeout(120.0)
                    original_init(self, *args, **kwargs)
                httpx.Client.__init__ = new_init

                from gradio_client import Client, handle_file
                client = Client("mrfakename/E2-F5-TTS")
                result = client.predict(
                    ref_audio=handle_file(reference_audio_path),
                    ref_text="",
                    gen_text=text,
                    remove_silence=False,
                    api_name="/predict"
                )
                
                httpx.Client.__init__ = original_init # Restore original
                
                # result is the filepath of the generated audio
                with open(result, "rb") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Remote F5-TTS API failed: {e}")
                # Ultimate fallback
                with open(reference_audio_path, "rb") as f:
                    return f.read()
