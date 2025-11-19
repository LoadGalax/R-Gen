"""
R-Gen Simulation Engine

Living world simulation system.
"""

from .core.world import World
from .core.time_manager import TimeManager
from .core.event_system import EventSystem, Event, EventTypes
from .core.state_manager import StateManager
from .simulation.simulator import WorldSimulator
from .entities.npc import LivingNPC
from .entities.location import LivingLocation
from .integration.generator_adapter import GeneratorAdapter
from .integration.entity_factory import EntityFactory

__version__ = "0.1.0"
__all__ = [
    "World",
    "TimeManager",
    "EventSystem",
    "Event",
    "EventTypes",
    "StateManager",
    "WorldSimulator",
    "LivingNPC",
    "LivingLocation",
    "GeneratorAdapter",
    "EntityFactory",
]
