import json
import pytest

from jarvisx.adapters.voice_interface import STTProvider, TTSProvider, VoiceManager
from jarvisx.runtime import create_default_runtime


def test_stt_transcription_handling():
    stt = STTProvider()
    
    # Test with valid JSON
    valid_payload = json.dumps({"text": "Hello Jarvis"}).encode("utf-8")
    assert stt.transcribe(valid_payload) == "Hello Jarvis"
    
    # Test with invalid JSON/raw bytes
    invalid_payload = b"Just raw audio bytes"
    assert stt.transcribe(invalid_payload) == "Simulated voice input text"


def test_tts_payload_generation():
    tts = TTSProvider()
    
    # Test Alfred with Focus mode
    mode_config_focus = {"mode": "focus", "pacing": "fast"}
    result_bytes = tts.synthesize("Task complete.", "alfred", mode_config_focus)
    result = json.loads(result_bytes.decode("utf-8"))
    
    assert result["text"] == "Task complete."
    assert result["voice_profile"] == "alfred"
    assert result["mode_config"]["mode"] == "focus"
    
    # Test Edith with Emergency mode
    mode_config_emergency = {"mode": "emergency", "pacing": "urgent"}
    result_bytes_edith = tts.synthesize("Warning.", "edith", mode_config_emergency)
    result_edith = json.loads(result_bytes_edith.decode("utf-8"))
    
    assert result_edith["text"] == "Warning."
    assert result_edith["voice_profile"] == "edith"
    assert result_edith["mode_config"]["mode"] == "emergency"


@pytest.mark.asyncio
async def test_voice_orchestration_flow():
    runtime = create_default_runtime()
    voice_manager = VoiceManager(runtime)
    
    # Simulate an incoming voice command to open youtube (handled by device agent)
    # The STT stub will extract the "text" field
    audio_data = json.dumps({"text": "open youtube"}).encode("utf-8")
    
    audio_out = await voice_manager.process_voice_input(audio_data, trace_id="test-trace-123")
    
    # Verify the audio output contains the correct TTS payload
    result = json.loads(audio_out.decode("utf-8"))
    
    # The device agent should handle it
    assert result["voice_profile"] == "device"
    assert result["status"] == "synthesized"
    
    # Simulate an incoming voice command for planner
    audio_data_planner = json.dumps({"text": "remind me to buy milk"}).encode("utf-8")
    audio_out_planner = await voice_manager.process_voice_input(audio_data_planner, trace_id="test-trace-456")
    
    result_planner = json.loads(audio_out_planner.decode("utf-8"))
    assert result_planner["voice_profile"] == "planner"
