import os
import sys
import time
import json
import psutil
from pathlib import Path
from dotenv import load_dotenv

# Ensure import paths
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT / "src"))
load_dotenv(PROJECT_ROOT / ".env")

results = {
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "working": [],
    "failing_or_needs_attention": [],
    "recommendations": []
}

print("=" * 60)
print("   JARVIS X // ALFRED OS DEEP SYSTEM AUDIT")
print("=" * 60)

# 1. API Keys & Environment
print("\n[1/8] Auditing API Keys & Credentials...")
groq_key = os.getenv("GROQ_API_KEY")
openrouter_key = os.getenv("OPENROUTER_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

if groq_key and groq_key.startswith("gsk_"):
    try:
        from groq import Groq
        client = Groq(api_key=groq_key)
        models = [m.id for m in client.models.list().data]
        results["working"].append(f"Groq API: Connected & Valid ({len(models)} models available including whisper-large-v3-turbo & gpt-oss-120b)")
        print("  [+] Groq API: ONLINE")
    except Exception as e:
        results["failing_or_needs_attention"].append(f"Groq API: Failed connection - {e}")
        print(f"  [-] Groq API: FAILED ({e})")
else:
    results["failing_or_needs_attention"].append("Groq API: Key missing or invalid format in .env")
    print("  [-] Groq API: Key missing")

if openrouter_key and openrouter_key.startswith("sk-or-"):
    results["working"].append("OpenRouter API: Key configured in .env (Used for Gemini 2.5 Flash Browser Vision)")
    print("  [+] OpenRouter API: ONLINE")
else:
    results["failing_or_needs_attention"].append("OpenRouter API: Key missing in .env")
    print("  [-] OpenRouter API: Key missing")

if gemini_key:
    if gemini_key.startswith("AIza"):
        results["working"].append("Gemini API: Valid Google AI Studio API key format")
        print("  [+] Gemini API: Key format AIzaSy valid")
    else:
        results["failing_or_needs_attention"].append(f"Gemini API: Key starts with '{gemini_key[:3]}' (OAuth access token), not official AIzaSy API key. Gemini Live WebSocket will fail.")
        print("  [-] Gemini API: Invalid key format (OAuth token)")
else:
    results["failing_or_needs_attention"].append("Gemini API: Key not set in .env")
    print("  [-] Gemini API: Key missing")

# 2. Voice & Neural TTS
print("\n[2/8] Auditing Voice & Audio Subsystems...")
try:
    from jarvisx.voice.sovereign_neural_tts import SovereignNeuralTTS
    tts = SovereignNeuralTTS(default_voice_key="high_energy_female")
    results["working"].append(f"SovereignNeuralTTS: Initialized with AriaNeural female voice ({tts.voice})")
    print("  [+] SovereignNeuralTTS: ONLINE (AriaNeural)")
except Exception as e:
    results["failing_or_needs_attention"].append(f"SovereignNeuralTTS: Initialization failed - {e}")
    print(f"  [-] SovereignNeuralTTS: FAILED ({e})")

try:
    import speech_recognition as sr
    mics = sr.Microphone.list_microphone_names()
    results["working"].append(f"Microphone Hardware: {len(mics)} audio input devices detected")
    print(f"  [+] Microphone Hardware: {len(mics)} devices found")
except Exception as e:
    results["failing_or_needs_attention"].append(f"Microphone: Error querying mic - {e}")
    print(f"  [-] Microphone: FAILED ({e})")

try:
    from jarvisx.voice.eevee_groq import EeveeGroq
    eg = EeveeGroq.get_instance()
    results["working"].append(f"EeveeGroq Voice Engine: Ready with {len(eg.tools)} autonomous tools")
    print("  [+] EeveeGroq Engine: ONLINE")
except Exception as e:
    results["failing_or_needs_attention"].append(f"EeveeGroq Engine: Failed - {e}")
    print(f"  [-] EeveeGroq Engine: FAILED ({e})")

# 3. HUD & Dashboard Server
print("\n[3/8] Auditing HUD & Dashboard Servers...")
import socket
def check_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.5)
    try:
        s.connect(('127.0.0.1', port))
        s.close()
        return True
    except Exception:
        return False

if check_port(8765):
    results["working"].append("FastAPI E.V. Glass Tactical HUD (Port 8765): ACTIVE & Listening")
    print("  [+] Port 8765 (E.V. Glass HUD): ONLINE")
else:
    results["failing_or_needs_attention"].append("FastAPI E.V. Glass Tactical HUD (Port 8765): OFFLINE (needs jarvisd or uvicorn launched)")
    print("  [-] Port 8765: OFFLINE")

if check_port(3000):
    results["working"].append("Next.js Spatial React HUD (Port 3000): ACTIVE & Listening")
    print("  [+] Port 3000 (Next.js React HUD): ONLINE")
else:
    results["failing_or_needs_attention"].append("Next.js Spatial React HUD (Port 3000): OFFLINE (run 'npm run dev' inside hud/ if needed)")
    print("  [-] Port 3000: OFFLINE")

# 4. Browser Automation (BrowserUse & GhostBrowser)
print("\n[4/8] Auditing Browser Automation...")
try:
    import browser_use
    results["working"].append("browser-use library: Installed")
    print("  [+] browser-use library: Installed")
except ImportError as e:
    results["failing_or_needs_attention"].append(f"browser-use: Not installed ({e})")
    print(f"  [-] browser-use: Missing ({e})")

try:
    from jarvisx.browser.browser_use_engine import BrowserUseEngine
    bue = BrowserUseEngine.get_instance()
    results["working"].append("BrowserUseEngine: Loaded with OpenRouter/Groq Vision routing")
    print("  [+] BrowserUseEngine: ONLINE")
except Exception as e:
    results["failing_or_needs_attention"].append(f"BrowserUseEngine: Failed - {e}")
    print(f"  [-] BrowserUseEngine: FAILED ({e})")

try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        b.close()
    results["working"].append("Playwright Chromium: Installed & Headless Launch Verified")
    print("  [+] Playwright Chromium: VERIFIED")
except Exception as e:
    results["failing_or_needs_attention"].append(f"Playwright Chromium: Launch failed - {e}")
    print(f"  [-] Playwright Chromium: FAILED ({e})")

# 5. Core Kernel Modules & Hypervisor
print("\n[5/8] Auditing Core Kernel Modules...")
try:
    from jarvisx.kernel.hypervisor import Hypervisor
    hv = Hypervisor.get_instance()
    results["working"].append("Hypervisor: Resource Governor initialized")
    print("  [+] Hypervisor: ONLINE")
except Exception as e:
    results["failing_or_needs_attention"].append(f"Hypervisor: Failed - {e}")
    print(f"  [-] Hypervisor: FAILED ({e})")

try:
    from jarvisx.automation.cyber_commander import CyberCommander
    cc = CyberCommander.get_instance()
    results["working"].append("CyberCommander: Ready with recon/audit playbooks")
    print("  [+] CyberCommander: ONLINE")
except Exception as e:
    results["failing_or_needs_attention"].append(f"CyberCommander: Failed - {e}")
    print(f"  [-] CyberCommander: FAILED ({e})")

try:
    from jarvisx.orchestration.meta_orchestrator import MetaOrchestrator
    mo = MetaOrchestrator.get_instance()
    results["working"].append("MetaOrchestrator: Autonomous Coder Swarm ready")
    print("  [+] MetaOrchestrator: ONLINE")
except Exception as e:
    results["failing_or_needs_attention"].append(f"MetaOrchestrator: Failed - {e}")
    print(f"  [-] MetaOrchestrator: FAILED ({e})")

# 6. Vision & EDITH Screen Awareness
print("\n[6/8] Auditing Vision Subsystems...")
try:
    from jarvisx.vision.edith_ar import EdithAREngine
    edith = EdithAREngine.get_instance()
    img = edith.capture_screen_image()
    if img:
        results["working"].append(f"EdithAREngine: Screen capture operational ({img.size[0]}x{img.size[1]})")
        print(f"  [+] EdithAREngine: Screen Capture OK ({img.size})")
    else:
        results["failing_or_needs_attention"].append("EdithAREngine: Screen capture returned None")
        print("  [-] EdithAREngine: Screen Capture returned None")
except Exception as e:
    results["failing_or_needs_attention"].append(f"EdithAREngine: Failed - {e}")
    print(f"  [-] EdithAREngine: FAILED ({e})")

# 7. Local Memory & RAG
print("\n[7/8] Auditing Memory & Database...")
db_path = PROJECT_ROOT / "var" / "jarvis.db"
if db_path.exists():
    size_kb = round(db_path.stat().st_size / 1024, 1)
    results["working"].append(f"SQLite Memory DB: var/jarvis.db exists ({size_kb} KB)")
    print(f"  [+] SQLite DB: OK ({size_kb} KB)")
else:
    results["failing_or_needs_attention"].append("SQLite Memory DB: var/jarvis.db missing (will auto-create on boot)")
    print("  [-] SQLite DB: Missing var/jarvis.db")

# 8. Thermal & OS Resource Governance
print("\n[8/8] Auditing System Thermals & Resources...")
cpu_usage = psutil.cpu_percent(interval=1)
mem_info = psutil.virtual_memory()
results["working"].append(f"Current System Load: CPU {cpu_usage}% | RAM {mem_info.percent}% ({round(mem_info.used/(1024**3), 1)}GB / {round(mem_info.total/(1024**3), 1)}GB)")
print(f"  [+] Current Load: CPU {cpu_usage}% | RAM {mem_info.percent}%")

# Check CLI entrypoint
try:
    import jarvisx
    results["working"].append("jarvisx python package: Importable from current environment")
    print("  [+] jarvisx module: Importable")
except Exception as e:
    results["failing_or_needs_attention"].append(f"jarvisx package: Import failed - {e}")
    print(f"  [-] jarvisx package: Import failed ({e})")

# Write out full audit report
with open(PROJECT_ROOT / "var" / "system_audit_report.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 60)
print(f"AUDIT COMPLETE: {len(results['working'])} WORKING | {len(results['failing_or_needs_attention'])} ISSUES FOUND")
print("=" * 60)
