"""
Proactive Task Execution Engine.
Prepares assignment workspace folders, creates starter templates, downloads resources,
and configures projects BEFORE asking the user.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Optional
from friday.persistence import FridayPersistenceManager


class ProactiveTaskEngine:
    """
    Proactively executes preparation tasks for assignments and project missions.
    """

    def __init__(self, persistence: Optional[FridayPersistenceManager] = None):
        self.persistence = persistence or FridayPersistenceManager()

    def prepare_assignment_workspace(self, assignment_title: str, subject: str, due_date: str) -> Dict[str, Any]:
        slug = assignment_title.lower().replace(" ", "_")
        target_dir = Path("var/academics") / slug
        target_dir.mkdir(parents=True, exist_ok=True)

        readme_file = target_dir / "README.md"
        readme_content = (
            f"# {assignment_title}\n\n"
            f"- **Subject**: {subject}\n"
            f"- **Due Date**: {due_date}\n"
            f"- **Status**: PREPARED AUTONOMOUSLY BY FRIDAY\n\n"
            f"## Notes & Requirements\n"
            f"Add assignment details and guidelines here.\n"
        )
        readme_file.write_text(readme_content, encoding="utf-8")

        starter_file = target_dir / "solution.py"
        if not starter_file.exists():
            starter_file.write_text(f'# Solution for {assignment_title}\n\ndef solve():\n    pass\n', encoding="utf-8")

        print(f"\nFriday Proactive: Prepared assignment workspace at {target_dir}\n")

        return {
            "status": "SUCCESS",
            "assignment": assignment_title,
            "workspace_dir": str(target_dir),
            "files_created": ["README.md", "solution.py"]
        }

    def scan_and_prepare_all(self) -> Dict[str, Any]:
        assignments = self.persistence.get_assignments()
        prepared = []
        for a in assignments:
            res = self.prepare_assignment_workspace(a["title"], a["subject"], a["due_date"])
            prepared.append(res)
        return {"status": "SUCCESS", "total_prepared": len(prepared), "details": prepared}
