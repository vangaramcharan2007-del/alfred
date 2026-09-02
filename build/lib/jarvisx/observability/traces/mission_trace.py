from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

class MissionTrace:
    """
    Manages structured mission trace records and persists them to logs/traces/<mission_id>.json.
    """
    def __init__(self, mission_id: str, user_request: str, trace_dir: Optional[str] = None):
        self.mission_id = mission_id
        self.user_request = user_request
        self.trace_dir = Path(trace_dir or "logs/traces")
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        self.start_time = time.time()
        self.reasoning_steps: List[str] = []
        self.selected_capabilities: List[str] = []
        self.selected_model: str = "qwen2.5-coder:7b"
        self.prompts_sent: List[str] = []
        self.tool_calls: List[Dict[str, Any]] = []
        self.files_created: List[str] = []
        self.files_modified: List[str] = []
        self.commands_executed: List[str] = []
        self.tests_run: List[Dict[str, Any]] = []
        self.failures: int = 0
        self.retries: int = 0
        self.final_result: str = "PENDING"

    def record_reasoning(self, step: str):
        self.reasoning_steps.append(step)

    def record_tool_call(self, tool_name: str, payload: Dict[str, Any], status: str = "SUCCESS"):
        self.tool_calls.append({
            "tool": tool_name,
            "payload": payload,
            "status": status,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

    def record_file_change(self, file_path: str, action: str = "created"):
        if action == "created" and file_path not in self.files_created:
            self.files_created.append(file_path)
        elif action == "modified" and file_path not in self.files_modified:
            self.files_modified.append(file_path)

    def record_command(self, cmd: str):
        self.commands_executed.append(cmd)

    def finalize(self, result: str = "SUCCESS") -> Dict[str, Any]:
        self.final_result = result
        duration = round(time.time() - self.start_time, 3)

        trace_data = {
            "mission_id": self.mission_id,
            "user_request": self.user_request,
            "duration": duration,
            "reasoning_steps": self.reasoning_steps,
            "selected_capabilities": self.selected_capabilities or ["coding.agent"],
            "selected_model": self.selected_model,
            "prompts_sent": self.prompts_sent,
            "tool_calls": self.tool_calls,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "commands_executed": self.commands_executed,
            "tests_run": self.tests_run,
            "failures": self.failures,
            "retries": self.retries,
            "final_result": self.final_result
        }

        trace_file = self.trace_dir / f"{self.mission_id}.json"
        trace_file.write_text(json.dumps(trace_data, indent=2), encoding="utf-8")
        return trace_data
