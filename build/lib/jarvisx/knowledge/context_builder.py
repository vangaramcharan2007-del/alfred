"""Context Composer for Alfred & LLM Prompts in Jarvis X."""

from __future__ import annotations
from typing import List, Optional
from jarvisx.knowledge.models import SearchResult


class KnowledgeContextComposer:
    """Builds token-budgeted, citation-grounded knowledge context blocks for Alfred."""

    def __init__(self, max_char_budget: int = 3500):
        self.max_char_budget = max_char_budget

    def compose_context(
        self,
        query: str,
        results: List[SearchResult],
        header_title: str = "RELEVANT KNOWLEDGE & OBSIDIAN VAULT CONTEXT",
    ) -> str:
        """Format search results into structured, cited markdown context."""
        if not results:
            return ""

        lines = [
            f"=== {header_title} ===",
            f"Query: \"{query}\"\n",
        ]
        curr_chars = sum(len(l) for l in lines)

        for idx, res in enumerate(results, 1):
            source_citation = f"[Source: {res.source_file} | {res.heading_path} | Hash: {res.provenance_hash}]"
            tags_str = f"Tags: {', '.join(res.tags)}" if res.tags else ""
            block = (
                f"--- Result {idx} (Score: {res.score} | Reason: {res.relevance_reason}) ---\n"
                f"{source_citation}\n"
                f"{tags_str}\n\n"
                f"{res.content.strip()}\n"
            )

            if curr_chars + len(block) > self.max_char_budget:
                remaining_budget = self.max_char_budget - curr_chars
                if remaining_budget > 150:
                    lines.append(block[:remaining_budget] + "\n...[truncated]")
                break

            lines.append(block)
            curr_chars += len(block)

        lines.append("=== END KNOWLEDGE CONTEXT ===\n")
        return "\n".join(lines)
