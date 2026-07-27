from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import uvicorn
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Jarvis X - Protocol Omega Dashboard")

# Ensure templates directory exists
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    """
    Serves the Industrial Web OS Dashboard.
    """
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={
            "cgpa": "9.2",
            "attendance": "85%",
            "next_class": "Transforms",
            "active_mode": "Distraction Vault ENGAGED"
        }
    )

@app.get("/api/status")
async def get_status():
    """
    Endpoint for live telemetry updates.
    """
    return {"status": "online", "omniroute": "connected", "termux_bridge": "secured"}

def run_server(port=8000):
    logger.info(f"Starting Protocol Omega Web OS on port {port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

if __name__ == "__main__":
    run_server()
