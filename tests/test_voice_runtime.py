import pytest
from jarvisx.interface.voice_runtime import VoiceRuntimeEngine

def test_voice_runtime_engine():
    engine = VoiceRuntimeEngine()

    res_alfred = engine.speak("Alfred voice test", persona="Alfred")
    assert res_alfred["persona"] == "Alfred"
    assert res_alfred["status"] == "spoken"

    res_friday = engine.speak("Friday voice test", persona="Friday")
    assert res_friday["persona"] == "Friday"
    assert res_friday["status"] == "spoken"

    waveform = engine.generate_waveform_data(text_length=30, samples=32)
    assert len(waveform) == 32
    assert all(0.0 <= val <= 1.0 for val in waveform)
