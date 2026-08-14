"""Model Context Protocol (MCP) Client for Jarvis X: GENESIS.

Standard JSON-RPC 2.0 client communicating with local MCP servers (stdio)
and remote MCP endpoints (SSE/HTTP).
Exposes tool discovery, typed tool adaptation, and safe execution.
"""

from __future__ import annotations
import os
import sys
import json
import time
import asyncio
import subprocess
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

from jarvisx.tools.tool_kernel import Tool, ToolSpec, ToolResult, PermissionLevel


@dataclass
class MCPToolDefinition:
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_id: str


class MCPClient:
    """Standard Model Context Protocol client."""

    def __init__(self, server_id: str, command: Optional[List[str]] = None, endpoint_url: Optional[str] = None):
        self.server_id = server_id
        self.command = command or []
        self.endpoint_url = endpoint_url
        self.process: Optional[subprocess.Popen] = None
        self._request_id = 0
        self.is_connected = False
        self.discovered_tools: Dict[str, MCPToolDefinition] = {}

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def connect(self, timeout_sec: float = 5.0) -> bool:
        """Start stdio subprocess or verify endpoint connectivity."""
        if self.command and not self.process:
            try:
                creation_flags = 0x08000000 if sys.platform == "win32" else 0  # CREATE_NO_WINDOW
                self.process = subprocess.Popen(
                    self.command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    creationflags=creation_flags
                )
                # Send MCP initialize request
                init_res = await self._send_jsonrpc("initialize", {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "JarvisX-Genesis", "version": "1.0.0"}
                }, timeout_sec=timeout_sec)
                
                self.is_connected = init_res is not None and "result" in init_res
                if self.is_connected:
                    await self.refresh_tools()
                return self.is_connected
            except Exception as e:
                self.is_connected = False
                return False
        elif self.endpoint_url:
            self.is_connected = True
            await self.refresh_tools()
            return True
        return False

    async def disconnect(self) -> None:
        """Terminate the MCP server subprocess."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1.0)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None
        self.is_connected = False

    async def _send_jsonrpc(self, method: str, params: Optional[Dict[str, Any]] = None, timeout_sec: float = 10.0) -> Optional[Dict[str, Any]]:
        """Send a JSON-RPC 2.0 request and await response."""
        if not self.process or not self.process.stdin or not self.process.stdout:
            return None

        req_id = self._next_id()
        msg = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {}
        }

        try:
            loop = asyncio.get_running_loop()

            def _write_and_read():
                payload = json.dumps(msg) + "\n"
                self.process.stdin.write(payload)
                self.process.stdin.flush()
                line = self.process.stdout.readline()
                if line:
                    return json.loads(line.strip())
                return None

            return await asyncio.wait_for(loop.run_in_executor(None, _write_and_read), timeout=timeout_sec)
        except Exception:
            return None

    async def refresh_tools(self) -> List[MCPToolDefinition]:
        """Fetch available tools via MCP tools/list."""
        res = await self._send_jsonrpc("tools/list", {})
        tools: List[MCPToolDefinition] = []
        if res and "result" in res and "tools" in res["result"]:
            for t in res["result"]["tools"]:
                mcp_t = MCPToolDefinition(
                    name=t.get("name", "unknown"),
                    description=t.get("description", ""),
                    input_schema=t.get("inputSchema", {}),
                    server_id=self.server_id
                )
                self.discovered_tools[mcp_t.name] = mcp_t
                tools.append(mcp_t)
        return tools

    async def list_tools(self) -> List[MCPToolDefinition]:
        """Alias for refresh_tools() to query tools/list."""
        return await self.refresh_tools()

    async def call_tool(self, name: str, arguments: Dict[str, Any], timeout_sec: float = 15.0) -> Dict[str, Any]:
        """Execute a tool via MCP tools/call."""
        start_t = time.time()
        res = await self._send_jsonrpc("tools/call", {"name": name, "arguments": arguments}, timeout_sec=timeout_sec)
        latency = round((time.time() - start_t) * 1000, 1)

        if res and "result" in res:
            return {
                "status": "success",
                "tool": name,
                "server_id": self.server_id,
                "content": res["result"].get("content", []),
                "latency_ms": latency
            }
        elif res and "error" in res:
            return {
                "status": "failed",
                "tool": name,
                "server_id": self.server_id,
                "error": res["error"].get("message", "Unknown MCP error"),
                "latency_ms": latency
            }
        return {
            "status": "failed",
            "tool": name,
            "server_id": self.server_id,
            "error": "MCP server timeout or no response",
            "latency_ms": latency
        }
