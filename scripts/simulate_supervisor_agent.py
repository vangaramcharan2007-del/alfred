import asyncio
from jarvisx.core.swarm_supervisor import SwarmSupervisor
from jarvisx.tools.db_manager import DatabaseManager

async def main():
    supervisor = SwarmSupervisor()
    dummy_task = "Analyze the incoming data stream and build a predictive model."
    
    print("Executing Orchestrator self-test...")
    aggregated_results = await supervisor.execute_complex_task(dummy_task)
    
    print("Aggregated Output:")
    print(aggregated_results)
    
    # Telemetry logging
    db = DatabaseManager()
    await db.execute_query('''CREATE TABLE IF NOT EXISTS agent_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, filepath TEXT)''')
    await db.execute_query("INSERT INTO agent_logs (action, filepath) VALUES (?, ?)", 
                           ("Swarm Supervisor Deployed", "src/jarvisx/core/swarm_supervisor.py"))
    
    print("Supervisor Architect Agent simulation complete.")

if __name__ == "__main__":
    asyncio.run(main())
