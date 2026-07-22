from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from jarvisx.core.capabilities.base import Capability, CapabilityProvider, ProviderError
from jarvisx.core.capabilities.evaluation import ProviderEvaluation


class SystemFileSystemProvider(CapabilityProvider):
    name = "SystemFileSystem"
    capability = Capability.FILE_SYSTEM

    def is_available(self) -> bool:
        return True

    def evaluate(self, task: dict[str, Any]) -> ProviderEvaluation:
        return ProviderEvaluation(
            provider_name=self.name,
            capability=self.capability.name,
            score=100.0,
            available=True,
            confidence=1.0,
            latency_ms=5.0,
            reason="Native Python pathlib implementation."
        )

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

    def verify(self, task: dict[str, Any]) -> bool:
        """
        Verify if the file system task succeeded.
        """
        action = task.get("action")
        target = task.get("target")
        if not target:
            return False
            
        target_path = Path(target)
        if action == "create_folder":
            return target_path.exists() and target_path.is_dir()
        elif action == "delete":
            return not target_path.exists()
            
        return True
