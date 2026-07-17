from typing import Dict, Any

class PlanningMetrics:
    """Tracks performance and resource usage metrics."""
    
    def __init__(self):
        self.token_usage = 0
        self.total_planning_latency = 0.0
        self.total_execution_latency = 0.0
        self.retries = 0
        self.replans = 0
        self.objectives_completed = 0
        self.objectives_failed = 0

    def record_tokens(self, count: int):
        self.token_usage += count

    def add_planning_latency(self, latency: float):
        self.total_planning_latency += latency

    def add_execution_latency(self, latency: float):
        self.total_execution_latency += latency

    def record_retry(self):
        self.retries += 1

    def record_replan(self):
        self.replans += 1

    def record_outcome(self, success: bool):
        if success:
            self.objectives_completed += 1
        else:
            self.objectives_failed += 1

    def get_metrics(self) -> Dict[str, Any]:
        total = self.objectives_completed + self.objectives_failed
        success_rate = (self.objectives_completed / total) if total > 0 else 0.0
        
        return {
            "token_usage": self.token_usage,
            "planning_latency": round(self.total_planning_latency, 2),
            "execution_latency": round(self.total_execution_latency, 2),
            "retries": self.retries,
            "replans": self.replans,
            "success_rate": round(success_rate, 2)
        }
