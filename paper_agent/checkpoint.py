"""
Checkpoint Module - Checkpoint management for resumable analysis.
"""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime


class CheckpointManager:
    """Manages checkpoints for resumable paper analysis."""

    def __init__(self, checkpoint_dir: str = ".checkpoints"):
        """
        Initialize the checkpoint manager.

        Args:
            checkpoint_dir: Directory to store checkpoint files
        """
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)

    def save_checkpoint(self, state: Dict[str, Any], checkpoint_name: str = "") -> str:
        """
        Save the current analysis state as a checkpoint.

        Args:
            state: The current analysis state
            checkpoint_name: Optional name for the checkpoint

        Returns:
            Path to the saved checkpoint file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate checkpoint filename
        if checkpoint_name:
            filename = f"{checkpoint_name}_{timestamp}.json"
        else:
            source = state.get("source", "unknown")
            title = state.get("title", "unknown")
            # Create a safe filename from source/title
            safe_name = "".join(c for c in f"{source}_{title}" if c.isalnum() or c in " -_")[:50]
            filename = f"checkpoint_{safe_name}_{timestamp}.json"

        checkpoint_path = os.path.join(self.checkpoint_dir, filename)

        # Add metadata to the checkpoint
        checkpoint_data = {
            "state": state,
            "metadata": {
                "saved_at": datetime.now().isoformat(),
                "completed_nodes": state.get("completed_nodes", []),
                "checkpoint_name": checkpoint_name
            }
        }

        try:
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)

            # Update state with checkpoint path
            state["checkpoint_path"] = checkpoint_path

            return checkpoint_path
        except (IOError, TypeError) as e:
            raise RuntimeError(f"Failed to save checkpoint: {e}")

    def load_checkpoint(self, checkpoint_path: str) -> Optional[Dict[str, Any]]:
        """
        Load analysis state from a checkpoint.

        Args:
            checkpoint_path: Path to the checkpoint file

        Returns:
            The saved state or None if loading failed
        """
        if not os.path.exists(checkpoint_path):
            return None

        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)

            state = checkpoint_data.get("state", {})
            metadata = checkpoint_data.get("metadata", {})

            # Restore checkpoint path in state
            state["checkpoint_path"] = checkpoint_path

            return state
        except (json.JSONDecodeError, KeyError, ValueError, IOError):
            return None

    def list_checkpoints(self) -> list[Dict[str, Any]]:
        """
        List all available checkpoints.

        Returns:
            List of checkpoint information dictionaries
        """
        checkpoints = []

        if not os.path.exists(self.checkpoint_dir):
            return checkpoints

        for filename in os.listdir(self.checkpoint_dir):
            if filename.endswith('.json'):
                checkpoint_path = os.path.join(self.checkpoint_dir, filename)

                try:
                    with open(checkpoint_path, 'r', encoding='utf-8') as f:
                        checkpoint_data = json.load(f)

                    metadata = checkpoint_data.get("metadata", {})
                    state = checkpoint_data.get("state", {})

                    checkpoints.append({
                        "path": checkpoint_path,
                        "filename": filename,
                        "saved_at": metadata.get("saved_at", "unknown"),
                        "completed_nodes": metadata.get("completed_nodes", []),
                        "source": state.get("source", "unknown"),
                        "title": state.get("title", "unknown"),
                        "paper_type": state.get("paper_type", "unknown")
                    })
                except (json.JSONDecodeError, KeyError, ValueError, IOError):
                    # Invalid checkpoint file, skip it
                    continue

        # Sort by saved_at (newest first)
        checkpoints.sort(
            key=lambda x: x.get("saved_at", ""),
            reverse=True
        )

        return checkpoints

    def delete_checkpoint(self, checkpoint_path: str) -> bool:
        """
        Delete a checkpoint file.

        Args:
            checkpoint_path: Path to the checkpoint file

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(checkpoint_path):
                os.remove(checkpoint_path)
                return True
        except OSError:
            pass
        return False

    def clear_all(self) -> int:
        """
        Delete all checkpoint files.

        Returns:
            Number of checkpoint files deleted
        """
        deleted = 0

        if not os.path.exists(self.checkpoint_dir):
            return deleted

        for filename in os.listdir(self.checkpoint_dir):
            if filename.endswith('.json'):
                checkpoint_path = os.path.join(self.checkpoint_dir, filename)
                try:
                    os.remove(checkpoint_path)
                    deleted += 1
                except OSError:
                    pass

        return deleted

    def get_checkpoint_path(self, checkpoint_name: str = "") -> str:
        """
        Get the path for a new checkpoint file (without saving).

        Args:
            checkpoint_name: Optional name for the checkpoint

        Returns:
            Path for a new checkpoint file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if checkpoint_name:
            filename = f"{checkpoint_name}_{timestamp}.json"
        else:
            filename = f"checkpoint_{timestamp}.json"

        return os.path.join(self.checkpoint_dir, filename)


# Global checkpoint manager instance
_global_checkpoint_manager: Optional[CheckpointManager] = None


def get_checkpoint_manager(checkpoint_dir: str = ".checkpoints") -> CheckpointManager:
    """
    Get or create the global checkpoint manager.

    Args:
        checkpoint_dir: Directory to store checkpoint files

    Returns:
        The global checkpoint manager instance
    """
    global _global_checkpoint_manager

    if _global_checkpoint_manager is None:
        _global_checkpoint_manager = CheckpointManager(checkpoint_dir)

    return _global_checkpoint_manager