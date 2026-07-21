import pytest
from unittest.mock import MagicMock
from jarvisx.core.whatsapp.manager import WhatsAppAutomationManager
from jarvisx.core.whatsapp.voice_bridge import WhatsAppVoiceBridge

@pytest.fixture
def mock_whatsapp_manager():
    manager = WhatsAppAutomationManager()
    manager.ui = MagicMock()
    manager.listener = MagicMock()
    manager.downloader = MagicMock()
    manager.uploader = MagicMock()
    manager.converter = MagicMock()
    manager.tts = MagicMock()
    return manager

def test_whatsapp_voice_bridge(mock_whatsapp_manager):
    bridge = WhatsAppVoiceBridge(mock_whatsapp_manager)
    
    reply = bridge.handle_intent("WHATSAPP_START_MONITOR", "monitor whatsapp")
    assert "monitoring WhatsApp" in reply
    
    reply = bridge.handle_intent("WHATSAPP_PAUSE_MONITOR", "pause")
    assert "paused" in reply
    
    reply = bridge.handle_intent("WHATSAPP_STATS", "stats")
    assert "haven't converted any documents" in reply
    
    mock_whatsapp_manager.files_converted_today = 3
    reply = bridge.handle_intent("WHATSAPP_STATS", "stats")
    assert "converted 3 Word documents" in reply
