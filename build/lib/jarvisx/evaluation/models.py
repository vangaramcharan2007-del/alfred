"""Data models and enums for Phase 102 Evidence-Based Intelligence Evaluation Layer."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Any, Dict, List, Optional


class EvidenceSupportState(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNKNOWN_FROM_VAULT = "UNKNOWN_FROM_VAULT"
    UNSUPPORTED = "UNSUPPORTED"


class FailureCategory(str, Enum):
    FACTUAL_ERROR = "factual_error"
    RETRIEVAL_MISS = "retrieval_miss"
    INCOMPLETE_CONTEXT = "incomplete_context"
    REASONING_ERROR = "reasoning_error"
    INSTRUCTION_DEVIATION = "instruction_deviation"
    OTHER = "other"


@dataclass
class EvidenceSource:
    """Represents a specific chunk/document providing grounding evidence."""
    source_file: str
    section_heading: str
    confidence: float
    chunk_id: str
    provenance_hash: str
    matched_claim_snippet: str = ""


@dataclass
class ClaimEvidence:
    """Represents a single claim extracted from a response and its evidence support state."""
    claim_text: str
    support_state: EvidenceSupportState
    confidence: float
    supporting_sources: List[EvidenceSource] = field(default_factory=list)


@dataclass
class EvidenceTrace:
    """Complete cryptographic evidence trace linking a response to its knowledge grounding."""
    response_id: str
    query: str
    claims: List[ClaimEvidence] = field(default_factory=list)
    sources: List[EvidenceSource] = field(default_factory=list)
    grounding_ratio: float = 0.0
    supported_claims_count: int = 0
    unknown_claims_count: int = 0
    unsupported_claims_count: int = 0


@dataclass
class RetrievalEvaluationResult:
    """Evaluation of the retrieved knowledge quality before response generation."""
    query: str
    total_retrieved: int
    top_score: float
    mean_score: float
    has_strong_grounding: bool
    retrieval_relevance_score: float
    top_sources: List[str] = field(default_factory=list)


@dataclass
class ResponseEvaluation:
    """Multi-factor evaluation record for an agent response."""
    response_id: str
    query: str
    answer_snippet: str
    grounding_score: float
    completeness_score: float
    clarity_score: float
    retrieval_confidence: float
    user_correction_penalty: float = 0.0
    final_quality_score: float = 0.0
    actor_role: str = "AlfredMaster"
    evidence_trace: Optional[EvidenceTrace] = None
    user_feedback: Optional[str] = None
    is_user_accepted: Optional[bool] = None
    created_at: float = field(default_factory=time.time)


@dataclass
class FailureRecord:
    """Failure log record connecting evaluation misses to Phase 97 Self-Improvement."""
    failure_id: str
    response_id: str
    category: FailureCategory
    cause: str
    user_correction: str
    corrective_action: str
    created_at: float = field(default_factory=time.time)


@dataclass
class SourceUtilityRecord:
    """Long-term utility tracking for a specific vault document."""
    source_file: str
    times_retrieved: int = 0
    times_successful: int = 0
    times_corrected: int = 0
    utility_score: float = 1.0
    last_updated: float = field(default_factory=time.time)


@dataclass
class IntelligenceScorecard:
    """High-level system intelligence and quality scorecard."""
    total_evaluations: int
    average_grounding_score: float
    average_quality_score: float
    user_satisfaction_rate: float
    total_failures_recorded: int
    top_utility_sources: List[Dict[str, Any]] = field(default_factory=list)
    recent_evaluations: List[Dict[str, Any]] = field(default_factory=list)
