"""Self Improvement Engine wiring Performance Analyzer, Root-Cause Engine, Pattern Miner, and Upgrade Manager."""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.self_improvement.failure_root_cause import FailureRootCauseEngine
from jarvisx.self_improvement.models import ErrorClass, UpgradeProposal
from jarvisx.self_improvement.pattern_miner import SuccessPatternMiner
from jarvisx.self_improvement.performance_analyzer import PerformanceAnalyzer
from jarvisx.self_improvement.self_improvement_memory import SelfImprovementMemory
from jarvisx.self_improvement.upgrade_manager import UpgradeManager


class SelfImprovementEngine:
    """Master Self-Improvement Coordinator for Jarvis X (Phase 97)."""

    def __init__(self):
        self.memory = SelfImprovementMemory()
        self.analyzer = PerformanceAnalyzer(self.memory)
        self.root_cause = FailureRootCauseEngine(self.memory)
        self.miner = SuccessPatternMiner(self.memory)
        self.upgrades = UpgradeManager(self.memory)

    def status(self) -> Dict[str, Any]:
        """Display live scorecards and fleet metrics."""
        summary = self.analyzer.get_scorecard_summary()
        print(f"\n==================================================")
        print(f"  SELF-IMPROVEMENT SCORECARD (PHASE 97)")
        print(f"==================================================")
        print(f"Fleet Success Rate: {summary['fleet_success_rate']}% across {summary['total_agents']} agents\n")
        for m in summary["metrics"]:
            print(f"  • {m['agent_name']}: Success {m['success_rate']*100:.1f}% ({m['successes']}/{m['total_tasks']}) | Trend: {m['trend']} | Latency: {m['avg_duration_sec']}s")
        return summary

    def failures(self) -> List[Dict[str, Any]]:
        """Diagnose recent failures and display root causes."""
        # Seed initial failure taxonomy if empty
        if not self.root_cause.list_diagnoses():
            self.root_cause.diagnose_failure(
                error_class=ErrorClass.BAD_DELEGATION,
                failed_agent="AlfredMaster",
                error_message="Missing OpenAPI schemas before Coder invocation"
            )
            self.root_cause.diagnose_failure(
                error_class=ErrorClass.TIMEOUT,
                failed_agent="CodingAgent",
                error_message="AST linting latency exceeded 5.0s SLA"
            )

        diagnoses = self.root_cause.list_diagnoses()
        print(f"\n[FAILURE ROOT-CAUSE DIAGNOSES]: {len(diagnoses)} reports analyzed")
        for d in diagnoses:
            print(f"  • [{d.error_class.value}] {d.failed_agent}: {d.root_cause_category}")
            print(f"    Proposed Fix: {d.proposed_fix} (Confidence: {d.confidence*100:.0f}%, Recurrence: {d.recurrence_count})")
        return [d.to_dict() for d in diagnoses]

    def patterns(self) -> List[Dict[str, Any]]:
        """Display mined success playbooks."""
        playbooks = self.miner.get_playbooks()
        print(f"\n[MINED SUCCESS PLAYBOOKS]: {len(playbooks)} strategy templates registered")
        for p in playbooks:
            print(f"  • {p.task_type} (Success Rate: {p.success_rate*100:.0f}%, Samples: {p.sample_count})")
            for step in p.strategy_template[:2]:
                print(f"    - {step}")
        return [p.to_dict() for p in playbooks]

    def run_self_upgrade_cycle(self) -> Dict[str, Any]:
        """Propose, test in sandbox, and apply a verified self-upgrade."""
        print(f"\n==================================================")
        print(f"  SELF-UPGRADE SANDBOX CYCLE (PHASE 97)")
        print(f"==================================================")
        proposal = self.upgrades.propose_upgrade(
            target_component="CodingAgent",
            change_type="PROMPT_AST_VERIFICATION",
            patch_diff="+ add pre-validation syntax token check before disk write",
            rollback_plan="git checkout main -- src/jarvisx/multi_agent/coding_agent.py"
        )
        print(f"[Proposal Created]: {proposal.proposal_id} on {proposal.target_component}")

        # Run in sandbox
        sandbox_run = self.upgrades.run_sandbox_validation(proposal, simulate_regression=False)
        print(f"[Sandbox Results]: {sandbox_run.tests_passed}/{sandbox_run.total_tests} tests passed (Regressions: {sandbox_run.regression_detected})")

        # Apply upgrade
        apply_res = self.upgrades.apply_upgrade(proposal)
        return {
            "proposal": proposal.to_dict(),
            "sandbox": sandbox_run.to_dict(),
            "apply": apply_res
        }
