"""
Cache Package - Caching utilities for paper analysis.
"""

from .lru_cache import LRUCache
from .disk_cache import DiskCache
from .cache_key import CacheKeyGenerator

__all__ = [
    "LRUCache",
    "DiskCache",
    "CacheKeyGenerator",
    "get_cache_key_generator",
]


def get_cache_key_generator() -> CacheKeyGenerator:
    """Get a cache key generator instance."""
    return CacheKeyGenerator()