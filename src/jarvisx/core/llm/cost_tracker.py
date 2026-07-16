import logging

logger = logging.getLogger(__name__)

class CostTracker:
    def __init__(self):
        self.daily_cloud_spend = 0.0
        self.monthly_cloud_spend = 0.0

    def track_cost(self, provider: str, tokens: int):
        # Stub cost calculation
        cost_per_1k = 0.03 if provider == "OpenAI" else 0.01
        cost = (tokens / 1000) * cost_per_1k
        self.daily_cloud_spend += cost
        self.monthly_cloud_spend += cost
        logger.debug(f"Tracked ${cost:.4f} for {tokens} tokens on {provider}.")
