from __future__ import annotations

from jarvisx.tools.base import BaseTool, ToolResult


class ResearchTool(BaseTool):
    name = "research"

    def summarize_local_note(self, text: str) -> ToolResult:
        clean = " ".join(text.strip().split())
        summary = clean[:240]
        if len(clean) > 240:
            summary += "..."
        return ToolResult(
            success=True,
            message="Prepared offline summary.",
            data={"summary": summary, "source": "local"},
        )
