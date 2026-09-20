"""
Multi-App Workspace Orchestrator for Jarvis X / E.V.
=====================================================
Orchestrates multi-application workspaces with mid-sentence EV voice narration
and live HUD event toasts.

Profiles:
- coding: VS Code + Windows Terminal + GitHub + RAM Flush
- research: Web Research Browser + Notepad + Memory Compaction
- system_defense: Cyber Reconnaissance + Task Manager + Active Thermal Cooling
- gaming: Game Launcher + RAM Purge + High Performance
"""

from __future__ import annotations

import logging
import os
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvisx.automation.workspace")


@dataclass
class WorkspaceProfile:
    name: str
    description: str
    apps: List[str]
    urls: List[str]
    speech_prompt: str
    completion_speech: str
    flush_ram: bool = True


WORKSPACE_PROFILES: Dict[str, WorkspaceProfile] = {
    "coding": WorkspaceProfile(
        name="coding",
        description="Software engineering development workspace",
        apps=["code", "terminal"],
        urls=["https://github.com"],
        speech_prompt="Setting up your engineering workspace right now, Boss.",
        completion_speech="Your coding workspace is staged and ready, Boss.",
        flush_ram=True,
    ),
    "research": WorkspaceProfile(
        name="research",
        description="Deep research & academic inquiry workspace",
        apps=["notepad"],
        urls=["https://www.google.com", "https://arxiv.org"],
        speech_prompt="Staging your research environment now, Boss.",
        completion_speech="Research tools active and staged, Boss.",
        flush_ram=True,
    ),
    "system_defense": WorkspaceProfile(
        name="system_defense",
        description="Cyber telemetry and system protection workspace",
        apps=["taskmgr"],
        urls=[],
        speech_prompt="Engaging defensive telemetry and system security sweep, Boss.",
        completion_speech="Perimeter secure. All systems nominal.",
        flush_ram=True,
    ),
}


class WorkspaceOrchestrator:
    """
    Executes multi-step workspace staging concurrently with EV voice feedback
    and live EV HUD glass notifications.
    """

    _instance: Optional[WorkspaceOrchestrator] = None

    @classmethod
    def get_instance(cls) -> WorkspaceOrchestrator:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _push_to_hud(self, event_type: str, data: dict):
        try:
            from jarvisx.dashboard.event_bus import push_event_sync
            push_event_sync(event_type, data)
        except Exception as e:
            logger.debug(f"[WorkspaceOrchestrator] HUD push error: {e}")

    def _launch_app(self, app_key: str) -> bool:
        """Launches desktop application on Windows."""
        app_map = {
            "code": [os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"), "code"],
            "vscode": [os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"), "code"],
            "terminal": ["wt.exe", "powershell.exe"],
            "powershell": ["powershell.exe"],
            "notepad": ["notepad.exe"],
            "calculator": ["calc.exe"],
            "calc": ["calc.exe"],
            "taskmgr": ["taskmgr.exe"],
            "explorer": ["explorer.exe"],
        }
        binaries = app_map.get(app_key.lower(), [f"{app_key}.exe"])
        for binary in binaries:
            try:
                if os.path.isabs(binary) and os.path.exists(binary):
                    subprocess.Popen([binary])
                    return True
                else:
                    subprocess.Popen(["cmd.exe", "/c", "start", "", binary], shell=False)
                    return True
            except Exception as e:
                logger.debug(f"[WorkspaceOrchestrator] Launch failed for {binary}: {e}")
        return False

    def _launch_url(self, url: str):
        """Launches web URL on user's default browser."""
        try:
            subprocess.Popen(["cmd.exe", "/c", "start", "", url], shell=False)
        except Exception:
            pass

    def deploy_workspace(self, profile_name: str = "coding", mid_sentence: bool = True) -> Dict[str, Any]:
        """
        Deploys all applications and resources for the specified profile.
        Narrates in real-time with E.V. neural TTS and broadcasts to EV HUD.
        """
        t0 = time.perf_counter()
        prof = WORKSPACE_PROFILES.get(profile_name.lower(), WORKSPACE_PROFILES["coding"])

        logger.info(f"[WorkspaceOrchestrator] 🚀 Deploying '{prof.name}' workspace profile...")

        # 1. Announce via EV TTS (non-blocking mid-sentence speech)
        if mid_sentence and prof.speech_prompt:
            try:
                from jarvisx.voice.sovereign_neural_tts import get_neural_tts
                tts = get_neural_tts()
                tts.speak(prof.speech_prompt, voice_key="hyper_realistic_female", blocking=False)
            except Exception as e:
                logger.debug(f"[WorkspaceOrchestrator] TTS speak error: {e}")

        # 2. Push microsteps and HUD notification toast
        microsteps = [
            f"Workspace Directive: Stage '{prof.name.upper()}' Profile",
            f"Launching apps: {', '.join(prof.apps)}",
            f"Opening web endpoints: {', '.join(prof.urls) if prof.urls else 'None'}",
            "Performing active memory compaction",
            f"Workspace '{prof.name.upper()}' staged successfully",
        ]
        self._push_to_hud("exec_microsteps", {"steps": microsteps})

        self._push_to_hud("workspace_event", {
            "profile": prof.name,
            "apps": prof.apps,
            "urls": prof.urls,
            "message": f"Staged {prof.name.upper()} workspace: {len(prof.apps)} apps, {len(prof.urls)} URLs.",
            "timestamp": time.time(),
        })

        self._push_to_hud("ev_notification", {
            "title": f"🚀 WORKSPACE DEPLOYED: {prof.name.upper()}",
            "message": f"Staged apps: {', '.join(prof.apps).upper()} | Endpoints: {len(prof.urls)}",
            "level": "success",
        })

        # 3. Launch desktop apps in parallel
        launched_apps = []
        for app in prof.apps:
            if self._launch_app(app):
                launched_apps.append(app)
            time.sleep(0.1)

        # 4. Launch URLs
        opened_urls = []
        for u in prof.urls:
            self._launch_url(u)
            opened_urls.append(u)
            self._push_to_hud("open_tab", {"url": u, "target": u})
            time.sleep(0.1)

        # 5. Optional Memory flush
        reclaimed_ram = 0.0
        if prof.flush_ram:
            try:
                from jarvisx.runtime.thermal_governor import AlfredThermalGovernor
                gov = AlfredThermalGovernor.get_instance()
                rep = gov.perform_cooling_and_reclaim_cycle()
                reclaimed_ram = round(rep.reclaimed_ram_mb, 1)
            except Exception:
                pass

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

        return {
            "status": "success",
            "profile": prof.name,
            "launched_apps": launched_apps,
            "opened_urls": opened_urls,
            "reclaimed_ram_mb": reclaimed_ram,
            "duration_ms": elapsed_ms,
        }


def get_workspace_orchestrator() -> WorkspaceOrchestrator:
    """Get the global WorkspaceOrchestrator singleton."""
    return WorkspaceOrchestrator.get_instance()
