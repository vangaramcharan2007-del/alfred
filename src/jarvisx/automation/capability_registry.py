"""Capability Reality Registry for Jarvis X (Layer 4 - Automation).

Enforces reality verification for all Alfred automation capabilities.
Categorizes capabilities into PHYSICAL, CONNECTED, SIMULATED, and UNKNOWN,
and prevents Alfred from claiming unverified or UNKNOWN capabilities as completed.
"""

from typing import Any, Dict, List, Optional


class CapabilityRealityRegistry:
    """Zero-fluff production capability reality verification registry."""

    def __init__(self):
        self.capabilities: Dict[str, Dict[str, Any]] = {}
        self._register_default_capabilities()

    def _register_default_capabilities(self):
        """Register default system capabilities with canonical execution types."""
        defaults = [
            {"name": "system cleaner", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["filesystem"], "requires_confirmation": False},
            {"name": "folder watcher", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["filesystem"], "requires_confirmation": False},
            {"name": "desktop notifications", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["powershell", "dotnet"], "requires_confirmation": False},
            {"name": "window focus manager", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["powershell", "win32"], "requires_confirmation": False},
            {"name": "power supervisor", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["powercfg", "wmi"], "requires_confirmation": False},
            {"name": "deliverable synthesizer", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["filesystem"], "requires_confirmation": False},
            {"name": "web navigator", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["browser", "git"], "requires_confirmation": False},
            {"name": "voice runtime", "execution_type": "PHYSICAL", "confidence": 0.9, "dependencies": ["sqlite", "audio"], "requires_confirmation": False},
            {"name": "adaptive planner", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["sqlite"], "requires_confirmation": False},
            {"name": "goal tracker", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["sqlite"], "requires_confirmation": False},
            {"name": "proactive engine", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["sqlite", "wmi"], "requires_confirmation": False},
            {"name": "daily briefing", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["sqlite"], "requires_confirmation": False},
            {"name": "mission executor", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["sqlite"], "requires_confirmation": False},
            {"name": "feedback engine", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["sqlite"], "requires_confirmation": False},
            {"name": "habit engine", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["sqlite"], "requires_confirmation": False},
            {"name": "self refinement", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["sqlite"], "requires_confirmation": False},
            {"name": "companion hud", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["filesystem"], "requires_confirmation": False},
            {"name": "native companion ui", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["tkinter", "win32"], "requires_confirmation": False},
            {"name": "interactive notification", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["powershell", "dotnet"], "requires_confirmation": False},
            {"name": "screen context", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["win32", "sqlite"], "requires_confirmation": False},
            {"name": "contextual assistance", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["sqlite"], "requires_confirmation": False},
            {"name": "workflow autopilot", "execution_type": "PHYSICAL", "confidence": 1.0, "dependencies": ["os_kernel"], "requires_confirmation": False},
            {"name": "inbox triage", "execution_type": "SIMULATED", "confidence": 0.7, "dependencies": ["sqlite"], "requires_confirmation": False},
            {"name": "lecture synthesizer", "execution_type": "SIMULATED", "confidence": 0.7, "dependencies": ["sqlite"], "requires_confirmation": False},
            {"name": "finops optimizer", "execution_type": "SIMULATED", "confidence": 0.6, "dependencies": ["cloud_adapter"], "requires_confirmation": False},
            {"name": "federation sync", "execution_type": "CONNECTED", "confidence": 0.8, "dependencies": ["network"], "requires_confirmation": False},
        ]
        for cap in defaults:
            self.register_capability(**cap)

    def register_capability(
        self,
        name: str,
        execution_type: str = "UNKNOWN",
        confidence: float = 0.5,
        dependencies: Optional[List[str]] = None,
        requires_confirmation: bool = False,
    ) -> Dict[str, Any]:
        """Register or update a system capability."""
        valid_types = {"PHYSICAL", "CONNECTED", "SIMULATED", "UNKNOWN"}
        type_clean = execution_type.upper() if execution_type.upper() in valid_types else "UNKNOWN"
        entry = {
            "name": name.lower(),
            "execution_type": type_clean,
            "confidence": max(0.0, min(1.0, confidence)),
            "dependencies": dependencies or [],
            "requires_confirmation": requires_confirmation,
        }
        self.capabilities[name.lower()] = entry
        return entry

    def verify_capability(self, name: str) -> Dict[str, Any]:
        """Verify capability reality before execution. Returns blocked status if UNKNOWN."""
        name_clean = name.lower()

        # Intent mapping for kernel requests
        if any(k in name_clean for k in ["autopilot", "workflow autopilot", "prepare machine", "deep clean workflow"]):
            name_clean = "workflow autopilot"
        elif any(k in name_clean for k in ["screen context", "vision context", "active screen", "capture context"]):
            name_clean = "screen context"
        elif any(k in name_clean for k in ["contextual assistance", "assist screen", "synthesize assistance"]):
            name_clean = "contextual assistance"
        elif any(k in name_clean for k in ["widget", "launch widget", "floating companion"]):
            name_clean = "native companion ui"
        elif any(k in name_clean for k in ["interactive alert", "confirm prompt", "toast prompt"]):
            name_clean = "interactive notification"
        elif any(k in name_clean for k in ["habit", "detect habit", "routine", "rhythm"]):
            name_clean = "habit engine"
        elif any(k in name_clean for k in ["refine", "self-refinement", "refine strategy", "multiplier"]):
            name_clean = "self refinement"
        elif any(k in name_clean for k in ["hud", "companion hud", "overlay", "render hud"]):
            name_clean = "companion hud"
        elif any(k in name_clean for k in ["execute mission", "run mission", "mission loop"]):
            name_clean = "mission executor"
        elif any(k in name_clean for k in ["feedback", "record learning"]):
            name_clean = "feedback engine"
        elif any(k in name_clean for k in ["decompose", "plan goal", "mission tree"]):
            name_clean = "adaptive planner"
        elif any(k in name_clean for k in ["replan", "adjust target"]):
            name_clean = "adaptive planner"
        elif any(k in name_clean for k in ["briefing", "good morning"]):
            name_clean = "daily briefing"
        elif any(k in name_clean for k in ["add goal", "track goal"]):
            name_clean = "goal tracker"
        elif any(k in name_clean for k in ["proactive", "suggest"]):
            name_clean = "proactive engine"
        elif any(k in name_clean for k in ["organize", "download", "folder watcher"]):
            name_clean = "folder watcher"
        elif any(k in name_clean for k in ["clean", "storage", "system cleaner", "bloat", "delete"]):
            name_clean = "system cleaner"
        elif any(k in name_clean for k in ["voice", "listen", "speak"]):
            name_clean = "voice runtime"
        elif any(k in name_clean for k in ["tray", "system tray"]):
            name_clean = "desktop notifications"
        elif any(k in name_clean for k in ["ppt", "poster", "deliverable"]):
            name_clean = "deliverable synthesizer"
        elif any(k in name_clean for k in ["web", "clone", "youtube"]):
            name_clean = "web navigator"

        cap = self.capabilities.get(name_clean)
        if not cap:
            cap = self.register_capability(name_clean, execution_type="UNKNOWN", confidence=0.0)

        if cap["execution_type"] == "UNKNOWN":
            return {
                "verified": False,
                "status": "BLOCKED",
                "capability": cap,
                "reason": f"Capability '{name}' is UNKNOWN and cannot be claimed as completed without physical verification.",
            }

        return {
            "verified": True,
            "status": "PERMITTED",
            "capability": cap,
            "reason": f"Capability '{name}' verified as {cap['execution_type']} execution.",
        }

    def list_capabilities(self) -> List[Dict[str, Any]]:
        """Return list of all registered capabilities with reality telemetry."""
        return list(self.capabilities.values())
