class PriorityEvaluator:
    """
    Determines urgency based on impact, confidence, and resource availability.
    """
    def evaluate(self, impact: float, confidence: float) -> str:
        """
        impact: 0.0 to 1.0
        confidence: 0.0 to 1.0
        Returns: critical, high, normal, low, background
        """
        score = impact * confidence
        
        if score > 0.8:
            return "critical"
        elif score > 0.6:
            return "high"
        elif score > 0.4:
            return "normal"
        elif score > 0.2:
            return "low"
        else:
            return "background"
