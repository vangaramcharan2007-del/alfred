import asyncio
import logging
import datetime
import threading

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("WARNING: 'requests' module not installed. Running in Mock Mode.")

from jarvisx.tools.db_manager import DatabaseManager

class IoTBridge:
    def __init__(self):
        self.webhook_url = "http://localhost:5678/webhook/biometric_trigger"
        self.db = DatabaseManager()

    def _fire_webhook(self, identity: str):
        payload = {
            "identity": identity,
            "timestamp": datetime.datetime.now().isoformat(),
            "action": "trigger_environmental_setup"
        }
        logging.info(f"IoT Bridge preparing webhook for identity: {identity}")
        
        if REQUESTS_AVAILABLE:
            try:
                # Setting tight timeout to prevent blocking the vision loop
                response = requests.post(self.webhook_url, json=payload, timeout=2.0)
                if response.status_code in [200, 201]:
                    logging.info(f"Webhook delivered successfully: {response.status_code}")
                else:
                    logging.warning(f"Webhook returned status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                logging.warning(f"Webhook delivery failed (graceful degradation): {e}")
        else:
            logging.info(f"[MOCK] Webhook fired to {self.webhook_url} with payload {payload}")

    def trigger_environmental_setup(self, identity: str):
        """
        Non-blocking callback handler to be invoked by the vision_matrix.
        """
        if identity.upper() in ["DAD", "VINNU"]:
            # Fire in a separate thread so vision matrix isn't blocked by networking IO
            threading.Thread(target=self._fire_webhook, args=(identity,), daemon=True).start()
        else:
            logging.info(f"Identity '{identity}' not authorized for environmental triggers.")

    async def telemetry_log(self):
        try:
            await self.db.execute_query('''CREATE TABLE IF NOT EXISTS agent_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, filepath TEXT)''')
            await self.db.execute_query("INSERT INTO agent_logs (action, filepath) VALUES (?, ?)", 
                                   ("Ambient Intelligence Bridge Active", "src/jarvisx/tools/iot_bridge.py"))
            logging.info("Telemetry logged successfully.")
        except Exception as e:
            logging.warning(f"Telemetry logging degraded gracefully: {e}")

async def self_test():
    bridge = IoTBridge()
    logging.info("Running IoT Bridge verification...")
    # Simulate a callback from vision_matrix
    bridge.trigger_environmental_setup("VINNU")
    
    # Wait briefly to let the detached thread execute
    await asyncio.sleep(1.0)
    await bridge.telemetry_log()
    print("IoT Bridge simulation complete.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(self_test())
