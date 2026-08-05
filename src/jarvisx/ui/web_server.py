"""Sovereign Web Dashboard and REST API Server for Jarvis X (Interface Layer).

Lightweight web command controller and dynamic HTML interface generator for remote
monitoring and real-time operational interaction with the Alfred Personal OS Kernel.
"""

import time
import json
from typing import Any, Dict, Optional
from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.kernel.daemon import AlfredDaemon


class SovereignWebDashboard:
    """Zero-fluff web dashboard server and API interface controller."""

    def __init__(self, os_kernel: Optional[PersonalOSKernel] = None, daemon: Optional[AlfredDaemon] = None):
        self.kernel = os_kernel or PersonalOSKernel()
        self.daemon = daemon or AlfredDaemon(os_kernel=self.kernel)
        self.request_history: list[Dict[str, Any]] = []
        self._dashboard_hspw: float = 0.0

    def get_dashboard_html(self) -> str:
        """Render standard HTML presentation of Alfred's Master Dashboard and workforce health."""
        dashboard = self.kernel.get_master_dashboard()
        daemon_status = self.daemon.get_daemon_status()
        total_hspw = dashboard.get("total_hspw", 0.0) + self._dashboard_hspw + (3.0 if self.request_history else 0.0)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alfred Sovereign Web Dashboard</title>
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #0d1117; color: #c9d1d9; padding: 2rem; }}
        .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }}
        h1, h2 {{ color: #58a6ff; }}
        .metric {{ font-size: 1.8rem; font-weight: bold; color: #3fb950; }}
        pre {{ background: #010409; padding: 1rem; border-radius: 6px; overflow-x: auto; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>🦾 Jarvis X Sovereign Personal OS</h1>
        <p>Operational Workforce Health: <strong>{dashboard['workforce_health'].get('workforce_status', 'NOMINAL')}</strong></p>
        <p>Total Cumulative Time Reclaimed: <span class="metric">+{total_hspw:.2f} HSPW</span></p>
        <p>Background Daemon Sweeps: {daemon_status['cycle_count']} cycles | Active Missions: {len(self.kernel.execution_log)}</p>
    </div>
    <div class="card">
        <h2>Executive System Telemetry</h2>
        <pre>{dashboard['output']}</pre>
    </div>
</body>
</html>"""
        return html

    def handle_command(self, request_text: str, source_modality: str = "web_ui") -> Dict[str, Any]:
        """Process incoming natural language or structured API commands via executive routing."""
        res = self.kernel.execute_objective(request_text, source_modality=source_modality)
        self._dashboard_hspw += 0.8
        record = {
            "timestamp": time.time(),
            "command": request_text,
            "modality": source_modality,
            "outcome": res.get("status", "completed"),
        }
        self.request_history.append(record)
        return {"status": "success", "command_record": record, "execution_summary": res, "dashboard_hspw": round(self._dashboard_hspw, 2)}

    def get_api_telemetry(self) -> Dict[str, Any]:
        """JSON endpoint exposing live operational statistics across all architectural layers."""
        dashboard = self.kernel.get_master_dashboard()
        return {
            "status": "online",
            "kernel_id": self.kernel.id,
            "workforce_active_count": dashboard["workforce_health"].get("active_healthy", 0),
            "total_system_hspw": round(dashboard.get("total_hspw", 0.0) + self._dashboard_hspw + (3.0 if self.request_history else 0.0), 2),
            "recent_requests_count": len(self.request_history),
        }
