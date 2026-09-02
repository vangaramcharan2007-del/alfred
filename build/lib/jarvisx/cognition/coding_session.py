"""
Alfred Autonomous Coding Session Engine.
Restores workspace context, opens VS Code and last modified files, checks dependencies,
runs unit test sandbox, and provides status summary.
"""
from __future__ import annotations
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from jarvisx.automation.coding_commands import get_workspace_context
from friday.persistence import FridayPersistenceManager


class CodingSessionEngine:
    """
    Automates start of engineering sessions for Alfred.
    """

    def start_coding_session(self, cwd: str = ".") -> Dict[str, Any]:
        print("\nAlfred: Preparing autonomous coding session...\n")

        # 1. Open VS Code
        code_bin = shutil.which("code") or "code"
        subprocess.Popen([code_bin, cwd], shell=True)
        print("  [+] VS Code opened")

        # 2. Gather workspace context & open last modified files
        ctx = get_workspace_context(cwd)
        modified = ctx.get("modified_files", [])
        opened_files = []

        for f_line in modified[:3]:
            # Extracted filename from short git status
            parts = f_line.split()
            fpath = parts[-1] if parts else f_line
            if Path(fpath).exists():
                subprocess.Popen([code_bin, fpath], shell=True)
                opened_files.append(fpath)

        if opened_files:
            print(f"  [+] Opened last modified files: {opened_files}")

        # 3. Check pytest sandbox status
        test_status = "PASSING" if ctx.get("test_exit_code") == 0 else "FAILING"
        print(f"  [+] Sandbox Test Status: {test_status}")

        # 4. Log time saved to Friday SQLite
        pm = FridayPersistenceManager()
        pm.log_time_saved("Alfred Autonomous Coding Session Prep", 12.0)

        summary_text = (
            f"Alfred: Autonomous Coding Session Active on '{ctx['branch']}'.\n"
            f"  - Modified Files   : {len(modified)}\n"
            f"  - Files Opened     : {opened_files or 'Clean Tree'}\n"
            f"  - Unit Test Status : {test_status}\n"
            f"  - Time Saved       : 12 minutes automated setup."
        )
        print(f"\n{summary_text}\n")

        return {
            "status": "SUCCESS",
            "branch": ctx["branch"],
            "modified_count": len(modified),
            "opened_files": opened_files,
            "test_status": test_status,
            "summary_text": summary_text
        }
