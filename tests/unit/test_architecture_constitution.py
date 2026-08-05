"""Unit tests verifying Phase 44B Architectural Constitution."""

import os
import pytest
from typing import Any, Dict

from jarvisx.architecture import (
    LAYER_REGISTRY,
    get_layer_for_module,
    ArchitectureContract,
    AgentContract,
    ArchitectureValidator,
)


def test_layer_registry_mapping():
    assert get_layer_for_module("jarvisx.config") == "human"
    assert get_layer_for_module("jarvisx.core") == "alfred"
    assert get_layer_for_module("jarvisx.architecture.contracts") == "alfred"
    assert get_layer_for_module("jarvisx.memory") == "agents"
    assert get_layer_for_module("jarvisx.tools") == "capabilities"
    assert get_layer_for_module("jarvisx.adapters") == "infrastructure"
    assert get_layer_for_module("jarvisx.ui") == "interface"


def test_architecture_contract_dependencies():
    # Downward dependencies allowed
    assert ArchitectureContract.is_valid_layer_dependency("human", "alfred") is True
    assert ArchitectureContract.is_valid_layer_dependency("alfred", "agents") is True
    assert ArchitectureContract.is_valid_layer_dependency("agents", "capabilities") is True
    assert ArchitectureContract.is_valid_layer_dependency("capabilities", "infrastructure") is True

    # Same layer allowed
    assert ArchitectureContract.is_valid_layer_dependency("agents", "agents") is True

    # Interface invoking higher layers allowed
    assert ArchitectureContract.is_valid_layer_dependency("interface", "alfred") is True

    # Inversion forbidden
    assert ArchitectureContract.is_valid_layer_dependency("infrastructure", "alfred") is False


def test_agent_contract_enforcement():
    class DummyAgent(AgentContract):
        def execute(self, task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
            return {"status": "success", "task_id": task.get("id")}

        def status(self) -> Dict[str, Any]:
            return {"health": "ok"}

        def report(self) -> str:
            return f"Agent {self.name} is operational."

    agent = DummyAgent(name="test_agent", purpose="testing", capabilities=["test"])
    assert agent.name == "test_agent"
    assert agent.execute({"id": 1}) == {"status": "success", "task_id": 1}
    assert agent.status() == {"health": "ok"}
    assert "operational" in agent.report()

    # Verify abstract class instantiation is impossible without implementing all methods
    class IncompleteAgent(AgentContract):
        pass

    with pytest.raises(TypeError):
        IncompleteAgent("fail", "fail", [])


def test_architecture_validator(tmp_path):
    # Test validator against existing jarvisx package root
    root_dir = os.path.join(os.path.dirname(__file__), "..", "..", "src", "jarvisx")
    if os.path.exists(root_dir):
        validator = ArchitectureValidator(root_dir)
        result = validator.validate()
        assert result.scanned_files > 0
        # Verify no circular dependencies exist
        circular_violations = [v for v in result.violations if v.violation_type == "CIRCULAR_DEPENDENCY"]
        assert len(circular_violations) == 0, f"Cycles found: {circular_violations}"
