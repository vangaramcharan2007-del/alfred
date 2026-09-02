class ConfidenceManager:
    def __init__(self):
        self.records = {}
    
    def get_confidence(self, agent: str) -> float:
        return self.records.get(agent, {}).get("confidence", 0.5)

    def update_confidence(self, agent: str, success: bool):
        if agent not in self.records:
            self.records[agent] = {"confidence": 0.5, "success_rate": 0.5, "last_used": None}
            
        current = self.records[agent]["confidence"]
        if success:
            new_conf = min(1.0, current + 0.1)
        else:
            new_conf = max(0.0, current - 0.2)
            
        self.records[agent]["confidence"] = new_conf
        
    def manage_confidence(self, agent: str):
        # implement decay, reinforcement, contradiction
        pass
