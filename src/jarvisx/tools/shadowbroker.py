import os
import urllib.request

class ShadowBrokerIngestor:
    def __init__(self, sandbox_dir: str = "C:\\Users\\vanga\\Documents\\Codex\\2026-07-11\\files-mentioned-by-the-user-you\\outputs\\project-jarvis-x\\src\\jarvisx\\sandbox"):
        self.sandbox_dir = sandbox_dir
        
    def ingest_script(self, raw_github_url: str, filename: str):
        os.makedirs(self.sandbox_dir, exist_ok=True)
        target_path = os.path.join(self.sandbox_dir, filename)
        
        try:
            with urllib.request.urlopen(raw_github_url) as response:
                content = response.read()
                
            with open(target_path, "wb") as f:
                f.write(content)
                
            return {"status": "success", "path": target_path}
        except Exception as e:
            return {"status": "error", "message": str(e)}
