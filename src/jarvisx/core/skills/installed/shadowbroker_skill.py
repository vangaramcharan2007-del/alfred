from typing import List, Dict, Any
from jarvisx.core.skills.skill import BaseSkill
from jarvisx.core.permissions.manager import PermissionManager
from jarvisx.integrations.shadowbroker.shadowbroker_adapter import ShadowBrokerAdapter

class ShadowBrokerOSINT(BaseSkill):
    """
    Accesses real-time geospatial intelligence, threat analysis, and OSINT data through the ShadowBroker network.
    """
    
    def __init__(self):
        super().__init__()
        self.permission_manager = PermissionManager()
        self.adapter = ShadowBrokerAdapter()
        
    @property
    def name(self) -> str:
        return "ShadowBrokerOSINT"
        
    @property
    def description(self) -> str:
        return "Accesses real-time geospatial intelligence, threat analysis, and OSINT data through the ShadowBroker network."
        
    @property
    def category(self) -> str:
        return "intelligence"
        
    @property
    def capabilities(self) -> List[str]:
        return [
            "OSINT research",
            "geospatial intelligence",
            "channel analysis"
        ]
        
    @property
    def tags(self) -> List[str]:
        return ["osint", "research", "intelligence", "geospatial"]
        
    @property
    def cost(self) -> str:
        return "medium"
        
    @property
    def success_rate(self) -> float:
        return 0.85
        
    @property
    def required_permissions(self) -> List[str]:
        return ["network_access"]

    @property
    def required_tools(self) -> List[str]:
        return ["shadowbroker_ask", "shadowbroker_playbook", "shadowbroker_status"]
        
    async def execute(self, task: str, context: Dict[str, Any] = None) -> str:
        """
        Executes a ShadowBroker operation.
        The task dictates which capability to invoke (ask, playbook, or status).
        """
        # Enforce permission boundary before network access
        if not self.permission_manager.request("execute network request to ShadowBroker", "shadowbroker-api"):
            return "Execution denied: Missing required permission 'network_access'."

        context = context or {}
        operation = context.get("operation", "ask")
        
        try:
            if operation == "ask":
                question = context.get("question", task)
                result = await self.adapter.ask(question)
                return f"ShadowBroker Result: {result}"
                
            elif operation == "playbook":
                playbook_name = context.get("playbook_name", "hot_snapshot")
                args = context.get("args", {})
                result = await self.adapter.run_playbook(playbook_name, args)
                return f"ShadowBroker Playbook '{playbook_name}' Result: {result}"
                
            elif operation == "status":
                result = await self.adapter.health_check()
                return f"ShadowBroker Status: {result}"
                
            else:
                return f"Unknown ShadowBroker operation: {operation}"
                
        except Exception as e:
            return f"ShadowBroker execution failed: {str(e)}"
