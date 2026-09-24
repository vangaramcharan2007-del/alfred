#!/usr/bin/env python3
"""
Jarvis X - Cold Start Rainmeter Configurator
1. Cleanly terminates any running Rainmeter process.
2. Writes a clean, valid Rainmeter.ini with Mond\\Clock active and dead-center.
3. Cold-starts Rainmeter so it reads the new config from disk.
"""

import os
import subprocess
import time

RAINMETER_INI = os.path.expanduser(r"~\AppData\Roaming\Rainmeter\Rainmeter.ini")
RAINMETER_EXE = r"C:\Program Files\Rainmeter\Rainmeter.exe"

CLEAN_INI = """[Rainmeter]
Logging=0
SkinPath=C:\\Users\\vanga\\OneDrive\\Documents\\Rainmeter\\Skins\\

[Mond\\Clock]
Active=1
WindowX=50%
WindowY=25%
AnchorX=50%
AnchorY=50%
ClickThrough=0
Draggable=1
SnapEdges=1
KeepOnScreen=1
AlwaysOnTop=0

[illustro\\Clock]
Active=0

[illustro\\Disk]
Active=0

[illustro\\System]
Active=0

[illustro\\Welcome]
Active=0
"""

def cold_start():
    print("[*] Quitting existing Rainmeter...")
    subprocess.run([RAINMETER_EXE, "!Quit"], check=False)
    time.sleep(1)
    subprocess.run(["taskkill", "/F", "/IM", "Rainmeter.exe"], capture_output=True, check=False)
    time.sleep(1.5)

    print("[*] Writing clean Rainmeter.ini with Mond\\Clock centered...")
    with open(RAINMETER_INI, "w", encoding="utf-16") as f:
        f.write(CLEAN_INI)
    print(f"[+] Written clean Rainmeter.ini to {RAINMETER_INI}")

    print("[*] Launching fresh Rainmeter instance...")
    cmd = f'cmd.exe /c start "" "{RAINMETER_EXE}"'
    subprocess.run(cmd, shell=True, check=False)
    time.sleep(2)

    # Check process
    out = subprocess.check_output("tasklist", text=True)
    is_up = any("rainmeter" in l.lower() for l in out.splitlines())
    print(f"[+] Rainmeter cold start complete! Running: {is_up}")

if __name__ == "__main__":
    cold_start()
