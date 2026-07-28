class LearningExplanation:
    def __init__(self):
        pass
        
    def generate(self, selected_agent: str, reasons: list) -> str:
        if not reasons:
            return f"Selected {selected_agent} based on cognitive evaluation."
        
        reasons_str = ", ".join(reasons)
        return f"Selected {selected_agent} because {reasons_str}."
