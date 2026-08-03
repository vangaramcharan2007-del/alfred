from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class GitHubIssue:
    number: int
    title: str
    body: str
    state: str = "open"
    assignee: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    milestone: Optional[str] = None
    comments: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "number": self.number,
            "title": self.title,
            "body": self.body,
            "state": self.state,
            "assignee": self.assignee,
            "labels": self.labels,
            "milestone": self.milestone,
            "comments": self.comments
        }

class GitHubIssueManager:
    def __init__(self):
        self._issues: Dict[int, GitHubIssue] = {}
        self._counter = 1

    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignee: Optional[str] = None,
        milestone: Optional[str] = None
    ) -> GitHubIssue:
        num = self._counter
        self._counter += 1
        issue = GitHubIssue(
            number=num,
            title=title,
            body=body,
            state="open",
            assignee=assignee,
            labels=labels or [],
            milestone=milestone,
            comments=[]
        )
        self._issues[num] = issue
        return issue

    def list_issues(self, state: str = "open") -> List[GitHubIssue]:
        return [i for i in self._issues.values() if state == "all" or i.state == state]

    def search_issues(self, query: str) -> List[GitHubIssue]:
        q = query.lower()
        return [i for i in self._issues.values() if q in i.title.lower() or q in i.body.lower()]

    def read_issue(self, issue_number: int) -> Optional[GitHubIssue]:
        return self._issues.get(issue_number)

    def close_issue(self, issue_number: int) -> bool:
        issue = self.read_issue(issue_number)
        if issue:
            issue.state = "closed"
            return True
        return False

    def add_comment(self, issue_number: int, comment_text: str, author: str = "JarvisX") -> Dict[str, Any]:
        issue = self.read_issue(issue_number)
        if not issue:
            raise KeyError(f"Issue #{issue_number} not found.")

        comment = {"author": author, "text": comment_text}
        issue.comments.append(comment)
        return comment

    def assign_issue(self, issue_number: int, assignee: str) -> bool:
        issue = self.read_issue(issue_number)
        if issue:
            issue.assignee = assignee
            return True
        return False

    def update_labels(self, issue_number: int, labels: List[str]) -> bool:
        issue = self.read_issue(issue_number)
        if issue:
            issue.labels = labels
            return True
        return False

    def set_milestone(self, issue_number: int, milestone: str) -> bool:
        issue = self.read_issue(issue_number)
        if issue:
            issue.milestone = milestone
            return True
        return False
