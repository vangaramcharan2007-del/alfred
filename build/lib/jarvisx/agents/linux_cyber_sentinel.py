"""
Pillar 3: Sovereign Linux Cybersecurity & Network Sentinel for Jarvis X / Alfred OS.
===================================================================================
Provides defensive network discovery, local device inventory, and static code
vulnerability analysis inside the Linux environment.
"""

from __future__ import annotations

import logging
import os
import re
import socket
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvisx.linux_cyber_sentinel")


@dataclass
class VulnerabilityFinding:
    file_path: str
    line_number: int
    rule_id: str
    severity: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    description: str
    snippet: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LinuxCyberSentinel:
    """Defensive cybersecurity and local network sentinel."""

    _instance: Optional["LinuxCyberSentinel"] = None

    def __init__(self) -> None:
        self.scan_history: List[Dict[str, Any]] = []

    @classmethod
    def get_instance(cls) -> "LinuxCyberSentinel":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def scan_local_network(self, ports_to_check: Optional[List[int]] = None) -> Dict[str, Any]:
        """Discovers local network interfaces and checks localhost / LAN port status."""
        ports = ports_to_check or [80, 443, 8000, 8080, 5000, 3000, 22]
        open_ports = []
        host = "127.0.0.1"

        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.05)
            result = s.connect_ex((host, port))
            if result == 0:
                open_ports.append(port)
            s.close()

        # Get local hostname and IP
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
        except Exception:
            local_ip = "127.0.0.1"

        summary = {
            "status": "success",
            "hostname": hostname,
            "local_ip": local_ip,
            "ports_scanned": len(ports),
            "open_local_ports": open_ports,
            "security_state": "SECURE" if not open_ports or all(p in (8000, 3000) for p in open_ports) else "NOTICE",
            "timestamp": time.time(),
        }
        self.scan_history.append(summary)
        return summary

    def audit_code_security(self, target_directory: str) -> Dict[str, Any]:
        """Scans a directory for common security vulnerabilities (hardcoded secrets, unsafe eval)."""
        rules = [
            (r"(?i)(api[_-]?key|secret|password|bearer)\s*=\s*['\"][A-Za-z0-9_\-]{16,}['\"]", "SEC-001", "CRITICAL", "Hardcoded API Key or Secret detected"),
            (r"(?i)\beval\s*\(", "SEC-002", "HIGH", "Dangerous use of dynamic eval()"),
            (r"(?i)\bexec\s*\(", "SEC-003", "HIGH", "Dangerous use of dynamic exec()"),
            (r"(?i)subprocess\.run\(.*shell\s*=\s*True", "SEC-004", "MEDIUM", "Unsafe shell=True in subprocess call"),
        ]

        findings: List[VulnerabilityFinding] = []
        target = Path(target_directory)

        if not target.exists():
            return {"status": "failed", "error": f"Directory not found: {target_directory}"}

        scanned_files_count = 0

        for root, _, files in os.walk(target):
            # Skip hidden and cache folders
            if any(part.startswith((".", "__", "venv", "node_modules")) for part in Path(root).parts):
                continue

            for file in files:
                if not file.endswith((".py", ".js", ".ts", ".sh")):
                    continue

                scanned_files_count += 1
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_idx, line in enumerate(f, 1):
                            for pattern, rule_id, severity, desc in rules:
                                if re.search(pattern, line):
                                    findings.append(VulnerabilityFinding(
                                        file_path=file_path,
                                        line_number=line_idx,
                                        rule_id=rule_id,
                                        severity=severity,
                                        description=desc,
                                        snippet=line.strip()[:100],
                                    ))
                except Exception:
                    pass

        return {
            "status": "success",
            "target_directory": str(target.resolve()),
            "files_scanned": scanned_files_count,
            "total_vulnerabilities": len(findings),
            "findings": [f.to_dict() for f in findings],
            "posture": "HEALTHY" if len(findings) == 0 else "ACTION_RECOMMENDED",
        }
