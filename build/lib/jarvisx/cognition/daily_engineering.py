"""
Daily Engineering Context & Briefing Generator.
Automatically detects active workspace, git branch, modified files, failing tests, TODOs,
and formats a personalized engineering context briefing.
"""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from jarvisx.automation.coding_commands import get_workspace_context, _call_ollama


class DailyEngineeringContext:
    """
    Generates intelligent daily engineering context and next recommended actions.
    """

    def generate_briefing(self, cwd: str = ".") -> Dict[str, Any]:
        ctx = get_workspace_context(cwd)

        branch = ctx.get("branch", "main")
        modified = ctx.get("modified_files", [])
        commits = ctx.get("recent_commits", [])
        todos = ctx.get("todos", [])
        test_code = ctx.get("test_exit_code", 0)

        hour = float(os.environ.get("MOCK_HOUR", 19.0))
        if hour < 12:
            greeting = "Good morning Ramcharan."
        elif hour < 17:
            greeting = "Good afternoon Ramcharan."
        else:
            greeting = "Good evening Ramcharan."

        status_desc = []
        if modified:
            status_desc.append(f"Jarvis X detected {len(modified)} modified file{'s' if len(modified) > 1 else ''}.")
        else:
            status_desc.append("Working tree is clean.")

        if commits:
            status_desc.append(f"Last commit: '{commits[0]}'.")

        if test_code != 0:
            status_desc.append("WARNING: Unit test sandbox has failing assertions.")
            rec_action = "Fixing failing tests via 'python -m jarvisx fix this'."
        elif modified:
            rec_action = f"Reviewing changes in {modified[0]} and running verification tests."
        elif todos:
            rec_action = f"Addressing open TODO: {todos[0]}."
        else:
            rec_action = "Continuing core architecture evolution."

        summary_text = (
            f"{greeting} { ' '.join(status_desc) }\n"
            f"Your recommended next action is: {rec_action}"
        )

        return {
            "status": "SUCCESS",
            "greeting": greeting,
            "branch": branch,
            "modified_count": len(modified),
            "modified_files": modified,
            "test_status": "PASSING" if test_code == 0 else "FAILING",
            "recommended_action": rec_action,
            "briefing_text": summary_text
        }
