"""
Jarvis X — Surgical Ephemeral Repository Ingestion & Auto-Purge Engine.
Clones repositories ephemerally into temporary sandbox, extracts only the required modules/files,
integrates them cleanly into the workspace, and instantly deletes all cloned bloat and .git history.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional


class SurgicalRepoExtractor:
    """
    Zero-Disk-Bloat Repository Ingestor.
    1. Shallow clone (--depth 1) into ephemeral temp directory.
    2. Extract only targeted files, algorithms, or directories.
    3. Copy clean modules into project workspace.
    4. Instantly eradicate temporary clone and .git bloat.
    """

    def __init__(self, workspace_root: str = "."):
        self.workspace = Path(workspace_root).resolve()

    def extract_and_integrate(
        self,
        repo_url: str,
        extract_paths: Optional[List[str]] = None,
        target_destination: str = "src/integrations",
        feature_intent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Ephemeral Clone -> Extract Required Modules -> Integrate -> Purge Temp Bloat.
        """
        repo_clean = repo_url.strip().strip("'\"")
        if not repo_clean.startswith(("http://", "https://", "git@")):
            if "/" in repo_clean:
                repo_clean = f"https://github.com/{repo_clean}.git"

        # Determine target destination path inside workspace
        dest_dir = self.workspace / target_destination
        dest_dir.mkdir(parents=True, exist_ok=True)

        extracted_files: List[str] = []
        total_cloned_bytes = 0
        integrated_bytes = 0

        # Create temporary sandbox directory that auto-purges
        with tempfile.TemporaryDirectory(prefix="alfred_repo_") as temp_dir:
            temp_path = Path(temp_dir)
            
            # 1. Shallow ephemeral clone (--depth 1, single branch)
            cmd = ["git", "clone", "--depth", "1", "--single-branch", repo_clean, str(temp_path / "repo")]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
                if res.returncode != 0:
                    return {
                        "status": "failed",
                        "error": f"Failed to shallow-clone repository: {res.stderr.strip() or res.stdout.strip()}",
                    }
            except subprocess.TimeoutExpired:
                return {"status": "failed", "error": "Shallow clone timed out after 90s."}
            except Exception as e:
                return {"status": "failed", "error": str(e)}

            cloned_repo_path = temp_path / "repo"

            # Calculate total temporary cloned size (including .git bloat)
            for root, dirs, files in os.walk(cloned_repo_path):
                for f in files:
                    try:
                        total_cloned_bytes += os.path.getsize(os.path.join(root, f))
                    except Exception:
                        pass

            # 2. Identify files to extract
            files_to_copy: List[Path] = []

            if extract_paths:
                for p in extract_paths:
                    candidate = cloned_repo_path / p
                    if candidate.is_file():
                        files_to_copy.append(candidate)
                    elif candidate.is_dir():
                        for subfile in candidate.rglob("*"):
                            if subfile.is_file() and not any(part.startswith(".") for part in subfile.parts):
                                files_to_copy.append(subfile)

            # If no explicit paths, auto-discover based on feature intent or key code files
            if not files_to_copy:
                files_to_copy = self._discover_relevant_files(cloned_repo_path, feature_intent)

            # 3. Copy only the selected files to destination
            for src_file in files_to_copy:
                try:
                    rel_path = src_file.relative_to(cloned_repo_path)
                    target_file = dest_dir / rel_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, target_file)
                    
                    file_size = target_file.stat().st_size
                    integrated_bytes += file_size
                    extracted_files.append(str(rel_path))
                except Exception as ex:
                    continue

        # 4. Ephemeral directory has now been completely deleted from disk!
        freed_mb = max(0.0, (total_cloned_bytes - integrated_bytes) / (1024 * 1024))
        integrated_kb = integrated_bytes / 1024

        return {
            "status": "success",
            "repo_url": repo_clean,
            "destination": str(dest_dir.relative_to(self.workspace)),
            "extracted_files_count": len(extracted_files),
            "extracted_files": extracted_files[:15],
            "integrated_size_kb": round(integrated_kb, 2),
            "disk_bloat_purged_mb": round(freed_mb, 2),
            "message": (
                f"Surgical integration complete! Extracted {len(extracted_files)} files ({integrated_kb:.1f} KB) "
                f"into '{dest_dir.relative_to(self.workspace)}'. "
                f"Purged {freed_mb:.1f} MB of temporary clone bloat and .git history from disk."
            ),
        }

    def fetch_raw_github_file(
        self,
        repo_owner_name: str,
        file_path_in_repo: str,
        target_local_path: Optional[str] = None,
        branch: str = "main",
    ) -> Dict[str, Any]:
        """
        Direct Zero-Clone file fetch via raw.githubusercontent.com (0 MB clone).
        """
        # Clean 'owner/repo'
        owner_repo = repo_owner_name.replace("https://github.com/", "").replace(".git", "").strip("/")
        raw_url = f"https://raw.githubusercontent.com/{owner_repo}/{branch}/{file_path_in_repo.lstrip('/')}"

        # Fallback to 'master' if 'main' fails
        req = urllib.request.Request(raw_url, headers={"User-Agent": "Alfred-OS"})
        content = None
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
        except Exception:
            raw_url_master = f"https://raw.githubusercontent.com/{owner_repo}/master/{file_path_in_repo.lstrip('/')}"
            try:
                with urllib.request.urlopen(urllib.request.Request(raw_url_master, headers={"User-Agent": "Alfred-OS"}), timeout=15) as resp:
                    content = resp.read().decode("utf-8", errors="ignore")
            except Exception as e:
                return {"status": "failed", "error": f"Could not fetch file from GitHub: {e}"}

        # Save locally if destination requested
        if target_local_path:
            save_path = self.workspace / target_local_path
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(content)
            dest_msg = f"Saved to {target_local_path}"
        else:
            filename = Path(file_path_in_repo).name
            save_path = self.workspace / "src" / "integrations" / filename
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(content)
            dest_msg = f"Saved to src/integrations/{filename}"

        return {
            "status": "success",
            "source_url": raw_url,
            "file_name": Path(file_path_in_repo).name,
            "size_bytes": len(content),
            "destination": dest_msg,
            "message": f"Zero-clone download complete for '{file_path_in_repo}' ({len(content)} bytes). {dest_msg}.",
        }

    def _discover_relevant_files(self, repo_path: Path, feature_intent: Optional[str] = None) -> List[Path]:
        """Auto-discover relevant Python/code files in the repository."""
        keywords = []
        if feature_intent:
            keywords = [w.lower() for w in re.findall(r'\w+', feature_intent) if len(w) > 2]

        found: List[Path] = []
        for file_path in repo_path.rglob("*"):
            if not file_path.is_file():
                continue
            if any(part.startswith((".", "__", "venv", "node_modules", "test", "tests")) for part in file_path.parts):
                continue
            if file_path.suffix in (".py", ".js", ".ts", ".go", ".rs", ".java", ".cpp", ".h"):
                # If keywords match filename or path
                if keywords:
                    if any(kw in file_path.name.lower() or kw in str(file_path).lower() for kw in keywords):
                        found.append(file_path)
                else:
                    found.append(file_path)

        # Return top 20 relevant files max
        return found[:20]


# Singleton accessor
_surgical_extractor: Optional[SurgicalRepoExtractor] = None

def get_surgical_extractor() -> SurgicalRepoExtractor:
    global _surgical_extractor
    if _surgical_extractor is None:
        _surgical_extractor = SurgicalRepoExtractor()
    return _surgical_extractor
