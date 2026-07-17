"""Resource Lock Manager — prevents concurrent access conflicts across agents."""
import asyncio
import logging
import time
from typing import Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class ResourceManager:
    """Manages exclusive locks on tools/resources to prevent agent conflicts."""

    _instance: Optional["ResourceManager"] = None

    def __init__(self):
        self._locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self._owners: Dict[str, str] = {}  # resource_name -> agent_id
        self._acquire_times: Dict[str, float] = {}

    @classmethod
    def get_instance(cls) -> "ResourceManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    async def acquire(self, resource_name: str, agent_id: str, timeout: float = 10.0) -> bool:
        """Acquire an exclusive lock on a resource."""
        try:
            acquired = await asyncio.wait_for(
                self._locks[resource_name].acquire(), timeout=timeout
            )
            if acquired:
                self._owners[resource_name] = agent_id
                self._acquire_times[resource_name] = time.time()
                logger.info(f"Resource '{resource_name}' locked by agent '{agent_id}'")
                return True
        except asyncio.TimeoutError:
            logger.warning(
                f"Agent '{agent_id}' timed out acquiring resource '{resource_name}' "
                f"(held by '{self._owners.get(resource_name, 'unknown')}')"
            )
        return False

    def release(self, resource_name: str, agent_id: str) -> bool:
        """Release a lock. Only the owning agent can release."""
        if self._owners.get(resource_name) != agent_id:
            logger.warning(f"Agent '{agent_id}' cannot release '{resource_name}' — not the owner")
            return False
        self._locks[resource_name].release()
        del self._owners[resource_name]
        if resource_name in self._acquire_times:
            del self._acquire_times[resource_name]
        logger.info(f"Resource '{resource_name}' released by agent '{agent_id}'")
        return True

    def is_locked(self, resource_name: str) -> bool:
        return resource_name in self._owners

    def get_owner(self, resource_name: str) -> Optional[str]:
        return self._owners.get(resource_name)

    def get_locked_resources(self) -> Dict[str, str]:
        return dict(self._owners)

    def force_release_all(self, agent_id: str):
        """Release all resources held by an agent (used during failure recovery)."""
        resources_to_release = [r for r, owner in self._owners.items() if owner == agent_id]
        for resource in resources_to_release:
            try:
                self._locks[resource].release()
            except RuntimeError:
                pass  # Lock already released
            del self._owners[resource]
            if resource in self._acquire_times:
                del self._acquire_times[resource]
        if resources_to_release:
            logger.info(f"Force-released {len(resources_to_release)} resources from agent '{agent_id}'")
