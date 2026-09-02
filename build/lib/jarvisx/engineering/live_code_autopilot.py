"""
Live Code Auto-Pilot & Ambient Self-Healing Watcher for Jarvis X.
Watches project directories continuously:
1. Detects file modifications on Save (Ctrl+S).
2. Silently validates syntax & AST in the background.
3. If an error is detected, autonomously invokes Gemini 3.6 Flash to generate a patch.
4. Applies the fix, verifies clean compilation, and notifies Alfred HUD.
"""

from __future__ import annotations

import ast
import json
import logging
import os
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("jarvisx.engineering.autopilot")


@dataclass
class CodeHealEvent:
    """Payload emitted when a file is healed."""
    file_path: str
    error_type: str
    error_message: str
    line_number: int
    patch_applied: str
    success: bool
    timestamp: float = 0.0


class LiveCodeAutopilot:
    """Continuous background watcher that auto-heals code on save."""

    def __init__(self, watch_dir: Optional[str] = None, check_interval_sec: float = 1.0):
        self.watch_dir = Path(watch_dir or ".").resolve()
        self.check_interval = check_interval_sec
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._file_mtimes: Dict[str, float] = {}
        self._listeners: List[Callable[[CodeHealEvent], None]] = []
        self.healed_events: List[CodeHealEvent] = []

    def add_listener(self, callback: Callable[[CodeHealEvent], None]):
        self._listeners.append(callback)

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._init_file_mtimes()
        self._thread = threading.Thread(
            target=self._watch_loop,
            daemon=True,
            name="LiveCodeAutopilotThread"
        )
        self._thread.start()
        logger.info(f"Live Code Auto-Pilot watching: {self.watch_dir}")

    def stop(self):
        self.is_running = False

    def _init_file_mtimes(self):
        """Records initial modification timestamps for all python files."""
        for root, dirs, files in os.walk(self.watch_dir):
            dirs[:] = [d for d in dirs if d not in ('.git', '.venv', '__pycache__', 'node_modules', '.pytest_cache')]
            for f in files:
                if f.endswith(".py"):
                    full_path = os.path.join(root, f)
                    try:
                        self._file_mtimes[full_path] = os.path.getmtime(full_path)
                    except Exception:
                        pass

    def _watch_loop(self):
        while self.is_running:
            try:
                self._check_file_changes()
            except Exception as e:
                logger.error(f"Autopilot watch error: {e}")
            time.sleep(self.check_interval)

    def _check_file_changes(self):
        for root, dirs, files in os.walk(self.watch_dir):
            dirs[:] = [d for d in dirs if d not in ('.git', '.venv', '__pycache__', 'node_modules', '.pytest_cache')]
            for f in files:
                if f.endswith(".py"):
                    full_path = os.path.join(root, f)
                    try:
                        mtime = os.path.getmtime(full_path)
                        prev_mtime = self._file_mtimes.get(full_path)

                        if prev_mtime is not None and mtime > prev_mtime:
                            self._file_mtimes[full_path] = mtime
                            # File changed on disk! Validate syntax
                            self._validate_and_heal_file(full_path)
                        elif prev_mtime is None:
                            self._file_mtimes[full_path] = mtime
                    except Exception:
                        pass


    def _validate_and_heal_file(self, file_path: str):
        """Validates Python AST and triggers self-healing if broken."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code_content = f.read()
        except Exception:
            return

        try:
            ast.parse(code_content)
            # Syntax is clean!
            return
        except SyntaxError as syn_err:
            logger.warning(f"Syntax error detected in {file_path}:{syn_err.lineno}: {syn_err.msg}")
            self.heal_file(file_path, code_content, str(syn_err), syn_err.lineno or 1)

    def heal_file(self, file_path: str, code_content: str, error_msg: str, line_no: int) -> Optional[CodeHealEvent]:
        """Autonomously fixes a broken file using Gemini 3.6 Flash."""
        from jarvisx.llm.llm_router import LLMRouter
        router = LLMRouter()

        prompt = f"""You are the Autonomous Code Healer for Jarvis X / Alfred OS.
Fix the syntax error in the following file.

File: {file_path}
Error: {error_msg} (Line {line_no})

Current Code:
```python
{code_content}
```

Respond ONLY with the complete corrected valid Python code. Do not include conversational text or markdown explanation."""

        import asyncio
        loop = None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

        if loop and loop.is_running():
            future = asyncio.run_coroutine_threadsafe(router.route_request(prompt), loop)
            res = future.result(timeout=15)
        else:
            res = asyncio.run(router.route_request(prompt))

        raw_output = res.get("result", {}).get("response", "")
        if not raw_output:
            return None

        # Clean markdown wrappers
        clean_code = raw_output.strip()
        if clean_code.startswith("```python"):
            clean_code = clean_code[9:]
        elif clean_code.startswith("```"):
            clean_code = clean_code[3:]
        if clean_code.endswith("```"):
            clean_code = clean_code[:-3]
        clean_code = clean_code.strip()

        # Validate that the healed code is valid AST
        try:
            ast.parse(clean_code)
            
            # Backup original
            bak_path = file_path + ".alfred_bak"
            with open(bak_path, "w", encoding="utf-8") as bf:
                bf.write(code_content)

            # Write fixed code
            with open(file_path, "w", encoding="utf-8") as wf:
                wf.write(clean_code)

            self._file_mtimes[file_path] = os.path.getmtime(file_path)

            event = CodeHealEvent(
                file_path=file_path,
                error_type="SyntaxError",
                error_message=error_msg,
                line_number=line_no,
                patch_applied="Auto-healed via Gemini 3.6 Flash",
                success=True,
                timestamp=time.time()
            )
            self.healed_events.append(event)
            for cb in self._listeners:
                try:
                    cb(event)
                except Exception:
                    pass

            logger.info(f"Successfully auto-healed: {file_path}")
            return event

        except SyntaxError as re_err:
            logger.error(f"Healed code still had syntax error: {re_err}")
            return None


def get_code_autopilot() -> LiveCodeAutopilot:
    return LiveCodeAutopilot()
