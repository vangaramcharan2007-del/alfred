from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from jarvisx.core.capabilities.evaluation import ProviderEvaluation, ProviderStatus


class NegotiationStrategy(ABC):
    """
    Interface for evaluating and ranking a list of provider evaluations.
    Alfred can use different strategies depending on the user's intent.
    """
    @abstractmethod
    def rank(self, evaluations: List[ProviderEvaluation]) -> List[ProviderEvaluation]:
        """Returns the evaluations sorted from best to worst according to the strategy."""
        pass

    def select(self, evaluations: List[ProviderEvaluation]) -> Optional[ProviderEvaluation]:
        """Returns the single best evaluation."""
        if not evaluations:
            return None
        ranked = self.rank(evaluations)
        return ranked[0] if ranked else None


class HighestScoreStrategy(NegotiationStrategy):
    """
    Selects the provider with the highest self-reported score, 
    but penalizes providers with poor health.
    """
    def rank(self, evaluations: List[ProviderEvaluation]) -> List[ProviderEvaluation]:
        valid_evals = [e for e in evaluations if e.available]
        
        def calculate_adjusted_score(e: ProviderEvaluation) -> float:
            # Base score from the provider
            score = e.score 
            
            # Apply learning/health penalties
            if e.health_status == ProviderStatus.DEGRADED:
                score *= 0.5
            elif e.health_status == ProviderStatus.OFFLINE:
                score *= 0.1
                
            # Factor in success rate history
            score *= e.success_rate
            
            return score
            
        return sorted(valid_evals, key=calculate_adjusted_score, reverse=True)


class HighestReliabilityStrategy(NegotiationStrategy):
    """
    Prioritizes providers with the highest historical success rate and confidence,
    ignoring features or speed.
    """
    def rank(self, evaluations: List[ProviderEvaluation]) -> List[ProviderEvaluation]:
        valid_evals = [e for e in evaluations if e.available and e.health_status != ProviderStatus.OFFLINE]
        
        def calculate_reliability(e: ProviderEvaluation) -> float:
            return (e.success_rate * 0.7) + (e.confidence * 0.3)
            
        return sorted(valid_evals, key=calculate_reliability, reverse=True)


class LowestLatencyStrategy(NegotiationStrategy):
    """
    Prioritizes the fastest provider (useful for realtime/voice responses).
    """
    def rank(self, evaluations: List[ProviderEvaluation]) -> List[ProviderEvaluation]:
        valid_evals = [e for e in evaluations if e.available and e.health_status != ProviderStatus.OFFLINE]
        
        def calculate_latency_score(e: ProviderEvaluation) -> float:
            # Lower latency is better, but it must still be reliable
            latency = e.latency_ms if e.latency_ms > 0 else 9999.0
            penalty = 1.0 if e.success_rate > 0.8 else 5.0
            return latency * penalty
            
        return sorted(valid_evals, key=calculate_latency_score)
