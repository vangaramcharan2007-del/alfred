"""Unit tests for Alfred Startup Announcer (Welcome, Schedule, and Progress)."""

import os
from unittest.mock import MagicMock, patch
import pytest

from jarvisx.startup.startup_announcer import StartupAnnouncer


def test_startup_announcer_generate_briefing_text():
    announcer = StartupAnnouncer()
    text = announcer.generate_briefing_text(persona="ALFRED")
    assert "Welcome Boss!" in text
    assert "Alfred OS is active" in text
    assert "The time is" in text
    assert "Standing by at your service" in text


def test_startup_announcer_announce_with_mock_voice(tmp_path):
    var_dir = str(tmp_path / "var")
    announcer = StartupAnnouncer(var_dir=var_dir)

    with patch("jarvisx.interface.voice_runtime.VoiceRuntimeEngine.speak") as mock_speak:
        res = announcer.announce(persona="ALFRED", speak=True, block=True)
        assert res["status"] == "ANNOUNCED"
        assert res["spoken"] is True
        assert "Welcome Boss!" in res["briefing_text"]
        # Verify log file was written
        log_file = os.path.join(var_dir, "logs", "startup_briefing.log")
        assert os.path.exists(log_file)
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Welcome Boss!" in content


def test_startup_announcer_silent_mode(tmp_path):
    var_dir = str(tmp_path / "var")
    announcer = StartupAnnouncer(var_dir=var_dir)
    res = announcer.announce(persona="ALFRED", speak=False, block=False)
    assert res["status"] == "ANNOUNCED"
    assert res["spoken"] is False
