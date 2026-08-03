import pytest
from jarvisx.capabilities.github.github_pull_request import GitHubPRManager

def test_github_pr_lifecycle():
    mgr = GitHubPRManager()
    pr = mgr.create_pr(
        title="feat: add OAuth2 auth flow",
        body="Implements OAuth2 login and token handling",
        head_branch="feature/oauth2"
    )

    assert pr.number == 101
    assert pr.state == "open"

    review = mgr.approve(101, comment="Looks great!")
    assert review["status"] == "APPROVED"

    summary = mgr.generate_summary(101)
    assert "PR #101: feat: add OAuth2 auth flow" in summary

    merged = mgr.merge(101)
    assert merged is True
    assert mgr.get_pr(101).state == "merged"
