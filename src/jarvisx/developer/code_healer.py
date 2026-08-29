"""
Autonomous Code Healer & Self-Repair Engine for Jarvis X.
Diagnoses bugs, fixes syntax & logical errors, and verifies patches inside a sandbox.
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from jarvisx.developer.sandbox_runner import SandboxTestRunner, TestExecutionResult
from jarvisx.mesh.mesh_router import MeshRouter, get_mesh_router
from jarvisx.security.audit_ledger import CryptographicAuditLedger

logger = logging.getLogger("jarvisx.code_healer")


@dataclass
class CodeHealReport:
    heal_id: str
    original_code: str
    error_message: str
    healed_code: str
    root_cause_explanation: str
    verification_success: bool
    iterations: int
    duration_ms: float
    audit_hash: str


class AutonomousCodeHealer:
    """Master engine for autonomous code diagnosis, repair, and sandbox validation."""

    _instance: Optional[AutonomousCodeHealer] = None

    def __init__(
        self,
        sandbox_runner: Optional[SandboxTestRunner] = None,
        mesh_router: Optional[MeshRouter] = None,
        audit_ledger: Optional[CryptographicAuditLedger] = None,
    ):
        self.sandbox = sandbox_runner or SandboxTestRunner()
        self.router = mesh_router or get_mesh_router()
        self.audit = audit_ledger or CryptographicAuditLedger(Path("var/db/audit_ledger.db"))

    @classmethod
    def get_instance(cls) -> AutonomousCodeHealer:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def heal_code(
        self,
        broken_code: str,
        error_message: str,
        test_script: Optional[str] = None,
        max_iterations: int = 3,
    ) -> CodeHealReport:
        """
        Executes autonomous diagnose -> patch -> sandbox test -> verify loop.
        """
        start_t = time.time()
        heal_id = f"heal_{int(start_t * 1000)}"
        current_code = broken_code
        current_error = error_message
        explanation = "Diagnosed and resolved logical syntax error."
        success = False
        iteration = 0

        for it in range(1, max_iterations + 1):
            iteration = it
            prompt = (
                f"You are Friday Dev Core, an autonomous software debugging agent.\n"
                f"Broken Code:\n```python\n{current_code}\n```\n\n"
                f"Error / Failure Message:\n```\n{current_error}\n```\n\n"
                f"Task:\n"
                f"1. Explain the root cause in 1 sentence.\n"
                f"2. Provide the 100% correct, working, fixed Python code.\n\n"
                f"Return JSON format:\n"
                f'{{"root_cause": "...", "fixed_code": "..."}}'
            )

            res = self.router.dispatch_intent(prompt, preferred_model="qwen2.5-coder:1.5b")
            raw = res.get("response", "")

            # Extract fixed code and root cause
            fixed_code = None
            try:
                m_json = re.search(r"(\{.*?\})", raw, re.DOTALL)
                if m_json:
                    data = json.loads(m_json.group(1))
                    fixed_code = data.get("fixed_code")
                    explanation = data.get("root_cause", explanation)
            except Exception:
                pass

            if not fixed_code:
                # Fallback extraction from markdown python block
                m_code = re.search(r"```(?:python)?\s*(.*?)\s*```", raw, re.DOTALL)
                if m_code:
                    fixed_code = m_code.group(1).strip()
                else:
                    fixed_code = raw.strip()

            current_code = fixed_code

            # Test healed code in sandbox
            test_target = f"{current_code}\n\n{test_script}" if test_script else current_code
            test_res = self.sandbox.run_code_snippet(test_target)

            if test_res.success:
                success = True
                break
            else:
                current_error = test_res.stderr or test_res.error_summary or "Execution failed"

        dur = round((time.time() - start_t) * 1000, 2)

        # Log repair to Cryptographic Audit Ledger
        audit_entry = self.audit.record_action(
            agent_id="friday_code_healer",
            action="CODE_SELF_HEAL_COMPLETED",
            input_payload={"heal_id": heal_id, "error": error_message[:150]},
            output_payload={"success": success, "iterations": iteration, "root_cause": explanation},
            status="SUCCESS" if success else "FAILED",
            metadata={"duration_ms": dur},
        )

        return CodeHealReport(
            heal_id=heal_id,
            original_code=broken_code,
            error_message=error_message,
            healed_code=current_code,
            root_cause_explanation=explanation,
            verification_success=success,
            iterations=iteration,
            duration_ms=dur,
            audit_hash=audit_entry.current_hash,
        )
