#!/usr/bin/env python3
"""
Live Demonstration Script for Phase 32: GitHub Engineering Capability
Demonstrates repository connection, issue reading, planning, branch creation, mock code changes,
multi-agent review generation, and PR summary.
"""

import asyncio
import json
import tempfile
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.core.capability_registry import CapabilityRegistry
from jarvisx.capabilities.github.github_capability import GitHubCapability

async def event_logger(event: Event):
    t = event.type
    p = event.payload
    if t == "github.connected":
        print(f"🔌 [HERMES EVENT] GitHub Capability Connected with {p.get('supported_actions')} supported actions.")
    elif t == "github.issue.created":
        print(f"📌 [HERMES EVENT] GitHub Issue #{p.get('number')} Created: '{p.get('title')}'")
    elif t == "github.pr.created":
        print(f"🔀 [HERMES EVENT] GitHub Pull Request #{p.get('number')} Created: '{p.get('title')}' ({p.get('head_branch')} -> {p.get('base_branch')})")
    elif t == "github.pr.reviewed":
        print(f"🛡️  [HERMES EVENT] GitHub PR #{p.get('number')} Reviewed: {p.get('review', {}).get('status')}")

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("      JARVIS X - PHASE 32 GITHUB ENGINEERING CAPABILITY DEMO")
    print("=" * 80)

    bus = HermesBus()
    bus.subscribe("github.connected", event_logger)
    bus.subscribe("github.issue.created", event_logger)
    bus.subscribe("github.pr.created", event_logger)
    bus.subscribe("github.pr.reviewed", event_logger)

    registry = CapabilityRegistry(bus=bus)
    github_cap = GitHubCapability(bus=bus)
    await github_cap.register_capability(registry)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        (repo_path / "main.py").write_text("def main(): pass\n", encoding="utf-8")

        print(f"\n📂 Step 1: Connecting to Local Repository at {repo_path}")
        repo_info = await registry.execute("github.engineering", "open", repo_path=str(repo_path))
        print(f"   Repository Language:  {repo_info['profile']['language'].upper()}")
        print(f"   Framework Detected:   {repo_info['profile']['framework']}")
        print(f"   Status Clean:         {repo_info['status']['clean']}")

        print("\n📌 Step 2: Creating and Reading GitHub Issue #1...")
        issue = await registry.execute(
            "github.engineering",
            "create_issue",
            title="Implement OAuth2 Authentication Flow",
            body="Users require secure JWT + OAuth2 authentication endpoints.",
            labels=["enhancement", "security"]
        )
        print(f"   Issue #{issue['number']} Created: '{issue['title']}' (Labels: {issue['labels']})")

        print("\n🌱 Step 3: Creating Git Feature Branch 'feature/oauth2-flow'...")
        branch = await registry.execute(
            "github.engineering",
            "create_branch",
            repo_path=str(repo_path),
            branch_name="feature/oauth2-flow"
        )
        print(f"   Active Branch: '{branch['name']}' (Commit SHA: {branch['commit_sha']})")

        print("\n✏️  Step 4: Simulating Code Changes for OAuth2 Implementation...")
        mock_changes = [
            {
                "file_path": "auth.py",
                "action": "created",
                "content_after": "import jwt\n\ndef login(user, secret):\n    # Core auth logic\n    return jwt.encode({'user': user}, secret, algorithm='HS256')\n"
            }
        ]

        print("\n🛡️  Step 5: Executing Multi-Agent GitHub Review Intelligence...")
        review_report = await registry.execute(
            "github.engineering",
            "generate_review",
            file_changes=mock_changes,
            idea_description="OAuth2 JWT Auth Flow"
        )
        print(f"   Review Approved:       {review_report['approved']}")
        print(f"   Quality Score:         {review_report['score']}")
        print(f"   Risk Level:            {review_report['risk_review']['risk_level']}")
        print(f"   Missing Tests Warning: {review_report['missing_tests_check']}")

        print("\n🔀 Step 6: Creating Pull Request #101...")
        pr = await registry.execute(
            "github.engineering",
            "create_pr",
            title="feat(auth): implement OAuth2 JWT flow",
            body="Closes #1. Implements JWT token generation and login route.",
            head_branch="feature/oauth2-flow",
            base_branch="main"
        )
        print(f"   Pull Request #{pr['number']} Created: '{pr['title']}'")

        print("\n✅ Step 7: Approving Pull Request #101...")
        review_result = await registry.execute(
            "github.engineering",
            "approve_pr",
            number=pr["number"],
            comment="Code review passed. Security and architecture checks approved."
        )
        print(f"   PR Approved by: {review_result['reviewer']} with status '{review_result['status']}'")

        print("\n✨ Phase 32 GitHub Engineering Capability Demonstration Complete!")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
