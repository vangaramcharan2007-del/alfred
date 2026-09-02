class Metrics:
    def __init__(self):
        self.cognitive_decisions_total = 0
        self.successful_predictions = 0
        self.fallback_decisions = 0

    def record_decision(self, success: bool, is_fallback: bool = False):
        self.cognitive_decisions_total += 1
        if success:
            self.successful_predictions += 1
        if is_fallback:
            self.fallback_decisions += 1

metrics = Metrics()
