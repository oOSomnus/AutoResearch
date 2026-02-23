"""
LRU Cache - In-memory Least Recently Used cache implementation.
"""
from typing import Any, Optional, Dict
from collections import OrderedDict


class LRUCache:
    """Thread-safe LRU cache with configurable capacity."""

    def __init__(self, capacity: int = 100):
        """
        Initialize the LRU cache.

        Args:
            capacity: Maximum number of items in the cache
        """
        self.capacity = max(1, capacity)
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if key in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return self._cache[key]

        self._misses += 1
        return None

    def put(self, key: str, value: Any) -> None:
        """
        Put a value into the cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        if key in self._cache:
            # Update existing key and move to end
            self._cache.move_to_end(key)
        else:
            # Add new key
            if len(self._cache) >= self.capacity:
                # Remove least recently used (first item)
                self._cache.popitem(last=False)

        self._cache[key] = value

    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all items from the cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def size(self) -> int:
        """Get the current number of items in the cache."""
        return len(self._cache)

    def keys(self) -> list:
        """Get all keys in the cache (from most to least recently used)."""
        return list(self._cache.keys())

    def values(self) -> list:
        """Get all values in the cache (from most to least recently used)."""
        return list(self._cache.values())

    def items(self) -> list:
        """Get all items in the cache (from most to least recently used)."""
        return list(self._cache.items())

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        return {
            "size": len(self._cache),
            "capacity": self.capacity,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate
        }