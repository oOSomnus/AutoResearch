"""
Cache Module - Cache management for paper analysis results.
"""
import os
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class CacheEntry:
    """A single cache entry."""
    cache_key: str
    analysis_data: Dict[str, Any]
    created_at: datetime
    accessed_at: datetime
    node_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "cache_key": self.cache_key,
            "analysis_data": self.analysis_data,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "node_name": self.node_name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheEntry":
        """Create from dictionary."""
        return cls(
            cache_key=data["cache_key"],
            analysis_data=data["analysis_data"],
            created_at=datetime.fromisoformat(data["created_at"]),
            accessed_at=datetime.fromisoformat(data.get("accessed_at", data["created_at"])),
            node_name=data.get("node_name", "")
        )


class CacheManager:
    """Manages caching of analysis results."""

    def __init__(self, cache_dir: str = ".cache", enabled: bool = True,
                 ttl_hours: int = 24):
        """
        Initialize the cache manager.

        Args:
            cache_dir: Directory to store cache files
            enabled: Whether caching is enabled
            ttl_hours: Time-to-live for cache entries in hours
        """
        self.cache_dir = cache_dir
        self.enabled = enabled
        self.ttl = timedelta(hours=ttl_hours)
        self._memory_cache: Dict[str, CacheEntry] = {}

        # Create cache directory if enabled
        if self.enabled:
            os.makedirs(self.cache_dir, exist_ok=True)

    def generate_cache_key(self, pdf_path: str, node_name: str,
                          content_hash: Optional[str] = None) -> str:
        """
        Generate a cache key for a given analysis.

        Args:
            pdf_path: Path to the PDF file
            node_name: Name of the analysis node
            content_hash: Optional hash of the content being analyzed

        Returns:
            A unique cache key string
        """
        # Get file hash if not provided
        if not content_hash:
            content_hash = self._get_file_hash(pdf_path)

        # Combine with node name
        key_string = f"{content_hash}:{node_name}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis result.

        Args:
            cache_key: The cache key

        Returns:
            Cached analysis data or None if not found/expired
        """
        if not self.enabled:
            return None

        # Check memory cache first
        if cache_key in self._memory_cache:
            entry = self._memory_cache[cache_key]
            if self._is_valid(entry):
                # Update access time
                entry.accessed_at = datetime.utcnow()
                return entry.analysis_data
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]

        # Check disk cache
        cache_file = self._get_cache_file_path(cache_key)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    entry_data = json.load(f)
                entry = CacheEntry.from_dict(entry_data)

                if self._is_valid(entry):
                    # Add to memory cache
                    entry.accessed_at = datetime.utcnow()
                    self._memory_cache[cache_key] = entry
                    return entry.analysis_data
                else:
                    # Remove expired entry
                    os.remove(cache_file)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Invalid cache file, remove it
                try:
                    os.remove(cache_file)
                except OSError:
                    pass

        return None

    def set(self, cache_key: str, analysis_data: Dict[str, Any],
           node_name: str = "") -> None:
        """
        Cache an analysis result.

        Args:
            cache_key: The cache key
            analysis_data: The analysis data to cache
            node_name: Name of the analysis node
        """
        if not self.enabled:
            return

        entry = CacheEntry(
            cache_key=cache_key,
            analysis_data=analysis_data,
            created_at=datetime.utcnow(),
            accessed_at=datetime.utcnow(),
            node_name=node_name
        )

        # Add to memory cache
        self._memory_cache[cache_key] = entry

        # Also save to disk
        cache_file = self._get_cache_file_path(cache_key)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2)
        except (IOError, TypeError):
            # Failed to write to disk, keep in memory only
            pass

    def clear(self) -> None:
        """Clear all cache entries."""
        self._memory_cache.clear()

        # Clear disk cache
        if self.enabled and os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass

    def clear_expired(self) -> int:
        """
        Clear expired cache entries.

        Returns:
            Number of entries cleared
        """
        cleared = 0

        # Clear expired from memory cache
        expired_keys = [
            key for key, entry in self._memory_cache.items()
            if not self._is_valid(entry)
        ]
        for key in expired_keys:
            del self._memory_cache[key]
            cleared += 1

        # Clear expired from disk cache
        if self.enabled and os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            entry_data = json.load(f)
                        entry = CacheEntry.from_dict(entry_data)
                        if not self._is_valid(entry):
                            os.remove(file_path)
                            cleared += 1
                    except (json.JSONDecodeError, KeyError, ValueError, OSError):
                        # Invalid or inaccessible cache file, remove it
                        try:
                            os.remove(file_path)
                            cleared += 1
                        except OSError:
                            pass

        return cleared

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        memory_count = len(self._memory_cache)
        disk_count = 0

        if self.enabled and os.path.exists(self.cache_dir):
            disk_count = sum(
                1 for filename in os.listdir(self.cache_dir)
                if filename.endswith('.json')
            )

        return {
            "enabled": self.enabled,
            "memory_entries": memory_count,
            "disk_entries": disk_count,
            "ttl_hours": self.ttl.total_seconds() / 3600
        }

    def _get_file_hash(self, file_path: str) -> str:
        """Get hash of a file for cache key generation."""
        # Simple hash based on file path and modification time
        # In production, you might want to hash the actual file content
        if not os.path.exists(file_path):
            return hashlib.md5(file_path.encode()).hexdigest()

        mtime = os.path.getmtime(file_path)
        hash_string = f"{file_path}:{mtime}"
        return hashlib.md5(hash_string.encode()).hexdigest()

    def _get_cache_file_path(self, cache_key: str) -> str:
        """Get the file path for a cache key."""
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def _is_valid(self, entry: CacheEntry) -> bool:
        """Check if a cache entry is still valid (not expired)."""
        return (datetime.utcnow() - entry.created_at) < self.ttl


# Global cache manager instance
_global_cache_manager: Optional[CacheManager] = None


def get_cache_manager(cache_dir: str = ".cache", enabled: bool = True,
                     ttl_hours: int = 24) -> CacheManager:
    """
    Get or create the global cache manager.

    Args:
        cache_dir: Directory to store cache files
        enabled: Whether caching is enabled
        ttl_hours: Time-to-live for cache entries in hours

    Returns:
        The global cache manager instance
    """
    global _global_cache_manager

    if _global_cache_manager is None:
        _global_cache_manager = CacheManager(cache_dir, enabled, ttl_hours)

    return _global_cache_manager