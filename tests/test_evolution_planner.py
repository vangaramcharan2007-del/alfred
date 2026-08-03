from jarvisx.evolution.improvement_detector import ImprovementProposal
from jarvisx.evolution.evolution_planner import EvolutionPlanner

def test_evolution_planner():
    planner = EvolutionPlanner()
    prop = ImprovementProposal(
        proposal_id="prop_100",
        problem="Low Python lint accuracy",
        proposed_solution="Integrate Ruff MCP",
        priority="HIGH"
    )
    mission = planner.create_mission(prop)

    assert mission.proposal_id == "prop_100"
    assert len(mission.steps) == 5
    assert "Research" in mission.steps[0]
