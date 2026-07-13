import os
from pathlib import Path
from typing import Optional

from jarvisx.core.health import HealthStatus
from jarvisx.core.logging import StructuredLogger
from jarvisx.tools.base import BaseTool, ToolResult


class CADTool(BaseTool):
    """Tool for generating OpenSCAD parametric designs."""
    name = "cad"

    def __init__(self, workspace_dir: str = "cad_workspace", logger: Optional[StructuredLogger] = None):
        self.workspace_dir = Path(workspace_dir).resolve()
        self.logger = logger or StructuredLogger()
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def generate_scad(self, filename: str, scad_code: str) -> ToolResult:
        """Saves OpenSCAD code to the workspace."""
        if not filename.endswith(".scad"):
            filename += ".scad"
            
        file_path = (self.workspace_dir / filename).resolve()
        
        # Security check: ensure path stays within workspace
        try:
            file_path.relative_to(self.workspace_dir.resolve())
        except ValueError:
            return ToolResult(success=False, message="Permission denied: outside CAD workspace.")
            
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(scad_code)
            self.logger.write("info", "cad.file_generated", path=str(file_path))
            return ToolResult(success=True, message=f"Generated CAD model at {file_path}")
        except Exception as e:
            self.logger.write("error", "cad.generation.failed", error=str(e))
            return ToolResult(success=False, message=f"Failed to generate CAD model: {e}")

    def health(self) -> HealthStatus:
        if self.workspace_dir.exists():
            return HealthStatus.ok("CAD workspace available.")
        return HealthStatus.fail("CAD workspace missing.")
