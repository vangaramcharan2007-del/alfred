"""Diagnostics Console — hidden by default, visible on request."""
from jarvisx.core.presence_manager import PresenceManager


class DiagnosticsConsole:
    """Renders internal state when the user says 'Alfred, show diagnostics.'"""

    def __init__(self, presence_manager: PresenceManager):
        self.presence = presence_manager

    def render(self) -> str:
        """Produce the full diagnostics readout."""
        snap = self.presence.get_diagnostics_snapshot()

        lines = [
            "============================",
            "ALFRED DIAGNOSTICS",
            "============================",
            "",
        ]

        # Active objectives
        lines.append("Active Objectives:")
        active = snap.get("active_objectives", {})
        if active:
            for oid, obj in active.items():
                lines.append(f"- {obj['title']} ({obj['progress']}%)")
        else:
            lines.append("- None")
        lines.append("")

        # Running agents
        lines.append("Running Agents:")
        agents = snap.get("running_agents", [])
        if agents:
            for a in agents:
                lines.append(f"- {a}")
        else:
            lines.append("- None")
        lines.append("")

        # Background jobs
        lines.append("Background Jobs:")
        jobs = snap.get("background_jobs", {})
        if jobs:
            for name in jobs:
                lines.append(f"- {name}")
        else:
            lines.append("- None")
        lines.append("")

        # Health
        lines.append(f"Health:\n- {snap.get('health', 'unknown')}")

        return "\n".join(lines)
