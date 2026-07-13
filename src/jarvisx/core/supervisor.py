import asyncio
import logging

class MasterSupervisor:
    def __init__(self):
        self.modules = []
        self.max_retries = 3

    def register_module(self, name: str, coroutine_factory):
        self.modules.append({
            "name": name,
            "factory": coroutine_factory,
            "retries": 0
        })

    async def _monitor_task(self, module):
        name = module["name"]
        factory = module["factory"]
        
        while module["retries"] < self.max_retries:
            try:
                # Start the module
                await factory()
                break # if it ends gracefully, stop restarting
            except Exception as e:
                module["retries"] += 1
                logging.error(f"Module {name} crashed. Retries: {module['retries']}/{self.max_retries}. Error: {e}")
                
                # In a real scenario, trigger Lazarus recovery protocol via sqlite log
                # log_to_sqlite("crash", name, str(e))
                
                if module["retries"] >= self.max_retries:
                    logging.critical(f"CRITICAL HUD ALERT: Module {name} failed permanently.")
                    # Trigger critical alert logic here
                    break
                    
                # Staggered restart delay
                await asyncio.sleep(2 ** module["retries"])

    async def run_all(self):
        tasks = [asyncio.create_task(self._monitor_task(m)) for m in self.modules]
        await asyncio.gather(*tasks)
