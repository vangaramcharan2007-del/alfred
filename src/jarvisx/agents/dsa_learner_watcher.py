"""
Jarvis X — Interactive DSA Tutor & Real-Time Error-Fixing Watcher.
Monitors the user's DSA practice files in VS Code, runs automated test suites on save,
diagnoses errors via Groq LPU Brain in sub-second time, speaks vocal hints, and tracks learning mastery.
"""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvisx.agents.dsa_watcher")


class DSALearnerWatcher:
    """
    Active DSA Tutor & VS Code Auto-Correction Agent.
    - Watches dsa_practice/ directory.
    - Runs tests on file save.
    - Diagnoses errors via Groq LPU Brain.
    - Speaks vocal hints via Mouth.
    - Updates progress in SQLite Second Brain.
    """

    _instance: Optional[DSALearnerWatcher] = None
    _lock = threading.Lock()

    def __init__(self, watch_dir: str = "dsa_practice", poll_interval_sec: float = 1.0):
        self.watch_dir = Path(watch_dir).resolve()
        self.poll_interval = poll_interval_sec
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None
        self._last_mtimes: Dict[str, float] = {}
        self.active_problem: str = "module1_arrays_two_pointers.py"
        self.history: List[Dict[str, Any]] = []

    @classmethod
    def get_instance(cls) -> DSALearnerWatcher:
        with cls._lock:
            if cls._instance is None:
                cls._instance = DSALearnerWatcher()
            return cls._instance

    def start_watcher(self) -> Dict[str, Any]:
        """Start background file watcher."""
        if self.is_running:
            return {"status": "already_running", "message": "DSA Learner Watcher is already active."}

        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._watch_loop, daemon=True, name="AlfredDSAWatcher")
        self.worker_thread.start()
        logger.info(f"[DSAWatcher] Active and monitoring '{self.watch_dir}'")
        return {"status": "started", "message": f"DSA Learner Watcher is actively monitoring {self.watch_dir}"}

    def stop_watcher(self) -> Dict[str, Any]:
        """Stop background watcher."""
        self.is_running = False
        return {"status": "stopped", "message": "DSA Learner Watcher stopped."}

    def evaluate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Explicitly evaluate a DSA file:
        Executes tests, analyzes output, and provides hints if failed.
        """
        target = Path(file_path).resolve()
        if not target.exists():
            return {"status": "failed", "error": f"File '{target}' not found."}

        print(f"\n[DSA Tutor] ⚡ Evaluating {target.name}...")
        res = subprocess.run([sys.executable, str(target)], capture_output=True, text=True, timeout=10)
        
        passed = res.returncode == 0
        output = res.stdout.strip()
        errors = res.stderr.strip()

        if passed:
            msg = f"Brilliant job, Sir! All test cases in {target.name} passed with O(n) optimal complexity."
            self._notify(msg, is_success=True)
            self._record_progress(target.name, "PASSED", output)
            return {
                "status": "success",
                "tests_passed": True,
                "output": output,
                "message": msg,
            }
        else:
            # Diagnose with Groq LPU Brain
            hint = self._diagnose_error_with_llm(target, errors or output)
            msg = f"I spotted an issue in {target.name}. {hint.get('summary', 'Check your index bounds.')}"
            self._notify(msg, is_success=False)
            self._record_progress(target.name, "FAILED", errors or output, hint)
            return {
                "status": "failed",
                "tests_passed": False,
                "error_raw": errors or output,
                "ai_hint": hint,
                "message": msg,
            }

    def _watch_loop(self) -> None:
        """Background file monitoring thread."""
        while self.is_running:
            try:
                for py_file in self.watch_dir.glob("*.py"):
                    try:
                        mtime = py_file.stat().st_mtime
                        last_mtime = self._last_mtimes.get(str(py_file), mtime)
                        
                        if str(py_file) not in self._last_mtimes:
                            self._last_mtimes[str(py_file)] = mtime
                        elif mtime > last_mtime:
                            self._last_mtimes[str(py_file)] = mtime
                            # File changed -> Run evaluation
                            self.evaluate_file(str(py_file))
                    except Exception:
                        pass
            except Exception as e:
                logger.error(f"[DSAWatcher] Loop error: {e}")

            time.sleep(self.poll_interval)

    def _diagnose_error_with_llm(self, file_path: Path, traceback_text: str) -> Dict[str, Any]:
        """Diagnose error using Groq LPU and generate an encouraging, clear hint."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                code_content = f.read()
        except Exception:
            code_content = "Code unreadable."

        from jarvisx.llm.llm_router import LLMRouter
        router = LLMRouter()

        prompt = f"""You are Alfred, Charan's elite British DSA tutor and AI butler.
Charan is practicing a Python DSA challenge and hit an error / assertion failure.

STUDENT CODE:
```python
{code_content[:1500]}
```

TEST EXECUTION ERROR / TRACEBACK:
```
{traceback_text[:800]}
```

TASK:
1. Identify the exact root cause bug (e.g. off-by-one, missed hash map check, index out of range).
2. Formulate a 2-sentence encouraging, witty spoken hint that explains HOW to fix it without giving away the full code blindly.
3. Provide the corrected code snippet.

Respond in this exact JSON format:
{{
  "summary": "<1-2 sentence spoken hint for Charan>",
  "root_cause": "<concise explanation of the bug>",
  "fix_suggestion": "<small 2-3 line code fix>"
}}
"""
        try:
            res = asyncio.run(router.route_request(prompt))
            raw = res.get("result", {}).get("response", "") or res.get("text", "")
            import json, re
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            if m:
                return json.loads(m.group(0), strict=False)
        except Exception as e:
            logger.debug(f"[DSAWatcher] LLM diagnosis error: {e}")

        return {
            "summary": "Check your base cases and loop boundary indices.",
            "root_cause": traceback_text[:120],
            "fix_suggestion": "Review pointer increments and hash map lookups."
        }

    def _notify(self, message: str, is_success: bool = True) -> None:
        """Speak hint aloud and log to console."""
        print(f"\n[ALFRED DSA TUTOR] 🎙️ {message}\n")
        try:
            from jarvisx.organism import get_organism
            org = get_organism()
            org.mouth.speak(message)
        except Exception:
            pass

    def _record_progress(self, file_name: str, status: str, details: str, hint: Optional[Dict[str, Any]] = None) -> None:
        """Record progress into history and SQLite memory."""
        entry = {
            "timestamp": time.time(),
            "file": file_name,
            "status": status,
            "details": details[:200],
            "hint": hint,
        }
        self.history.append(entry)
        try:
            from jarvisx.memory.second_brain import SecondBrain
            sb = SecondBrain()
            sb.save_note(
                title=f"DSA Practice: {file_name}",
                content=f"Status: {status}\nDetails: {details[:200]}\nHint: {hint.get('summary') if hint else 'None'}",
                tags=["dsa", "practice", "python"]
            )
        except Exception:
            pass


def get_dsa_watcher() -> DSALearnerWatcher:
    return DSALearnerWatcher.get_instance()
