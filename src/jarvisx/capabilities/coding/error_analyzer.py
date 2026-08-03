from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class DebuggingContext:
    exception_type: str
    error_message: str
    failing_file: Optional[str] = None
    line_number: Optional[int] = None
    function_name: Optional[str] = None
    likely_root_cause: str = "Unknown error"
    traceback_snippet: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exception_type": self.exception_type,
            "error_message": self.error_message,
            "failing_file": self.failing_file,
            "line_number": self.line_number,
            "function_name": self.function_name,
            "likely_root_cause": self.likely_root_cause,
            "traceback_snippet": self.traceback_snippet
        }

class ErrorAnalyzer:
    def analyze_traceback(self, stderr_output: str, stdout_output: str = "") -> DebuggingContext:
        full_text = f"{stdout_output}\n{stderr_output}".strip()
        if not full_text:
            return DebuggingContext(
                exception_type="UnknownError",
                error_message="No error output recorded.",
                likely_root_cause="Empty output stream"
            )

        # Common Python exception regex match e.g. "ZeroDivisionError: division by zero"
        exc_match = re.search(r'([A-Za-z_][A-Za-z0-9_]*Error|[A-Za-z_][A-Za-z0-9_]*Exception):\s*(.*)', full_text)
        exception_type = exc_match.group(1) if exc_match else "ExecutionError"
        error_message = exc_match.group(2).strip() if exc_match else full_text.splitlines()[-1]

        # File & line number extraction from stack trace
        # e.g. File "main.py", line 15, in calculate
        file_match = re.findall(r'File "([^"]+)", line (\d+)(?:, in ([^\n]+))?', full_text)
        failing_file = None
        line_number = None
        function_name = None

        if file_match:
            # Pick the last frame in user code (exclude site-packages / stdlib)
            user_frames = [f for f in file_match if "site-packages" not in f[0] and "Python" not in f[0]]
            target_frame = user_frames[-1] if user_frames else file_match[-1]
            failing_file = target_frame[0]
            line_number = int(target_frame[1])
            function_name = target_frame[2].strip() if target_frame[2] else None

        # Determine likely root cause based on exception type and error text
        root_cause = f"Exception '{exception_type}' raised: {error_message}"
        if "ZeroDivisionError" in exception_type or "division by zero" in error_message.lower():
            root_cause = "Division by zero without zero guard check"
        elif "TypeError" in exception_type:
            root_cause = "Type mismatch or invalid parameter type in function call"
        elif "KeyError" in exception_type:
            root_cause = "Accessing missing key in dictionary or response object"
        elif "AttributeError" in exception_type:
            root_cause = "Attempting to access non-existent property/attribute or NoneType object"
        elif "SyntaxError" in exception_type or "IndentationError" in exception_type:
            root_cause = "Syntax error or bad indentation in code file"
        elif "AssertionError" in exception_type or "assert" in error_message.lower():
            root_cause = "Test assertion failure: output did not match expected value"

        # Capture last 10 lines for snippet
        snippet_lines = full_text.splitlines()[-10:]
        traceback_snippet = "\n".join(snippet_lines)

        return DebuggingContext(
            exception_type=exception_type,
            error_message=error_message,
            failing_file=failing_file,
            line_number=line_number,
            function_name=function_name,
            likely_root_cause=root_cause,
            traceback_snippet=traceback_snippet
        )
