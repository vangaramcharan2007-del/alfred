"""
Jarvis X - JaxCore Ecosystem Manager
Provides programmatic control over JaxCore skins, modules, and Rainmeter telemetry.
"""
import os
import subprocess
import time
import sys

RAINMETER_EXE = r"C:\Program Files\Rainmeter\Rainmeter.exe"
INI_PATH = os.path.expanduser(r"~\AppData\Roaming\Rainmeter\Rainmeter.ini")
SKINS_DIR = r"C:\Users\vanga\OneDrive\Documents\Rainmeter\Skins"

MODULES = {
    "clock": (r"GhostMinimal\Clock", "Clock.ini"),
    "players": (r"ModularPlayers\Main", "Main.ini"),
    "visualizer": (r"ModularVisualizer\Main", "Main.ini"),
    "flyouts": (r"YourFlyouts\Main", "Main.ini"),
    "mixer": (r"YourMixer\Main", "Main.ini"),
    "idled": (r"IdleStyle\Main", "Main.ini"),
    "core": (r"#JaxCore\Main", "Home.ini"),
}

def is_rainmeter_running():
    try:
        out = subprocess.check_output("tasklist", text=True)
        return any("rainmeter" in l.lower() for l in out.splitlines())
    except:
        return False

def activate_module(name):
    if name not in MODULES:
        print(f"[!] Unknown module: {name}. Available: {list(MODULES.keys())}")
        return
    config, ini = MODULES[name]
    subprocess.run([RAINMETER_EXE, "!ActivateConfig", config, ini])
    print(f"[+] Activated module: {name} ({config}\\{ini})")

def deactivate_module(name):
    if name not in MODULES:
        print(f"[!] Unknown module: {name}")
        return
    config, _ = MODULES[name]
    subprocess.run([RAINMETER_EXE, "!DeactivateConfig", config])
    print(f"[-] Deactivated module: {name} ({config})")

def status():
    print("=== JaxCore Module Status ===")
    print("Rainmeter Process Active:", is_rainmeter_running())
    if not os.path.exists(INI_PATH):
        print("Rainmeter.ini not found.")
        return
    
    with open(INI_PATH, "r", encoding="utf-16", errors="ignore") as f:
        content = f.read()

    for name, (config, ini) in MODULES.items():
        sec = f"[{config}]"
        active = "Inactive (0)"
        if sec in content:
            idx = content.find(sec)
            nxt = content.find("[", idx + 1)
            chunk = content[idx:nxt] if nxt != -1 else content[idx:]
            if "Active=1" in chunk:
                active = "ACTIVE (1)"
        print(f"  * {name:<12} [{config}]: {active}")

def start_rainmeter():
    if is_rainmeter_running():
        print("[!] Rainmeter is already running.")
        return
    subprocess.Popen([r"cmd.exe", "/c", "start", "", RAINMETER_EXE], shell=False)
    time.sleep(2)
    print(f"[+] Started Rainmeter! Status: {'Active' if is_rainmeter_running() else 'Starting...'}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "status":
            status()
        elif cmd == "start":
            start_rainmeter()
        elif cmd == "activate" and len(sys.argv) > 2:
            activate_module(sys.argv[2].lower())
        elif cmd == "deactivate" and len(sys.argv) > 2:
            deactivate_module(sys.argv[2].lower())
        else:
            print("Usage: python manage_jaxcore.py [status|start|activate <mod>|deactivate <mod>]")
    else:
        status()

