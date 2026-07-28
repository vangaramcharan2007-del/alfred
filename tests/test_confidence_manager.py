import pytest
from jarvisx.cognition.confidence_manager import ConfidenceManager

def test_confidence_manager_update():
    manager = ConfidenceManager()
    assert manager.get_confidence("agent1") == 0.5
    
    manager.update_confidence("agent1", True)
    assert manager.get_confidence("agent1") > 0.5
    
    manager.update_confidence("agent1", False)
    assert manager.get_confidence("agent1") < 0.6
