from __future__ import annotations

import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.api import create_alfred_api_server
from jarvisx.clients.edith import EdithClient
from jarvisx.runtime import create_default_runtime


class AlfredApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        runtime = create_default_runtime(
            log_path=root / "jarvisx.jsonl",
            obsidian_vault=root / "vault",
        )
        self.server = create_alfred_api_server(runtime, host="127.0.0.1", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.client = EdithClient(base_url=f"http://{host}:{port}", timeout=5.0)

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5.0)
        self.temp_dir.cleanup()

    def test_status_endpoint_connectivity(self) -> None:
        response = self.client.status(trace_id="trace-status")

        self.assertTrue(response["handled"])
        self.assertEqual(response["trace_id"], "trace-status")
        self.assertEqual(response["status"], "ok")
        self.assertIn("hermes", response["checks"])

    def test_chat_propagates_trace_id(self) -> None:
        response = self.client.chat("Open YouTube", trace_id="trace-chat")

        self.assertTrue(response["handled"])
        self.assertEqual(response["trace_id"], "trace-chat")
        self.assertEqual(response["agent_id"], "device")
        self.assertEqual(response["data"]["intent"]["agent_id"], "device")

    def test_device_action_routes_through_device_agent(self) -> None:
        response = self.client.device_action(
            "open_app",
            {"app_name": "YouTube"},
            trace_id="trace-device",
        )

        self.assertTrue(response["handled"])
        self.assertEqual(response["trace_id"], "trace-device")
        self.assertEqual(response["agent_id"], "device")
        self.assertEqual(
            response["data"]["result"]["data"]["package_hint"],
            "com.google.android.youtube",
        )

    def test_notify_routes_as_device_notification(self) -> None:
        response = self.client.notify(
            title="Jarvis X",
            body="Memory scan complete",
            trace_id="trace-notify",
        )

        self.assertTrue(response["handled"])
        self.assertEqual(response["trace_id"], "trace-notify")
        self.assertEqual(response["agent_id"], "device")
        self.assertEqual(response["data"]["result"]["data"]["action"], "notification")

    def test_unsupported_device_action_returns_failure(self) -> None:
        response = self.client.device_action("teleport", {}, trace_id="trace-fail")

        self.assertFalse(response["handled"])
        self.assertEqual(response["trace_id"], "trace-fail")
        self.assertEqual(response["agent_id"], "alfred")
        self.assertEqual(
            response["data"]["failure"]["what_failed"],
            "unsupported_device_action",
        )


if __name__ == "__main__":
    unittest.main()
