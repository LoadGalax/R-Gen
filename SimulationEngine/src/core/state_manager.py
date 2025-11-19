"""
State Management System

Handles saving and loading of world simulation state.
"""

import json
import pickle
import gzip
from pathlib import Path
from typing import Optional, Any, Dict
from datetime import datetime


class StateManager:
    """
    Manages serialization and deserialization of world state.

    Supports:
    - JSON format (human-readable, no custom objects)
    - Pickle format (full Python objects, faster)
    - Compressed saves (gzip)
    - Autosave functionality
    - State versioning
    """

    VERSION = "1.0.0"

    def __init__(self, save_directory: str = "saves"):
        """
        Initialize state manager.

        Args:
            save_directory: Directory to store save files
        """
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)

        # Autosave settings
        self.autosave_enabled = False
        self.autosave_interval = 300  # seconds
        self.last_autosave = None

    def save_json(self, world_state: Dict[str, Any], filename: str,
                  compressed: bool = False) -> str:
        """
        Save world state as JSON.

        Args:
            world_state: Dictionary containing world state
            filename: Name of save file (without extension)
            compressed: Whether to compress the file

        Returns:
            Path to saved file
        """
        # Add metadata
        save_data = {
            "version": self.VERSION,
            "timestamp": datetime.now().isoformat(),
            "compressed": compressed,
            "world_state": world_state
        }

        # Determine file extension
        ext = ".json.gz" if compressed else ".json"
        filepath = self.save_directory / f"{filename}{ext}"

        # Save
        if compressed:
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2)

        return str(filepath)

    def load_json(self, filename: str) -> Dict[str, Any]:
        """
        Load world state from JSON.

        Args:
            filename: Name of save file (with or without extension)

        Returns:
            World state dictionary
        """
        # Try different extensions
        filepath = None
        for ext in [".json", ".json.gz", ""]:
            test_path = self.save_directory / f"{filename}{ext}"
            if test_path.exists():
                filepath = test_path
                break

        if filepath is None:
            raise FileNotFoundError(f"Save file not found: {filename}")

        # Load based on compression
        if filepath.suffix == ".gz":
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                save_data = json.load(f)
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

        # Validate version
        version = save_data.get("version", "unknown")
        if version != self.VERSION:
            print(f"Warning: Save file version {version} differs from current {self.VERSION}")

        return save_data["world_state"]

    def save_pickle(self, world_object: Any, filename: str,
                   compressed: bool = True) -> str:
        """
        Save world state as pickle (supports complex Python objects).

        Args:
            world_object: World object to save
            filename: Name of save file
            compressed: Whether to compress

        Returns:
            Path to saved file
        """
        ext = ".pkl.gz" if compressed else ".pkl"
        filepath = self.save_directory / f"{filename}{ext}"

        # Create save data with metadata
        save_data = {
            "version": self.VERSION,
            "timestamp": datetime.now().isoformat(),
            "world": world_object
        }

        if compressed:
            with gzip.open(filepath, 'wb') as f:
                pickle.dump(save_data, f, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open(filepath, 'wb') as f:
                pickle.dump(save_data, f, protocol=pickle.HIGHEST_PROTOCOL)

        return str(filepath)

    def load_pickle(self, filename: str) -> Any:
        """
        Load world state from pickle.

        Args:
            filename: Name of save file

        Returns:
            World object
        """
        # Try different extensions
        filepath = None
        for ext in [".pkl", ".pkl.gz", ""]:
            test_path = self.save_directory / f"{filename}{ext}"
            if test_path.exists():
                filepath = test_path
                break

        if filepath is None:
            raise FileNotFoundError(f"Save file not found: {filename}")

        # Load based on compression
        if filepath.suffix == ".gz":
            with gzip.open(filepath, 'rb') as f:
                save_data = pickle.load(f)
        else:
            with open(filepath, 'rb') as f:
                save_data = pickle.load(f)

        # Validate version
        version = save_data.get("version", "unknown")
        if version != self.VERSION:
            print(f"Warning: Save file version {version} differs from current {self.VERSION}")

        return save_data["world"]

    def list_saves(self) -> list:
        """
        List all save files.

        Returns:
            List of save file information
        """
        saves = []

        for filepath in self.save_directory.glob("*"):
            if filepath.suffix in [".json", ".pkl", ".gz"]:
                saves.append({
                    "name": filepath.stem,
                    "path": str(filepath),
                    "size": filepath.stat().st_size,
                    "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                    "format": "pickle" if ".pkl" in filepath.name else "json",
                    "compressed": ".gz" in filepath.name
                })

        return sorted(saves, key=lambda x: x["modified"], reverse=True)

    def delete_save(self, filename: str) -> bool:
        """
        Delete a save file.

        Args:
            filename: Name of save file

        Returns:
            True if deleted, False if not found
        """
        # Try different extensions
        for ext in [".json", ".json.gz", ".pkl", ".pkl.gz", ""]:
            filepath = self.save_directory / f"{filename}{ext}"
            if filepath.exists():
                filepath.unlink()
                return True

        return False

    def autosave(self, world_state: Dict[str, Any], name_prefix: str = "autosave") -> Optional[str]:
        """
        Perform autosave if enabled and interval has passed.

        Args:
            world_state: World state to save
            name_prefix: Prefix for autosave filename

        Returns:
            Path to save file if autosave occurred, None otherwise
        """
        if not self.autosave_enabled:
            return None

        now = datetime.now()

        # Check if enough time has passed
        if self.last_autosave is not None:
            elapsed = (now - self.last_autosave).total_seconds()
            if elapsed < self.autosave_interval:
                return None

        # Perform autosave
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"{name_prefix}_{timestamp}"
        filepath = self.save_json(world_state, filename, compressed=True)

        self.last_autosave = now

        # Keep only last N autosaves
        self._cleanup_autosaves(name_prefix, keep=5)

        return filepath

    def _cleanup_autosaves(self, prefix: str, keep: int = 5):
        """
        Remove old autosave files, keeping only the most recent.

        Args:
            prefix: Autosave filename prefix
            keep: Number of autosaves to keep
        """
        autosaves = []
        for filepath in self.save_directory.glob(f"{prefix}_*"):
            autosaves.append((filepath, filepath.stat().st_mtime))

        # Sort by modification time (newest first)
        autosaves.sort(key=lambda x: x[1], reverse=True)

        # Delete old autosaves
        for filepath, _ in autosaves[keep:]:
            filepath.unlink()

    def enable_autosave(self, interval_seconds: int = 300):
        """
        Enable autosaving.

        Args:
            interval_seconds: Seconds between autosaves
        """
        self.autosave_enabled = True
        self.autosave_interval = interval_seconds
        self.last_autosave = datetime.now()

    def disable_autosave(self):
        """Disable autosaving"""
        self.autosave_enabled = False
