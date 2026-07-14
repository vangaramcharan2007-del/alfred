import asyncio
import os
from jarvisx.core.rag_vault import RAGVault
from jarvisx.tools.db_manager import DatabaseManager
from jarvisx.core.message_bus import EventBus

async def main():
    # 1. Self test RAG Vault
    vault = RAGVault(db_path="test_chroma_db")
    dummy_text = "The quick brown fox jumps over the lazy dog. This is a dummy document for testing RAG chunking and semantic search retrieval."
    vault.embed_document("doc_001", dummy_text, metadata={"source": "test"})
    
    results = vault.query_vault("What jumps over the dog?")
    print("RAG Query Results:")
    for i, res in enumerate(results):
        print(f" {i+1}. {res}")
        
    # 2. Telemetry
    db = DatabaseManager()
    await db.execute_query('''CREATE TABLE IF NOT EXISTS agent_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, filepath TEXT)''')
    await db.execute_query("INSERT INTO agent_logs (action, filepath) VALUES (?, ?)", 
                           ("RAG Vault Initialized", "src/jarvisx/core/rag_vault.py"))
    
    bus = EventBus()
    await bus.publish("agent_completed", {"role": "Memory_Architect_Agent", "result": "Local RAG Vault Deployed"})
    print("Memory Agent simulation complete.")

if __name__ == "__main__":
    asyncio.run(main())
