import logging
from .pattern_detector import PatternDetector

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    Generates optimization recommendations based on detected patterns.
    """
    def __init__(self, detector: PatternDetector):
        self.detector = detector

    def generate_recommendations(self) -> list:
        failures = self.detector.detect_frequent_failures()
        recommendations = []
        
        for fail in failures:
            if "testing" in fail.lower() or "tests" in fail.lower():
                recommendations.append("Testing delays increased completion time. Future recommendation: Schedule testing earlier and allocate additional workers.")
            elif "frontend" in fail.lower():
                recommendations.append("Frontend tasks frequently wait on backend APIs. Recommendation: Generate mock APIs automatically during planning.")
            else:
                recommendations.append(f"Frequent failure detected: '{fail}'. Consider allocating more resources or breaking down the task.")
                
        return recommendations
