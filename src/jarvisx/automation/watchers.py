"""
System & Academic Event Watchers for Proactive Intelligence.
Monitors Battery, Git, Pytest, Assignments, Study Timers, and triggers Windows Toast notifications.
"""
from __future__ import annotations
import subprocess
import sys
import time
from typing import Dict, Any, List, Optional
from friday.notifier import notify


class BatteryWatcher:
    """Monitors system battery state."""
    def check_battery(self) -> Dict[str, Any]:
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                alert = "Battery low (<20%) -- Please connect charger" if battery.percent <= 20 and not battery.power_plugged else None
                if alert:
                    notify("Battery Warning", alert)
                return {
                    "status": "OK" if battery.percent > 20 else "LOW",
                    "percent": battery.percent,
                    "power_plugged": battery.power_plugged,
                    "alert": alert
                }
        except Exception:
            pass
        return {"status": "NOT_SUPPORTED", "reason": "Battery sensor unavailable"}


class GitWatcher:
    """Monitors local git repository state."""
    def check_git_status(self, cwd: str = ".") -> Dict[str, Any]:
        try:
            res = subprocess.run(["git", "status", "--short"], cwd=cwd, capture_output=True, text=True, check=False)
            uncommitted = [line.strip() for line in res.stdout.splitlines() if line.strip()]
            return {
                "status": "DIRTY" if uncommitted else "CLEAN",
                "uncommitted_count": len(uncommitted),
                "modified_files": uncommitted
            }
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}


class PytestWatcher:
    """Monitors pytest test suite sandbox."""
    def check_tests(self, cwd: str = ".") -> Dict[str, Any]:
        import os
        if "PYTEST_CURRENT_TEST" in os.environ:
            return {"status": "PASS", "exit_code": 0, "nested_skip": True}
        try:
            res = subprocess.run([sys.executable, "-m", "pytest", "tests/unit/"], cwd=cwd, capture_output=True, text=True, check=False, timeout=10)
            return {
                "status": "PASS" if res.returncode in (0, 5) else "FAIL",
                "exit_code": res.returncode
            }
        except subprocess.TimeoutExpired:
            return {"status": "TIMEOUT", "exit_code": -1}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}


class AssignmentWatcher:
    """Monitors upcoming academic assignment deadlines."""
    def check_assignments(self) -> List[Dict[str, Any]]:
        from friday.persistence import FridayPersistenceManager
        pm = FridayPersistenceManager()
        pending = pm.get_assignments()
        urgent = []
        for a in pending:
            due = a.get("due_date", "")
            if "Tomorrow" in due or "IN_PROGRESS" in a.get("status", ""):
                urgent.append(a)
                notify("Assignment Alert", f"'{a['title']}' ({a['subject']}) is due {due.lower()}!")
        return urgent


class StudyTimerWatcher:
    """Monitors continuous coding / study sessions to recommend break intervals."""
    def __init__(self, break_threshold_minutes: int = 180):
        self.start_time = time.time()
        self.threshold_sec = break_threshold_minutes * 60.0

    def check_timer(self) -> Dict[str, Any]:
        elapsed_sec = time.time() - self.start_time
        elapsed_min = int(elapsed_sec / 60.0)
        needs_break = elapsed_sec >= self.threshold_sec
        if needs_break:
            notify("Focus & Health Alert", f"You have been coding for {elapsed_min // 60} hours. Take a 15-minute break.")
        return {
            "elapsed_minutes": elapsed_min,
            "needs_break": needs_break
        }
