import os
import shutil
from bs4 import BeautifulSoup
import logging

class UIInjector:
    def __init__(self, index_path="C:\\Users\\vanga\\Documents\\Codex\\2026-07-11\\files-mentioned-by-the-user-you\\outputs\\project-jarvis-x\\src\\jarvisx\\dashboard\\index.html"):
        self.index_path = index_path

    def inject_component(self, target_id: str, html_snippet: str) -> bool:
        if not os.path.exists(self.index_path):
            logging.error(f"UI file {self.index_path} not found.")
            return False

        # Create safety backup
        backup_path = self.index_path + ".bak"
        shutil.copy2(self.index_path, backup_path)

        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "html.parser")
            target_node = soup.find(id=target_id)

            if not target_node:
                logging.error(f"Target node with ID '{target_id}' not found.")
                # Restore backup and return
                shutil.copy2(backup_path, self.index_path)
                return False

            # Create component node
            new_component = BeautifulSoup(html_snippet, "html.parser")
            target_node.append(new_component)

            with open(self.index_path, "w", encoding="utf-8") as f:
                f.write(str(soup))
                
            return True
            
        except Exception as e:
            logging.error(f"Failed to inject UI component: {e}")
            shutil.copy2(backup_path, self.index_path)
            return False
