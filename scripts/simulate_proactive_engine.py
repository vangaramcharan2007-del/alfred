import asyncio
import logging
from jarvisx.core.proactive_alfred import ProactiveAlfred

logging.basicConfig(level=logging.INFO)

async def main():
    print("--- Simulating Proactive Autonomy Engine ---")
    alfred = ProactiveAlfred()
    await alfred.run_cron_cycle()
    print("God Mode Simulation Complete.")

if __name__ == "__main__":
    asyncio.run(main())
