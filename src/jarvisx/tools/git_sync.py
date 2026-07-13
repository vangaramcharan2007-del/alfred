import subprocess
import os
import time

class GitSyncAgent:
    def __init__(self, repo_dir: str = "C:\\Users\\vanga\\src\\jarvisx"):
        self.repo_dir = repo_dir

    def run_sync(self):
        if not os.path.exists(self.repo_dir):
            return {"status": "error", "message": f"Repo dir {self.repo_dir} not found."}
            
        try:
            # 1. Fetch
            subprocess.run(["git", "fetch"], cwd=self.repo_dir, check=True, capture_output=True)
            
            # 2. Check status against remote
            status_output = subprocess.run(
                ["git", "status", "-uno"], 
                cwd=self.repo_dir, 
                check=True, 
                capture_output=True, 
                text=True
            ).stdout
            
            if "Your branch is behind" in status_output:
                return {"status": "warning", "message": "Local branch is behind. Aborting sync."}
                
            # 3. Check for local changes
            changes = subprocess.run(["git", "status", "--porcelain"], cwd=self.repo_dir, check=True, capture_output=True, text=True).stdout
            if not changes.strip():
                return {"status": "ok", "message": "No local changes to commit."}
                
            # 4. Add, Commit, Push
            subprocess.run(["git", "add", "."], cwd=self.repo_dir, check=True)
            subprocess.run(["git", "commit", "-m", "Auto-sync"], cwd=self.repo_dir, check=True)
            subprocess.run(["git", "push"], cwd=self.repo_dir, check=True)
            
            return {"status": "success", "message": "Git sync completed successfully."}
            
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": f"Git command failed: {e.stderr.decode() if e.stderr else str(e)}"}
