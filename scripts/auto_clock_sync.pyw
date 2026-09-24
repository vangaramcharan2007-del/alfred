"""
Jarvis X - Deprecated Legacy Clock Sync Shim
Redirects cleanly to the unified Wallpaper Chameleon Engine.
"""
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = PROJECT_ROOT / "scripts" / "wallpaper_chameleon_engine.py"

if __name__ == "__main__":
    if ENGINE_SCRIPT.exists():
        subprocess.run([sys.executable, str(ENGINE_SCRIPT)], check=False)
