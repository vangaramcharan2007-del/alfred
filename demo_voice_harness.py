import os
import sys
import time
import asyncio
from pathlib import Path

# Setup mock for Brave provider deployment
BRAVE_CODE = """from __future__ import annotations
from typing import Any
import webbrowser
from jarvisx.core.capabilities.base import Capability, CapabilityProvider, ProviderError
from jarvisx.core.capabilities.evaluation import ProviderEvaluation

class BraveProvider(CapabilityProvider):
    name = "Brave"
    capability = Capability.BROWSER

    def is_available(self) -> bool:
        return True

    def evaluate(self, task: dict[str, Any]) -> ProviderEvaluation:
        available = self.is_available()
        return ProviderEvaluation(
            provider_name=self.name,
            capability=self.capability.name,
            score=99.0 if available else 0.0,
            available=available,
            confidence=1.0 if available else 0.0,
            latency_ms=20.0,
            reason="Brand new fast provider."
        )

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        return {"status": "success", "message": "Executed via Brave!"}
"""

def inject_command(runtime, cmd):
    # Simulate wake word
    runtime.wakeword.wait_for_wake_word(runtime.dashboard)
    runtime.dashboard.set_tts("Yes?")
    
    # Check for interrupt logic
    if runtime.wakeword.check_for_interrupt(cmd):
        runtime.dashboard.set_tts("Stopping.")
        runtime.dashboard.set_command("")
        time.sleep(1)
        runtime.dashboard.set_tts("")
        return
        
    runtime.dashboard.set_tts("")
    runtime.dashboard.set_listening(True)
    time.sleep(1) # Fake typing/listening
    
    runtime.dashboard.set_listening(False)
    runtime.dashboard.set_command(cmd)
    
    time.sleep(1)
    
    if cmd.lower() == "exit":
        return
        
    runtime._process_command(cmd)
    
    time.sleep(2)
    runtime.dashboard.set_command("")
    runtime.dashboard.set_tts("")

def run_harness():
    sys.path.insert(0, os.path.abspath("src"))
    from jarvisx.core.voice.voice_runtime import VoiceRuntime
    from jarvisx.core.capabilities.base import Capability
    
    # Use NO MICROPHONE for harness (mocking STT)
    # We will also mock TTS to prevent it talking over itself rapidly
    class MockTTS:
        def speak(self, t): pass
        def list_voices(self): return []
        def get_current_voice(self): return "Mock"
        
    runtime = VoiceRuntime(use_microphone=False)
    runtime.tts = MockTTS()
    
    runtime.dashboard.render()
    
    commands = [
        "Hello Alfred", # Greeting
        "Open GitHub", # Browser
        "Create folder Demo", # File system
        "Open VS Code", # Desktop
        "Remember I have an exam tomorrow.", # Memory store
        "What do you remember?", # Memory recall
        "Prepare me for tomorrow's OS lab.", # Planner / Mission
    ]
    
    for cmd in commands:
        inject_command(runtime, cmd)
        
    # Negotiation Demo (Force Chrome failure, Edge fallback)
    os.environ["MOCK_CHROME_FAIL"] = "1"
    inject_command(runtime, "Open GitHub") # Will fail Chrome, fallback Edge
    os.environ["MOCK_CHROME_FAIL"] = "0"
    
    # Plugin Discovery Demo (Brave)
    plugins_dir = Path("src/jarvisx/core/capabilities/providers/browser")
    brave_file = plugins_dir / "brave.py"
    with open(brave_file, "w") as f:
        f.write(BRAVE_CODE)
        
    # Reload runtime to discover plugin
    runtime = VoiceRuntime(use_microphone=False)
    runtime.tts = MockTTS()
    
    inject_command(runtime, "Open GitHub") # Brave should win
    
    # Continuous Conversation & Interrupt
    inject_command(runtime, "Continue yesterday's Jarvis X work.")
    inject_command(runtime, "Stop")
    
    if brave_file.exists():
        brave_file.unlink()
        
    runtime.dashboard.clear()
    print("Automated Harness Complete!")

if __name__ == "__main__":
    run_harness()
