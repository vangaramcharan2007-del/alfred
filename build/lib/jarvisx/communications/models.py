"""
Data Models for Alfred Communications & Dispatch Intelligence Subsystem.
Supports Multi-Channel Ingestion: Emails, SMS, WhatsApp, Telegram, Phone Calls, and System Notifications.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class CommunicationChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    TELEGRAM = "TELEGRAM"
    PHONE_CALL = "PHONE_CALL"
    SYSTEM_NOTIFICATION = "SYSTEM_NOTIFICATION"


class ImportanceCategory(str, Enum):
    CRITICAL_ACTION_REQUIRED = "CRITICAL_ACTION_REQUIRED"
    FYI_IMPORTANT = "FYI_IMPORTANT"
    ROUTINE = "ROUTINE"
    SPAM_NOISE = "SPAM_NOISE"


@dataclass
class InboundCommunication:
    id: str
    channel: CommunicationChannel
    sender: str
    sender_name: str
    subject: str
    body: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NeuralDeductionResult:
    item_id: str
    importance_category: ImportanceCategory
    urgency_score: int  # 1 (lowest) to 10 (highest)
    reasoning_trace: str
    executive_summary: str
    recommended_action: str
    suggested_reply: Optional[str] = None
    should_alert_user: bool = False
    audit_hash: str = ""


@dataclass
class OutboundDispatchResult:
    dispatch_id: str
    recipient: str
    channel: CommunicationChannel
    action_performed: str  # e.g., "SENT_TEXT", "ANSWERED_CALL_AI", "FORWARDED_DIGEST"
    generated_content: str
    llm_rationale: str
    status: str
    latency_ms: float
    audit_hash: str
