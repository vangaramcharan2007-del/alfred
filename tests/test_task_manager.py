import pytest
from jarvisx.core.task_manager import TaskManager

def test_task_lifecycle():
    manager = TaskManager()
    
    manager.create_task("job_1", "node1", "agent1", "tr1")
    task = manager.get_task("job_1")
    
    assert task is not None
    assert task["status"] == "SUBMITTED"
    
    manager.update_status("job_1", "RUNNING", progress=50)
    task = manager.get_task("job_1")
    
    assert task["status"] == "RUNNING"
    assert task["progress"] == 50
    
    manager.update_status("job_1", "COMPLETED")
    assert manager.get_task("job_1")["status"] == "COMPLETED"
    
    active = manager.list_active_tasks()
    assert len(active) == 0

def test_invalid_status():
    manager = TaskManager()
    manager.create_task("job_2", "node1", "agent1", "tr1")
    manager.update_status("job_2", "INVALID_STATUS")
    
    # Should ignore invalid status
    assert manager.get_task("job_2")["status"] == "SUBMITTED"
