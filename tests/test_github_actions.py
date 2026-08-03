import pytest
from jarvisx.capabilities.github.github_actions import GitHubActionsManager

def test_github_actions_manager():
    mgr = GitHubActionsManager()
    runs = mgr.read_workflow_runs(".")
    assert len(runs) >= 2

    failed = mgr.list_failed_workflows(".")
    assert len(failed) >= 1

    logs = mgr.retrieve_logs("run_102")
    assert "ConnectionTimeout" in logs

    summary = mgr.summarize_failures("run_102")
    assert "ConnectionTimeout" in summary

    triggered = mgr.trigger_workflow("deploy.yml")
    assert triggered["status"] == "in_progress"
