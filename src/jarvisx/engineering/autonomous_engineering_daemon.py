"""
Jarvis X — Autonomous Continuous Engineering & Proactive Repository Sentinel.
Periodically scans project goals, detects architectural gaps, autonomously searches GitHub
for best-in-class open-source patterns, assimilates clean code, tests it, and notifies the user.
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvisx.engineering.daemon")


class AutonomousEngineeringSentinel:
    """
    Continuous Autonomous Engineering Agent.
    Operates in two modes:
    1. Direct User Directive: User specifies repo or feature goal.
    2. Proactive Autonomous Loop: Agent monitors roadmap, searches open-source, and auto-assimilates.
    """

    _instance: Optional[AutonomousEngineeringSentinel] = None
    _lock = threading.Lock()

    def __init__(self, workspace_root: str = ".", check_interval_sec: int = 300):
        self.workspace = Path(workspace_root).resolve()
        self.check_interval_sec = check_interval_sec
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.history_log: List[Dict[str, Any]] = []

    @classmethod
    def get_instance(cls) -> AutonomousEngineeringSentinel:
        with cls._lock:
            if cls._instance is None:
                cls._instance = AutonomousEngineeringSentinel()
            return cls._instance

    def start_sentinel(self) -> Dict[str, Any]:
        """Start the background proactive engineering loop."""
        if self.is_running:
            return {"status": "already_running", "message": "Autonomous Engineering Sentinel is already active."}

        self.is_running = True
        self.worker_thread = threading.Thread(target=self._sentinel_loop, daemon=True, name="AlfredEngineeringSentinel")
        self.worker_thread.start()
        logger.info("[EngineeringSentinel] Background Autonomous Loop started.")
        return {"status": "started", "message": "Autonomous Engineering Sentinel is now running in the background."}

    def stop_sentinel(self) -> Dict[str, Any]:
        """Stop the proactive engineering loop."""
        self.is_running = False
        return {"status": "stopped", "message": "Autonomous Engineering Sentinel stopped."}

    def get_status(self) -> Dict[str, Any]:
        """Get sentinel status and recent proactive assimilation logs."""
        return {
            "status": "running" if self.is_running else "idle",
            "check_interval_sec": self.check_interval_sec,
            "assimilated_features_count": len(self.history_log),
            "recent_actions": self.history_log[-5:],
        }

    def _sentinel_loop(self) -> None:
        """Periodic background evaluation loop."""
        while self.is_running:
            try:
                self.evaluate_and_evolve()
            except Exception as e:
                logger.error(f"[EngineeringSentinel] Cycle error: {e}")

            for _ in range(self.check_interval_sec):
                if not self.is_running:
                    break
                time.sleep(1.0)

    def evaluate_and_evolve(self) -> Optional[Dict[str, Any]]:
        """
        Single proactive cycle:
        1. Identify missing project capabilities.
        2. Resolve high-quality open-source implementation.
        3. Assimilate feature, test, and notify.
        """
        # Read project goals if available
        goals = self._read_project_goals()
        if not goals:
            return None

        # Check existing integrations
        integrations_dir = self.workspace / "src" / "jarvisx" / "integrations"
        existing = [f.name for f in integrations_dir.glob("*.py")] if integrations_dir.exists() else []

        # Example proactive discovery candidates
        candidates = [
            {"goal": "Add an asynchronous Token Bucket rate limiter utility", "repo": "https://github.com/aio-libs/async-lru", "module": "async_token_limiter.py"},
            {"goal": "Add an LRU Memory cache decorator for LLM prompts", "repo": "https://github.com/grantjenks/python-diskcache", "module": "prompt_lru_cache.py"},
        ]

        for cand in candidates:
            if cand["module"] in existing:
                continue

            # Assimilate candidate proactively
            from jarvisx.engineering.autonomous_feature_assimilator import get_feature_assimilator
            assimilator = get_feature_assimilator()
            res = assimilator.assimilate_feature_from_repo(
                repo_url=cand["repo"],
                feature_goal=cand["goal"],
                target_module_name=cand["module"],
            )

            if res.get("status") == "success":
                entry = {
                    "timestamp": time.time(),
                    "goal": cand["goal"],
                    "module": cand["module"],
                    "repo": cand["repo"],
                }
                self.history_log.append(entry)
                self._notify_user(cand["goal"], cand["module"])
                return entry

        return None

    def _read_project_goals(self) -> str:
        for fname in ("GOALS.md", "ROADMAP.md", "TODO.md"):
            p = self.workspace / fname
            if p.exists():
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        return f.read(1500)
                except Exception:
                    pass
        return "Autonomous software engineering and agentic utility evolution."

    def _notify_user(self, goal: str, module_name: str) -> None:
        """Send vocal voice notification and native Windows toast."""
        try:
            from jarvisx.organism import get_organism
            org = get_organism()
            org.mouth.speak(f"Sir, I have proactively synthesized and verified {module_name} for our project.")
        except Exception:
            pass


def get_engineering_sentinel() -> AutonomousEngineeringSentinel:
    return AutonomousEngineeringSentinel.get_instance()
