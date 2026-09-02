import asyncio
import sqlite3
import os
import logging

class DatabaseManager:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path: str = None):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        if db_path is None:
            self.db_path = "E:\\Jarvis\\cache.db" if os.path.exists("E:\\Jarvis") else "cache.db"
        else:
            self.db_path = db_path
            
        self.conn = None
        self._initialized = True
        self._init_connection()

    def _init_connection(self):
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.execute("PRAGMA busy_timeout=5000;")
        except Exception as e:
            logging.error(f"DatabaseManager init failed: {e}")

    async def execute_query(self, query: str, params: tuple = None) -> list:
        async with self._lock:
            try:
                if self.conn is None:
                    self._init_connection()
                    
                cursor = self.conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                    
                if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP")):
                    self.conn.commit()
                    return []
                else:
                    return cursor.fetchall()
            except Exception as e:
                logging.error(f"Database execution error on '{query}': {e}")
                return []

# Self-test logic
async def self_test():
    db = DatabaseManager("test_cache.db")
    await db.execute_query('''CREATE TABLE IF NOT EXISTS test_writes (id INTEGER PRIMARY KEY AUTOINCREMENT, val TEXT)''')
    
    async def write_task(val):
        await db.execute_query("INSERT INTO test_writes (val) VALUES (?)", (val,))
        
    tasks = [write_task(f"test_val_{i}") for i in range(10)]
    await asyncio.gather(*tasks)
    
    results = await db.execute_query("SELECT COUNT(*) FROM test_writes")
    print(f"Self-test complete. Rows written: {results[0][0] if results else 0}")
    
    # Cleanup test db
    db.conn.close()
    if os.path.exists("test_cache.db"):
        os.remove("test_cache.db")

if __name__ == "__main__":
    asyncio.run(self_test())
