from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.permission_manager import PermissionManager, PermissionLevel

class PermissionDeniedException(PermissionError):
    pass

@dataclass
class FileChangeRecord:
    file_path: str
    action: str  # "created", "modified", "deleted"
    content_before: Optional[str] = None
    content_after: Optional[str] = None

class CodeExecutor:
    def __init__(self, permission_manager: Optional[PermissionManager] = None):
        self.permission_manager = permission_manager or PermissionManager()

    def check_write_permission(self, capability_name: str = "coding_agent") -> bool:
        return self.permission_manager.check_permission(capability_name, PermissionLevel.WRITE)

    def write_file(self, repo_root: str, relative_path: str, content: str, capability_name: str = "coding_agent") -> FileChangeRecord:
        if not self.check_write_permission(capability_name):
            raise PermissionDeniedException(f"Write permission denied for capability '{capability_name}'.")

        root = Path(repo_root)
        full_path = (root / relative_path).resolve()
        
        # Ensure path safety - prevent directory traversal outside root
        if root.resolve() not in full_path.parents and root.resolve() != full_path:
            raise PermissionDeniedException("Target path is outside repository root.")

        full_path.parent.mkdir(parents=True, exist_ok=True)

        action = "modified" if full_path.exists() else "created"
        content_before = None
        if action == "modified":
            try:
                content_before = full_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                content_before = ""

        full_path.write_text(content, encoding="utf-8")

        return FileChangeRecord(
            file_path=relative_path,
            action=action,
            content_before=content_before,
            content_after=content
        )
