import sqlite3
import logging
import uuid
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class InitiativeStore:
    """
    Persistent storage for initiative tracking: risks, opportunities, anomalies, and scheduled actions.
    Uses SQLite WAL mode.
    """
    def __init__(self, db_path="var/initiative.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS observations (
                id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS recommendations (
                id TEXT PRIMARY KEY,
                observation_id TEXT,
                proposal TEXT NOT NULL,
                priority TEXT DEFAULT 'normal',
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(observation_id) REFERENCES observations(id)
            );
            
            CREATE TABLE IF NOT EXISTS scheduled_actions (
                id TEXT PRIMARY KEY,
                recommendation_id TEXT,
                action_payload TEXT NOT NULL,
                execution_time DATETIME,
                status TEXT DEFAULT 'scheduled',
                FOREIGN KEY(recommendation_id) REFERENCES recommendations(id)
            );
            
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                recommendation_id TEXT,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(recommendation_id) REFERENCES recommendations(id)
            );
        ''')
        self.conn.commit()

    def log_observation(self, category: str, details: dict) -> str:
        obs_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO observations (id, category, details) VALUES (?, ?, ?)",
            (obs_id, category, json.dumps(details))
        )
        self.conn.commit()
        return obs_id

    def add_recommendation(self, observation_id: str, proposal: str, priority: str = "normal") -> str:
        rec_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO recommendations (id, observation_id, proposal, priority) VALUES (?, ?, ?, ?)",
            (rec_id, observation_id, proposal, priority)
        )
        self.conn.commit()
        return rec_id
        
    def get_pending_recommendations(self) -> list:
        cursor = self.conn.execute("SELECT * FROM recommendations WHERE status = 'pending' ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
