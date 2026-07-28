from typing import Dict, List, Optional
import hashlib
import secrets

from jarvisx.core.logging import StructuredLogger

class NodeAuthenticator:
    """
    Manages node authentication and authorization.
    Prevents unauthorized machines from joining the mesh or executing tasks.
    """
    def __init__(self, logger: Optional[StructuredLogger] = None):
        self.logger = logger or StructuredLogger()
        # In a real system, these would be loaded from a secure vault or config
        self._authorized_nodes: Dict[str, Dict[str, object]] = {}
        self._revoked_nodes: set[str] = set()

    def register_trusted_node(self, node_id: str, secret_key: str, permission_level: str = "standard", allowed_capabilities: Optional[List[str]] = None) -> None:
        """Admin function to pre-register a node's credentials and permissions."""
        hashed_key = hashlib.sha256(secret_key.encode()).hexdigest()
        self._authorized_nodes[node_id] = {
            "key_hash": hashed_key,
            "permission_level": permission_level,
            "allowed_capabilities": allowed_capabilities or []
        }
        self.logger.write("info", "auth.node_registered", node=node_id)

    def authenticate_node(self, node_id: str, provided_key: str) -> bool:
        """Validates a node's credentials during connection."""
        if node_id in self._revoked_nodes:
            self.logger.write("warning", "auth.rejected_revoked_node", node=node_id)
            return False
            
        if node_id not in self._authorized_nodes:
            self.logger.write("warning", "auth.rejected_unknown_node", node=node_id)
            return False
            
        stored_hash = self._authorized_nodes[node_id]["key_hash"]
        provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
        
        # Prevent timing attacks
        if secrets.compare_digest(stored_hash, provided_hash): # type: ignore
            return True
            
        self.logger.write("warning", "auth.rejected_invalid_key", node=node_id)
        return False

    def authorize_task(self, node_id: str, required_capabilities: List[str]) -> bool:
        """Checks if an authenticated node has permission to execute specific capabilities."""
        if node_id not in self._authorized_nodes or node_id in self._revoked_nodes:
            return False
            
        node_info = self._authorized_nodes[node_id]
        if node_info["permission_level"] == "admin":
            return True # Admins can run anything
            
        allowed = node_info.get("allowed_capabilities", [])
        if not allowed:
            return True # If no specific restrictions, assume allowed (open mesh model)
            
        # If restrictions exist, all required capabilities must be allowed
        for cap in required_capabilities:
            if cap not in allowed: # type: ignore
                self.logger.write("warning", "auth.unauthorized_capability", node=node_id, capability=cap)
                return False
        return True

    def revoke_node(self, node_id: str) -> None:
        """Permanently ban a node from the mesh."""
        self._revoked_nodes.add(node_id)
        if node_id in self._authorized_nodes:
            del self._authorized_nodes[node_id]
        self.logger.write("info", "auth.node_revoked", node=node_id)
