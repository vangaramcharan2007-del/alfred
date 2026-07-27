"""Integration test - verify all modules import cleanly."""
from jarvisx.agents.friday import FridayAgent
print("FridayAgent OK")

from jarvisx.api.server import app
print("Server OK")

from jarvisx.core.distraction_vault import GuardianMonitor
print("Guardian OK")

from jarvisx.core.ingestion.campusweb import CampusWebEngine
print("CampusWeb OK")

from jarvisx.core.ingestion.gcr import GCREngine
print("GCR OK")

from jarvisx.core.continuous_voice import ContinuousVoiceEngine
print("VoiceEngine OK")

from jarvisx.core.llm_router import OmniRouterClient
print("OmniRoute OK")

from jarvisx.tools.termux import TermuxTool
print("Termux OK")

print("\n=== ALL MODULES VERIFIED ===")
