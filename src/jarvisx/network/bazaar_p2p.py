"""
The Bazaar — Distributed P2P Agent Economy.
Allows local Jarvis instances to discover each other over a network, 
broadcast tasks, and bid on compute loads using synthetic tokens.
"""
import logging
import random
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class BazaarP2PNode:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.node_id = f"jarvis_node_{random.randint(1000, 9999)}"
        self.balance = 1000.0 # Synthetic compute tokens

    def _discover_peers(self) -> List[str]:
        """Simulate UDP multicast discovery of other Jarvis nodes."""
        return [f"jarvis_node_{random.randint(1000,9999)}" for _ in range(3)]

    def broadcast_task(self, task_description: str, compute_bounty: float) -> Dict[str, Any]:
        """Broadcast a task to the P2P swarm to outsource work."""
        logger.info(f"[Bazaar] Broadcasting task: '{task_description}' for {compute_bounty} tokens...")
        
        if self.balance < compute_bounty:
            return {"status": "error", "error": "Insufficient compute tokens."}
            
        peers = self._discover_peers()
        logger.info(f"[Bazaar] Found {len(peers)} peers on local subnet. Negotiating bids...")
        
        time.sleep(1) # Simulate network negotation
        
        winning_node = random.choice(peers)
        logger.info(f"[Bazaar] Node {winning_node} accepted the bounty. Offloading task...")
        
        # Deduct balance
        self.balance -= compute_bounty
        
        logger.info(f"[Bazaar] Task complete via {winning_node}. Remaining Balance: {self.balance:.2f} tokens.")
        
        return {
            "status": "success",
            "task": task_description,
            "executor_node": winning_node,
            "cost": compute_bounty,
            "remaining_balance": self.balance
        }
