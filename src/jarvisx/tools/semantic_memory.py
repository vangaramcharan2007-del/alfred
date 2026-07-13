import asyncio
import aiofiles
import os
import sqlite3
import math
import time
from typing import List, Tuple

class SemanticMemory:
    def __init__(self, db_path="E:\\Jarvis\\cache.db", root_dir="C:\\Users\\vanga\\Documents\\Codex\\2026-07-11\\files-mentioned-by-the-user-you\\outputs\\project-jarvis-x"):
        self.db_path = db_path if os.path.exists("E:\\Jarvis") else "cache.db"
        self.root_dir = root_dir
        self._init_db()

    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS semantic_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT,
                    chunk_text TEXT,
                    token_count INTEGER,
                    timestamp REAL
                )
            ''')
            conn.commit()
            conn.close()
        except Exception:
            pass

    async def _read_file_chunks(self, filepath: str, chunk_size: int = 500) -> List[str]:
        chunks = []
        try:
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                content = await f.read()
                words = content.split()
                for i in range(0, len(words), chunk_size):
                    chunks.append(" ".join(words[i:i + chunk_size]))
        except Exception:
            pass
        return chunks

    async def index_directory(self, target_dir: str):
        tasks = []
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    tasks.append(self._process_and_store(filepath))
        await asyncio.gather(*tasks)

    async def _process_and_store(self, filepath: str):
        chunks = await self._read_file_chunks(filepath)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            for chunk in chunks:
                cursor.execute(
                    "INSERT INTO semantic_index (filepath, chunk_text, token_count, timestamp) VALUES (?, ?, ?, ?)",
                    (filepath, chunk, len(chunk.split()), time.time())
                )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def _cosine_similarity(self, vec1: dict, vec2: dict) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        sum1 = sum([val**2 for val in vec1.values()])
        sum2 = sum([val**2 for val in vec2.values()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        return float(numerator) / denominator

    def _text_to_vector(self, text: str) -> dict:
        words = text.lower().split()
        return {word: words.count(word) for word in set(words)}

    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, str, float]]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT filepath, chunk_text FROM semantic_index")
            rows = cursor.fetchall()
            conn.close()

            query_vec = self._text_to_vector(query)
            results = []
            
            for filepath, chunk in rows:
                chunk_vec = self._text_to_vector(chunk)
                sim = self._cosine_similarity(query_vec, chunk_vec)
                if sim > 0:
                    results.append((filepath, chunk, sim))

            results.sort(key=lambda x: x[2], reverse=True)
            return results[:top_k]
        except Exception:
            return []
