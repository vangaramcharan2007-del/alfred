from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class GitHubPullRequest:
    number: int
    title: str
    body: str
    head_branch: str
    base_branch: str = "main"
    state: str = "open"
    reviews: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "number": self.number,
            "title": self.title,
            "body": self.body,
            "head_branch": self.head_branch,
            "base_branch": self.base_branch,
            "state": self.state,
            "reviews": self.reviews
        }

class GitHubPRManager:
    def __init__(self):
        self._prs: Dict[int, GitHubPullRequest] = {}
        self._counter = 101

    def create_pr(self, title: str, body: str, head_branch: str, base_branch: str = "main") -> GitHubPullRequest:
        num = self._counter
        self._counter += 1
        pr = GitHubPullRequest(
            number=num,
            title=title,
            body=body,
            head_branch=head_branch,
            base_branch=base_branch,
            state="open",
            reviews=[]
        )
        self._prs[num] = pr
        return pr

    def get_pr(self, number: int) -> Optional[GitHubPullRequest]:
        return self._prs.get(number)

    def update_pr(self, number: int, title: Optional[str] = None, body: Optional[str] = None) -> bool:
        pr = self.get_pr(number)
        if pr:
            if title: pr.title = title
            if body: pr.body = body
            return True
        return False

    def review_pr(self, number: int, status: str, comment: str, reviewer: str = "JarvisX Reviewer") -> Dict[str, Any]:
        pr = self.get_pr(number)
        if not pr:
            raise KeyError(f"Pull Request #{number} not found.")

        review_record = {
            "reviewer": reviewer,
            "status": status,  # "APPROVED", "CHANGES_REQUESTED", "COMMENTED"
            "comment": comment
        }
        pr.reviews.append(review_record)
        return review_record

    def approve(self, number: int, comment: str = "Approved.") -> Dict[str, Any]:
        return self.review_pr(number, "APPROVED", comment)

    def request_changes(self, number: int, comment: str) -> Dict[str, Any]:
        return self.review_pr(number, "CHANGES_REQUESTED", comment)

    def merge(self, number: int) -> bool:
        pr = self.get_pr(number)
        if pr:
            pr.state = "merged"
            return True
        return False

    def close(self, number: int) -> bool:
        pr = self.get_pr(number)
        if pr:
            pr.state = "closed"
            return True
        return False

    def generate_summary(self, number: int) -> str:
        pr = self.get_pr(number)
        if not pr:
            return "Pull Request not found."
        return (
            f"## PR #{pr.number}: {pr.title}\n"
            f"**Branch:** `{pr.head_branch}` -> `{pr.base_branch}` | **State:** {pr.state}\n\n"
            f"### Description\n{pr.body}\n\n"
            f"### Review Status\n"
            + ("\n".join(f"- **{r['reviewer']}**: {r['status']} - {r['comment']}" for r in pr.reviews) if pr.reviews else "No reviews recorded yet.")
        )

    def generate_release_notes(self, numbers: List[int]) -> str:
        notes = ["# Release Notes\n"]
        for num in numbers:
            pr = self.get_pr(num)
            if pr:
                notes.append(f"- **#{pr.number}**: {pr.title} (`{pr.head_branch}`)")
        return "\n".join(notes)
