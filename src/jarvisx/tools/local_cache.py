import sqlite3
import time
import threading

class LocalL1Cache:
    def __init__(self, db_path: str = "E:\\Jarvis\\cache.db", expiration_minutes: int = 5):
        self.db_path = db_path
        self.expiration_seconds = expiration_minutes * 60
        self.local = threading.local()
        self._init_db()

    def _get_conn(self):
        if not hasattr(self.local, "conn"):
            # check_same_thread=False allows sharing but using threading.local() is safer
            self.local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self.local.conn

    def _init_db(self):
        try:
            conn = self._get_conn()
            conn.execute('''
                CREATE TABLE IF NOT EXISTS l1_responses (
                    query TEXT PRIMARY KEY,
                    response TEXT,
                    timestamp REAL
                )
            ''')
            conn.commit()
        except Exception:
            pass # Fallback for E: drive missing

    def get_cached_response(self, query: str) -> str | None:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT response, timestamp FROM l1_responses WHERE query = ?", (query,))
            row = cursor.fetchone()
            
            if row:
                response, timestamp = row
                if time.time() - timestamp < self.expiration_seconds:
                    return response
                else:
                    # Expired
                    cursor.execute("DELETE FROM l1_responses WHERE query = ?", (query,))
                    conn.commit()
            return None
        except Exception:
            return None

    def insert_response(self, query: str, response: str):
        try:
            conn = self._get_conn()
            conn.execute('''
                INSERT OR REPLACE INTO l1_responses (query, response, timestamp)
                VALUES (?, ?, ?)
            ''', (query, response, time.time()))
            conn.commit()
        except Exception:
            pass
