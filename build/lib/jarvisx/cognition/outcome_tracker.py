class OutcomeTracker:
    def __init__(self, metrics=None):
        self.metrics = metrics
        self.outcomes = []

    def record_outcome(self, task: str, agent: str, success: bool, duration: float, satisfaction: float = 0.0):
        self.outcomes.append({
            "task": task,
            "agent": agent,
            "success": success,
            "duration": duration,
            "satisfaction": satisfaction
        })
        if self.metrics:
            self.metrics.record_decision(success)
        
        # Send to LearningEngine...
