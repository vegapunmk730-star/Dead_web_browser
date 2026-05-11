import time
from typing import Any, Optional
from infrastructure.logging.logger import get_logger

log = get_logger("cache")

CACHE_TTL = 3600
CACHE_MAX = 500


class MemoryCache:
    def __init__(self):
        self._store: dict = {}
        self._ttl = CACHE_TTL
        self._max = CACHE_MAX
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            self._misses += 1
            return None
        if time.time() - entry["ts"] > self._ttl:
            del self._store[key]
            self._misses += 1
            return None
        self._hits += 1
        return entry["data"]

    def set(self, key: str, data: Any) -> None:
        if len(self._store) >= self._max:
            oldest = min(self._store.items(), key=lambda x: x[1]["ts"])
            del self._store[oldest[0]]
        self._store[key] = {"data": data, "ts": time.time()}

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

    def metrics(self) -> dict:
        total = self._hits + self._misses
        return {
            "entries":  len(self._store),
            "hits":     self._hits,
            "misses":   self._misses,
            "hit_rate": round(self._hits / total, 3) if total else 0,
        }


cache = MemoryCache()
