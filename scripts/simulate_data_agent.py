import asyncio
import os
from jarvisx.tools.db_manager import DatabaseManager
from jarvisx.core.message_bus import EventBus

async def main():
    db = DatabaseManager()
    await db.execute_query('''CREATE TABLE IF NOT EXISTS agent_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, filepath TEXT)''')
    await db.execute_query("INSERT INTO agent_logs (action, filepath) VALUES (?, ?)", 
                           ("Generated ML Pipeline Template", "src/jarvisx/exports/ml_pipeline_template.py"))
    
    bus = EventBus()
    await bus.publish("agent_completed", {"role": "Data_Agent", "result": "ML Pipeline Template Generated"})
    print("Data Agent simulation complete.")

if __name__ == "__main__":
    asyncio.run(main())
