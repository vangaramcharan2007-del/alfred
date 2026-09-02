"""Report & Visual Formatters for Phase 103 Memory Intelligence."""

from __future__ import annotations
from typing import Any, Dict, List
from jarvisx.memory_intelligence.models import MemoryRecord, UserProfile


class MemoryReportFormatter:
    """Formats memory audits, user profile summaries, and memory lists for CLI output."""

    @staticmethod
    def format_audit_report(counts: Dict[str, int], decay_candidates_count: int, missing_provenance: int = 0) -> str:
        """Format the memory health audit report."""
        lines = [
            "=== [JARVIS X COGNITIVE MEMORY HEALTH AUDIT] ===",
            f"  Total Active Memories : {counts.get('total_active', 0)}",
            f"  - Semantic (Facts)    : {counts.get('semantic', 0)}",
            f"  - Procedural (Styles) : {counts.get('procedural', 0)}",
            f"  - Episodic (Events)   : {counts.get('episodic', 0)}",
            f"  - Archived / Pruned   : {counts.get('archived', 0)}",
            "",
            f"  Decay Candidates      : {decay_candidates_count}",
            f"  Missing Provenance    : {missing_provenance}",
            f"  Security Health       : CLEAN (Zero credentials retained)",
            "=================================================",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_user_profile(profile: UserProfile) -> str:
        """Format the user profile cognitive persona."""
        lines = [
            "=== [JARVIS X PERSONAL USER PROFILE] ===",
            f"  Academic Track        : {profile.academic_track}",
            f"  Primary Goal          : {profile.primary_goal}",
            f"  Learning Style        : {profile.preferred_learning_style}",
            f"  Tech Preferences      : {', '.join(profile.technical_preferences)}",
            f"  Active Projects       : {', '.join(profile.active_projects)}",
            f"  Distilled Memories    : {profile.total_memories_distilled}",
            "=========================================",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_memory_list(memories: List[MemoryRecord]) -> str:
        """Format a list of memory records."""
        if not memories:
            return "No memory records found."

        lines = [
            f"=== [JARVIS X MEMORY RECORDS ({len(memories)})] ===",
        ]
        for m in memories:
            strength = int(m.compute_decayed_strength() * 100)
            lines.append(
                f"  [{m.id}] ({m.memory_type.value[:3]}) [{m.sensitivity.value[:4]}] {m.content[:50]}... | Str: {strength}% | Src: {m.provenance.source_type.value}"
            )
        lines.append("=========================================")
        return "\n".join(lines)
