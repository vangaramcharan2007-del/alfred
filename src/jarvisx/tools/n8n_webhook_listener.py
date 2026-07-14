import asyncio
import threading
import logging
from typing import Dict, Any

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("WARNING: Flask not installed. Running in Mock Mode.")

from jarvisx.core.swarm_supervisor import SwarmSupervisor
from jarvisx.tools.db_manager import DatabaseManager

app = None
if FLASK_AVAILABLE:
    app = Flask(__name__)
    # Disable flask output to keep simulation clean
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    supervisor = SwarmSupervisor()
    
    # Wrapper to run async functions in a Flask synchronous route
    def run_async(coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        loop.close()
        return result

    @app.route('/api/jarvis/execute', methods=['POST'])
    def execute_task():
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({"status": "error", "message": "Missing 'task' in payload"}), 400
        
        task = data['task']
        logging.info(f"Webhook received task: {task}")
        
        try:
            response_data = run_async(supervisor.execute_complex_task(task))
            result_str = f"Task completed. {len(response_data.get('results', []))} workers returned data."
            return jsonify({"status": "success", "response": result_str, "data": response_data}), 200
        except Exception as e:
            logging.error(f"Error routing task: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

class WebhookListenerNode:
    def __init__(self, port=5000):
        self.port = port
        self.server_thread = None
        self.db = DatabaseManager()
    
    def start_server(self):
        if FLASK_AVAILABLE:
            logging.info(f"Starting Flask n8n webhook listener on port {self.port}...")
            # Run without reloader in background thread
            app.run(host='127.0.0.1', port=self.port, use_reloader=False, debug=False)
        else:
            logging.info("[MOCK] Webhook server started.")
            
    def run_in_background(self):
        self.server_thread = threading.Thread(target=self.start_server, daemon=True)
        self.server_thread.start()

    async def telemetry_log(self):
        try:
            await self.db.execute_query('''CREATE TABLE IF NOT EXISTS agent_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, filepath TEXT)''')
            await self.db.execute_query("INSERT INTO agent_logs (action, filepath) VALUES (?, ?)", 
                                   ("n8n Webhook Listener Active", "src/jarvisx/tools/n8n_webhook_listener.py"))
        except Exception as e:
            pass # degrade gracefully in mock
