import os
from pathlib import Path


class FileSystem:
    """Safe local file system manipulation tool."""
    
    def __init__(self, root_dir: str = "."):
        # The project root is typically where the runtime is created or the current working directory.
        self.project_root = Path(root_dir).resolve()
        self.sandbox_dir = self.project_root / "jarvis_workspace"
        
        # Ensure the sandbox directory exists
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        
    def _enforce_sandbox(self, path: str) -> Path:
        """Resolves the path and ensures it's within the sandbox."""
        resolved = (self.sandbox_dir / path).resolve()
        if not str(resolved).startswith(str(self.sandbox_dir)):
            raise PermissionError(f"Access denied: path '{path}' is outside the sandbox.")
        return resolved
        
    def read_file(self, path: str) -> str:
        """Reads a file within the sandbox."""
        target = self._enforce_sandbox(path)
        if not target.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not target.is_file():
            raise IsADirectoryError(f"Path is a directory, not a file: {path}")
            
        with open(target, "r", encoding="utf-8") as f:
            return f.read()

    def write_file(self, path: str, content: str) -> None:
        """Writes to a file within the sandbox (creates directories if needed)."""
        target = self._enforce_sandbox(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
            
    def edit_file(self, path: str, old_text: str, new_text: str) -> None:
        """Applies a localized text replacement in a file within the sandbox."""
        content = self.read_file(path)
        if old_text not in content:
            raise ValueError(f"Could not find exact text '{old_text}' in file {path}")
        
        new_content = content.replace(old_text, new_text)
        self.write_file(path, new_content)
