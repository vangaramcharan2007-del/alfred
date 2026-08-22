import sys
import time
import requests

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

API_URL = "http://localhost:8000/ingest-telemetry"


def run_simulation():
    print("🚀 Starting AEGIS Telemetry Simulator...")
    
    for i in range(1, 6):
        payload = {"heart_rate": 72, "temperature": 36.8}
        print(f"[Normal Baseline] Sending: {payload}")
        try:
            res = requests.post(API_URL, json=payload)
            print(f"  -> Response: {res.status_code} {res.json()}")
        except Exception as e:
            print(f"  -> Error sending payload: {e}")
        time.sleep(2)
        
    print("\n⚠️ INJECTING CRITICAL ANOMALY ⚠️")
    payload = {"heart_rate": 135, "temperature": 39.5}
    print(f"[Critical Event] Sending: {payload}")
    try:
        res = requests.post(API_URL, json=payload)
        print(f"  -> Response: {res.status_code} {res.json()}")
    except Exception as e:
        print(f"  -> Error sending payload: {e}")
    
if __name__ == "__main__":
    run_simulation()
