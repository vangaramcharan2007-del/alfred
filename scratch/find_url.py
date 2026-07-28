import sqlite3
import shutil
import os

def get_nptel_url():
    history_path = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\History")
    temp_path = "temp_history.db"
    
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
    c.execute("SELECT url FROM urls WHERE url LIKE '%nptel.ac.in/noc%' AND url LIKE '%assessment%' ORDER BY last_visit_time DESC LIMIT 1")
    row = c.fetchone()
    
    if row:
        print("[FOUND_URL]: " + row[0])
    else:
        # try a broader search
        c.execute("SELECT url FROM urls WHERE url LIKE '%nptel.ac.in/%' ORDER BY last_visit_time DESC LIMIT 10")
        rows = c.fetchall()
        for r in rows:
            print("[RECENT_URL]: " + r[0])
            
    conn.close()
    os.remove(temp_path)

if __name__ == "__main__":
    get_nptel_url()
