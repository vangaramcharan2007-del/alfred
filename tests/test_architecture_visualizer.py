import pytest
from jarvisx.capabilities.coding.architecture_models import SystemArchitecture, Component
from jarvisx.capabilities.coding.architecture_visualizer import ArchitectureVisualizer

def test_architecture_visualizer_mermaid():
    vis = ArchitectureVisualizer()
    sys_arch = SystemArchitecture(
        project_name="VisualizerTest",
        components=[
            Component(name="Frontend", responsibility="UI", dependencies=["API"]),
            Component(name="API", responsibility="Backend logic", dependencies=["DB"])
        ],
        technology_stack={"backend": "FastAPI", "database": "PostgreSQL"},
        data_flow=["Client -> API -> Database"]
    )

    comp_diagram = vis.generate_component_diagram(sys_arch)
    data_diagram = vis.generate_data_flow_diagram(sys_arch)
    dep_diagram = vis.generate_dependency_diagram(sys_arch)

    assert "```mermaid" in comp_diagram
    assert "graph TD" in comp_diagram
    assert "sequenceDiagram" in data_diagram
    assert "flowchart LR" in dep_diagram
