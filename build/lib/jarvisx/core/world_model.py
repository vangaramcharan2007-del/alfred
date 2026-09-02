from __future__ import annotations

from typing import Dict, Any, List, Optional
import json
from contextlib import closing

from jarvisx.tools.operational_db import OperationalDatabase


class WorldModel:
    """
    Maintains a structured understanding of projects, goals, deadlines, schedules,
    active missions, dependencies, and unfinished work.
    Persists state to the OperationalDatabase.
    """
    
    def __init__(self, op_db: OperationalDatabase):
        self.op_db = op_db
        
        # Initialize tables if needed
        self._init_db()

    def _init_db(self) -> None:
        with closing(self.op_db._get_connection()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS world_model (
                    entity_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def save_entity(self, entity_id: str, entity_type: str, data: Dict[str, Any]) -> bool:
        """Saves an entity (project, goal, deadline, etc.) to the world model."""
        try:
            with closing(self.op_db._get_connection()) as conn:
                conn.execute(
                    """
                    INSERT INTO world_model (entity_id, entity_type, data, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(entity_id) DO UPDATE SET
                        data = excluded.data,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (entity_id, entity_type, json.dumps(data))
                )
                conn.commit()
            return True
        except Exception:
            return False

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        with closing(self.op_db._get_connection()) as conn:
            cursor = conn.execute("SELECT data FROM world_model WHERE entity_id = ?", (entity_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None

    def get_entities_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        entities = []
        with closing(self.op_db._get_connection()) as conn:
            cursor = conn.execute("SELECT data FROM world_model WHERE entity_type = ?", (entity_type,))
            for row in cursor.fetchall():
                entities.append(json.loads(row[0]))
        return entities

    def delete_entity(self, entity_id: str) -> bool:
        try:
            with closing(self.op_db._get_connection()) as conn:
                conn.execute("DELETE FROM world_model WHERE entity_id = ?", (entity_id,))
                conn.commit()
            return True
        except Exception:
            return False

    def get_world_summary(self) -> Dict[str, Any]:
        """Provides a high-level summary of the world state for Mission Control."""
        return {
            "projects": len(self.get_entities_by_type("project")),
            "goals": len(self.get_entities_by_type("goal")),
            "deadlines": len(self.get_entities_by_type("deadline")),
            "schedules": len(self.get_entities_by_type("schedule"))
        }
