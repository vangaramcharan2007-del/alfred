import asyncio
import time
import urllib.request
import urllib.error
import json
import logging

logging.basicConfig(level=logging.INFO)

from jarvisx.tools.n8n_webhook_listener import WebhookListenerNode, FLASK_AVAILABLE

async def main():
    listener = WebhookListenerNode(port=5000)
    
    print("Starting Webhook Listener in background...")
    listener.run_in_background()
    
    # Wait for server to boot
    time.sleep(2)
    
    print("Simulating n8n POST request...")
    if FLASK_AVAILABLE:
        url = "http://127.0.0.1:5000/api/jarvis/execute"
        data = json.dumps({"task": "query RAG for DFS algorithm"}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                print(f"Webhook Response: {result}")
        except urllib.error.URLError as e:
            print(f"Failed to hit webhook endpoint: {e}")
    else:
        print("[MOCK] Simulated POST request successful. Output: {'status': 'success'}")
        
    print("Executing telemetry logging...")
    await listener.telemetry_log()
    print("Network Architect Worker simulation complete.")

if __name__ == "__main__":
    asyncio.run(main())
