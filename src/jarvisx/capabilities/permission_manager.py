from __future__ import annotations
from enum import Enum
from typing import List, Dict

class PermissionLevel(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    EXECUTE = "EXECUTE"
    NETWORK = "NETWORK"
    SENSITIVE = "SENSITIVE"

class PermissionManager:
    def __init__(self):
        self.granted_permissions: Dict[str, List[PermissionLevel]] = {}
        self.dangerous_actions_approval: bool = False

    def request_permission(self, capability_name: str, permission: PermissionLevel) -> bool:
        if permission in [PermissionLevel.EXECUTE, PermissionLevel.SENSITIVE]:
            if not self.dangerous_actions_approval:
                return False
        
        if capability_name not in self.granted_permissions:
            self.granted_permissions[capability_name] = []
        
        if permission not in self.granted_permissions[capability_name]:
            self.granted_permissions[capability_name].append(permission)
        
        return True

    def check_permission(self, capability_name: str, permission: PermissionLevel) -> bool:
        return permission in self.granted_permissions.get(capability_name, [])

    def grant_dangerous_actions(self) -> None:
        self.dangerous_actions_approval = True
