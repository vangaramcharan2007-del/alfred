"""
Aegis Harness — Agentic Evaluation & Sandbox.
Provides a safe environment to execute agent-generated code, run benchmarks,
and grade the agent's performance without risking the host OS.
"""
import logging
import time
import random
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AegisHarness:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def evaluate_agent_code(self, agent_id: str, code_payload: str, test_suite: str) -> Dict[str, Any]:
        """Runs the agent's code in a mocked sandbox and scores it."""
        logger.info(f"[AegisHarness] Received code payload from {agent_id}. Initializing Sandbox...")
        
        # In production: Use Docker SDK or gVisor to run the code securely
        time.sleep(1) # Simulating sandbox boot
        
        logger.info(f"[AegisHarness] Executing payload against test suite: {test_suite}...")
        
        # Simulate test execution
        success = random.random() > 0.2  # 80% pass rate simulation
        score = random.randint(85, 100) if success else random.randint(40, 70)
        
        result = "PASSED" if success else "FAILED"
        logger.info(f"[AegisHarness] Evaluation {result}. Reward Score: {score}/100")
        
        return {
            "status": "success",
            "agent_id": agent_id,
            "passed": success,
            "reward_score": score,
            "sandbox_logs": f"Executed {len(code_payload)} bytes. Tests: {result}."
        }
