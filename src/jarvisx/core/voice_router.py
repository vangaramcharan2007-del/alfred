import asyncio

class VoiceRouter:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.running = False
        self._worker_task = None

    async def start(self):
        self.running = True
        self._worker_task = asyncio.create_task(self._process_queue())

    async def stop(self):
        self.running = False
        if self._worker_task:
            self._worker_task.cancel()

    async def process_voice_command(self, text: str):
        words = text.strip().split()
        if len(words) < 3:
            # Ignore strings under 3 words to filter out noise
            return
        await self.queue.put(text)

    async def _process_queue(self):
        while self.running:
            try:
                command = await self.queue.get()
                await self.execute_l2_cloud(command)
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                pass

    async def execute_l2_cloud(self, text: str):
        # Stub for L2 processing
        await asyncio.sleep(1)
