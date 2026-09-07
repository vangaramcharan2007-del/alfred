"""Jarvis X Autonomous Academic & Homework Sentinel.

Monitors multi-channel academic sources, normalizes assignments,
auto-solves homework, generates documents, alerts the user, and manages submissions.
"""

from jarvisx.academic.models import (
    AcademicTask,
    AlertEvent,
    ChannelSource,
    StudentProfile,
    TaskPriority,
    TaskStatus,
    TaskType,
)
from jarvisx.academic.channel_hub import ChannelHub
from jarvisx.academic.normalizer import AssignmentNormalizer
from jarvisx.academic.solver_engine import AcademicSolverEngine
from jarvisx.academic.document_compiler import AcademicDocumentCompiler
from jarvisx.academic.alert_dispatcher import AcademicAlertDispatcher
from jarvisx.academic.submission_engine import AcademicSubmissionEngine
from jarvisx.academic.persistence import AcademicPersistenceManager
from jarvisx.academic.sentinel_daemon import AcademicSentinelDaemon
from jarvisx.academic.agent import AcademicSentinelAgent, get_academic_agent
from jarvisx.academic.session_vault import SessionVault
from jarvisx.academic.resilient_scraper import ResilientScraper
from jarvisx.academic.multimodal_anchor import MultiModalAnchor
from jarvisx.academic.stylometry_engine import StylometryEngine
from jarvisx.academic.resilience_controller import ResilienceController

__all__ = [
    "AcademicTask",
    "AlertEvent",
    "ChannelSource",
    "StudentProfile",
    "TaskPriority",
    "TaskStatus",
    "TaskType",
    "ChannelHub",
    "AssignmentNormalizer",
    "AcademicSolverEngine",
    "AcademicDocumentCompiler",
    "AcademicAlertDispatcher",
    "AcademicSubmissionEngine",
    "AcademicPersistenceManager",
    "AcademicSentinelDaemon",
    "AcademicSentinelAgent",
    "get_academic_agent",
    "SessionVault",
    "ResilientScraper",
    "MultiModalAnchor",
    "StylometryEngine",
    "ResilienceController",
]

