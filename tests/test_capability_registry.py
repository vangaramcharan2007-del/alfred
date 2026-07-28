import pytest
from jarvisx.agents.capability_registry import CapabilityRegistry, AgentManifest

def test_registry_loads_manifests():
    registry = CapabilityRegistry()
    # It should automatically load the manifests we created in Phase 2
    agents = registry.list_agents()
    assert len(agents) >= 3
    ids = [a.id for a in agents]
    assert "friday" in ids
    assert "edith" in ids
    assert "vision" in ids

def test_discover_capability():
    registry = CapabilityRegistry()
    results = registry.discover_capability(["study_management"])
    assert len(results) > 0
    # Friday should be highly confident for study_management
    assert results[0]["agent"] == "friday"
    
def test_rank_agents():
    registry = CapabilityRegistry()
    # Edith is mobile/reminders, Friday is productivity
    # If we ask for reminders, Edith should rank highest
    ranked = registry.rank_agents(["reminders"])
    assert "edith" in ranked
    assert ranked[0] == "edith"
