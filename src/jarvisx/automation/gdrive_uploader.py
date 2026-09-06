"""
GOOGLE DRIVE WORKFLOW & LINK HELPER
Facilitates uploading eCurricula PDF assignment submissions to Google Drive,
generating public share links ('Anyone with the link can view'), and validating them.
"""

import os
import re
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any


class GDriveHelper:
    """Manages Google Drive upload and link sharing for eCurricula submissions."""

    def __init__(self, target_folder_name: str = "SRM_DSA_Unit2"):
        self.target_folder_name = target_folder_name
        self.drive_url = "https://drive.google.com/drive/my-drive"

    def open_drive_in_browser(self):
        """Opens Google Drive in the user's default browser."""
        try:
            cmd = f'cmd.exe /c start "" "{self.drive_url}"'
            subprocess.Popen(cmd, shell=True)
            return True
        except Exception:
            return webbrowser.open(self.drive_url)

    def reveal_pdf_in_explorer(self, pdf_path: str):
        """Highlights the generated PDF in Windows File Explorer for instant drag & drop into Drive."""
        abs_path = str(Path(pdf_path).resolve())
        if os.path.exists(abs_path):
            subprocess.Popen(f'explorer /select,"{abs_path}"')
            return True
        return False

    @staticmethod
    def validate_and_normalize_drive_link(raw_link: str) -> Dict[str, Any]:
        """
        Validates whether a link is a valid Google Drive share link and
        converts it to a clean viewable link for eCurricula.
        """
        raw_link = raw_link.strip()
        # Extract file ID from patterns:
        # /file/d/FILE_ID/...
        # id=FILE_ID
        # /d/FILE_ID
        patterns = [
            r"/file/d/([a-zA-Z0-9_-]{25,})",
            r"id=([a-zA-Z0-9_-]{25,})",
            r"/d/([a-zA-Z0-9_-]{25,})"
        ]

        file_id = None
        for pat in patterns:
            match = re.search(pat, raw_link)
            if match:
                file_id = match.group(1)
                break

        if not file_id and len(raw_link) >= 25 and not raw_link.startswith("http"):
            file_id = raw_link  # Raw ID passed directly

        if file_id:
            normalized = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
            return {
                "valid": True,
                "file_id": file_id,
                "share_link": normalized,
                "message": "Valid Google Drive public share link"
            }
        else:
            return {
                "valid": False,
                "file_id": None,
                "share_link": raw_link,
                "message": "Invalid Google Drive link format. Ensure it contains /file/d/<FILE_ID>/"
            }
