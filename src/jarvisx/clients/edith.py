from __future__ import annotations

import json
from typing import Any, Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4


class EdithClient:
    """Lightweight local client that talks only to Alfred's REST API."""

    def __init__(self, *, base_url: str = "http://127.0.0.1:8765", timeout: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def chat(self, message: str, *, trace_id: Optional[str] = None) -> dict[str, Any]:
        return self._post("/chat", {"message": message}, trace_id=trace_id)

    def status(self, *, trace_id: Optional[str] = None) -> dict[str, Any]:
        return self._request("GET", "/status", trace_id=trace_id)

    def notify(
        self,
        *,
        title: str,
        body: str,
        trace_id: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._post("/notify", {"title": title, "body": body}, trace_id=trace_id)

    def device_action(
        self,
        action: str,
        parameters: Optional[dict[str, object]] = None,
        *,
        trace_id: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._post(
            "/device_action",
            {"action": action, "parameters": parameters or {}},
            trace_id=trace_id,
        )

    def _post(
        self,
        path: str,
        payload: dict[str, object],
        *,
        trace_id: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._request("POST", path, payload=payload, trace_id=trace_id)

    def _request(
        self,
        method: str,
        path: str,
        *,
        payload: Optional[dict[str, object]] = None,
        trace_id: Optional[str] = None,
    ) -> dict[str, Any]:
        request_trace_id = trace_id or uuid4().hex
        request_payload = dict(payload or {})
        if method == "POST":
            request_payload["trace_id"] = request_trace_id
            data = json.dumps(request_payload).encode("utf-8")
        else:
            data = None
        request = Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={
                "Content-Type": "application/json",
                "X-Trace-ID": request_trace_id,
            },
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            return json.loads(exc.read().decode("utf-8"))
