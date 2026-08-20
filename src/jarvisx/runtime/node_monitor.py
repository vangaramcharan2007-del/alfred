"""Jarvis X: Worker Node Online Monitor.
Polls all GPU worker nodes every 60 seconds and fires a Windows toast
notification + prints to console as soon as any node comes online.
"""

import time
import urllib.request
import urllib.error
import subprocess
import sys

NODES = {
    "Worker 1 - RTX 3050": "100.77.90.36",
    "Worker 3 - RTX 5050": "100.81.36.31",
}

PORT = 11434
POLL_INTERVAL = 60  # seconds

already_online = set()


def is_node_online(ip: str) -> bool:
    try:
        req = urllib.request.urlopen(f"http://{ip}:{PORT}/api/tags", timeout=3)
        return req.status == 200
    except Exception:
        return False


def toast(title: str, message: str):
    """Windows 10/11 toast notification via PowerShell."""
    ps = f"""
Add-Type -AssemblyName System.Windows.Forms
$n = New-Object System.Windows.Forms.NotifyIcon
$n.Icon = [System.Drawing.SystemIcons]::Information
$n.BalloonTipTitle = "{title}"
$n.BalloonTipText = "{message}"
$n.Visible = $true
$n.ShowBalloonTip(8000)
Start-Sleep -Seconds 9
$n.Dispose()
"""
    subprocess.Popen(
        ["powershell", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-Command", ps],
        creationflags=0x08000000
    )


def main():
    print("=" * 54)
    print("  [*] JARVIS X: NODE ONLINE MONITOR STARTED")
    print(f"  Polling every {POLL_INTERVAL}s. Will notify when nodes come up.")
    print("=" * 54)

    for name, ip in NODES.items():
        if is_node_online(ip):
            already_online.add(name)
            print(f"  [ALREADY ONLINE] {name} ({ip})")
        else:
            print(f"  [WAITING]        {name} ({ip})")

    print()

    while True:
        time.sleep(POLL_INTERVAL)
        for name, ip in NODES.items():
            online = is_node_online(ip)
            if online and name not in already_online:
                already_online.add(name)
                msg = f"{name} ({ip}) just came online!"
                print(f"\n[!!!] NODE ONLINE: {msg}")
                toast("Jarvis X - Node Online!", msg)
            elif not online and name in already_online:
                already_online.discard(name)
                print(f"\n[---] NODE OFFLINE: {name} ({ip})")


if __name__ == "__main__":
    main()
