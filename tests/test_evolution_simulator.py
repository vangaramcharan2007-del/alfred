from jarvisx.evolution.improvement_detector import ImprovementProposal
from jarvisx.evolution.evolution_simulator import EvolutionSimulator

def test_evolution_simulator():
    simulator = EvolutionSimulator()
    prop = ImprovementProposal("p1", "Missing linter", "Integrate Ruff MCP", "HIGH")
    sim = simulator.simulate_upgrade(prop)

    assert sim.proposal_id == "p1"
    assert sim.expected_benefit_pct > 0.0
    assert sim.recommendation == "PROCEED"
