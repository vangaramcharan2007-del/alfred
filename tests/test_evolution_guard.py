from jarvisx.evolution.improvement_detector import ImprovementProposal
from jarvisx.evolution.evolution_guard import EvolutionGuard

def test_evolution_guard_rules():
    guard = EvolutionGuard()

    prop_safe = ImprovementProposal("p1", "Low coverage", "Refactor unit tests", "LOW")
    res_safe = guard.evaluate_safety(prop_safe)
    assert res_safe["safe"] is True
    assert res_safe["approval_required"] is False

    prop_forbidden = ImprovementProposal("p2", "Corrupted memory", "Delete capability core.memory", "HIGH")
    res_forbidden = guard.evaluate_safety(prop_forbidden)
    assert res_forbidden["safe"] is False
    assert res_forbidden["approval_required"] is True

    prop_high_risk = ImprovementProposal("p3", "Auth leak", "Migrate security settings", "HIGH")
    res_high_risk = guard.evaluate_safety(prop_high_risk)
    assert res_high_risk["safe"] is True
    assert res_high_risk["approval_required"] is True
