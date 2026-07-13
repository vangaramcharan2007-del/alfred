import json
from http import HTTPStatus
import threading
import time
import unittest
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

from jarvisx.api import create_alfred_api_server
from jarvisx.runtime import create_default_runtime


class DashboardApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = create_default_runtime()
        cls.server = create_alfred_api_server(cls.runtime, port=0)
        cls.port = cls.server.server_address[1]
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(0.1)  # allow server to start

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join(timeout=1)

    def _get(self, path: str) -> tuple[int, dict]:
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}")
            with urllib.request.urlopen(req) as response:
                body = response.read().decode("utf-8")
                return response.status, json.loads(body)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            return e.code, json.loads(body)

    def _post(self, path: str, payload: dict) -> tuple[int, dict]:
        data = json.dumps(payload).encode("utf-8")
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", data=data, method="POST")
            req.add_header("Content-Type", "application/json")
            req.add_header("Content-Length", str(len(data)))
            with urllib.request.urlopen(req) as response:
                body = response.read().decode("utf-8")
                return response.status, json.loads(body)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            return e.code, json.loads(body)

    def test_dashboard_html_serves(self) -> None:
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{self.port}/dashboard")
            with urllib.request.urlopen(req) as response:
                self.assertEqual(response.status, HTTPStatus.OK)
                body = response.read().decode("utf-8")
                self.assertIn("<title>Jarvis X — Dashboard</title>", body)
        except urllib.error.HTTPError as e:
            self.fail(f"Dashboard failed to load: {e.code}")

    def test_api_state(self) -> None:
        status, data = self._get("/api/state")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn("mode", data)
        self.assertIn("personalities", data)
        self.assertIn("health", data)
        self.assertIn("recent_logs", data)
        self.assertEqual(data["mode"]["mode"], "companion")

    def test_api_agents(self) -> None:
        status, data = self._get("/api/agents")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn("agents", data)
        self.assertTrue(isinstance(data["agents"], list))
        # Ensure we got at least one agent
        self.assertTrue(len(data["agents"]) > 0)
        
    def test_api_logs(self) -> None:
        # Write a dummy log
        self.runtime.alfred.logger.write("info", "test log entry")
        status, data = self._get("/api/logs")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn("logs", data)
        self.assertTrue(isinstance(data["logs"], list))
        self.assertTrue(len(data["logs"]) > 0)
        self.assertEqual(data["logs"][-1]["message"], "test log entry")

    def test_api_mode_switch(self) -> None:
        status, data = self._post("/api/mode", {"mode": "focus"})
        self.assertEqual(status, HTTPStatus.OK)
        self.assertTrue(data["success"])
        
        # Verify the state reflects the mode change
        status, state_data = self._get("/api/state")
        self.assertEqual(state_data["mode"]["mode"], "focus")

        # Reset to companion
        self._post("/api/mode", {"mode": "companion"})


if __name__ == "__main__":
    unittest.main()
