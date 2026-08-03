from __future__ import annotations
import shutil
import uuid
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class OpenHandsWorkspace:
    workspace_id: str
    path: str
    is_persistent: bool = True
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "path": self.path,
            "is_persistent": self.is_persistent,
            "is_active": self.is_active,
            "metadata": self.metadata
        }

class OpenHandsWorkspaceManager:
    def __init__(self, base_workspace_dir: Optional[str] = None):
        self.base_dir = Path(base_workspace_dir or "./sandbox/openhands_workspaces")
        self.workspaces: Dict[str, OpenHandsWorkspace] = {}

    def create_workspace(self, path: Optional[str] = None, persistent: bool = True) -> OpenHandsWorkspace:
        wid = f"oh_ws_{uuid.uuid4().hex[:8]}"
        ws_path = Path(path) if path else self.base_dir / wid
        ws_path.mkdir(parents=True, exist_ok=True)

        workspace = OpenHandsWorkspace(
            workspace_id=wid,
            path=str(ws_path.resolve()),
            is_persistent=persistent,
            is_active=True,
            metadata={"created_via": "OpenHandsWorkspaceManager"}
        )
        self.workspaces[wid] = workspace
        return workspace

    def open_repository(self, repo_path: str) -> OpenHandsWorkspace:
        path = Path(repo_path).resolve()
        for ws in self.workspaces.values():
            if ws.path == str(path):
                ws.is_active = True
                return ws
        return self.create_workspace(path=str(path), persistent=True)

    def close_workspace(self, workspace_id: str) -> bool:
        ws = self.workspaces.get(workspace_id)
        if ws:
            ws.is_active = False
            return True
        return False

    def reset_workspace(self, workspace_id: str) -> bool:
        ws = self.workspaces.get(workspace_id)
        if ws:
            ws.metadata["reset_count"] = ws.metadata.get("reset_count", 0) + 1
            return True
        return False

    def cleanup(self, workspace_id: str) -> bool:
        ws = self.workspaces.get(workspace_id)
        if ws:
            ws.is_active = False
            if not ws.is_persistent and Path(ws.path).exists():
                shutil.rmtree(ws.path, ignore_errors=True)
            del self.workspaces[workspace_id]
            return True
        return False

    def get_workspace(self, workspace_id: str) -> Optional[OpenHandsWorkspace]:
        return self.workspaces.get(workspace_id)

    def list_workspaces(self) -> List[OpenHandsWorkspace]:
        return list(self.workspaces.values())
