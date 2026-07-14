import asyncio
import os
from jarvisx.tools.db_manager import DatabaseManager
from jarvisx.core.message_bus import EventBus

async def main():
    db = DatabaseManager()
    await db.execute_query('''CREATE TABLE IF NOT EXISTS agent_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, filepath TEXT)''')
    await db.execute_query("INSERT INTO agent_logs (action, filepath) VALUES (?, ?)", 
                           ("NLP Sentiment Engine Generated", "src/jarvisx/exports/nlp_sentiment_analyzer.py"))
    
    bus = EventBus()
    await bus.publish("agent_completed", {"role": "NLP_Agent", "result": "NLP Engine Deployed"})
    print("NLP Agent simulation complete.")

if __name__ == "__main__":
    asyncio.run(main())
