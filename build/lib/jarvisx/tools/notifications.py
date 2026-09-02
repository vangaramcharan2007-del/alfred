from __future__ import annotations

from jarvisx.tools.base import BaseTool, ToolResult


class NotificationTool(BaseTool):
    name = "notification"

    def prepare_notification(self, title: str, body: str) -> ToolResult:
        return ToolResult(
            success=True,
            message="Prepared notification payload.",
            data={
                "title": title,
                "body": body,
                "execution_layer": "Edith or Android notification adapter",
            },
        )
