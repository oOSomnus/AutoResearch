"""
Disk Cache - Persistent disk-based cache implementation.
"""
import os
import json
import pickle
from typing import Any, Optional, Dict
from datetime import datetime, timedelta


class DiskCache:
    """Persistent disk-based cache with TTL support."""

    def __init__(self, cache_dir: str = ".disk_cache", ttl_hours: int = 24):
        """
        Initialize the disk cache.

        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live for cache entries in hours
        """
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)

        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)

        # Metadata file
        self.metadata_file = os.path.join(cache_dir, ".metadata.json")
        self._metadata = self._load_metadata()

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        cache_file = self._get_cache_file(key)

        if not os.path.exists(cache_file):
            return None

        # Check if expired
        metadata = self._metadata.get(key)
        if metadata:
            created_at = datetime.fromisoformat(metadata.get("created_at", ""))
            if (datetime.now() - created_at) > self.ttl:
                # Expired, delete the file
                self._delete_cache_file(key)
                return None

        # Load value from file
        try:
            with open(cache_file, 'rb') as f:
                value = pickle.load(f)

            # Update access time in metadata
            if key in self._metadata:
                self._metadata[key]["accessed_at"] = datetime.now().isoformat()
                self._save_metadata()

            return value
        except (pickle.PickleError, EOFError, IOError):
            # Corrupted file, delete it
            self._delete_cache_file(key)
            return None

    def put(self, key: str, value: Any) -> None:
        """
        Put a value into the cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        cache_file = self._get_cache_file(key)
        now = datetime.now().isoformat()

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)

            # Update metadata
            self._metadata[key] = {
                "created_at": now,
                "accessed_at": now,
                "size": os.path.getsize(cache_file)
            }
            self._save_metadata()

        except (pickle.PickleError, IOError) as e:
            # Failed to write, delete the partial file
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                except OSError:
                    pass

    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False otherwise
        """
        return self._delete_cache_file(key)

    def clear(self) -> None:
        """Clear all items from the cache."""
        # Delete all cache files
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.cache'):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    os.remove(file_path)
                except OSError:
                    pass

        # Clear metadata
        self._metadata.clear()
        self._save_metadata()

    def clear_expired(self) -> int:
        """
        Clear expired cache entries.

        Returns:
            Number of entries cleared
        """
        cleared = 0
        now = datetime.now()

        expired_keys = [
            key for key, meta in self._metadata.items()
            if (now - datetime.fromisoformat(meta.get("created_at", ""))) > self.ttl
        ]

        for key in expired_keys:
            if self._delete_cache_file(key):
                cleared += 1

        return cleared

    def size(self) -> int:
        """Get the current number of items in the cache."""
        return len(self._metadata)

    def keys(self) -> list:
        """Get all keys in the cache."""
        return list(self._metadata.keys())

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_size = sum(meta.get("size", 0) for meta in self._metadata.values())
        expired = 0
        now = datetime.now()

        for meta in self._metadata.values():
            if (now - datetime.fromisoformat(meta.get("created_at", ""))) > self.ttl:
                expired += 1

        return {
            "size": len(self._metadata),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "expired_entries": expired,
            "ttl_hours": self.ttl.total_seconds() / 3600
        }

    def _get_cache_file(self, key: str) -> str:
        """Get the file path for a cache key."""
        # Use MD5 hash of key as filename
        import hashlib
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hash_key}.cache")

    def _delete_cache_file(self, key: str) -> bool:
        """Delete cache file and metadata for a key."""
        cache_file = self._get_cache_file(key)

        # Delete cache file
        deleted = False
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                deleted = True
            except OSError:
                pass

        # Remove from metadata
        if key in self._metadata:
            del self._metadata[key]
            self._save_metadata()

        return deleted

    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from file."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        return {}

    def _save_metadata(self) -> None:
        """Save metadata to file."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self._metadata, f, ensure_ascii=False, indent=2)
        except IOError:
            pass