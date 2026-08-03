from __future__ import annotations
import time
from typing import Dict, Any, List, Optional
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.core.capability_descriptor import CapabilityDescriptor
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.github.github_repository import GitHubRepositoryManager
from jarvisx.capabilities.github.github_issue import GitHubIssueManager
from jarvisx.capabilities.github.github_pull_request import GitHubPRManager
from jarvisx.capabilities.github.github_review import GitHubReviewIntelligence
from jarvisx.capabilities.github.github_actions import GitHubActionsManager
from jarvisx.capabilities.coding.pipeline.code_executor import FileChangeRecord
from jarvisx.mcp.mcp_manager import MCPManager
from jarvisx.capabilities.coding.metrics import CodingMetrics

class GitHubCapability:
    def __init__(
        self,
        bus: Optional[HermesBus] = None,
        mcp_manager: Optional[MCPManager] = None,
        metrics: Optional[CodingMetrics] = None
    ):
        self.bus = bus or HermesBus()
        self.mcp_manager = mcp_manager
        self.metrics = metrics or CodingMetrics()

        self.repo_mgr = GitHubRepositoryManager()
        self.issue_mgr = GitHubIssueManager()
        self.pr_mgr = GitHubPRManager()
        self.review_intel = GitHubReviewIntelligence()
        self.actions_mgr = GitHubActionsManager()

    def get_descriptor(self) -> CapabilityDescriptor:
        actions = [
            "clone", "open", "analyze", "list_branches", "checkout_branch", "create_branch", "delete_branch",
            "fetch", "pull", "push", "status", "diff",
            "list_issues", "search_issues", "read_issue", "create_issue", "close_issue", "add_comment", "assign_issue", "update_labels", "set_milestone",
            "create_pr", "update_pr", "review_pr", "approve_pr", "request_changes", "merge_pr", "close_pr", "generate_summary", "generate_release_notes",
            "generate_review",
            "read_workflows", "list_failed_workflows", "retrieve_logs", "trigger_workflow", "cancel_workflow", "summarize_failures"
        ]

        return CapabilityDescriptor(
            id="github.engineering",
            name="GitHub Engineering Capability",
            version="1.0.0",
            author="Jarvis X",
            category="coding",
            permissions=["READ", "WRITE", "EXECUTE"],
            supported_actions=actions,
            handler=self.handle_action
        )

    async def register_capability(self, registry: CapabilityRegistry) -> None:
        descriptor = self.get_descriptor()
        await registry.register(descriptor)

        # Hermes event: github.connected
        await self.bus.publish(Event(
            type="github.connected",
            source="github_capability",
            payload={"status": "connected", "supported_actions": len(descriptor.supported_actions)}
        ))

    async def handle_action(self, action: str, **kwargs) -> Any:
        # Check MCP fallback preference
        if self.mcp_manager and "github" in self.mcp_manager.list_connected_servers():
            client = self.mcp_manager.get_client("github")
            if client:
                try:
                    return await client.call_tool(action, kwargs)
                except Exception:
                    pass  # Fallback to local implementation

        # Local implementation handling
        if action == "clone":
            self.metrics.repositories_opened += 1
            return self.repo_mgr.clone_repository(kwargs["repo_url"], kwargs["dest_dir"])
        elif action == "open":
            self.metrics.repositories_opened += 1
            return self.repo_mgr.open_repository(kwargs["repo_path"])
        elif action == "analyze":
            return self.repo_mgr.analyze_repository(kwargs["repo_path"])
        elif action == "list_branches":
            return [b.to_dict() for b in self.repo_mgr.list_branches(kwargs["repo_path"])]
        elif action == "create_branch":
            return self.repo_mgr.create_branch(kwargs["repo_path"], kwargs["branch_name"]).to_dict()
        elif action == "status":
            return self.repo_mgr.status(kwargs["repo_path"])
        elif action == "diff":
            return self.repo_mgr.diff(kwargs["repo_path"])

        # Issues
        elif action == "create_issue":
            issue = self.issue_mgr.create_issue(
                title=kwargs["title"],
                body=kwargs["body"],
                labels=kwargs.get("labels"),
                assignee=kwargs.get("assignee")
            )
            self.metrics.issues_processed += 1
            await self.bus.publish(Event(
                type="github.issue.created",
                source="github_capability",
                payload=issue.to_dict()
            ))
            return issue.to_dict()
        elif action == "read_issue":
            issue = self.issue_mgr.read_issue(kwargs["issue_number"])
            return issue.to_dict() if issue else None
        elif action == "add_comment":
            comment = self.issue_mgr.add_comment(kwargs["issue_number"], kwargs["comment_text"])
            await self.bus.publish(Event(
                type="github.issue.updated",
                source="github_capability",
                payload={"issue_number": kwargs["issue_number"], "action": "comment_added"}
            ))
            return comment

        # PRs
        elif action == "create_pr":
            pr = self.pr_mgr.create_pr(
                title=kwargs["title"],
                body=kwargs["body"],
                head_branch=kwargs["head_branch"],
                base_branch=kwargs.get("base_branch", "main")
            )
            self.metrics.prs_created += 1
            await self.bus.publish(Event(
                type="github.pr.created",
                source="github_capability",
                payload=pr.to_dict()
            ))
            return pr.to_dict()
        elif action == "approve_pr":
            review = self.pr_mgr.approve(kwargs["number"], kwargs.get("comment", "Approved."))
            await self.bus.publish(Event(
                type="github.pr.reviewed",
                source="github_capability",
                payload={"number": kwargs["number"], "review": review}
            ))
            return review

        # Review Intelligence
        elif action == "generate_review":
            changes = kwargs.get("file_changes", [])
            file_change_records = [
                FileChangeRecord(
                    file_path=c["file_path"],
                    action=c.get("action", "modified"),
                    content_after=c.get("content_after", "")
                ) for c in changes
            ]
            rev_report = await self.review_intel.generate_comprehensive_review(
                file_changes=file_change_records,
                idea_description=kwargs.get("idea_description")
            )
            self.metrics.reviews_generated += 1
            return rev_report

        # Actions
        elif action == "read_workflows":
            self.metrics.workflow_runs += 1
            runs = self.actions_mgr.read_workflow_runs(kwargs.get("repo_path", "."))
            await self.bus.publish(Event(
                type="github.actions.completed",
                source="github_capability",
                payload={"count": len(runs)}
            ))
            return runs

        raise NotImplementedError(f"Action '{action}' is not handled by GitHubCapability.")
