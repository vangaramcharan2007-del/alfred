"""High-Speed Localhost/Socket IPC Server for Jarvis X Daemon."""

from __future__ import annotations
import logging
import socket
import threading
from typing import Any, Callable, Dict, Optional
from jarvisx.runtime.ipc_protocol import IPCMessage, IPCMessageType

logger = logging.getLogger("jarvisx.ipc_server")


class IPCServer:
    """Ultra-low-latency TCP loopback server listening on localhost:10404."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 10404,
        command_handler: Optional[Callable[[str], Dict[str, Any]]] = None,
        event_handler: Optional[Callable[[str, Dict[str, Any]], Dict[str, Any]]] = None,
        briefing_handler: Optional[Callable[[], str]] = None,
        status_handler: Optional[Callable[[], Dict[str, Any]]] = None,
        shutdown_handler: Optional[Callable[[], None]] = None,
    ):
        self.host = host
        self.port = port
        self.command_handler = command_handler
        self.event_handler = event_handler
        self.briefing_handler = briefing_handler
        self.status_handler = status_handler
        self.shutdown_handler = shutdown_handler
        self._server_socket: Optional[socket.socket] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Bind socket and start listening in a background thread."""
        if self._running:
            return

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(16)
        self._server_socket.settimeout(0.5)

        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, name="IPCServerThread", daemon=True)
        self._thread.start()
        logger.info(f"IPC Server listening on {self.host}:{self.port}")

    def stop(self):
        """Stop listening and close socket."""
        self._running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _listen_loop(self):
        while self._running:
            try:
                client_sock, _ = self._server_socket.accept()
                client_thread = threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True)
                client_thread.start()
            except socket.timeout:
                continue
            except Exception:
                if not self._running:
                    break

    def _handle_client(self, client_sock: socket.socket):
        client_sock.settimeout(5.0)
        try:
            buffer = b""
            while b"\n" not in buffer:
                chunk = client_sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk

            if not buffer:
                return

            req = IPCMessage.deserialize(buffer)
            resp = self._process_request(req)
            client_sock.sendall(resp.serialize())
        except Exception as e:
            err_resp = IPCMessage(
                msg_type=IPCMessageType.ERROR,
                status="ERROR",
                error=str(e),
            )
            try:
                client_sock.sendall(err_resp.serialize())
            except Exception:
                pass
        finally:
            try:
                client_sock.close()
            except Exception:
                pass

    def _process_request(self, req: IPCMessage) -> IPCMessage:
        """Route IPC request to appropriate handler."""
        if req.msg_type == IPCMessageType.PING:
            return IPCMessage(
                msg_id=req.msg_id,
                msg_type=IPCMessageType.RESPONSE,
                payload={"pong": True, "message": "Jarvis X IPC Gateway Online"},
            )

        elif req.msg_type == IPCMessageType.GET_STATUS:
            status_data = self.status_handler() if self.status_handler else {"status": "ONLINE"}
            return IPCMessage(
                msg_id=req.msg_id,
                msg_type=IPCMessageType.RESPONSE,
                payload=status_data,
            )

        elif req.msg_type == IPCMessageType.GET_BRIEFING:
            briefing = self.briefing_handler() if self.briefing_handler else "No briefing available."
            return IPCMessage(
                msg_id=req.msg_id,
                msg_type=IPCMessageType.RESPONSE,
                payload={"briefing": briefing},
            )

        elif req.msg_type == IPCMessageType.TRIGGER_EVENT:
            event_name = req.payload.get("event", "")
            event_payload = req.payload.get("data", {})
            res = self.event_handler(event_name, event_payload) if self.event_handler else {"triggered": True}
            return IPCMessage(
                msg_id=req.msg_id,
                msg_type=IPCMessageType.RESPONSE,
                payload=res,
            )

        elif req.msg_type == IPCMessageType.EXECUTE_COMMAND:
            command_text = req.payload.get("command", "")
            result = self.command_handler(command_text) if self.command_handler else {"output": "No handler configured."}
            return IPCMessage(
                msg_id=req.msg_id,
                msg_type=IPCMessageType.RESPONSE,
                payload=result,
            )

        elif req.msg_type == IPCMessageType.SHUTDOWN:
            if self.shutdown_handler:
                threading.Thread(target=self.shutdown_handler, daemon=True).start()
            return IPCMessage(
                msg_id=req.msg_id,
                msg_type=IPCMessageType.RESPONSE,
                payload={"status": "SHUTDOWN_INITIATED"},
            )

        return IPCMessage(
            msg_id=req.msg_id,
            msg_type=IPCMessageType.ERROR,
            status="ERROR",
            error=f"Unknown message type: {req.msg_type}",
        )
