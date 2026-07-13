import time
import requests
import json
import concurrent.futures
from uuid import uuid4

BASE_URL = "http://localhost:8765"

WORKFLOWS = [
    "I need you to write a Python script that calculates fibonacci.",
    "Show me my current study notes for biology.",
    "Plan my week for the upcoming project deadline.",
    "Remind me to call John tomorrow at 5 PM.",
    "Draft a 3D model specification for a custom mechanical keyboard case.",
    "Automate my email sorting for invoices."
]

def send_chat(message: str) -> dict:
    start_time = time.time()
    try:
        resp = requests.post(
            f"{BASE_URL}/chat",
            json={"message": message, "trace_id": uuid4().hex},
            timeout=30
        )
        latency = time.time() - start_time
        return {"success": resp.status_code == 200, "latency": latency, "status": resp.status_code}
    except Exception as e:
        return {"success": False, "latency": time.time() - start_time, "error": str(e)}

def run_simulation(concurrent_users: int = 5, requests_per_user: int = 4):
    print(f"Starting Daily Driver Simulation: {concurrent_users} users, {requests_per_user} requests each")
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = []
        for _ in range(concurrent_users):
            for _ in range(requests_per_user):
                import random
                msg = random.choice(WORKFLOWS)
                futures.append(executor.submit(send_chat, msg))
                
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            
    success_count = sum(1 for r in results if r.get("success"))
    total_time = sum(r["latency"] for r in results)
    avg_latency = total_time / len(results) if results else 0
    
    print("\n--- Simulation Results ---")
    print(f"Total Requests: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    print(f"Average Latency: {avg_latency:.2f}s")
    
    if success_count == len(results):
        print("✓ All workflows executed successfully.")
    else:
        print("! Some workflows failed.")

if __name__ == "__main__":
    run_simulation()
