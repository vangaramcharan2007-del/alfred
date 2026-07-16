import logging
from .learning_store import LearningStore

logger = logging.getLogger(__name__)

class WorkforceAnalytics:
    """
    Evaluates individual and team worker performance over time.
    """
    def __init__(self, store: LearningStore):
        self.store = store

    def record_task_outcome(self, worker_id: str, success: bool, duration_ms: int):
        # Fetch current
        cursor = self.store.conn.execute("SELECT * FROM worker_metrics WHERE worker_id = ?", (worker_id,))
        row = cursor.fetchone()
        
        if row:
            total = row["total_tasks"] + 1
            successes = row["successful_tasks"] + (1 if success else 0)
            failures = row["failed_tasks"] + (1 if not success else 0)
            avg_dur = ((row["average_duration_ms"] * row["total_tasks"]) + duration_ms) // total
            
            self.store.conn.execute(
                "UPDATE worker_metrics SET total_tasks=?, successful_tasks=?, failed_tasks=?, average_duration_ms=? WHERE worker_id=?",
                (total, successes, failures, avg_dur, worker_id)
            )
        else:
            self.store.conn.execute(
                "INSERT INTO worker_metrics (worker_id, total_tasks, successful_tasks, failed_tasks, average_duration_ms) VALUES (?, 1, ?, ?, ?)",
                (worker_id, 1 if success else 0, 1 if not success else 0, duration_ms)
            )
        self.store.conn.commit()

    def get_agent_report(self) -> str:
        cursor = self.store.conn.execute("SELECT * FROM worker_metrics")
        rows = cursor.fetchall()
        
        if not rows:
            return "No workforce data available."
            
        report_lines = []
        for r in rows:
            rate = int((r["successful_tasks"] / r["total_tasks"]) * 100) if r["total_tasks"] > 0 else 0
            report_lines.append(f"{r['worker_id']}:\n{rate}% success rate\n")
            
        return "\n".join(report_lines)
