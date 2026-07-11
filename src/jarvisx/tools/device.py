from __future__ import annotations

from jarvisx.tools.base import BaseTool, ToolResult


SUPPORTED_DEVICE_ACTIONS = ("open_app", "notification", "speak_text")


class DeviceTool(BaseTool):
    name = "device"

    def prepare_device_action(self, action: str, parameters: dict[str, object]) -> ToolResult:
        if action == "open_app":
            return self.prepare_open_app(str(parameters.get("app_name", "")))
        if action == "notification":
            return self.prepare_notification(
                title=str(parameters.get("title", "Jarvis X")),
                body=str(parameters.get("body", "")),
            )
        if action == "speak_text":
            return self.prepare_speak_text(str(parameters.get("text", "")))
        return ToolResult(
            success=False,
            message=f"Unsupported device action: {action}.",
            data={"supported_actions": list(SUPPORTED_DEVICE_ACTIONS)},
        )

    def prepare_open_app(self, app_name: str) -> ToolResult:
        normalized = app_name.strip() or "requested app"
        package_hints = {
            "youtube": "com.google.android.youtube",
            "chrome": "com.android.chrome",
            "gmail": "com.google.android.gm",
            "whatsapp": "com.whatsapp",
        }
        return ToolResult(
            success=True,
            message=f"Prepared Android launch action for {normalized}.",
            data={
                "action": "android.intent.action.MAIN",
                "category": "android.intent.category.LAUNCHER",
                "package_hint": package_hints.get(normalized.lower()),
                "app_name": normalized,
                "execution_layer": "Edith or MacroDroid adapter",
            },
        )

    def prepare_notification(self, *, title: str, body: str) -> ToolResult:
        clean_title = title.strip() or "Jarvis X"
        clean_body = body.strip()
        if not clean_body:
            return ToolResult(
                success=False,
                message="Notification body was empty.",
                data={"action": "notification"},
            )
        return ToolResult(
            success=True,
            message="Prepared Android notification action.",
            data={
                "action": "notification",
                "title": clean_title,
                "body": clean_body,
                "execution_layer": "Edith or MacroDroid adapter",
            },
        )

    def prepare_speak_text(self, text: str) -> ToolResult:
        clean_text = text.strip()
        if not clean_text:
            return ToolResult(
                success=False,
                message="Speech text was empty.",
                data={"action": "speak_text"},
            )
        return ToolResult(
            success=True,
            message="Prepared text-to-speech action.",
            data={
                "action": "speak_text",
                "text": clean_text,
                "execution_layer": "Edith local voice adapter",
            },
        )
