import os
import asyncio
import logging
import threading
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class BrowserUseEngine:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        self._running = False
        load_dotenv()
        
    def _push_to_ui(self, event_type: str, data: dict):
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def execute_task(self, task_description: str):
        """
        Spawns a browser-use agent to complete the given task asynchronously.
        """
        if not self._running:
            logger.warning("[BrowserUse] Engine not started.")
            return

        def _run():
            try:
                # We run this in a new event loop since it's a thread
                asyncio.run(self._async_execute(task_description))
            except Exception as e:
                logger.error(f"[BrowserUse] Failed to execute task: {e}")
                self._push_to_ui("ghost_event", {"action": "Error", "text": str(e)})

        logger.info(f"[BrowserUse] Dispatching task: {task_description}")
        self._push_to_ui("ghost_event", {"action": "Browser Agent Deployed", "text": task_description})
        threading.Thread(target=_run, daemon=True).start()

    async def _async_execute(self, task_description: str):
        try:
            from browser_use import Agent
            
            # Use Groq if available (via OpenAI compatible endpoint), fallback to OpenRouter, fallback to OpenAI
            llm = None
            if os.getenv("OPENROUTER_API_KEY"):
                from browser_use.llm.openrouter.chat import ChatOpenRouter
                llm = ChatOpenRouter(
                    model="google/gemini-2.5-flash", 
                    api_key=os.getenv("OPENROUTER_API_KEY")
                )
            elif os.getenv("GROQ_API_KEY"):
                from browser_use.llm.openai.like import ChatOpenAILike
                llm = ChatOpenAILike(
                    model="llama-3.2-90b-vision-preview", 
                    api_key=os.getenv("GROQ_API_KEY"),
                    base_url="https://api.groq.com/openai/v1"
                )
            elif os.getenv("OPENAI_API_KEY"):
                from browser_use.llm.openai.chat import ChatOpenAI
                llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
            else:
                raise ValueError("No valid LLM API Key found for browser-use (OPENROUTER_API_KEY or GROQ_API_KEY required).")
                
            agent = Agent(
                task=task_description,
                llm=llm
            )
            
            self._push_to_ui("ghost_event", {"action": "Execution Started", "text": "Browser taken over."})
            result = await agent.run()
            
            logger.info(f"[BrowserUse] Result: {result}")
            self._push_to_ui("ghost_event", {"action": "Task Completed", "text": str(result)[:200]})
        except Exception as e:
            logger.error(f"[BrowserUse] Exception during async execution: {e}")
            self._push_to_ui("ghost_event", {"action": "Failed", "text": str(e)})

    def start(self):
        if self._running:
            return
        self._running = True
        logger.info("[BrowserUse] BrowserUse AI Engine Online.")
