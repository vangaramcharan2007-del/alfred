"""Metrics tracker for the Jarvis X Developer Console."""
import time
import threading
from typing import Optional
from contextlib import closing
import sqlite3
import traceback

from jarvisx.tools.dev_console.state import ConsoleState
from jarvisx.core.execution.persistent_queue import PersistentQueue

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class ConsoleMetrics:
    """Periodically updates performance and resource metrics in ConsoleState."""
    
    def __init__(self, state: ConsoleState, queue: PersistentQueue, scheduler=None):
        self.state = state
        self.queue = queue
        self.scheduler = scheduler
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._metrics_loop, daemon=True)
        self._thread.start()
        
    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            
    def _metrics_loop(self):
        while self._running:
            self._update_system_metrics()
            self._update_queue_metrics()
            self._update_timing_metrics()
            self._update_scheduler_metrics()
            time.sleep(1.0)
            
    def _update_scheduler_metrics(self):
        if self.scheduler and hasattr(self.scheduler, "_scheduled"):
            with self.state.lock:
                self.state.scheduler_queue = len(self.scheduler._scheduled)
                
    def _update_system_metrics(self):
        if not PSUTIL_AVAILABLE:
            return
            
        with self.state.lock:
            try:
                self.state.cpu_percent = psutil.cpu_percent()
                self.state.ram_percent = psutil.virtual_memory().percent
                self.state.thread_count = threading.active_count()
                
                # Count threads whose name includes "BackgroundWorker"
                self.state.worker_threads = sum(
                    1 for t in threading.enumerate() 
                    if "BackgroundWorker" in t.name or "Worker" in t.name
                )
            except Exception:
                pass

    def _update_queue_metrics(self):
        # Update queue size and DB latency
        try:
            start_time = time.perf_counter()
            with closing(sqlite3.connect(self.queue.db_path)) as conn, conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM objectives WHERE status = 'QUEUED'")
                row = cursor.fetchone()
                if row:
                    with self.state.lock:
                        self.state.queue_size = row[0]
            
            # Simple measure of SQLite latency for a basic query
            latency = (time.perf_counter() - start_time) * 1000.0
            with self.state.lock:
                self.state.sqlite_latency = latency
                self.state.db_status = "CONNECTED"
        except Exception:
            with self.state.lock:
                self.state.db_status = "ERROR"

    def _update_timing_metrics(self):
        with self.state.lock:
            if self.state.start_time and self.state.objective_status == "RUNNING":
                self.state.elapsed_time = time.time() - self.state.start_time
