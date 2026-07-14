# src/jarvisx/core/device_role_manager.py

class DeviceRoleManager:
    """
    Assigns and tracks the role of each node in the mesh.
    Roles: Primary UI, Headless Worker, Mobile Relay
    """
    def __init__(self):
        self.node_roles = {}

    def assign_role(self, node_id: str, role: str):
        pass

    def get_primary_node(self) -> str:
        return ""
