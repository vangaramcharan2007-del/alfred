import subprocess
import os
import sqlite3

class GitSyncAgent:
    def __init__(self, repo_dir: str = "C:\\Users\\vanga\\Documents\\Codex\\2026-07-11\\files-mentioned-by-the-user-you\\outputs\\project-jarvis-x"):
        self.repo_dir = repo_dir
        self.db_path = "E:\\Jarvis\\cache.db"

    def log_to_sqlite(self, stage: str, error_message: str):
        try:
            # Fallback for E: drive missing, just use local
            db_path = self.db_path if os.path.exists("E:\\Jarvis") else "cache.db"
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS git_errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stage TEXT,
                    error_message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('INSERT INTO git_errors (stage, error_message) VALUES (?, ?)', (stage, error_message))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def execute_secure_push(self, commit_message: str = "Auto-sync") -> dict:
        if not os.path.exists(self.repo_dir):
            return {"status": "error", "message": f"Repo dir {self.repo_dir} not found."}
            
        try:
            # 1. Fetch
            fetch_res = subprocess.run(["git", "fetch"], cwd=self.repo_dir, capture_output=True, text=True)
            if fetch_res.returncode != 0:
                self.log_to_sqlite("fetch", fetch_res.stderr)
                return {"status": "error", "message": f"Fetch failed: {fetch_res.stderr}"}
            
            # 2. Check local changes
            status_res = subprocess.run(["git", "status", "--porcelain"], cwd=self.repo_dir, capture_output=True, text=True)
            if status_res.returncode != 0:
                self.log_to_sqlite("status", status_res.stderr)
                return {"status": "error", "message": "Status failed"}
                
            if not status_res.stdout.strip():
                return {"status": "ok", "message": "No local changes to commit."}
                
            # 3. Add
            add_res = subprocess.run(["git", "add", "."], cwd=self.repo_dir, capture_output=True, text=True)
            if add_res.returncode != 0:
                self.log_to_sqlite("add", add_res.stderr)
                return {"status": "error", "message": "Add failed"}
                
            # 4. Commit
            commit_res = subprocess.run(["git", "commit", "-m", commit_message], cwd=self.repo_dir, capture_output=True, text=True)
            
            # 5. Push
            push_res = subprocess.run(["git", "push"], cwd=self.repo_dir, capture_output=True, text=True)
            if push_res.returncode != 0:
                self.log_to_sqlite("push", push_res.stderr)
                return {"status": "error", "message": "Push failed"}
            
            return {"status": "success", "message": "Git sync completed successfully."}
            
        except Exception as e:
            self.log_to_sqlite("exception", str(e))
            return {"status": "error", "message": str(e)}
