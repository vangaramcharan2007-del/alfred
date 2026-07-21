from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from jarvisx.core.capabilities.base import Capability, CapabilityProvider, ProviderError


class SystemFileSystemProvider(CapabilityProvider):
    name = "SystemFileSystem"
    capability = Capability.FILE_SYSTEM

    def is_available(self) -> bool:
        return True

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Executes file system actions.
        task shape: {"action": "create_folder" | "delete", "target": "path/to/target"}
        """
        action = task.get("action")
        target = task.get("target")

        if not action or not target:
            raise ProviderError("FileSystem task requires 'action' and 'target'.")

        target_path = Path(target)

        if action == "create_folder":
            target_path.mkdir(parents=True, exist_ok=True)
            return {"status": "success", "message": f"Successfully created folder {target}."}
            
        elif action == "delete":
            if target_path.is_dir():
                shutil.rmtree(target_path)
            elif target_path.is_file():
                target_path.unlink()
            return {"status": "success", "message": f"Successfully deleted {target}."}
            
        else:
            raise ProviderError(f"Unsupported file system action: {action}")
