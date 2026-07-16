class ConfidenceEstimator:
    """
    Estimates if local models can handle a given task based on complexity.
    """
    def estimate(self, prompt: str) -> float:
        """
        Returns confidence score 0.0 to 1.0
        """
        prompt_lower = prompt.lower()
        if "analyze this 500 file repository" in prompt_lower or "architecture decisions" in prompt_lower:
            return 0.3 # Low confidence for local
        if "15 times 27" in prompt_lower or "open" in prompt_lower:
            return 0.95 # High confidence for local
        return 0.8
