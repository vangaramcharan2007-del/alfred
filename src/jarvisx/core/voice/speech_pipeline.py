import logging
import asyncio

logger = logging.getLogger(__name__)

class SpeechPipeline:
    """
    Streaming speech-to-text pipeline wrapping faster-whisper/Whisper.cpp.
    Supports offline mode, partial transcripts, and speaker interruption.
    Latency target: < 1 second.
    """
    def __init__(self):
        self.transcribing = False
        self.partial_transcript = ""

    async def transcribe_stream(self, audio_stream) -> str:
        """
        Consumes an async generator of audio chunks.
        Yields partial transcripts if needed, returns final transcript.
        """
        self.transcribing = True
        logger.debug("Speech pipeline started transcription.")
        
        # Simulate processing stream
        await asyncio.sleep(0.5)
        
        self.transcribing = False
        return "Simulated full transcript"
        
    def abort_transcription(self):
        """Called when interruption is detected."""
        self.transcribing = False
        self.partial_transcript = ""
        logger.info("Speech transcription aborted.")
