import pytest
from jarvisx.capabilities.github.github_issue import GitHubIssueManager

def test_github_issue_lifecycle():
    mgr = GitHubIssueManager()
    issue = mgr.create_issue(title="Fix authentication bug", body="Token refresh failing", labels=["bug"])

    assert issue.number == 1
    assert issue.state == "open"

    comment = mgr.add_comment(1, "Investigating stack trace.")
    assert comment["text"] == "Investigating stack trace."

    assigned = mgr.assign_issue(1, "JarvisXDev")
    assert assigned is True
    assert mgr.read_issue(1).assignee == "JarvisXDev"

    closed = mgr.close_issue(1)
    assert closed is True
    assert mgr.read_issue(1).state == "closed"
