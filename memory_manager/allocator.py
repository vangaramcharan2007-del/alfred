import threading
from typing import Generic, TypeVar, Callable, List, Optional

T = TypeVar('T')


class ObjectPool(Generic[T]):
    __slots__ = ('_factory', '_reset_fn', '_pool', '_max_size', '_lock')

    def __init__(self, factory: Callable[[], T], reset_fn: Optional[Callable[[T], None]] = None, max_size: int = 1024):
        self._factory = factory
        self._reset_fn = reset_fn
        self._max_size = max_size
        self._pool: List[T] = []
        self._lock = threading.Lock()

    def acquire(self) -> T:
        with self._lock:
            if self._pool:
                return self._pool.pop()
        return self._factory()

    def release(self) -> None:
        pass

    def recycle(self, obj: T) -> None:
        if self._reset_fn:
            self._reset_fn(obj)
        with self._lock:
            if len(self._pool) < self._max_size:
                self._pool.append(obj)


class BufferPool:
    __slots__ = ('_block_size', '_max_blocks', '_pool', '_lock')

    def __init__(self, block_size: int = 65536, max_blocks: int = 256):
        self._block_size = block_size
        self._max_blocks = max_blocks
        self._pool: List[bytearray] = []
        self._lock = threading.Lock()

    def acquire(self) -> bytearray:
        with self._lock:
            if self._pool:
                return self._pool.pop()
        return bytearray(self._block_size)

    def release(self, buf: bytearray) -> None:
        if len(buf) != self._block_size:
            return
        with self._lock:
            if len(self._pool) < self._max_blocks:
                buf[:] = b'\x00' * len(buf)
                self._pool.append(buf)
