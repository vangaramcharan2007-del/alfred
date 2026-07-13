import asyncio
import httpx
import sqlite3
import os
import logging
import json

class WebhookSentinel:
    def __init__(self, db_path="E:\\Jarvis\\cache.db"):
        self.db_path = db_path if os.path.exists("E:\\Jarvis") else "cache.db"
        self._init_db()

    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS webhook_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    payload TEXT,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            conn.commit()
            conn.close()
        except Exception:
            pass

    async def send_webhook(self, url: str, payload: dict):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=2.0)
                response.raise_for_status()
        except Exception as e:
            logging.error(f"Webhook failed: {e}. Queueing offline.")
            self._queue_offline(url, payload)

    def _queue_offline(self, url: str, payload: dict):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("INSERT INTO webhook_queue (url, payload) VALUES (?, ?)", (url, json.dumps(payload)))
            conn.commit()
            conn.close()
        except Exception:
            pass
