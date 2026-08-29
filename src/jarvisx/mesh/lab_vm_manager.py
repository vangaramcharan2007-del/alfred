"""
Lab VM Node Manager & Health Sentinel for Jarvis X.
Coordinates the physical lab VM (LAB-VM-01) integration into the distributed GPU mesh.
"""

from __future__ import annotations

import json
import logging
import time
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from jarvisx.security.audit_ledger import CryptographicAuditLedger

logger = logging.getLogger("jarvisx.lab_vm")


@dataclass
class LabVMNodeStatus:
    node_id: str
    hostname: str
    tailscale_ip: str
    is_online: bool
    service_status: str
    available_models: List[str]
    latency_ms: float
    deployment_readiness: str
    last_ping_time: str


class LabVMManager:
    """Manages physical lab VM integration, probe checks, and deployment verification."""

    _instance: Optional[LabVMManager] = None

    def __init__(self, audit_ledger: Optional[CryptographicAuditLedger] = None):
        self.audit = audit_ledger or CryptographicAuditLedger(Path("var/db/audit_ledger.db"))
        self.default_ip = "100.81.36.40"
        self.hostname = "LAB-VM-01"

    @classmethod
    def get_instance(cls) -> LabVMManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def probe_node_health(self, target_ip: Optional[str] = None) -> LabVMNodeStatus:
        """Pings and audits the Lab VM node over Tailscale."""
        ip = target_ip or self.default_ip
        url = f"http://{ip}:11434/api/tags"
        start_t = time.time()
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")

        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                dur = round((time.time() - start_t) * 1000, 1)
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name") for m in data.get("models", [])]

                status = LabVMNodeStatus(
                    node_id="LAB-VM-01",
                    hostname=self.hostname,
                    tailscale_ip=ip,
                    is_online=True,
                    service_status="ACTIVE_COMPUTING",
                    available_models=models,
                    latency_ms=dur,
                    deployment_readiness="READY_FOR_DISTRIBUTED_WORKLOADS",
                    last_ping_time=now_str,
                )
        except Exception:
            dur = round((time.time() - start_t) * 1000, 1)
            status = LabVMNodeStatus(
                node_id="LAB-VM-01",
                hostname=self.hostname,
                tailscale_ip=ip,
                is_online=False,
                service_status="STANDBY_AWAITING_PHYSICAL_LAB_BOOT",
                available_models=["qwen2.5-coder:1.5b", "deepseek-r1:1.5b"],
                latency_ms=dur,
                deployment_readiness="DEPLOYMENT_SCRIPT_READY_FOR_LAB_DAY",
                last_ping_time=now_str,
            )

        # Record health check in Cryptographic Audit Ledger
        self.audit.record_action(
            agent_id="lab_vm_sentinel",
            action="LAB_VM_HEALTH_PROBED",
            input_payload={"node_id": status.node_id, "ip": ip},
            output_payload=asdict(status),
            status="SUCCESS",
            metadata={"latency_ms": dur},
        )

        return status
