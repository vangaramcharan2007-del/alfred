"""Resource Lock Manager — prevents concurrent access conflicts across agents using file-based IPC locks."""
import os
import time
import json
import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

LOCKS_DIR = "var/locks"

class ResourceManager:
    """Manages exclusive locks on tools/resources across multiple OS processes."""

    _instance: Optional["ResourceManager"] = None

    def __init__(self):
        os.makedirs(LOCKS_DIR, exist_ok=True)

    @classmethod
    def get_instance(cls) -> "ResourceManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def _get_lock_path(self, resource_name: str) -> str:
        # Sanitize resource name for filesystem
        safe_name = "".join(c if c.isalnum() else "_" for c in resource_name)
        return os.path.join(LOCKS_DIR, f"{safe_name}.lock")

    async def acquire(self, resource_name: str, agent_id: str, timeout: float = 10.0) -> bool:
        """Acquire an exclusive file-based lock on a resource."""
        lock_path = self._get_lock_path(resource_name)
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # O_EXCL ensures this operation is atomic
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                try:
                    data = json.dumps({
                        "agent_id": agent_id,
                        "resource": resource_name,
                        "timestamp": time.time()
                    })
                    os.write(fd, data.encode("utf-8"))
                finally:
                    os.close(fd)
                logger.info(f"Resource '{resource_name}' locked by agent '{agent_id}'")
                return True
            except (FileExistsError, PermissionError):
                await asyncio.sleep(0.1)
                
        logger.warning(f"Agent '{agent_id}' timed out acquiring resource '{resource_name}'")
        return False

    def release(self, resource_name: str, agent_id: str) -> bool:
        """Release a lock. Only the owning agent can release."""
        lock_path = self._get_lock_path(resource_name)
        if not os.path.exists(lock_path):
            return True
            
        try:
            with open(lock_path, "r") as f:
                data = json.load(f)
            if data.get("agent_id") == agent_id:
                os.remove(lock_path)
                logger.info(f"Resource '{resource_name}' released by agent '{agent_id}'")
                return True
            else:
                logger.warning(f"Agent '{agent_id}' cannot release '{resource_name}' — not the owner")
                return False
        except (json.JSONDecodeError, FileNotFoundError):
            # If the file is corrupted or gone, assume it's released or we can delete it
            try:
                os.remove(lock_path)
            except FileNotFoundError:
                pass
            return True

    def is_locked(self, resource_name: str) -> bool:
        return os.path.exists(self._get_lock_path(resource_name))

    def get_owner(self, resource_name: str) -> Optional[str]:
        lock_path = self._get_lock_path(resource_name)
        try:
            with open(lock_path, "r") as f:
                data = json.load(f)
                return data.get("agent_id")
        except Exception:
            return None

    def get_locked_resources(self) -> Dict[str, str]:
        if not os.path.exists(LOCKS_DIR):
            return {}
        resources = {}
        for filename in os.listdir(LOCKS_DIR):
            if filename.endswith(".lock"):
                try:
                    with open(os.path.join(LOCKS_DIR, filename), "r") as f:
                        data = json.load(f)
                        if "resource" in data and "agent_id" in data:
                            resources[data["resource"]] = data["agent_id"]
                except Exception:
                    pass
        return resources

    def force_release_all(self, agent_id: str):
        """Release all resources held by an agent (used during failure recovery)."""
        resources = self.get_locked_resources()
        count = 0
        for resource, owner in resources.items():
            if owner == agent_id:
                try:
                    os.remove(self._get_lock_path(resource))
                    count += 1
                except FileNotFoundError:
                    pass
        if count > 0:
            logger.info(f"Force-released {count} resources from agent '{agent_id}'")
