"""
Cache Key Generator - Generate cache keys based on content hash.
"""
import hashlib
import os
from typing import Optional


class CacheKeyGenerator:
    """Generates cache keys based on content hashing."""

    def __init__(self, hash_algorithm: str = "sha256"):
        """
        Initialize the cache key generator.

        Args:
            hash_algorithm: Hash algorithm to use (md5, sha256, etc.)
        """
        self.hash_algorithm = hash_algorithm

    def generate_key(self, pdf_path: str, node_name: str,
                    content_hash: Optional[str] = None,
                    additional_params: Optional[dict] = None) -> str:
        """
        Generate a cache key for analysis.

        Args:
            pdf_path: Path to the PDF file
            node_name: Name of the analysis node
            content_hash: Optional pre-computed content hash
            additional_params: Optional additional parameters to include in key

        Returns:
            A unique cache key string
        """
        # Get file hash if not provided
        if content_hash is None:
            content_hash = self._get_file_hash(pdf_path)

        # Build key string
        key_parts = [content_hash, node_name]

        # Add additional parameters if provided
        if additional_params:
            sorted_params = sorted(additional_params.items())
            key_parts.extend(f"{k}={v}" for k, v in sorted_params)

        key_string = ":".join(key_parts)

        # Hash the key string
        hash_obj = hashlib.new(self.hash_algorithm)
        hash_obj.update(key_string.encode('utf-8'))

        return hash_obj.hexdigest()

    def generate_key_from_content(self, content: str, node_name: str,
                                  additional_params: Optional[dict] = None) -> str:
        """
        Generate a cache key directly from content.

        Args:
            content: The content being analyzed
            node_name: Name of the analysis node
            additional_params: Optional additional parameters

        Returns:
            A unique cache key string
        """
        # Hash the content
        hash_obj = hashlib.new(self.hash_algorithm)
        hash_obj.update(content.encode('utf-8'))
        content_hash = hash_obj.hexdigest()

        # Build key string
        key_parts = [content_hash, node_name]

        if additional_params:
            sorted_params = sorted(additional_params.items())
            key_parts.extend(f"{k}={v}" for k, v in sorted_params)

        key_string = ":".join(key_parts)

        # Hash the key string
        hash_obj = hashlib.new(self.hash_algorithm)
        hash_obj.update(key_string.encode('utf-8'))

        return hash_obj.hexdigest()

    def _get_file_hash(self, file_path: str) -> str:
        """
        Get hash of a file.

        Args:
            file_path: Path to the file

        Returns:
            Hash of the file
        """
        if not os.path.exists(file_path):
            # Hash the path if file doesn't exist
            hash_obj = hashlib.new(self.hash_algorithm)
            hash_obj.update(file_path.encode('utf-8'))
            return hash_obj.hexdigest()

        # Hash file content and modification time
        # This is efficient and handles file updates
        mtime = os.path.getmtime(file_path)
        file_size = os.path.getsize(file_path)

        hash_obj = hashlib.new(self.hash_algorithm)
        hash_obj.update(f"{file_path}:{mtime}:{file_size}".encode('utf-8'))

        return hash_obj.hexdigest()