"""
Jarvis X — Autonomous Git Repository Integrator & Developer CLI Engine.
Enables Alfred to clone, pull, commit, push, analyze, and integrate remote and local codebases.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class GitRepoIntegrator:
    """Zero-fluff production Git & Codebase Integration Engine."""

    def __init__(self, default_workspace: str = "."):
        self.workspace = Path(default_workspace).resolve()

    def clone_repository(
        self,
        repo_url: str,
        target_dir: Optional[str] = None,
        branch: Optional[str] = None,
        depth: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Clone a remote Git repository into the workspace."""
        repo_clean = repo_url.strip().strip("'\"")
        
        # If user gave a shorthand like 'owner/repo' or 'github.com/owner/repo'
        if not repo_clean.startswith(("http://", "https://", "git@")):
            if "/" in repo_clean:
                repo_clean = f"https://github.com/{repo_clean}.git"

        # Determine target folder name if not provided
        if not target_dir:
            match = re.search(r'/([^/]+?)(?:\.git)?$', repo_clean)
            folder_name = match.group(1) if match else "cloned_repo"
            target_path = self.workspace / folder_name
        else:
            target_path = Path(target_dir)
            if not target_path.is_absolute():
                target_path = self.workspace / target_path

        cmd = ["git", "clone"]
        if branch:
            cmd.extend(["-b", branch])
        if depth:
            cmd.extend(["--depth", str(depth)])
        cmd.extend([repo_clean, str(target_path)])

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if res.returncode != 0:
                return {
                    "status": "failed",
                    "error": res.stderr.strip() or res.stdout.strip() or "Git clone returned non-zero exit code.",
                    "command": " ".join(cmd),
                }

            # Inspect cloned repo
            structure = self._inspect_repo_structure(target_path)
            return {
                "status": "success",
                "message": f"Successfully cloned repository into '{target_path.name}'.",
                "repo_url": repo_clean,
                "target_path": str(target_path),
                "structure": structure,
            }
        except subprocess.TimeoutExpired:
            return {"status": "failed", "error": "Git clone timed out after 120 seconds."}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def get_repo_status(self, repo_dir: Optional[str] = None) -> Dict[str, Any]:
        """Get git status and branch information for a repository."""
        target_path = Path(repo_dir).resolve() if repo_dir else self.workspace
        if not (target_path / ".git").exists():
            return {"status": "failed", "error": f"Path '{target_path}' is not a git repository."}

        try:
            branch_res = subprocess.run(["git", "branch", "--show-current"], cwd=str(target_path), capture_output=True, text=True, timeout=10)
            current_branch = branch_res.stdout.strip() or "HEAD"

            status_res = subprocess.run(["git", "status", "--porcelain"], cwd=str(target_path), capture_output=True, text=True, timeout=10)
            status_lines = [line.strip() for line in status_res.stdout.splitlines() if line.strip()]

            log_res = subprocess.run(["git", "log", "-1", "--oneline"], cwd=str(target_path), capture_output=True, text=True, timeout=10)
            latest_commit = log_res.stdout.strip()

            return {
                "status": "success",
                "repo_path": str(target_path),
                "branch": current_branch,
                "latest_commit": latest_commit,
                "modified_files_count": len(status_lines),
                "changes": status_lines[:20],
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def sync_repository(
        self,
        repo_dir: Optional[str] = None,
        commit_message: str = "Update from Alfred OS",
        push: bool = True,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Stage all changes, commit, and push to remote."""
        target_path = Path(repo_dir).resolve() if repo_dir else self.workspace
        if not (target_path / ".git").exists():
            return {"status": "failed", "error": f"Path '{target_path}' is not a git repository."}

        try:
            # 1. Add
            add_res = subprocess.run(["git", "add", "."], cwd=str(target_path), capture_output=True, text=True, timeout=15)
            if add_res.returncode != 0:
                return {"status": "failed", "stage": "add", "error": add_res.stderr.strip()}

            # 2. Check if anything to commit
            status_res = subprocess.run(["git", "status", "--porcelain"], cwd=str(target_path), capture_output=True, text=True, timeout=10)
            if not status_res.stdout.strip():
                return {"status": "success", "message": "No new changes to commit. Working tree is clean."}

            # 3. Commit
            commit_res = subprocess.run(["git", "commit", "-m", commit_message], cwd=str(target_path), capture_output=True, text=True, timeout=15)
            if commit_res.returncode != 0:
                return {"status": "failed", "stage": "commit", "error": commit_res.stderr.strip()}

            # 4. Push if requested
            push_output = "Committed locally."
            if push:
                target_branch = branch or "main"
                push_res = subprocess.run(["git", "push", "origin", target_branch], cwd=str(target_path), capture_output=True, text=True, timeout=30)
                if push_res.returncode != 0:
                    # Try plain git push without explicit origin branch
                    push_res = subprocess.run(["git", "push"], cwd=str(target_path), capture_output=True, text=True, timeout=30)
                push_output = push_res.stdout.strip() or push_res.stderr.strip() or "Pushed to remote."

            return {
                "status": "success",
                "message": f"Successfully committed changes: '{commit_message}'",
                "push_status": push_output,
                "commit_summary": commit_res.stdout.strip(),
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def integrate_repository(
        self,
        repo_url_or_path: str,
        install_dependencies: bool = False,
    ) -> Dict[str, Any]:
        """
        Comprehensive repository integration:
        Clones or targets existing repository, analyzes tech stack, files, entry points, and returns architecture breakdown.
        """
        # If URL, clone it first
        if repo_url_or_path.startswith(("http://", "https://", "git@")) or ("/" in repo_url_or_path and not os.path.exists(repo_url_or_path)):
            clone_res = self.clone_repository(repo_url_or_path)
            if clone_res.get("status") != "success":
                return clone_res
            repo_path = Path(clone_res["target_path"])
        else:
            repo_path = Path(repo_url_or_path).resolve()
            if not repo_path.exists():
                return {"status": "failed", "error": f"Path '{repo_path}' does not exist."}

        structure = self._inspect_repo_structure(repo_path)
        
        return {
            "status": "success",
            "repo_name": repo_path.name,
            "repo_path": str(repo_path),
            "tech_stack": structure.get("tech_stack"),
            "entry_points": structure.get("entry_points"),
            "key_files": structure.get("key_files"),
            "total_files": structure.get("total_files"),
            "readme_preview": structure.get("readme_preview"),
            "message": f"Repository '{repo_path.name}' integrated successfully into Alfred OS workspace.",
        }

    def execute_terminal_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout_seconds: int = 60,
    ) -> Dict[str, Any]:
        """Safely execute shell/CLI command in workspace."""
        target_cwd = str(Path(cwd).resolve()) if cwd else str(self.workspace)

        # Block destructive root wipe commands
        cmd_clean = command.strip()
        if re.search(r'\b(rm\s+-rf\s+/|format\s+[c-z]:|rd\s+/s\s+/q\s+c:\\)\b', cmd_clean, re.I):
            return {"status": "blocked", "error": "Destructive system wipe commands are blocked by Alfred Safety Sentinel."}

        try:
            res = subprocess.run(
                cmd_clean,
                cwd=target_cwd,
                capture_output=True,
                text=True,
                shell=True,
                timeout=timeout_seconds,
            )
            return {
                "status": "success" if res.returncode == 0 else "failed",
                "exit_code": res.returncode,
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip(),
                "command": cmd_clean,
            }
        except subprocess.TimeoutExpired:
            return {"status": "failed", "error": f"Command timed out after {timeout_seconds}s."}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _inspect_repo_structure(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze repository architecture and key files."""
        key_files = []
        tech_stack = []
        entry_points = []
        total_files = 0
        readme_preview = ""

        # Check common project files
        if (repo_path / "pyproject.toml").exists() or (repo_path / "requirements.txt").exists():
            tech_stack.append("Python")
        if (repo_path / "package.json").exists():
            tech_stack.append("Node.js / JavaScript")
        if (repo_path / "Cargo.toml").exists():
            tech_stack.append("Rust")
        if (repo_path / "go.mod").exists():
            tech_stack.append("Go")
        if (repo_path / "pom.xml").exists() or (repo_path / "build.gradle").exists():
            tech_stack.append("Java")

        # Read README preview
        for readme_name in ("README.md", "readme.md", "README.txt", "README"):
            readme_file = repo_path / readme_name
            if readme_file.exists():
                try:
                    with open(readme_file, "r", encoding="utf-8", errors="ignore") as f:
                        readme_preview = f.read(800).strip()
                    break
                except Exception:
                    pass

        # Scan directory files
        try:
            for item in repo_path.iterdir():
                if item.name.startswith((".git", ".venv", "__pycache__", "node_modules")):
                    continue
                key_files.append(item.name)
                if item.is_file() and item.name in ("main.py", "app.py", "index.js", "server.js", "main.go"):
                    entry_points.append(item.name)
        except Exception:
            pass

        return {
            "tech_stack": tech_stack or ["General Codebase"],
            "key_files": key_files[:25],
            "entry_points": entry_points,
            "readme_preview": readme_preview,
        }


# Singleton accessor
_integrator_instance: Optional[GitRepoIntegrator] = None

def get_git_integrator() -> GitRepoIntegrator:
    global _integrator_instance
    if _integrator_instance is None:
        _integrator_instance = GitRepoIntegrator()
    return _integrator_instance
