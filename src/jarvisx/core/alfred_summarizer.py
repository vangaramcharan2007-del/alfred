"""Alfred Summarizer — translates internal agent activity into human-readable Alfred messages."""
from typing import List, Dict, Any


class AlfredSummarizer:
    """Converts raw internal events into polished, user-facing Alfred dialogue."""

    # Mapping of internal actions to conversational phrasing
    _ACTION_TEMPLATES = {
        "requirements_gathered": "I've reviewed the requirements.",
        "architecture_completed": "The architecture has been finalized.",
        "frontend_built": "The frontend is ready.",
        "deploy_frontend": "Frontend deployment is complete.",
        "configure_domain": "Domain configuration is underway.",
        "verify_ssl": "SSL certificate has been verified.",
        "build_frontend": "I've finished building the frontend.",
        "indexing_memory": "Updating my memory index.",
        "monitoring_disk": "Monitoring system resources.",
        "verifying_tasks": "Verifying task completion.",
    }

    @staticmethod
    def summarize_activity(internal_events: List[str]) -> str:
        """Turn a list of internal event strings into a single Alfred sentence."""
        readable = []
        for event in internal_events:
            template = AlfredSummarizer._ACTION_TEMPLATES.get(event)
            if template:
                readable.append(template)
            else:
                # Fall back to a cleaned-up version
                readable.append(event.replace("_", " ").capitalize() + ".")

        if not readable:
            return "Everything is proceeding as expected."
        return " ".join(readable)

    @staticmethod
    def summarize_objective_progress(title: str, progress: int, remaining: List[str]) -> str:
        """Generate an Alfred-style status update for a single objective."""
        if progress >= 100:
            return f'I\'ve completed "{title}".'
        parts = [f'Working on "{title}" - {progress}% complete.']
        if remaining:
            next_task = remaining[0].replace("_", " ")
            parts.append(f"Next up: {next_task}.")
        return " ".join(parts)

    @staticmethod
    def summarize_agents_hidden(agent_names: List[str]) -> str:
        """Generate a polished summary hiding agent internals."""
        count = len(agent_names)
        if count == 0:
            return "Standing by."
        elif count == 1:
            return "I have one subsystem working on this."
        else:
            return f"I have {count} subsystems coordinating in the background."

    @staticmethod
    def format_alfred_says(message: str) -> str:
        """Wrap a message in the Alfred presentation format."""
        return f'Alfred:\n"{message}"'
