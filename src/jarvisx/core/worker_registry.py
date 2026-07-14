import logging
import time
from typing import Dict

class WorkerRegistry:
    """Maintains a registry of available distributed nodes and their capabilities."""
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        
    def register_node(self, node_id: str, capabilities: list):
        self.nodes[node_id] = {
            'capabilities': capabilities,
            'last_seen': time.time(),
            'status': 'ONLINE'
        }
        logging.info(f"[Registry] Node registered: {node_id} with {capabilities}")
        
    def get_online_nodes(self):
        return {k: v for k, v in self.nodes.items() if v['status'] == 'ONLINE'}
