import gc
import sys
import time
import threading


class AdaptiveGCTuner:
    __slots__ = ('_check_interval', '_alloc_threshold', '_stop_event', '_thread', '_last_allocs')

    def __init__(self, check_interval_sec: float = 2.0, alloc_threshold: int = 100_000):
        self._check_interval = check_interval_sec
        self._alloc_threshold = alloc_threshold
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._last_allocs = 0

    def start((self) -> None:
        gc.disable()
        gc.set_threshold(700_000, 10, 10)
        self._last_allocs = self._get_alloc_count()
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join()
        gc.enable()

    def _get_alloc_count(self) -> int:
        return gc.get_count()[0]

    def _monitor_loop(self) -> None:
        while not self._stop_event.is_set():
            time.sleep(self._check_interval)
            current_count = self._get_alloc_count()
            delta = current_count - self._last_allocs

            if delta > self._alloc_threshold:
                gc.collect(generation=0)

            if gc.get_count()[1] > 10:
                gc.collect(generation=1)

            self._last_allocs = self._get_alloc_count()

    def force_full_collection(self) -> None:
        gc.collect()
