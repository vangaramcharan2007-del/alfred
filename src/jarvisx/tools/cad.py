import os
from pathlib import Path
from typing import Optional

from jarvisx.core.health import HealthStatus
from jarvisx.core.logging import StructuredLogger
from jarvisx.tools.base import BaseTool, ToolResult
import traceback


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

    def generate_cadquery(self, filename: str, script_code: str) -> ToolResult:
        """Executes CadQuery python code and saves to workspace."""
        if not (filename.endswith(".stl") or filename.endswith(".step")):
            filename += ".stl"
            
        file_path = (self.workspace_dir / filename).resolve()
        
        # Security check: ensure path stays within workspace
        try:
            file_path.relative_to(self.workspace_dir.resolve())
        except ValueError:
            return ToolResult(success=False, message="Permission denied: outside CAD workspace.")
            
        script_path = self.workspace_dir / f"build_{Path(filename).stem}.py"
        try:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_code)
                
            # We use exec in a sandboxed-ish environment with cadquery imported
            namespace = {}
            try:
                import cadquery as cq
                namespace['cq'] = cq
            except ImportError:
                return ToolResult(success=False, message="cadquery is not installed in the environment.")
                
            # The script is expected to define a variable `result` which is a cq.Workplane or similar
            exec(script_code, namespace)
            
            if 'result' in namespace:
                cq.exporters.export(namespace['result'], str(file_path))
                self.logger.write("info", "cad.cadquery.success", path=str(file_path))
                return ToolResult(success=True, message=f"Generated CAD model at {file_path}")
            else:
                return ToolResult(success=False, message="Script executed but 'result' variable was not defined to export.")
                
        except Exception as e:
            error_trace = traceback.format_exc()
            self.logger.write("error", "cad.cadquery.failed", error=str(e), trace=error_trace)
            return ToolResult(success=False, message=f"Failed to generate CadQuery model: {e}")

    def health(self) -> HealthStatus:
        if self.workspace_dir.exists():
            return HealthStatus.ok("CAD workspace available.")
        return HealthStatus.fail("CAD workspace missing.")
