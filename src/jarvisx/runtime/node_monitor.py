"""Jarvis X: Universal Worker Node Monitor + Auto-Upgrade Engine.

Dynamically reads ALL worker nodes from mesh_router.py registry.
- No manual updates needed when new nodes are added.
- Polls every 60s, fires Windows toast on connect/disconnect.
- Auto-pulls the node's assigned model if missing on reconnect.
"""

import time
import urllib.request
import http.client
import json
import subprocess
import sys
import os

# Ensure UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project src to path so we can import mesh_router
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "src"))

PORT = 11434
POLL_INTERVAL = 60  # seconds

already_online: set = set()
upgrade_done: set = set()


def load_workers() -> dict:
    """Dynamically load all registered workers from MeshRouter.
    Falls back to empty dict if import fails.
    """
    try:
        from jarvisx.mesh.mesh_router import MeshRouter
        router = MeshRouter()
        # Filter out PENDING nodes (no real IP yet)
        active = {
            name: info for name, info in router.workers.items()
            if "PENDING" not in info.get("ip", "")
        }
        return active
    except Exception as e:
        print(f"  [!] Could not load MeshRouter workers: {e}")
        return {}


def is_node_online(ip_url: str) -> bool:
    try:
        clean = ip_url.replace("http://", "").replace("https://", "").split(":")[0]
        req = urllib.request.urlopen(f"http://{clean}:{PORT}/api/tags", timeout=4)
        return req.status == 200
    except Exception:
        return False


def get_node_models(ip_url: str) -> list:
    try:
        clean = ip_url.replace("http://", "").replace("https://", "").split(":")[0]
        req = urllib.request.urlopen(f"http://{clean}:{PORT}/api/tags", timeout=4)
        data = json.loads(req.read())
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def remote_pull(ip_url: str, model: str) -> bool:
    """Trigger a streaming model pull on a remote Ollama node."""
    clean_ip = ip_url.replace("http://", "").replace("https://", "").split(":")[0]
    print(f"  [*] Remote pulling: {model} on {clean_ip}...")
    body = json.dumps({"name": model, "stream": True}).encode()
    try:
        conn = http.client.HTTPConnection(clean_ip, PORT, timeout=3600)
        conn.request("POST", "/api/pull", body=body, headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        last_pct = ""
        while True:
            chunk = resp.readline()
            if not chunk:
                break
            try:
                obj = json.loads(chunk.decode())
                total = obj.get("total", 0)
                completed = obj.get("completed", 0)
                status = obj.get("status", "")
                if total and completed:
                    pct = f"{round(completed / total * 100, 1)}%"
                    if pct != last_pct:
                        print(f"\r  [downloading] {model}: {pct}   ", end="", flush=True)
                        last_pct = pct
                elif status and status != last_pct:
                    print(f"  [{status}]")
                    last_pct = status
            except Exception:
                pass
        conn.close()
        print(f"\n  [+] Pull complete: {model} on {clean_ip}")
        return True
    except Exception as e:
        print(f"  [!] Pull error for {model} on {clean_ip}: {e}")
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


def handle_node_online(worker_id: str, info: dict):
    """Called when a node just came online. Toast + auto-upgrade."""
    name = info.get("name", worker_id)
    ip = info.get("ip", "")
    target_model = info.get("model", "")
    hardware = info.get("hardware", "GPU")

    print(f"\n[!!!] NODE ONLINE: {name} | {hardware} | {ip}")
    toast("Jarvis X - Node Online!", f"{name} ({hardware}) is now online!")

    if not target_model:
        return

    existing = get_node_models(ip)
    model_base = target_model.split(":")[0]
    already_has = any(model_base in em for em in existing)

    if already_has:
        print(f"  [OK] Target model '{target_model}' already present. No upgrade needed.")
        upgrade_done.add(worker_id)
        return

    print(f"  [UPGRADE] Missing model: {target_model}. Starting remote pull...")
    toast("Jarvis X - Auto-Upgrade", f"Pulling {target_model} on {name} silently...")

    success = remote_pull(ip, target_model)
    if success:
        upgrade_done.add(worker_id)
        toast("Jarvis X - Upgrade Complete!", f"{target_model} is now live on {name}!")
        print(f"  [+] {name} is now fully upgraded with {target_model}!")


def main():
    print("=" * 60)
    print("  [*] JARVIS X: UNIVERSAL NODE MONITOR + AUTO-UPGRADE")
    print(f"  Reads workers dynamically from MeshRouter registry.")
    print(f"  Polling every {POLL_INTERVAL}s | Auto-pulls on reconnect.")
    print("=" * 60)

    while True:
        workers = load_workers()

        if not workers:
            print("  [!] No active workers found in registry. Retrying in 60s...")
            time.sleep(POLL_INTERVAL)
            continue

        for worker_id, info in workers.items():
            name = info.get("name", worker_id)
            ip = info.get("ip", "")
            online = is_node_online(ip)

            if online and worker_id not in already_online:
                already_online.add(worker_id)
                upgrade_done.discard(worker_id)
                handle_node_online(worker_id, info)

            elif not online and worker_id in already_online:
                already_online.discard(worker_id)
                print(f"\n[---] NODE OFFLINE: {name} ({ip})")
                toast("Jarvis X - Node Offline", f"{name} went offline.")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
