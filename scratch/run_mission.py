import sys
import os

# Ensure the src directory is in the python path
sys.path.insert(0, os.path.abspath("src"))

from jarvisx.core.media.orchestrator import CinematicOrchestrator

try:
    from jarvisx.core.voice.tts_engine import TTSEngine
    tts = TTSEngine()
except:
    tts = None

if __name__ == "__main__":
    print("Launching Project Tirupati Cinematic Editor...")
    orchestrator = CinematicOrchestrator(tts_engine=tts)
    success = orchestrator.execute_mission(contact_name="Ravindar vanga")
    if success:
        print("Mission executed successfully.")
    else:
        print("Mission failed.")
