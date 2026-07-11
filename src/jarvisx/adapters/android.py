from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


MACRODROID_PACKAGE = "com.arlosoft.macrodroid"
MACRODROID_ACTION = "com.projectjarvisx.MACRODROID_INTENT"


@dataclass(frozen=True)
class MacroDroidIntent:
    android_action: str
    package: str
    extras: dict[str, str]

    def to_dict(self) -> dict[str, object]:
        return {
            "adapter": "macrodroid",
            "delivery": "android_broadcast_intent",
            "android_action": self.android_action,
            "package": self.package,
            "extras": self.extras,
            "adb_preview": self.adb_preview(),
        }

    def adb_preview(self) -> str:
        extra_args = " ".join(
            f"--es {key} \"{value}\""
            for key, value in sorted(self.extras.items())
        )
        return f"am broadcast -a {self.android_action} -p {self.package} {extra_args}".strip()


class MacroDroidIntentAdapter:
    """Builds local MacroDroid intent payloads without executing Android actions."""

    def __init__(
        self,
        *,
        android_action: str = MACRODROID_ACTION,
        package: str = MACRODROID_PACKAGE,
    ) -> None:
        self.android_action = android_action
        self.package = package

    def open_app(
        self,
        *,
        app_name: str,
        package_hint: Optional[str],
        trace_id: Optional[str],
    ) -> MacroDroidIntent:
        extras = self._base_extras("open_app", trace_id=trace_id)
        extras["app_name"] = app_name
        if package_hint:
            extras["package_hint"] = package_hint
        return self._intent(extras)

    def notification(self, *, title: str, body: str, trace_id: Optional[str]) -> MacroDroidIntent:
        extras = self._base_extras("notification", trace_id=trace_id)
        extras["title"] = title
        extras["body"] = body
        return self._intent(extras)

    def speak_text(self, *, text: str, trace_id: Optional[str]) -> MacroDroidIntent:
        extras = self._base_extras("speak_text", trace_id=trace_id)
        extras["text"] = text
        return self._intent(extras)

    def _base_extras(self, action: str, *, trace_id: Optional[str]) -> dict[str, str]:
        extras = {"jarvis_action": action}
        if trace_id:
            extras["trace_id"] = trace_id
        return extras

    def _intent(self, extras: dict[str, str]) -> MacroDroidIntent:
        return MacroDroidIntent(
            android_action=self.android_action,
            package=self.package,
            extras=extras,
        )
