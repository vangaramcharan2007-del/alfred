"""Formatting and Presentation for Intelligence Evaluation Reports."""

from __future__ import annotations
from typing import List
from jarvisx.evaluation.models import IntelligenceScorecard, ResponseEvaluation


class EvaluationReportFormatter:
    """Formats evaluation traces and scorecards for human inspection and CLI output."""

    @staticmethod
    def format_evaluation(eval_record: ResponseEvaluation) -> str:
        """Format a single evaluation record with full evidence trace."""
        lines = [
            f"[RESPONSE EVALUATION]: {eval_record.response_id}",
            f"  Query:               {eval_record.query}",
            f"  Grounding Score:     {int(eval_record.grounding_score * 100)}%",
            f"  Completeness Score:  {int(eval_record.completeness_score * 100)}%",
            f"  Clarity Score:       {int(eval_record.clarity_score * 100)}%",
            f"  Retrieval Confidence:{int(eval_record.retrieval_confidence * 100)}%",
        ]

        if eval_record.user_correction_penalty > 0:
            lines.append(f"  Correction Penalty: -{int(eval_record.user_correction_penalty * 100)}%")

        lines.append(f"  Final Quality Score: {int(eval_record.final_quality_score * 100)}%")
        lines.append(f"  Actor Role:          {eval_record.actor_role}")

        if eval_record.is_user_accepted is not None:
            status_str = "ACCEPTED" if eval_record.is_user_accepted else "CORRECTED"
            lines.append(f"  User Feedback:       {status_str} - {eval_record.user_feedback or 'None'}")

        if eval_record.evidence_trace and eval_record.evidence_trace.sources:
            lines.append("\n  [EVIDENCE SOURCES]:")
            for s in eval_record.evidence_trace.sources[:4]:
                lines.append(f"    * {s.source_file} ({s.section_heading}) [Confidence: {s.confidence}, Hash: {s.provenance_hash}]")

        if eval_record.evidence_trace and eval_record.evidence_trace.claims:
            lines.append("\n  [CLAIM GROUNDING BREAKDOWN]:")
            for c in eval_record.evidence_trace.claims[:4]:
                lines.append(f"    * [{c.support_state.value}] {c.claim_text[:80]}...")

        return "\n".join(lines)

    @staticmethod
    def format_scorecard(scorecard: IntelligenceScorecard) -> str:
        """Format high-level intelligence scorecard."""
        lines = [
            "=========================================",
            "      JARVIS X INTELLIGENCE SCORECARD    ",
            "=========================================",
            f"  Total Evaluations:     {scorecard.total_evaluations}",
            f"  Average Grounding:     {int(scorecard.average_grounding_score * 100)}%",
            f"  Average Quality Score: {int(scorecard.average_quality_score * 100)}%",
            f"  User Satisfaction:     {int(scorecard.user_satisfaction_rate * 100)}%",
            f"  Recorded Failures:     {scorecard.total_failures_recorded}",
            "",
            "  [TOP KNOWLEDGE SOURCES BY UTILITY]:",
        ]

        if scorecard.top_utility_sources:
            for s in scorecard.top_utility_sources:
                lines.append(f"    * {s['source_file']} (Retrieved: {s['times_retrieved']}x, Utility: {int(s['utility_score'] * 100)}%)")
        else:
            lines.append("    * (No historical source utility data yet)")

        return "\n".join(lines)

    @staticmethod
    def format_history(evaluations: List[ResponseEvaluation]) -> str:
        """Format historical evaluation table."""
        lines = [
            "=========================================",
            "    JARVIS X INTELLIGENCE HISTORY        ",
            "=========================================",
        ]
        if not evaluations:
            lines.append("  (No evaluation history found)")
            return "\n".join(lines)

        for e in evaluations[:15]:
            status_char = "✓" if e.is_user_accepted is True else ("✗" if e.is_user_accepted is False else "•")
            lines.append(
                f"  [{status_char}] {e.response_id} | Q: '{e.query[:35]}...' | Grounding: {int(e.grounding_score * 100)}% | Quality: {int(e.final_quality_score * 100)}%"
            )

        return "\n".join(lines)
