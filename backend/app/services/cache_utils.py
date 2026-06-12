import time
from collections import OrderedDict
from threading import RLock


class TTLCache:
    def __init__(self, ttl_seconds: int = 600, max_size: int = 256) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_size = max(1, max_size)
        self._store: OrderedDict[str, tuple[float, object]] = OrderedDict()
        self._lock = RLock()

    def get(self, key: str):
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None

            expires_at, value = item
            if time.time() > expires_at:
                self._store.pop(key, None)
                return None

            self._store.move_to_end(key)
            return value

    def set(self, key: str, value) -> None:
        with self._lock:
            self._evict_expired()
            expires_at = time.time() + self.ttl_seconds
            self._store[key] = (expires_at, value)
            self._store.move_to_end(key)

            while len(self._store) > self.max_size:
                self._store.popitem(last=False)

    def _evict_expired(self) -> None:
        now = time.time()
        expired_keys = [
            key
            for key, (expires_at, _value) in self._store.items()
            if now > expires_at
        ]
        for key in expired_keys:
            self._store.pop(key, None)
