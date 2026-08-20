"""Jarvis X: Worker Node Online Monitor + Auto-Upgrade Engine.

Polls all GPU worker nodes every 60 seconds.
- Fires Windows toast notification when any node comes online.
- Auto-triggers remote model upgrades when a node reconnects.
"""

import time
import urllib.request
import urllib.error
import http.client
import json
import subprocess
import sys

# Windows UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

NODES = {
    "Worker 1 - RTX 4050": "100.77.90.36",
    "Worker 3 - RTX 5050": "100.81.36.31",
}

# Models to auto-pull on each node when it comes online (if not already present)
AUTO_UPGRADE = {
    "Worker 1 - RTX 4050": ["qwen2.5-coder:7b-instruct"],
    "Worker 3 - RTX 5050": ["deepseek-r1:14b"],
}

PORT = 11434
POLL_INTERVAL = 60  # seconds

already_online: set = set()
upgrade_done: set = set()  # tracks nodes we've already triggered upgrade for


def is_node_online(ip: str) -> bool:
    try:
        req = urllib.request.urlopen(f"http://{ip}:{PORT}/api/tags", timeout=4)
        return req.status == 200
    except Exception:
        return False


def get_node_models(ip: str) -> list:
    try:
        req = urllib.request.urlopen(f"http://{ip}:{PORT}/api/tags", timeout=4)
        data = json.loads(req.read())
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def remote_pull(ip: str, model: str):
    """Trigger a streaming model pull on a remote Ollama node."""
    print(f"  [*] Triggering remote pull: {model} on {ip}...")
    body = json.dumps({"name": model, "stream": True}).encode()
    try:
        conn = http.client.HTTPConnection(ip, PORT, timeout=1800)
        conn.request("POST", "/api/pull", body=body, headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        last_pct = ""
        while True:
            chunk = resp.readline()
            if not chunk:
                break
            try:
                obj = json.loads(chunk.decode())
                status = obj.get("status", "")
                total = obj.get("total", 0)
                completed = obj.get("completed", 0)
                if total and completed:
                    pct = f"{round(completed/total*100, 1)}%"
                    if pct != last_pct:
                        print(f"\r  [downloading] {model}: {pct}   ", end="", flush=True)
                        last_pct = pct
                elif status and status != last_pct:
                    print(f"  [{status}]")
                    last_pct = status
            except Exception:
                pass
        conn.close()
        print(f"\n  [+] Pull complete: {model} on {ip}")
        return True
    except Exception as e:
        print(f"  [!] Pull failed for {model} on {ip}: {e}")
        return False


def toast(title: str, message: str):
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


def handle_node_online(name: str, ip: str):
    """Called when a node just came online. Show toast + trigger upgrades."""
    print(f"\n[!!!] NODE ONLINE: {name} ({ip})")
    existing_models = get_node_models(ip)
    print(f"  Current models: {existing_models or 'none'}")

    # Toast notification
    toast("Jarvis X - Node Online!", f"{name} ({ip}) is back online!")

    # Auto-upgrade: pull any missing models
    targets = AUTO_UPGRADE.get(name, [])
    missing = [m for m in targets if not any(m.split(":")[0] in em for em in existing_models)]

    if not missing:
        print(f"  [OK] All target models already present on {name}. No upgrade needed.")
        upgrade_done.add(name)
        return

    for model in missing:
        print(f"  [UPGRADE] Pulling {model} on {name}...")
        toast("Jarvis X - Auto-Upgrade", f"Pulling {model} on {name} silently...")
        success = remote_pull(ip, model)
        if success:
            upgrade_done.add(name)
            toast("Jarvis X - Upgrade Complete!", f"{model} is now live on {name}!")


def main():
    print("=" * 56)
    print("  [*] JARVIS X: NODE MONITOR + AUTO-UPGRADE ENGINE")
    print(f"  Polling every {POLL_INTERVAL}s | Auto-pulls on reconnect")
    print("=" * 56)

    # Initial state
    for name, ip in NODES.items():
        if is_node_online(ip):
            already_online.add(name)
            models = get_node_models(ip)
            print(f"  [ALREADY ONLINE] {name} ({ip}) | {models}")
        else:
            print(f"  [WAITING]        {name} ({ip})")
    print()

    while True:
        time.sleep(POLL_INTERVAL)
        for name, ip in NODES.items():
            online = is_node_online(ip)

            if online and name not in already_online:
                already_online.add(name)
                upgrade_done.discard(name)  # reset so upgrade re-runs
                handle_node_online(name, ip)

            elif not online and name in already_online:
                already_online.discard(name)
                print(f"\n[---] NODE OFFLINE: {name} ({ip})")
                toast("Jarvis X - Node Offline", f"{name} went offline.")


if __name__ == "__main__":
    main()
