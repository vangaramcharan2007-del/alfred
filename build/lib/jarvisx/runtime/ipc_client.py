"""Lightweight IPC Client for Jarvis X CLI and Hotkey triggers."""

from __future__ import annotations
import socket
import time
from typing import Any, Dict, Optional, Tuple
from jarvisx.runtime.ipc_protocol import IPCMessage, IPCMessageType


class IPCClient:
    """Client for fast communication with the running Jarvis X Daemon."""

    def __init__(self, host: str = "127.0.0.1", port: int = 10404, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def send_request(self, msg: IPCMessage) -> Tuple[bool, Optional[IPCMessage], float]:
        """Send message to daemon and receive response with measured roundtrip latency."""
        start_time = time.perf_counter()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.host, self.port))
                sock.sendall(msg.serialize())

                buffer = b""
                while b"\n" not in buffer:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    buffer += chunk

                latency_ms = (time.perf_counter() - start_time) * 1000.0
                if not buffer:
                    return False, None, latency_ms

                resp = IPCMessage.deserialize(buffer)
                return True, resp, latency_ms
        except Exception:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return False, None, latency_ms

    def ping(self) -> Tuple[bool, float]:
        """Check if daemon is alive and measure IPC latency in milliseconds."""
        req = IPCMessage(msg_type=IPCMessageType.PING)
        ok, resp, lat = self.send_request(req)
        return (ok and resp is not None and resp.status == "OK"), lat

    def get_status(self) -> Tuple[bool, Dict[str, Any], float]:
        """Fetch real-time daemon state."""
        req = IPCMessage(msg_type=IPCMessageType.GET_STATUS)
        ok, resp, lat = self.send_request(req)
        if ok and resp:
            return True, resp.payload, lat
        return False, {}, lat

    def execute_command(self, command_text: str) -> Tuple[bool, Dict[str, Any], float]:
        """Execute CLI command directly in the warm daemon."""
        req = IPCMessage(msg_type=IPCMessageType.EXECUTE_COMMAND, payload={"command": command_text})
        ok, resp, lat = self.send_request(req)
        if ok and resp:
            return True, resp.payload, lat
        return False, {"error": "Failed to connect to daemon"}, lat

    def get_briefing(self) -> Tuple[bool, str, float]:
        """Request daily morning briefing."""
        req = IPCMessage(msg_type=IPCMessageType.GET_BRIEFING)
        ok, resp, lat = self.send_request(req)
        if ok and resp:
            return True, resp.payload.get("briefing", ""), lat
        return False, "", lat

    def trigger_event(self, event_name: str, payload: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], float]:
        """Trigger an ambient system event."""
        req = IPCMessage(
            msg_type=IPCMessageType.TRIGGER_EVENT,
            payload={"event": event_name, "data": payload or {}},
        )
        ok, resp, lat = self.send_request(req)
        if ok and resp:
            return True, resp.payload, lat
        return False, {}, lat

    def shutdown(self) -> Tuple[bool, float]:
        """Request graceful daemon shutdown."""
        req = IPCMessage(msg_type=IPCMessageType.SHUTDOWN)
        ok, resp, lat = self.send_request(req)
        return (ok and resp is not None), lat
