import asyncio
import psutil
import time

class TelemetryEngine:
    def __init__(self, interval: int = 1):
        self.interval = interval
        self.running = False
        self._last_net_io = psutil.net_io_counters()
        self._last_time = time.time()

    async def start(self):
        self.running = True
        asyncio.create_task(self._loop())

    def stop(self):
        self.running = False

    async def _loop(self):
        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory().percent
                
                current_net_io = psutil.net_io_counters()
                current_time = time.time()
                
                dt = current_time - self._last_time
                if dt > 0:
                    bytes_sent_sec = (current_net_io.bytes_sent - self._last_net_io.bytes_sent) / dt
                    bytes_recv_sec = (current_net_io.bytes_recv - self._last_net_io.bytes_recv) / dt
                else:
                    bytes_sent_sec = 0
                    bytes_recv_sec = 0
                    
                self._last_net_io = current_net_io
                self._last_time = current_time
                
            except psutil.AccessDenied:
                pass
            except Exception:
                pass
                
            await asyncio.sleep(self.interval)
