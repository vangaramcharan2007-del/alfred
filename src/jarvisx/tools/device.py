from __future__ import annotations

from typing import Optional

from jarvisx.adapters.android import MacroDroidIntentAdapter
from jarvisx.tools.base import BaseTool, ToolResult


SUPPORTED_DEVICE_ACTIONS = ("open_app", "notification", "speak_text")


class DeviceTool(BaseTool):
    name = "device"

    def __init__(self, *, android_adapter: Optional[MacroDroidIntentAdapter] = None) -> None:
        self.android_adapter = android_adapter or MacroDroidIntentAdapter()

    def prepare_device_action(
        self,
        action: str,
        parameters: dict[str, object],
        *,
        trace_id: Optional[str] = None,
    ) -> ToolResult:
        if action == "open_app":
            return self.prepare_open_app(str(parameters.get("app_name", "")), trace_id=trace_id)
        if action == "notification":
            return self.prepare_notification(
                title=str(parameters.get("title", "Jarvis X")),
                body=str(parameters.get("body", "")),
                trace_id=trace_id,
            )
        if action == "speak_text":
            return self.prepare_speak_text(str(parameters.get("text", "")), trace_id=trace_id)
        return ToolResult(
            success=False,
            message=f"Unsupported device action: {action}.",
            data={"action": action, "trace_id": trace_id, "supported_actions": list(SUPPORTED_DEVICE_ACTIONS)},
        )

    def prepare_open_app(self, app_name: str, *, trace_id: Optional[str] = None) -> ToolResult:
        normalized = app_name.strip() or "requested app"
        package_hints = {
            "youtube": "com.google.android.youtube",
            "chrome": "com.android.chrome",
            "gmail": "com.google.android.gm",
            "whatsapp": "com.whatsapp",
        }
        package_hint = package_hints.get(normalized.lower())
        intent = self.android_adapter.open_app(
            app_name=normalized,
            package_hint=package_hint,
            trace_id=trace_id,
        )
        return ToolResult(
            success=True,
            message=f"Prepared Android launch action for {normalized}.",
            data={
                "action": "open_app",
                "trace_id": trace_id,
                "package_hint": package_hint,
                "app_name": normalized,
                "execution_layer": "MacroDroid intent adapter",
                "macrodroid_intent": intent.to_dict(),
            },
        )

    def prepare_notification(
        self,
        *,
        title: str,
        body: str,
        trace_id: Optional[str] = None,
    ) -> ToolResult:
        clean_title = title.strip() or "Jarvis X"
        clean_body = body.strip()
        if not clean_body:
            return ToolResult(
                success=False,
                message="Notification body was empty.",
                data={"action": "notification", "trace_id": trace_id},
            )
        intent = self.android_adapter.notification(
            title=clean_title,
            body=clean_body,
            trace_id=trace_id,
        )
        return ToolResult(
            success=True,
            message="Prepared Android notification action.",
            data={
                "action": "notification",
                "trace_id": trace_id,
                "title": clean_title,
                "body": clean_body,
                "execution_layer": "MacroDroid intent adapter",
                "macrodroid_intent": intent.to_dict(),
            },
        )

    def prepare_speak_text(self, text: str, *, trace_id: Optional[str] = None) -> ToolResult:
        clean_text = text.strip()
        if not clean_text:
            return ToolResult(
                success=False,
                message="Speech text was empty.",
                data={"action": "speak_text", "trace_id": trace_id},
            )
        intent = self.android_adapter.speak_text(text=clean_text, trace_id=trace_id)
        return ToolResult(
            success=True,
            message="Prepared text-to-speech action.",
            data={
                "action": "speak_text",
                "trace_id": trace_id,
                "text": clean_text,
                "execution_layer": "MacroDroid intent adapter",
                "macrodroid_intent": intent.to_dict(),
            },
        )
