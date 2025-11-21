"""
Game Source Module - Self-contained game logic

Includes:
- ContentGenerator for dynamic content generation
- World simulation system (World, NPCs, Locations)
- All game logic independent of external engines
"""

# Content Generation
from .content_generator import ContentGenerator

# World Simulation
from .core.world import World
from .core.time_manager import TimeManager
from .core.event_system import EventSystem, Event, EventTypes
from .core.state_manager import StateManager
from .simulation.simulator import WorldSimulator
from .entities.npc import LivingNPC
from .entities.location import LivingLocation
from .integration.generator_adapter import GeneratorAdapter
from .integration.entity_factory import EntityFactory

__version__ = "1.0.0"
__all__ = [
    "ContentGenerator",
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
