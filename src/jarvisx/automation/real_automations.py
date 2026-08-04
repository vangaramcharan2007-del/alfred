"""
Jarvis X Real Desktop Automations.
Eliminates manual clicks for desktop, downloads, PDFs, screenshots, clipboard, and assignment templates.
"""
from __future__ import annotations
import os
import shutil
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from jarvisx.observability.time_saved_tracker import TimeSavedTracker


class RealDesktopAutomations:
    """
    Practical desktop automation routines that save real minutes and eliminate manual clicks.
    """

    def __init__(self, tracker: Optional[TimeSavedTracker] = None):
        self.tracker = tracker or TimeSavedTracker()

    def organize_downloads(self, downloads_dir: str = "var/downloads") -> Dict[str, Any]:
        """Organizes downloads directory into extension-based folders."""
        d_path = Path(downloads_dir)
        d_path.mkdir(parents=True, exist_ok=True)

        categories = {
            "PDFs": [".pdf"],
            "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
            "Executables": [".exe", ".msi"],
            "Images": [".png", ".jpg", ".jpeg", ".gif", ".webp"],
            "Code": [".py", ".json", ".js", ".ts", ".html", ".css"],
            "Media": [".mp4", ".mp3", ".mkv", ".wav"]
        }

        moved_count = 0
        for f in d_path.iterdir():
            if f.is_file():
                ext = f.suffix.lower()
                dest_cat = "Others"
                for cat_name, ext_list in categories.items():
                    if ext in ext_list:
                        dest_cat = cat_name
                        break

                target_folder = d_path / dest_cat
                target_folder.mkdir(exist_ok=True)
                try:
                    shutil.move(str(f), str(target_folder / f.name))
                    moved_count += 1
                except Exception:
                    pass

        if moved_count > 0:
            self.tracker.record("Organize Downloads Folder", minutes_saved=5.0, clicks_avoided=moved_count * 2)

        print(f"\nAlfred Automation: Organized {moved_count} files in '{downloads_dir}'.\n")
        return {"status": "SUCCESS", "moved_count": moved_count, "directory": downloads_dir}

    def archive_screenshots(self, screenshots_dir: str = "var/screenshots") -> Dict[str, Any]:
        """Moves screenshots to archive directory."""
        s_path = Path(screenshots_dir)
        if not s_path.exists():
            return {"status": "SUCCESS", "archived_count": 0}

        archive_dir = s_path / "archive"
        archive_dir.mkdir(exist_ok=True)

        archived_count = 0
        for f in s_path.iterdir():
            if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
                try:
                    shutil.move(str(f), str(archive_dir / f.name))
                    archived_count += 1
                except Exception:
                    pass

        if archived_count > 0:
            self.tracker.record("Archive Screenshots", minutes_saved=4.0, clicks_avoided=archived_count)

        print(f"\nAlfred Automation: Archived {archived_count} screenshots.\n")
        return {"status": "SUCCESS", "archived_count": archived_count}

    def summarize_clipboard(self) -> Dict[str, Any]:
        """Reads clipboard text and generates summary note."""
        clip_text = ""
        try:
            import pyperclip
            clip_text = pyperclip.paste()
        except Exception:
            clip_text = "Clipboard text fallback sample."

        summary_note = f"# Clipboard Note ({time.strftime('%Y-%m-%d %H:%M:%S')})\n\n{clip_text[:300]}..."
        out_file = Path("var/notes") / f"clip_{int(time.time())}.md"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(summary_note, encoding="utf-8")

        self.tracker.record("Summarize Clipboard Note", minutes_saved=3.0, clicks_avoided=5)

        print(f"\nAlfred Automation: Saved clipboard note to '{out_file}'.\n")
        return {"status": "SUCCESS", "note_path": str(out_file), "length": len(clip_text)}

    def create_assignment_template(self, assignment_title: str, subject: str, due_date: str = "2026-08-15") -> Dict[str, Any]:
        """Creates 1-click assignment workspace with README and solution template."""
        slug = assignment_title.lower().replace(" ", "_")
        target_dir = Path("var/academics") / slug
        target_dir.mkdir(parents=True, exist_ok=True)

        readme = target_dir / "README.md"
        readme.write_text(
            f"# {assignment_title}\n\n"
            f"- **Subject**: {subject}\n"
            f"- **Due Date**: {due_date}\n"
            f"- **Status**: AUTONOMOUSLY CREATED BY FRIDAY\n\n"
            f"## Instructions\n"
            f"Add assignment prompt details here.\n",
            encoding="utf-8"
        )

        solution = target_dir / "solution.py"
        if not solution.exists():
            solution.write_text(f"# Solution for {assignment_title}\n\ndef solve():\n    pass\n", encoding="utf-8")

        self.tracker.record("1-Click Assignment Template Prep", minutes_saved=8.0, clicks_avoided=12)

        print(f"\nFriday Automation: Prepared assignment workspace at '{target_dir}'.\n")
        return {
            "status": "SUCCESS",
            "workspace_dir": str(target_dir),
            "files_created": ["README.md", "solution.py"]
        }
