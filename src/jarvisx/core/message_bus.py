import asyncio
import logging

class EventBus:
    def __init__(self):
        self._subscribers = {}
        self._queue = asyncio.Queue()
        self._running = False
        self._worker_task = None

    def subscribe(self, event_type: str, callback):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback):
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)

    async def publish(self, event_type: str, payload: dict):
        await self._queue.put((event_type, payload))

    async def start(self):
        self._running = True
        self._worker_task = asyncio.create_task(self._process_events())

    async def stop(self):
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()

    async def _process_events(self):
        while self._running:
            try:
                event_type, payload = await self._queue.get()
                if event_type in self._subscribers:
                    for callback in self._subscribers[event_type]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                asyncio.create_task(callback(payload))
                            else:
                                callback(payload)
                        except Exception as e:
                            logging.error(f"EventBus callback error on {event_type}: {e}")
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"EventBus processing error: {e}")
