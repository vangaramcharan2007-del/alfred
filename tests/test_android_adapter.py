from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.adapters.android import MACRODROID_ACTION, MACRODROID_PACKAGE
from jarvisx.tools.device import DeviceTool


class AndroidAdapterTests(unittest.TestCase):
    def test_open_app_builds_macrodroid_intent(self) -> None:
        tool = DeviceTool()

        result = tool.prepare_device_action(
            "open_app",
            {"app_name": "YouTube"},
            trace_id="trace-open",
        )

        self.assertTrue(result.success)
        data = result.data
        intent = data["macrodroid_intent"]
        self.assertEqual(data["action"], "open_app")
        self.assertEqual(data["trace_id"], "trace-open")
        self.assertEqual(intent["android_action"], MACRODROID_ACTION)
        self.assertEqual(intent["package"], MACRODROID_PACKAGE)
        self.assertEqual(intent["extras"]["jarvis_action"], "open_app")
        self.assertEqual(intent["extras"]["trace_id"], "trace-open")
        self.assertEqual(intent["extras"]["package_hint"], "com.google.android.youtube")

    def test_notification_builds_macrodroid_intent(self) -> None:
        tool = DeviceTool()

        result = tool.prepare_device_action(
            "notification",
            {"title": "Jarvis X", "body": "Build complete"},
            trace_id="trace-notification",
        )

        self.assertTrue(result.success)
        intent = result.data["macrodroid_intent"]
        self.assertEqual(result.data["action"], "notification")
        self.assertEqual(intent["extras"]["jarvis_action"], "notification")
        self.assertEqual(intent["extras"]["title"], "Jarvis X")
        self.assertEqual(intent["extras"]["body"], "Build complete")
        self.assertEqual(intent["extras"]["trace_id"], "trace-notification")

    def test_speak_text_builds_macrodroid_intent(self) -> None:
        tool = DeviceTool()

        result = tool.prepare_device_action(
            "speak_text",
            {"text": "Mission ready"},
            trace_id="trace-speak",
        )

        self.assertTrue(result.success)
        intent = result.data["macrodroid_intent"]
        self.assertEqual(result.data["action"], "speak_text")
        self.assertEqual(intent["extras"]["jarvis_action"], "speak_text")
        self.assertEqual(intent["extras"]["text"], "Mission ready")
        self.assertEqual(intent["extras"]["trace_id"], "trace-speak")

    def test_invalid_action_returns_failure(self) -> None:
        tool = DeviceTool()

        result = tool.prepare_device_action("teleport", {}, trace_id="trace-invalid")

        self.assertFalse(result.success)
        self.assertEqual(result.data["trace_id"], "trace-invalid")
        self.assertIn("open_app", result.data["supported_actions"])


if __name__ == "__main__":
    unittest.main()
