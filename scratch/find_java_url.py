import sqlite3
import shutil
import os
import time

def find_java_url():
    history_path = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\History")
    temp_path = "temp_history2.db"
    
    if not os.path.exists(history_path):
        print("[Error]: Chrome history not found at " + history_path)
        return
        
    try:
        shutil.copy2(history_path, temp_path)
    except Exception as e:
        print("[Error]: Could not copy history: " + str(e))
        return
        
    conn = sqlite3.connect(temp_path)
    c = conn.cursor()
    # Search for NPTEL assignment URLs
    c.execute("SELECT url, title FROM urls WHERE url LIKE '%nptel.ac.in/%' AND (title LIKE '%Java%' OR url LIKE '%assessment%') ORDER BY last_visit_time DESC LIMIT 20")
    rows = c.fetchall()
    
    conn.close()
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    for row in rows:
        print(f"[FOUND]: {row[1]} -> {row[0]}")

if __name__ == "__main__":
    find_java_url()
