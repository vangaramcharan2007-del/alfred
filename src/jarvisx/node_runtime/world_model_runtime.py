import logging
import time

logger = logging.getLogger("WorldModelRuntime")

class WorldModelRuntime:
    """
    Maintains a live, in-memory graph of the user's environment, devices, and context.
    """
    def __init__(self):
        self.state = {
            "devices": {},
            "user_context": "working",
            "last_updated": time.time()
        }

    def update_device_state(self, node_id: str, telemetry: dict):
        self.state["devices"][node_id] = telemetry
        self.state["last_updated"] = time.time()
        logger.debug(f"WorldModel updated for device {node_id}")

    def get_snapshot(self):
        return self.state
