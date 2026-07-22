import asyncio
import logging
import os
import subprocess
import aiohttp
from typing import Optional

logger = logging.getLogger(__name__)

class OmniRouteManager:
    """
    Lifecycle manager for the OmniRoute AI gateway.
    Responsible for detecting, starting, monitoring, and shutting down OmniRoute.
    """
    
    def __init__(self):
        self.host = os.getenv("OMNIROUTE_HOST", "127.0.0.1")
        self.port = int(os.getenv("OMNIROUTE_PORT", "20128"))
        self.path = os.getenv("OMNIROUTE_PATH", "modules/OmniRoute")
        self.process: Optional[subprocess.Popen] = None
        self.base_url = f"http://{self.host}:{self.port}"
        
    def detect_installation(self) -> bool:
        """Checks if OmniRoute is installed at the configured path."""
        if os.path.exists(self.path) and os.path.isdir(self.path):
            return True
        logger.warning(f"OmniRoute not found at {self.path}")
        return False
        
    async def start(self) -> bool:
        """Starts the OmniRoute background process."""
        if not self.detect_installation():
            return False
            
        if await self.check_health():
            logger.info("OmniRoute is already running.")
            return True
            
        logger.info("Starting OmniRoute Gateway...")
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            self.process = subprocess.Popen(
                ["npm", "run", "start"], 
                cwd=self.path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                shell=(os.name == 'nt')
            )
            
            for _ in range(10):
                if await self.check_health():
                    logger.info("OmniRoute Gateway started successfully.")
                    return True
                await asyncio.sleep(1)
                
            logger.error("OmniRoute Gateway failed to start in time.")
            self.stop()
            return False
            
        except Exception as e:
            logger.error(f"Failed to start OmniRoute: {e}")
            return False
            
    async def check_health(self) -> bool:
        """Checks if OmniRoute is responding to health checks."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=2) as response:
                    return response.status == 200
        except Exception:
            return False

    def stop(self):
        """Gracefully stops the OmniRoute process if we started it."""
        if self.process:
            logger.info("Stopping OmniRoute Gateway...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            logger.info("OmniRoute Gateway stopped.")
