import weakref
import threading
from collections import OrderedDict
from typing import Any, Optional, TypeVar, Generic

K = TypeVar('K')
V = TypeVar('V')


class LRUWeakValueCache(Generic[K, V]):
    __slots__ = ('_max_size', '_data', '_order', '_lock')

    def __init__(self, max_size: int = 2048):
        self._max_size = max_size
        self._data: weakref.WeakValueDictionary[K, V] = weakref.WeakValueDictionary()
        self._order: OrderedDict[K, None] = OrderedDict()
        self._lock = threading.RLock()

    def get(self, key: K) -> Optional[V]:
        with self._lock:
            val = self._data.get(key)
            if val is not None:
                self._order.move_to_end(key)
            return val

    def put(self, key: K, val: V) -> None:
        with self._lock:
            if key in self._order:
                self._order.move_to_end(key)
            else:
                self._order[key] = None

            self._data[key] = val

            while len(self._order) > self._max_size:
                evict_key, _ = self._order.popitem(last=False)
                self._data.pop(evict_key, None)

    def invalidate(self, key: K) -> None:
        with self._lock:
            self._order.pop(key, None)
            self._data.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._order.clear()
            self._data.clear()
