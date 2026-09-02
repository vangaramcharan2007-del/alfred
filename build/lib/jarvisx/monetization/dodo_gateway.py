"""Decoupled Monetization and Dodo Payments Gateway for Jarvis X: GENESIS.

Architectural Rule: This module is strictly separated from core agent planning,
memory, inference, and computer-use layers.
"""

from __future__ import annotations
import os
import json
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SubscriptionPlan:
    plan_id: str
    name: str
    price_usd: float
    monthly_token_quota: int
    features: list[str]


class DodoPaymentsGateway:
    """Independent monetization bridge for Dodo Payments API."""

    PLANS = {
        "free": SubscriptionPlan(
            plan_id="plan_free",
            name="Community Free",
            price_usd=0.0,
            monthly_token_quota=100_000,
            features=["Local Inference", "UACC Desktop Control", "Core Memory"]
        ),
        "pro": SubscriptionPlan(
            plan_id="plan_pro",
            name="Genesis Pro",
            price_usd=19.99,
            monthly_token_quota=5_000_000,
            features=["Unlimited Distributed Mesh", "Priority Cloud Fallback", "Full Multi-Agent Missions"]
        )
    }

    def __init__(self, api_key: Optional[str] = None, webhook_secret: Optional[str] = None):
        self.api_key = api_key or os.environ.get("DODO_PAYMENTS_API_KEY", "")
        self.webhook_secret = webhook_secret or os.environ.get("DODO_WEBHOOK_SECRET", "")

    def create_checkout_session(self, customer_email: str, plan_id: str = "pro") -> Dict[str, Any]:
        """Generate a Dodo Payments checkout session URL."""
        plan = self.PLANS.get(plan_id, self.PLANS["free"])
        return {
            "status": "success",
            "checkout_url": f"https://checkout.dodopayments.com/buy/{plan.plan_id}?email={customer_email}",
            "plan_name": plan.name,
            "amount_usd": plan.price_usd
        }

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify authenticity of incoming Dodo webhook."""
        if not self.webhook_secret:
            return True  # Dev mode
        import hmac
        import hashlib
        computed = hmac.new(self.webhook_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed, signature)


_GLOBAL_DODO_GATEWAY: Optional[DodoPaymentsGateway] = None


def get_dodo_gateway() -> DodoPaymentsGateway:
    global _GLOBAL_DODO_GATEWAY
    if _GLOBAL_DODO_GATEWAY is None:
        _GLOBAL_DODO_GATEWAY = DodoPaymentsGateway()
    return _GLOBAL_DODO_GATEWAY
