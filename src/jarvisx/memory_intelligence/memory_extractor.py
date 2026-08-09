"""Selective Memory Extractor for Phase 103."""

from __future__ import annotations
import re
from typing import List, Optional

from jarvisx.memory_intelligence.importance_ranker import MemoryImportanceRanker
from jarvisx.memory_intelligence.memory_security import MemorySecurityGuard
from jarvisx.memory_intelligence.models import (
    MemoryExtractionCandidate,
    MemorySensitivity,
    MemorySource,
    MemoryType,
)


class MemoryExtractor:
    """Extracts candidate cognitive memories from conversation turns while aggressively rejecting trivial noise."""

    # Trivial conversation noise that must NOT be stored
    TRIVIAL_NOISE_PATTERNS = [
        re.compile(r"(?i)^(?:hi|hello|hey|good\s+(?:morning|evening|afternoon)|howdy|sup)\b"),
        re.compile(r"(?i)^(?:what\s+is\s+the\s+weather|is\s+it\s+raining|what\s+time\s+is\s+it)"),
        re.compile(r"(?i)^(?:thank\s+you|thanks|thx|ok|okay|cool|got\s+it|bye|see\s+ya|[\s\.,!?-]+)+$"),
        re.compile(r"(?i)^what\s+is\s+\d+\s*[\+\-\*\/]\s*\d+"),
    ]

    # Explicit memory triggers
    EXPLICIT_TRIGGERS = [
        re.compile(r"(?i)remember\s+that\s+(.*)"),
        re.compile(r"(?i)my\s+preference\s+is\s+(.*)"),
        re.compile(r"(?i)i\s+prefer\s+(.*)"),
        re.compile(r"(?i)i\s+learn\s+better\s+by\s+(.*)"),
        re.compile(r"(?i)i\s+am\s+(?:targeting|preparing\s+for|studying)\s+(.*)"),
    ]

    def __init__(self):
        self.ranker = MemoryImportanceRanker()

    def extract_candidates(
        self,
        text: str,
        source: MemorySource = MemorySource.CONVERSATION,
        source_ref: str = "",
    ) -> List[MemoryExtractionCandidate]:
        """Analyze text and propose structured memory candidates."""
        cleaned_text = text.strip()
        if not cleaned_text:
            return []

        # 1. Security Check: Reject secrets & credentials
        is_safe, reject_reason = MemorySecurityGuard.validate_memory_for_storage(cleaned_text)
        if not is_safe:
            return [
                MemoryExtractionCandidate(
                    content=cleaned_text,
                    memory_type=MemoryType.SEMANTIC,
                    importance=0.0,
                    confidence=0.0,
                    sensitivity=MemorySensitivity.SECRET,
                    source=source,
                    evidence=cleaned_text,
                    should_store=False,
                    rejection_reason=reject_reason,
                )
            ]

        # 2. Noise Check: Reject trivial conversation greetings/weather
        for pattern in self.TRIVIAL_NOISE_PATTERNS:
            if pattern.search(cleaned_text):
                return [
                    MemoryExtractionCandidate(
                        content=cleaned_text,
                        memory_type=MemoryType.SEMANTIC,
                        importance=0.02,
                        confidence=0.1,
                        sensitivity=MemorySensitivity.PUBLIC,
                        source=source,
                        evidence=cleaned_text,
                        should_store=False,
                        rejection_reason="REJECTED: Trivial conversational noise (greeting/weather/acknowledgement).",
                    )
                ]

        candidates: List[MemoryExtractionCandidate] = []
        text_lower = cleaned_text.lower()

        # Check explicit user triggers
        matched_explicit = False
        for trigger in self.EXPLICIT_TRIGGERS:
            m = trigger.search(cleaned_text)
            if m:
                matched_explicit = True
                extracted_fact = m.group(1) if m.groups() else cleaned_text
                
                # Classify type
                if any(w in text_lower for w in ("learn", "study", "code", "work", "habit")):
                    mem_type = MemoryType.PROCEDURAL
                else:
                    mem_type = MemoryType.SEMANTIC

                importance = self.ranker.compute_importance(
                    content=cleaned_text,
                    memory_type=mem_type,
                    source=MemorySource.USER_EXPLICIT,
                    user_explicit=True,
                )

                candidates.append(
                    MemoryExtractionCandidate(
                        content=cleaned_text,
                        memory_type=mem_type,
                        importance=importance,
                        confidence=0.98,
                        sensitivity=MemorySensitivity.PERSONAL,
                        source=MemorySource.USER_EXPLICIT,
                        evidence=cleaned_text,
                        tags=["user_preference", "explicit"],
                        should_store=True,
                    )
                )
                break

        if matched_explicit:
            return candidates

        # 3. Check for Episodic achievements / milestones
        if any(w in text_lower for w in ("completed", "released", "fixed", "passed", "scored", "failed")):
            importance = self.ranker.compute_importance(
                content=cleaned_text,
                memory_type=MemoryType.EPISODIC,
                source=source,
            )
            candidates.append(
                MemoryExtractionCandidate(
                    content=cleaned_text,
                    memory_type=MemoryType.EPISODIC,
                    importance=importance,
                    confidence=0.90,
                    sensitivity=MemorySensitivity.PERSONAL,
                    source=source,
                    evidence=cleaned_text,
                    tags=["milestone", "event"],
                    should_store=importance >= 0.40,
                )
            )
            return candidates

        # 4. Check for Semantic facts (BTech, CGPA, Stack, Tools)
        if any(w in text_lower for w in ("btech", "cse", "cgpa", "exam", "syllabus", "python", "dsa", "offline")):
            importance = self.ranker.compute_importance(
                content=cleaned_text,
                memory_type=MemoryType.SEMANTIC,
                source=source,
            )
            candidates.append(
                MemoryExtractionCandidate(
                    content=cleaned_text,
                    memory_type=MemoryType.SEMANTIC,
                    importance=importance,
                    confidence=0.88,
                    sensitivity=MemorySensitivity.PERSONAL,
                    source=source,
                    evidence=cleaned_text,
                    tags=["fact", "profile"],
                    should_store=importance >= 0.35,
                )
            )
            return candidates

        # 5. Default generic query -> reject storing unless high importance
        importance = self.ranker.compute_importance(
            content=cleaned_text,
            memory_type=MemoryType.SEMANTIC,
            source=source,
        )
        should_store = importance >= 0.65

        candidates.append(
            MemoryExtractionCandidate(
                content=cleaned_text,
                memory_type=MemoryType.SEMANTIC,
                importance=importance,
                confidence=0.60,
                sensitivity=MemorySensitivity.PUBLIC,
                source=source,
                evidence=cleaned_text,
                should_store=should_store,
                rejection_reason=None if should_store else "REJECTED: Low relevance/importance score.",
            )
        )

        return candidates
