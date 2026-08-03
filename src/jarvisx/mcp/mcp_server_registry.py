from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class MCPServerConfig:
    name: str
    server_type: str  # "Filesystem", "GitHub", "Docker", "SQLite", "Postgres", "Playwright", "Browser", "Supabase", "Terminal"
    command_or_url: str = ""
    enabled: bool = True
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "server_type": self.server_type,
            "command_or_url": self.command_or_url,
            "enabled": self.enabled,
            "params": self.params
        }

class MCPServerRegistry:
    def __init__(self):
        self._servers: Dict[str, MCPServerConfig] = {}
        self._populate_defaults()

    def _populate_defaults(self):
        default_types = [
            ("filesystem", "Filesystem", "npx -y @modelcontextprotocol/server-filesystem"),
            ("github", "GitHub", "npx -y @modelcontextprotocol/server-github"),
            ("docker", "Docker", "docker run mcp/docker"),
            ("sqlite", "SQLite", "npx -y @modelcontextprotocol/server-sqlite"),
            ("postgres", "Postgres", "npx -y @modelcontextprotocol/server-postgres"),
            ("playwright", "Playwright", "npx -y @modelcontextprotocol/server-playwright"),
            ("browser", "Browser", "npx -y @modelcontextprotocol/server-puppeteer"),
            ("supabase", "Supabase", "npx -y @modelcontextprotocol/server-supabase"),
            ("terminal", "Terminal", "npx -y @modelcontextprotocol/server-terminal")
        ]
        for name, stype, cmd in default_types:
            self.register_server(MCPServerConfig(name=name, server_type=stype, command_or_url=cmd, enabled=True))

    def register_server(self, config: MCPServerConfig) -> None:
        self._servers[config.name] = config

    def unregister_server(self, name: str) -> bool:
        if name in self._servers:
            del self._servers[name]
            return True
        return False

    def get_server(self, name: str) -> Optional[MCPServerConfig]:
        return self._servers.get(name)

    def list_servers(self) -> List[MCPServerConfig]:
        return list(self._servers.values())
