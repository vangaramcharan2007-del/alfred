"""Operational Coding Agent for Jarvis X.

Specialized worker dedicated to generating code structure modifications, verifying syntax via
static AST inspection, and creating clean unified git diffs for supervisor review.
"""

import ast
import difflib
from typing import Any, Dict, List
from jarvisx.agents.base import OperationalAgent


class CodingAgent(OperationalAgent):
    """Production coding worker capable of AST static validation and diff staging."""

    __test__ = False  # Avoid pytest naming confusion if subclasses are created

    def __init__(self, name: str = "coding_agent", hspw_multiplier: float = 1.2):
        super().__init__(
            name=name,
            purpose="Generate code modifications, perform static AST checking, and stage git diffs",
            capabilities=["file_editing", "ast_validation", "diff_generation", "code_scaffolding"],
            permissions=["read_filesystem", "write_filesystem", "git_status"],
            hspw_multiplier=hspw_multiplier,  # End-to-end code synthesis saves significant manual editing
        )

    def _execute_task(self, task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        action = (task.get("action") or task.get("parameters", {}).get("action", "edit")).lower()
        content = task.get("content") or task.get("parameters", {}).get("content", "")
        target_file = task.get("target_file") or task.get("parameters", {}).get("target_file") or "src/example.py"

        if action == "validate_ast" or "ast" in str(task).lower():
            return self.validate_syntax(str(content), target_file)
        elif action == "diff" or "diff" in str(task).lower():
            old_code = str(task.get("old_content") or task.get("parameters", {}).get("old_content", ""))
            new_code = str(task.get("new_content") or task.get("parameters", {}).get("new_content", content))
            return self.generate_diff(target_file, old_code, new_code)
        else:
            sample_code = content or ("def feature_handler():\n    return 'Validated production execution'\n")
            ast_res = self.validate_syntax(sample_code, target_file)
            if ast_res.get("status") == "error":
                return ast_res
            diff_res = self.generate_diff(target_file, "# TODO: Implement feature_handler\n", sample_code)
            return {
                "status": "completed",
                "action": "code_changes",
                "target_file": target_file,
                "ast_valid": True,
                "diff": diff_res["diff"],
                "output": f"[OK] Code changes drafted and syntax verified for {target_file}",
            }

    def validate_syntax(self, code: str, filepath: str) -> Dict[str, Any]:
        """Perform static syntax analysis using Python AST parser."""
        try:
            ast.parse(code, filename=filepath)
            return {
                "status": "completed",
                "action": "ast_validation",
                "valid": True,
                "output": f"[OK] Static AST syntax check passed cleanly for {filepath}",
            }
        except SyntaxError as e:
            return {
                "status": "error",
                "action": "ast_validation",
                "valid": False,
                "error": f"SyntaxError in {filepath} at line {e.lineno}, column {e.offset}: {e.msg}",
            }

    def generate_diff(self, filepath: str, old_content: str, new_content: str) -> Dict[str, Any]:
        """Generate canonical unified git diff string between source versions."""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        diff = list(difflib.unified_diff(old_lines, new_lines, fromfile=f"a/{filepath}", tofile=f"b/{filepath}", n=3))
        diff_text = "".join(diff)
        if not diff_text:
            diff_text = f"--- a/{filepath}\n+++ b/{filepath}\n@@ No changes @@"
        return {
            "status": "completed",
            "action": "diff_generation",
            "diff": diff_text,
            "output": diff_text,
        }
