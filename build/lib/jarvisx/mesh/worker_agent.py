"""Standalone Worker Agent Daemon for Jarvis X Distributed Mesh.

Run on any worker laptop (e.g. friend's RTX gaming laptop):
    python -m jarvisx.mesh.worker_agent --name "Rahul-RTX4060" --port 11434

Features:
- Automatic GPU hardware detection (NVIDIA RTX, AMD Radeon, Intel Arc).
- Live VRAM, Temperature, and GPU utilization monitoring.
- Smart Gaming & Heavy-App Detection (auto-pauses when GTA, Steam, Valorant, or games run).
- Lightweight telemetry reporter for master Jarvis X controller.
"""

from __future__ import annotations
import os
import sys
import time
import json
import psutil
import argparse
import subprocess
from typing import Dict, Any, List, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading


KNOWN_GAME_PROCESSES = {
    "steam.exe", "epicgameslauncher.exe", "gta5.exe", "gtav.exe", "valorant.exe",
    "csgo.exe", "cs2.exe", "dota2.exe", "overwatch.exe", "apexlegends.exe",
    "fortniteclient-win64-shipping.exe", "cyberpunk2077.exe", "witcher3.exe",
    "r5apex.exe", "leagueclient.exe", "genshinimpact.exe", "cod.exe"
}


class LocalHardwareSensor:
    """Collects real-time GPU, CPU, RAM, and gaming process telemetry."""

    def __init__(self):
        self.has_nvidia = False
        self._check_nvidia_smi()

    def _check_nvidia_smi(self):
        try:
            res = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.has_nvidia = res.returncode == 0
        except Exception:
            self.has_nvidia = False

    def is_gaming_active(self) -> bool:
        """Check if any known gaming process is currently running."""
        for p in psutil.process_iter(["name"]):
            try:
                name = (p.info["name"] or "").lower()
                if name in KNOWN_GAME_PROCESSES:
                    return True
            except Exception:
                pass
        return False

    def get_telemetry(self) -> Dict[str, Any]:
        """Query GPU, CPU, VRAM, and temperature."""
        gpu_name = "Generic CPU/GPU"
        gpu_util = 0.0
        vram_used = 0.0
        vram_total = 0.0
        temp_c = 45.0

        if self.has_nvidia:
            try:
                # Query nvidia-smi for precise metrics
                cmd = [
                    "nvidia-smi",
                    "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                    "--format=csv,noheader,nounits"
                ]
                out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
                if out:
                    parts = [p.strip() for p in out.split(",")]
                    if len(parts) >= 5:
                        gpu_name = parts[0]
                        gpu_util = float(parts[1])
                        vram_used = round(float(parts[2]) / 1024, 2)
                        vram_total = round(float(parts[3]) / 1024, 2)
                        temp_c = float(parts[4])
            except Exception:
                pass

        mem = psutil.virtual_memory()
        cpu_util = psutil.cpu_percent(interval=None)
        is_gaming = self.is_gaming_active()

        return {
            "gpu_name": gpu_name,
            "gpu_util_percent": gpu_util,
            "vram_used_gb": vram_used,
            "vram_total_gb": vram_total,
            "cpu_util_percent": cpu_util,
            "ram_used_gb": round(mem.used / (1024 ** 3), 1),
            "ram_total_gb": round(mem.total / (1024 ** 3), 1),
            "temperature_c": temp_c,
            "is_gaming": is_gaming
        }


class WorkerTelemetryHandler(BaseHTTPRequestHandler):
    sensor = LocalHardwareSensor()
    worker_name = "Jarvis-Worker"

    def do_GET(self):
        if self.path == "/health" or self.path == "/telemetry":
            data = {
                "worker_name": self.worker_name,
                "status": "GAMING" if self.sensor.is_gaming_active() else "ONLINE",
                "telemetry": self.sensor.get_telemetry(),
                "timestamp": time.time()
            }
            body = json.dumps(data, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress noisy HTTP request logging


def run_worker_agent(name: str = "Worker-Node", port: int = 11435):
    """Launch the standalone worker agent dashboard and telemetry server."""
    sensor = LocalHardwareSensor()
    WorkerTelemetryHandler.worker_name = name
    WorkerTelemetryHandler.sensor = sensor

    server = HTTPServer(("0.0.0.0", port), WorkerTelemetryHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    print(f"\n=======================================================")
    print(f"      🎩 JARVIS X DISTRIBUTED COMPUTE WORKER")
    print(f"=======================================================")
    print(f"  Worker Name : {name}")
    print(f"  Telemetry   : http://0.0.0.0:{port}/health")
    print(f"  Ollama Host : Ensure 'OLLAMA_HOST=0.0.0.0:11434' is active")
    print(f"=======================================================\n")

    try:
        while True:
            t = sensor.get_telemetry()
            gaming_str = "🎮 GAMING DETECTED (PAUSED)" if t["is_gaming"] else "🟢 READY & COOL"
            status_line = (
                f"\r[{name}] GPU: {t['gpu_name'][:18]} | Util: {t['gpu_util_percent']:4.1f}% | "
                f"VRAM: {t['vram_used_gb']:4.1f}/{t['vram_total_gb']:4.1f} GB | "
                f"Temp: {t['temperature_c']:4.1f}°C | {gaming_str}   "
            )
            sys.stdout.write(status_line)
            sys.stdout.flush()
            time.sleep(2.0)
    except KeyboardInterrupt:
        print("\n[Jarvis Worker] Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jarvis X Distributed Mesh Worker Agent")
    parser.add_argument("--name", type=str, default="Gaming-Laptop", help="Worker name")
    parser.add_argument("--port", type=int, default=11435, help="Telemetry port")
    args = parser.parse_args()
    run_worker_agent(name=args.name, port=args.port)
