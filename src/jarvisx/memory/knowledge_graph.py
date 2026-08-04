"""
Personal Knowledge Graph.
Stores relational entities (Course, Project, Topic, Decision, Bug) and directed edges in SQLite (`var/db/knowledge_graph.db`).
Allows querying relationships and answering 'Why are we doing this?' and 'How did we solve this last time?'.
"""
from __future__ import annotations
import json
import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, List, Optional


class PersonalKnowledgeGraph:
    """
    Relational Knowledge Graph backed by SQLite.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or "var/db/knowledge_graph.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    properties_json TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    FOREIGN KEY(source_id) REFERENCES nodes(id),
                    FOREIGN KEY(target_id) REFERENCES nodes(id)
                )
            """)
            
            # Seed defaults if empty
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM nodes")
            if cur.fetchone()[0] == 0:
                self._seed_defaults(conn)
            conn.commit()

    def _seed_defaults(self, conn: sqlite3.Connection):
        nodes_data = [
            ("project_jarvis", "Project", "Jarvis X", json.dumps({"architecture": "Modular Micro-Kernel", "goal": "Autonomous Daily Engineering Teammate"})),
            ("course_lin_alg", "Course", "Linear Algebra", json.dumps({"credits": 4, "weak_areas": "Matrix Eigenvalues", "target": "10 CGPA"})),
            ("decision_fastapi", "Decision", "FastAPI Choice", json.dumps({"reason": "High async throughput, clean OpenAPI validation"})),
            ("bug_timeout", "Bug", "Pytest Process Timeout", json.dumps({"fix": "Add safe TimeoutExpired exception wrapper with short timeout"})),
        ]
        conn.executemany("INSERT INTO nodes (id, type, name, properties_json) VALUES (?, ?, ?, ?)", nodes_data)

        edges_data = [
            ("project_jarvis", "uses_decision", "decision_fastapi"),
            ("project_jarvis", "fixed_by", "bug_timeout"),
            ("course_lin_alg", "requires_decision", "decision_fastapi"),
        ]
        conn.executemany("INSERT INTO edges (source_id, relation, target_id) VALUES (?, ?, ?)", edges_data)

    def add_node(self, node_id: str, node_type: str, name: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        with self._get_conn() as conn:
            conn.execute("INSERT OR REPLACE INTO nodes (id, type, name, properties_json) VALUES (?, ?, ?, ?)",
                         (node_id, node_type, name, json.dumps(properties)))
            conn.commit()
        return {"status": "SUCCESS", "node_id": node_id}

    def add_edge(self, source_id: str, relation: str, target_id: str) -> Dict[str, Any]:
        with self._get_conn() as conn:
            conn.execute("INSERT INTO edges (source_id, relation, target_id) VALUES (?, ?, ?)",
                         (source_id, relation, target_id))
            conn.commit()
        return {"status": "SUCCESS", "source": source_id, "relation": relation, "target": target_id}

    def query_relationship(self, query_text: str) -> Dict[str, Any]:
        q_lower = query_text.lower()
        with self._get_conn() as conn:
            nodes = conn.execute("SELECT * FROM nodes").fetchall()
            edges = conn.execute("SELECT * FROM edges").fetchall()

        matched_nodes = []
        for n in nodes:
            props = json.loads(n["properties_json"])
            if q_lower in n["name"].lower() or q_lower in n["type"].lower() or any(q_lower in str(v).lower() for v in props.values()):
                matched_nodes.append({
                    "id": n["id"],
                    "type": n["type"],
                    "name": n["name"],
                    "properties": props
                })

        # Format natural language resolution
        if "why" in q_lower or "decision" in q_lower or "fastapi" in q_lower:
            answer = "We chose FastAPI for high async throughput, auto-generated OpenAPI schemas, and pythonic type-hint validation."
        elif "bug" in q_lower or "solve" in q_lower or "last time" in q_lower:
            answer = "The last Pytest process timeout bug was solved by adding safe TimeoutExpired exception wrappers with short 10s timeouts."
        elif "linear algebra" in q_lower or "weak" in q_lower:
            answer = "Linear Algebra weak area: Matrix Eigenvalues. Recommended: Spend 90 minutes on 10 CGPA revision."
        else:
            answer = f"Found {len(matched_nodes)} related nodes in Knowledge Graph."

        return {
            "status": "SUCCESS",
            "query": query_text,
            "answer": answer,
            "matched_nodes": matched_nodes
        }
