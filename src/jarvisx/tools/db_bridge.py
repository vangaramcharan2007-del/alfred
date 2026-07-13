import asyncio
import sqlite3
import time
import logging

class DBBridge:
    def __init__(self, local_db_path="E:\\Jarvis\\cache.db", supabase_client=None):
        self.local_db_path = local_db_path
        self.supabase = supabase_client
        self.running = False

    def _get_conn(self):
        return sqlite3.connect(self.local_db_path, check_same_thread=False)

    async def start(self, interval=60):
        self.running = True
        while self.running:
            await self._sync_loop()
            await asyncio.sleep(interval)

    def stop(self):
        self.running = False

    async def _sync_loop(self):
        if not self.supabase:
            return

        conn = None
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Ensure the column exists safely
            try:
                cursor.execute('ALTER TABLE l1_responses ADD COLUMN synced INTEGER DEFAULT 0')
                conn.commit()
            except sqlite3.OperationalError:
                pass # Column exists
            
            # Fetch un-synced rows
            cursor.execute('''
                SELECT rowid, query, response, timestamp 
                FROM l1_responses 
                WHERE synced = 0
            ''')
            rows = cursor.fetchall()
            
            if not rows:
                return

            for rowid, query, response, timestamp in rows:
                retries = 0
                synced = False
                
                # Exponential backoff retry loop
                while retries < 3 and not synced:
                    try:
                        # Upsert operation to Supabase
                        data = {
                            "query": query,
                            "response": response,
                            "timestamp": timestamp
                        }
                        
                        # Note: supabase-python uses .execute()
                        res = self.supabase.table('telemetry_logs').upsert(data, on_conflict="query").execute()
                        
                        if res:
                            synced = True
                            # Mark as synced locally
                            cursor.execute('UPDATE l1_responses SET synced = 1 WHERE rowid = ?', (rowid,))
                            conn.commit()
                            
                    except Exception as e:
                        retries += 1
                        logging.warning(f"Supabase sync failed (attempt {retries}/3): {e}")
                        await asyncio.sleep(2 ** retries)
                        
        except Exception as e:
            logging.error(f"DB Bridge local access error: {e}")
        finally:
            if conn:
                conn.close()
