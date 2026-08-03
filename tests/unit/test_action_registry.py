import pytest
from jarvisx.automation.action_registry import ActionRegistry, Action, OpenAppAction, ExecuteTerminalAction
from jarvisx.automation.watchers import BatteryWatcher, GitWatcher, PytestWatcher

def test_action_interface():
    action = OpenAppAction("vscode")
    assert action.id == "app.open.vscode"
    assert action.can_execute() is True
    
    # Dry-run execution test
    dry_res = action.execute(dry_run=True)
    assert dry_res["status"] == "DRY_RUN"
    assert "[Dry-Run]" in dry_res["message"]

def test_action_registry_singleton_and_execution():
    registry = ActionRegistry.get_instance()
    assert "app.open.vscode" in registry.actions
    assert "terminal.execute" in registry.actions

    # Test workflow execution in dry-run mode
    wf_res = registry.execute_workflow("Start Jarvis Development", dry_run=True)
    assert wf_res["status"] == "SUCCESS"
    assert wf_res["steps_executed"] == 3

def test_watchers():
    battery_watcher = BatteryWatcher()
    bat_res = battery_watcher.check_battery()
    assert "status" in bat_res

    git_watcher = GitWatcher()
    git_res = git_watcher.check_git_status()
    assert git_res["status"] in ["CLEAN", "DIRTY"]

    pytest_watcher = PytestWatcher()
    py_res = pytest_watcher.check_tests()
    assert py_res["status"] in ["PASS", "FAIL"]
