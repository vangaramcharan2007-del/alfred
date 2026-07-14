import asyncio
import os
from src.jarvisx.tools.db_manager import DatabaseManager
from src.jarvisx.core.message_bus import EventBus

async def main():
    db = DatabaseManager()
    await db.execute_query('''CREATE TABLE IF NOT EXISTS agent_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, filepath TEXT)''')
    await db.execute_query("INSERT INTO agent_logs (action, filepath) VALUES (?, ?)", 
                           ("Generated OOP Reference", "src/jarvisx/exports/oop_reference.cpp"))
    
    bus = EventBus()
    await bus.publish("agent_completed", {"role": "Dev_Agent", "result": "C++ OOP Matrix Generated"})
    print("Agent simulation complete.")

if __name__ == "__main__":
    asyncio.run(main())
