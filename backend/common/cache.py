from time import time
from typing import Optional, Any


class _Cache:
    def __init__(self):
        self.store = {}

    def get(self, key, default: Any = None) -> Any:
        item = self.store.get(key, default)
        if item and item["expire"] is not None and item["expire"] < time():
            self.delete(key)
            return default
        return item["value"] if item else default

    def set(self, key, value, ttl: Optional[int] = None):
        self.store[key] = {
            "value": value,
            "expire": time() + ttl if ttl is not None else None,
        }

    def delete(self, key):
        if key in self.store:
            del self.store[key]

    def clear(self):
        self.store.clear()


Cache = _Cache()
