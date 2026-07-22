from typing import List, Dict, Any
from jarvisx.core.skills.skill import BaseSkill
from jarvisx.core.llm_router import OmniRouterClient
from jarvisx.core.model_policy import ModelPolicy

class ResearchSkill(BaseSkill):
    """
    Skill for researching a topic and summarizing the findings using the OmniRoute Gateway.
    """
    
    @property
    def name(self) -> str:
        return "Research Assistant"
        
    @property
    def description(self) -> str:
        return "Researches a topic by executing a structured workflow: search, summarize, format."
        
    @property
    def required_tools(self) -> List[str]:
        # We don't have a real web search tool in Jarvis X yet, but we'd request it here.
        # For now, it just requests the LLM to hallucinate or summarize based on its knowledge.
        return []
        
    @property
    def category(self) -> str:
        return "research"
        
    @property
    def tags(self) -> List[str]:
        return ["search", "summarize", "information", "research"]
        
    @property
    def cost(self) -> str:
        return "low"
        
    async def execute(self, task: str, context: Dict[str, Any] = None) -> str:
        router = OmniRouterClient()
        policy = ModelPolicy()
        
        ctx = policy.evaluate(agent_name="ResearchSkill", task_description=task)
        
        messages = [
            {"role": "system", "content": "You are a Research Assistant. Summarize the requested topic with key bullet points and a conclusion."},
            {"role": "user", "content": f"Research Task: {task}"}
        ]
        
        try:
            result = await router.chat(messages=messages, model=ctx.model, context=ctx.metadata)
            return result
        except Exception as e:
            return f"Research failed: {str(e)}"
