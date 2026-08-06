"""Alfred Companion HUD Controller for Jarvis X (Layer 4 - Automation).

Generates native desktop companion HUD HTML overlay and real-time status telemetry bridge.
"""

import os
from typing import Any, Dict, Optional


class CompanionHUDController:
    """Zero-fluff production companion HUD overlay controller."""

    def __init__(self, hud_path: str = "var/config/alfred_hud.html"):
        self.hud_path = os.path.abspath(hud_path)
        os.makedirs(os.path.dirname(self.hud_path), exist_ok=True)

    def render_companion_hud(self, os_kernel: Any) -> Dict[str, Any]:
        """Synthesize and render desktop HUD HTML status overlay."""
        db_stat = os_kernel.get_master_dashboard()
        hspw = db_stat.get("total_hspw", 0.0)
        suggs = db_stat.get("proactive_suggestions", [])
        goals = db_stat.get("active_goals", [])

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Alfred Personal OS - Desktop HUD</title>
    <style>
        body {{ background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', Tahoma, sans-serif; padding: 20px; }}
        .hud-card {{ background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; margin-bottom: 15px; }}
        .badge {{ background-color: #238636; color: #ffffff; padding: 4px 8px; border-radius: 4px; font-weight: bold; }}
        .warning {{ background-color: #d29922; color: #0d1117; }}
    </style>
</head>
<body>
    <div class="hud-card">
        <h2>Alfred OS Desktop Companion HUD <span class="badge">ACTIVE</span></h2>
        <p><strong>Total Time Saved:</strong> +{hspw:.2f} HSPW</p>
        <p><strong>Active Goals Tracked:</strong> {len(goals)}</p>
        <p><strong>Proactive Intelligence Recommendations:</strong> {len(suggs)}</p>
    </div>
</body>
</html>
"""
        with open(self.hud_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return {
            "status": "RENDERED",
            "hud_file": self.hud_path,
            "total_hspw": hspw,
            "active_goals_count": len(goals),
            "suggestions_count": len(suggs),
        }
