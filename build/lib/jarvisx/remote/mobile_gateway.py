"""
High-Level Mobile Gateway Facade for Jarvis X Remote Operations.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from jarvisx.remote.telegram_sentinel_bridge import (
    MobileMessageRequest,
    MobileMessageResponse,
    TelegramSentinelBridge,
)


class MobileRemoteGateway:
    """Singleton gateway coordinating all mobile and remote bot communications."""

    _instance: Optional[MobileRemoteGateway] = None

    def __init__(self, bridge: Optional[TelegramSentinelBridge] = None):
        self.bridge = bridge or TelegramSentinelBridge()

    @classmethod
    def get_instance(cls) -> MobileRemoteGateway:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def handle_incoming_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches an incoming JSON webhook payload from Telegram/WhatsApp."""
        user_id = str(payload.get("user_id", payload.get("from", "unknown")))
        user_name = str(payload.get("user_name", "Mobile Operator"))
        text = str(payload.get("text", payload.get("message", "")))
        timestamp = float(payload.get("timestamp", 0.0))

        req = MobileMessageRequest(
            user_id=user_id,
            user_name=user_name,
            text=text,
            timestamp=timestamp,
        )

        resp = self.bridge.process_mobile_message(req)
        return {
            "recipient_id": resp.recipient_id,
            "status": resp.status,
            "reply": resp.formatted_reply,
            "action_type": resp.action_type,
            "latency_ms": resp.latency_ms,
            "audit_hash": resp.audit_hash[:20] + "...",
        }
