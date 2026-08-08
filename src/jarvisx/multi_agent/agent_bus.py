"""Inter-Agent Communication Bus for Phase 96 Multi-Agent Operating System."""

from __future__ import annotations
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from jarvisx.multi_agent.models import AgentMessage, MessageType


class AgentCommunicationBus:
    """Inter-Agent Message Bus providing decoupled pub/sub, point-to-point requests, and message replay."""

    def __init__(self, db_path: str = "var/db/agent_bus.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.subscribers: Dict[str, List[Callable[[AgentMessage], None]]] = {}
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    sender TEXT,
                    recipient TEXT,
                    msg_type TEXT,
                    topic TEXT,
                    payload_json TEXT,
                    timestamp REAL
                )
            """)
            conn.commit()

    def subscribe(self, recipient: str, callback: Callable[[AgentMessage], None]) -> None:
        """Register a subscriber handler for a specific agent role/name or 'BROADCAST'."""
        if recipient not in self.subscribers:
            self.subscribers[recipient] = []
        self.subscribers[recipient].append(callback)

    def publish(self, message: AgentMessage) -> None:
        """Persist message to disk and dispatch to active in-memory subscribers."""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO messages (id, sender, recipient, msg_type, topic, payload_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                message.id,
                message.sender,
                message.recipient,
                message.msg_type.value,
                message.topic,
                json.dumps(message.payload),
                message.timestamp,
            ))
            conn.commit()

        # Dispatch to specific recipient
        if message.recipient in self.subscribers:
            for cb in self.subscribers[message.recipient]:
                try:
                    cb(message)
                except Exception as e:
                    print(f"[Agent Bus Error]: Failed to dispatch to {message.recipient}: {e}")

        # Dispatch to broadcast subscribers
        if message.recipient == "ALL" and "ALL" in self.subscribers:
            for cb in self.subscribers["ALL"]:
                try:
                    cb(message)
                except Exception:
                    pass

    def get_messages(self, limit: int = 50) -> List[AgentMessage]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, sender, recipient, msg_type, topic, payload_json, timestamp FROM messages ORDER BY timestamp ASC LIMIT ?", (limit,))
            return [
                AgentMessage(
                    id=r[0],
                    sender=r[1],
                    recipient=r[2],
                    msg_type=MessageType(r[3]),
                    topic=r[4],
                    payload=json.loads(r[5]),
                    timestamp=r[6],
                )
                for r in cur.fetchall()
            ]

    def replay_messages(self) -> int:
        """Replay all stored bus messages to verify state continuity after restart."""
        msgs = self.get_messages(100)
        for m in msgs:
            if m.recipient in self.subscribers:
                for cb in self.subscribers[m.recipient]:
                    cb(m)
        return len(msgs)
