import time


class TTLCache:
    def __init__(self, ttl_seconds: int = 600) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[float, object]] = {}

    def get(self, key: str):
        item = self._store.get(key)
        if item is None:
            return None

        expires_at, value = item
        if time.time() > expires_at:
            self._store.pop(key, None)
            return None

        return value

    def set(self, key: str, value) -> None:
        expires_at = time.time() + self.ttl_seconds
        self._store[key] = (expires_at, value)
