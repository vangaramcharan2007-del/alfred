from __future__ import annotations
import subprocess
import sys
from typing import Dict, Any, Optional

class BatteryWatcher:
    """
    Monitors system battery state and returns alerts if low.
    """
    def check_battery(self) -> Dict[str, Any]:
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "status": "OK" if battery.percent > 20 else "LOW",
                    "percent": battery.percent,
                    "power_plugged": battery.power_plugged,
                    "alert": "Battery low (<20%) -- Please connect charger" if battery.percent <= 20 else None
                }
        except Exception:
            pass
        return {"status": "NOT_SUPPORTED", "reason": "Battery sensor unavailable"}


class GitWatcher:
    """
    Monitors local git repository for modified or uncommitted files.
    """
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
    """
    Monitors pytest unit test suite status.
    """
    def check_tests(self, cwd: str = ".") -> Dict[str, Any]:
        try:
            res = subprocess.run([sys.executable, "-m", "pytest", "tests/unit/"], cwd=cwd, capture_output=True, text=True, check=False)
            return {
                "status": "PASS" if res.returncode == 0 else "FAIL",
                "exit_code": res.returncode
            }
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
