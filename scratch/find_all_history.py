import sqlite3
import shutil
import os
import glob

def find_history():
    profiles = glob.glob(os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Profile *"))
    profiles.append(os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default"))
    
    for profile in profiles:
        history_path = os.path.join(profile, "History")
        if not os.path.exists(history_path):
            continue
            
        temp_path = f"temp_history_{os.path.basename(profile)}.db"
        try:
            shutil.copy2(history_path, temp_path)
            conn = sqlite3.connect(temp_path)
            c = conn.cursor()
            c.execute("SELECT url, title FROM urls WHERE url LIKE '%nptel.ac.in/%' AND (title LIKE '%Java%' OR url LIKE '%assessment%') ORDER BY last_visit_time DESC LIMIT 5")
            rows = c.fetchall()
            conn.close()
            os.remove(temp_path)
            
            if rows:
                print(f"\n--- Found in {os.path.basename(profile)} ---")
                for row in rows:
                    print(f"[FOUND]: {row[1]}\n         {row[0]}")
        except Exception as e:
            print(f"[Error] reading {profile}: {e}")

if __name__ == "__main__":
    find_history()
