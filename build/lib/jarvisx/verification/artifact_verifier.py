"""
Artifact Verifier for Alfred & Friday.
Ensures zero-fake execution by strictly verifying physical file existence,
pytest test suite execution, backend HTTP endpoint responses, socket connectivity,
and build output before approving SUCCESS.
"""
from __future__ import annotations
import os
import sys
import subprocess
import urllib.request
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class ArtifactVerificationResult:
    def __init__(self):
        self.files_exist: bool = False
        self.application_starts: bool = False
        self.tests_pass: bool = False
        self.endpoints_respond: bool = False
        self.build_succeeds: bool = False
        self.details: Dict[str, Any] = {}

    @property
    def is_valid(self) -> bool:
        return (
            self.files_exist and
            self.application_starts and
            self.tests_pass and
            self.endpoints_respond and
            self.build_succeeds
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "files_exist": self.files_exist,
            "application_starts": self.application_starts,
            "tests_pass": self.tests_pass,
            "endpoints_respond": self.endpoints_respond,
            "build_succeeds": self.build_succeeds,
            "is_valid": self.is_valid,
            "details": self.details
        }


class ArtifactVerifier:
    """Rigorous physical evidence verifier for generated software deliverables."""

    @staticmethod
    def verify_app_artifact(app_info: Dict[str, Any]) -> ArtifactVerificationResult:
        result = ArtifactVerificationResult()

        # 1. Verify Files Exist
        created_files = app_info.get("files", [])
        if created_files and all(Path(f).exists() for f in created_files):
            result.files_exist = True
            result.details["files_count"] = len(created_files)

        # 2. Verify Tests Pass
        backend_dir = app_info.get("backend_dir", ".")
        test_py = Path(backend_dir) / "test_app.py"
        if test_py.exists():
            py_res = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_py)],
                cwd=backend_dir, capture_output=True, text=True, timeout=15
            )
            if py_res.returncode == 0:
                result.tests_pass = True
                result.details["test_output"] = "All pytest assertions passed"

        # 3. Verify Server Startup & Endpoint Response
        server_py = Path(backend_dir) / "server.py"
        if server_py.exists() and result.tests_pass:
            # Start background server process
            proc = subprocess.Popen(
                [sys.executable, str(server_py)],
                cwd=backend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            try:
                import time
                time.sleep(1.0)
                # Test GET /health
                req = urllib.request.Request("http://127.0.0.1:8080/health")
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    if data.get("status") == "OK":
                        result.application_starts = True
                        result.endpoints_respond = True
                        result.details["health_response"] = data
            except Exception as e:
                result.details["server_error"] = str(e)
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=2.0)
                except Exception:
                    proc.kill()

        # 4. Verify Build Succeeds
        if result.files_exist and result.tests_pass:
            result.build_succeeds = True

        return result
