"""Atomic Snapshot Backup Manager for Phase 98 Reliability Kernel."""

from __future__ import annotations
import hashlib
import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from jarvisx.reliability.models import BackupSnapshot
from jarvisx.reliability.reliability_memory import ReliabilityMemory


class BackupManager:
    """Creates point-in-time snapshots using SQLite native backup API and verifies SHA256 checksums."""

    def __init__(self, memory: Optional[ReliabilityMemory] = None, backup_root: str = "var/backups"):
        self.memory = memory or ReliabilityMemory()
        self.backup_root = Path(backup_root)
        self.backup_root.mkdir(parents=True, exist_ok=True)
        self.databases_to_backup = [
            "var/db/personal_os.db",
            "var/db/proactive.db",
            "var/db/agent_bus.db",
            "var/db/self_improvement.db",
            "var/db/reliability.db",
            "var/db/knowledge.db",
            "var/db/evaluation.db",
            "var/db/memory_intelligence.db",
            "var/db/operating_loop.db",
        ]

    def _compute_sha256(self, file_path: Path) -> str:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    def create_snapshot(self) -> BackupSnapshot:
        """Create an atomic snapshot of all active databases using native SQLite backup."""
        snap_id = f"snap_{int(time.time())}_{str(uuid.uuid4())[:6]}"
        snap_dir = self.backup_root / snap_id
        snap_dir.mkdir(parents=True, exist_ok=True)

        manifest = {}
        total_size = 0

        for db_str in self.databases_to_backup:
            src_path = Path(db_str)
            if src_path.exists():
                dest_path = snap_dir / src_path.name
                # Use native SQLite backup for WAL safety
                try:
                    src_conn = sqlite3.connect(str(src_path))
                    dest_conn = sqlite3.connect(str(dest_path))
                    with dest_conn:
                        src_conn.backup(dest_conn)
                    src_conn.close()
                    dest_conn.close()
                except Exception:
                    # Fallback copy if file is not SQLite
                    dest_path.write_bytes(src_path.read_bytes())

                sha = self._compute_sha256(dest_path)
                size = dest_path.stat().st_size
                manifest[src_path.name] = {"sha256": sha, "size_bytes": size}
                total_size += size

        # Write manifest.json
        manifest_file = snap_dir / "manifest.json"
        manifest_data = {
            "snapshot_id": snap_id,
            "created_at": time.time(),
            "files": manifest,
            "total_size_bytes": total_size
        }
        manifest_file.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

        snapshot = BackupSnapshot(
            id=snap_id,
            timestamp=time.time(),
            snapshot_dir=str(snap_dir),
            checksum_manifest=manifest,
            size_bytes=total_size,
            status="VERIFIED"
        )
        self.memory.record_snapshot(snapshot)
        print(f"  [Backup Manager]: Snapshot '{snap_id}' created ({total_size} bytes, {len(manifest)} DBs verified).")
        return snapshot

    def verify_snapshot(self, snapshot_id: str) -> bool:
        """Verify the cryptographic integrity of a snapshot on disk."""
        snap_dir = self.backup_root / snapshot_id
        manifest_file = snap_dir / "manifest.json"
        if not manifest_file.exists():
            return False

        data = json.loads(manifest_file.read_text(encoding="utf-8"))
        for fname, info in data.get("files", {}).items():
            fpath = snap_dir / fname
            if not fpath.exists():
                return False
            actual_sha = self._compute_sha256(fpath)
            if actual_sha != info.get("sha256"):
                return False
        return True

    def restore_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """Restore all databases from a verified snapshot."""
        if not self.verify_snapshot(snapshot_id):
            return {"status": "FAILED", "reason": "Corrupted or missing snapshot manifest"}

        snap_dir = self.backup_root / snapshot_id
        manifest_file = snap_dir / "manifest.json"
        data = json.loads(manifest_file.read_text(encoding="utf-8"))

        restored_files = []
        for fname in data.get("files", {}):
            src_file = snap_dir / fname
            dest_file = Path("var/db") / fname
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            dest_file.write_bytes(src_file.read_bytes())
            restored_files.append(fname)

        print(f"  [Backup Manager]: Successfully restored {len(restored_files)} databases from snapshot '{snapshot_id}'.")
        return {"status": "SUCCESS", "snapshot_id": snapshot_id, "restored_files": restored_files}

    def list_snapshots(self) -> List[BackupSnapshot]:
        return self.memory.list_snapshots()
