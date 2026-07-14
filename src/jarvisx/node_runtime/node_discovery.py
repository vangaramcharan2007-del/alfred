import logging
import time

logger = logging.getLogger("NodeDiscovery")

class NodeDiscoveryService:
    """
    Discovers nearby nodes, advertises capabilities, registers mesh members,
    and removes stale members based on metadata.
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.known_peers = {}

    def advertise_presence(self):
        logger.debug(f"Advertising presence for {self.node_id}")
        return {
            "node_id": self.node_id,
            "device_type": "laptop",
            "capabilities": ["compute", "storage", "llm_inference"],
            "health_state": "HEALTHY",
            "trust_level": 1.0,
            "timestamp": time.time()
        }

    def register_peer(self, peer_metadata: dict):
        peer_id = peer_metadata.get("node_id")
        if peer_id and peer_id != self.node_id:
            self.known_peers[peer_id] = peer_metadata
            logger.info(f"Registered peer: {peer_id}")

    def get_active_peers(self) -> list:
        # In a real implementation, this would filter by timestamp
        return list(self.known_peers.keys())
