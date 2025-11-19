"""
Base Entity Class

Abstract base for all simulation entities.
"""

from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import uuid


class BaseEntity(ABC):
    """
    Base class for all entities in the simulation.

    Provides common functionality like:
    - Unique ID generation
    - State management
    - Update lifecycle
    - Serialization
    """

    def __init__(self, entity_id: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        """
        Initialize entity.

        Args:
            entity_id: Unique identifier (generated if not provided)
            data: Initial entity data
        """
        self.id = entity_id or str(uuid.uuid4())
        self.data = data or {}
        self.active = True
        self.created_at = 0  # Set by world when added
        self.last_update = 0

    @abstractmethod
    def update(self, delta_time: float, world_context: Any):
        """
        Update entity state.

        Called each simulation tick.

        Args:
            delta_time: Time elapsed since last update (in simulation minutes)
            world_context: Reference to the world
        """
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize entity to dictionary.

        Returns:
            Dictionary representation
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any], world_context: Any) -> 'BaseEntity':
        """
        Deserialize entity from dictionary.

        Args:
            data: Dictionary data
            world_context: Reference to the world

        Returns:
            Entity instance
        """
        pass

    def destroy(self):
        """Mark entity as inactive/destroyed"""
        self.active = False

    def is_active(self) -> bool:
        """Check if entity is active"""
        return self.active

    def get_id(self) -> str:
        """Get entity ID"""
        return self.id

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
