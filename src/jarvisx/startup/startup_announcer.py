"""Alfred Windows Boot & Startup Announcer.

Generates and speaks the personalized welcome, schedule briefing, and progress summary
whenever the laptop starts or the daemon boots.
"""

from __future__ import annotations

import datetime
import logging
import os
import shutil
import sys
import threading
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvisx.startup_announcer")


class StartupAnnouncer:
    """Intelligent startup voice greeter and daily briefing broadcaster."""

    def __init__(self, var_dir: str = "var"):
        self.var_dir = var_dir

    def generate_briefing_text(self, persona: str = "ALFRED") -> str:
        """Compose the natural spoken startup briefing covering welcome, schedule, and progress."""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%A, %B %d")
        salutation = "Boss" if persona.upper() == "FRIDAY" else "Boss"

        # 1. Warm Greeting & Time
        greeting = f"Welcome {salutation}! Alfred OS is active and fully operational. The time is {time_str} on {date_str}."

        # 2. Goals & Schedule Progress
        schedule_parts = []
        try:
            from jarvisx.personal_os.goal_manager import GoalManager
            from jarvisx.personal_os.life_memory import LifeMemory
            life_mem = LifeMemory(os.path.join(self.var_dir, "db", "life_memory.db"))
            gm = GoalManager(memory=life_mem)
            goals = gm.list_goals()
            if goals:
                active_goals = [g for g in goals if g.status.value in ("active", "at_risk")]
                if active_goals:
                    top_goal = active_goals[0]
                    schedule_parts.append(
                        f"Your primary focus is '{top_goal.title}', currently at {int(top_goal.progress_pct)}% completion."
                    )
                    pending_milestones = [m for m in top_goal.milestones if not m.completed]
                    if pending_milestones:
                        schedule_parts.append(f"Next milestone: '{pending_milestones[0].title}'.")
        except Exception as e:
            logger.debug(f"Goal status lookup: {e}")

        # 3. System & Workspace Progress Summary
        progress_parts = []
        try:
            import psutil
            mem = psutil.virtual_memory()
            ram_free_gb = round(mem.available / (1024 ** 3), 1)
            progress_parts.append(f"System memory has {ram_free_gb} gigabytes available.")
        except Exception:
            pass

        try:
            from jarvisx.missions.persistence import MissionPersistenceManager
            pm = MissionPersistenceManager(os.path.join(self.var_dir, "db", "missions.db"))
            active_ckpts = pm.list_active_checkpoints()
            if active_ckpts:
                progress_parts.append(f"You have {len(active_ckpts)} in-flight mission checkpoint ready to resume.")
        except Exception:
            pass

        schedule_summary = " ".join(schedule_parts) if schedule_parts else "All scheduled milestones are up to date."
        progress_summary = " ".join(progress_parts) if progress_parts else "All core systems nominal."

        full_briefing = f"{greeting} {schedule_summary} {progress_summary} Standing by at your service."
        return full_briefing

    def announce(self, persona: str = "ALFRED", speak: bool = True, block: bool = False) -> Dict[str, Any]:
        """Generate briefing, log to disk, and speak aloud via native Windows TTS."""
        briefing_text = self.generate_briefing_text(persona=persona)

        # Log briefing
        log_dir = os.path.join(self.var_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "startup_briefing.log")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {briefing_text}\n")
        except Exception:
            pass

        # Speak via Windows Voice Runtime
        if speak:
            def _speak_worker():
                try:
                    from jarvisx.interface.voice_runtime import VoiceRuntimeEngine
                    voice = VoiceRuntimeEngine()
                    voice.speak(briefing_text, persona="Alfred")
                except Exception as e:
                    logger.warning(f"Startup speech synthesis: {e}")

            if block:
                _speak_worker()
            else:
                t = threading.Thread(target=_speak_worker, daemon=True)
                t.start()

        return {
            "status": "ANNOUNCED",
            "persona": persona,
            "briefing_text": briefing_text,
            "spoken": speak,
            "timestamp": timestamp,
        }
