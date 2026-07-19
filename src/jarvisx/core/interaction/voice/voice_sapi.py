import subprocess
import sys
from .base_voice import BaseVoiceAdapter

class SapiVoiceAdapter(BaseVoiceAdapter):
    """
    Windows native SAPI5 Text-to-Speech via pyttsx3.
    Uses subprocess to guarantee completely non-blocking execution on Windows.
    """
    
    def speak(self, text: str, block: bool = False):
        # We run a small one-liner in a new process so it never blocks or crashes the orchestrator COM thread
        code = f"""
import pyttsx3
try:
    engine = pyttsx3.init()
    engine.say({repr(text)})
    engine.runAndWait()
except:
    pass
"""
        if block:
            subprocess.run([sys.executable, "-c", code], capture_output=True)
        else:
            # Fire and forget
            subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
