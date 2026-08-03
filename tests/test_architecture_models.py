import pytest
from jarvisx.capabilities.coding.architecture_models import SystemArchitecture, Component, ArchitectureDecision

def test_architecture_models_serialization():
    comp = Component(
        name="APIGateway",
        responsibility="Routes REST requests",
        dependencies=["AuthService"],
        interfaces=["REST /api"]
    )
    dec = ArchitectureDecision(
        decision="Use FastAPI",
        alternatives_considered=["Flask", "Django"],
        reasoning="Async performance",
        tradeoffs=["Smaller ecosystem"]
    )

    sys_arch = SystemArchitecture(
        project_name="TestSystem",
        requirements=["High throughput"],
        components=[comp],
        technology_stack={"backend": "FastAPI"},
        data_flow=["Client -> APIGateway"],
        api_design=[{"endpoint": "/health"}],
        database_design=[{"table": "users"}],
        risks=["Latency"],
        decisions=[dec]
    )

    d = sys_arch.to_dict()
    assert d["project_name"] == "TestSystem"
    assert len(d["components"]) == 1
    assert d["components"][0]["name"] == "APIGateway"
    assert len(d["decisions"]) == 1
    assert d["decisions"][0]["decision"] == "Use FastAPI"
