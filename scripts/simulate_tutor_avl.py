import asyncio
import os
from jarvisx.tools.db_manager import DatabaseManager
from jarvisx.core.message_bus import EventBus

async def main():
    db = DatabaseManager()
    await db.execute_query('''CREATE TABLE IF NOT EXISTS study_telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, status TEXT, timestamp REAL)''')
    await db.execute_query("INSERT INTO study_telemetry (topic, status, timestamp) VALUES (?, ?, ?)", 
                           ("AVL Trees", "MASTERED", 0.0))
    
    bus = EventBus()
    await bus.publish("tutor_completed", {"topic": "AVL Trees", "status": "MASTERED"})
    print("TutorAgent simulation complete for AVL Trees.")

if __name__ == "__main__":
    asyncio.run(main())
