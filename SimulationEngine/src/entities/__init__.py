"""
Entity classes for simulation
"""

from .base_entity import BaseEntity
from .npc import LivingNPC
from .location import LivingLocation

__all__ = [
    "BaseEntity",
    "LivingNPC",
    "LivingLocation",
]
