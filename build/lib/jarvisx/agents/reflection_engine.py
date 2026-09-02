"""Reflection Engine for Phase 91 Autonomous Mission Brain."""

from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, Any, List
from jarvisx.agents.action_models import ActionProposal, ExecutionResult, ReflectionResult


class ReflectionEngine:
    """Evaluates step efficacy, checks artifact creation, and determines replanning needs."""

    def evaluate(
        self,
        goal: str,
        proposal: ActionProposal,
        result: ExecutionResult,
        total_milestones: int,
        completed_count: int,
    ) -> ReflectionResult:
        """Reflect on action execution outcome and compute goal progress."""
        what_succeeded = []
        what_failed = []

        if result.status == "SUCCESS":
            what_succeeded.append(f"{proposal.capability_name}: {proposal.expected_outcome}")
            # Verify artifacts on disk
            for art in result.artifacts_created:
                if Path(art).exists():
                    what_succeeded.append(f"Artifact verified on disk: {art}")
        else:
            what_failed.append(f"{proposal.capability_name} failed: {result.error or 'Unknown error'}")

        # Compute goal progress (0.0 to 1.0)
        progress = round(completed_count / max(total_milestones, 1), 2)
        is_achieved = (completed_count >= total_milestones) and (len(what_failed) == 0)

        notes = f"Progress: {int(progress * 100)}%. Step {proposal.step_index} execution outcome: {result.status}."

        return ReflectionResult(
            goal_progress=progress,
            is_goal_achieved=is_achieved,
            requires_replanning=(result.status == "FAILED"),
            what_succeeded=what_succeeded,
            what_failed=what_failed,
            recommended_next_action="proceed" if result.status == "SUCCESS" else "replan",
            reflection_notes=notes
        )
