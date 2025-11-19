"""
World Class

Main container for the living simulation.
"""

from typing import Dict, List, Optional, Any
from .time_manager import TimeManager
from .event_system import EventSystem, EventTypes
from .state_manager import StateManager
from ..integration.generator_adapter import GeneratorAdapter
from ..integration.entity_factory import EntityFactory
from ..entities.npc import LivingNPC
from ..entities.location import LivingLocation


class World:
    """
    Main world simulation container.

    Manages:
    - All living entities (NPCs, locations, etc.)
    - Time progression
    - Event system
    - State persistence
    - Integration with GenerationEngine
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize world.

        Args:
            seed: Random seed for generation
        """
        # Core systems
        self.time_manager = TimeManager()
        self.event_system = EventSystem()
        self.state_manager = StateManager()
        self.generator_adapter = GeneratorAdapter(seed=seed)

        # Entity storage
        self.locations: Dict[str, LivingLocation] = {}
        self.npcs: Dict[str, LivingNPC] = {}

        # World metadata
        self.seed = seed
        self.name = "New World"
        self.description = ""

        # Stats
        self.total_simulation_time = 0  # Total minutes simulated

    @classmethod
    def create_new(cls, num_locations: int = 10, seed: Optional[int] = None,
                   name: str = "New World") -> 'World':
        """
        Create a new world with generated content.

        Args:
            num_locations: Number of locations to generate
            seed: Random seed
            name: World name

        Returns:
            New World instance
        """
        world = cls(seed=seed)
        world.name = name

        # Generate initial world data
        print(f"Generating world with {num_locations} locations...")
        world_data = world.generator_adapter.create_initial_world(num_locations)

        # Convert to living entities
        print("Converting to living entities...")
        entities = EntityFactory.create_world_from_generated(world_data, world)

        # Add to world
        world.locations = entities["locations"]
        for npc in entities["npcs"]:
            world.npcs[npc.id] = npc

        print(f"World created with {len(world.locations)} locations and {len(world.npcs)} NPCs")

        # Publish world creation event
        world.event_system.publish_event(
            EventTypes.LOCATION_CREATED,
            data={
                "world_name": name,
                "num_locations": len(world.locations),
                "num_npcs": len(world.npcs)
            }
        )

        return world

    def update(self, delta_time: float):
        """
        Update all entities in the world.

        Args:
            delta_time: Minutes to advance simulation
        """
        # Advance time
        self.time_manager.advance_minutes(int(delta_time))
        self.total_simulation_time += delta_time

        # Update all locations
        for location in self.locations.values():
            location.update(delta_time, self)

        # Update all NPCs
        for npc in self.npcs.values():
            npc.update(delta_time, self)

        # Process events
        self.event_system.process_events()

        # Check for hour/day transitions
        self._check_time_events()

    def _check_time_events(self):
        """Check for significant time events"""
        current_hour = self.time_manager.current_hour
        current_day = self.time_manager.current_day

        # Hour passed event
        if hasattr(self, '_last_hour'):
            if current_hour != self._last_hour:
                self.event_system.publish_event(
                    EventTypes.HOUR_PASSED,
                    data={"hour": current_hour}
                )
        self._last_hour = current_hour

        # Day passed event
        if hasattr(self, '_last_day'):
            if current_day != self._last_day:
                self.event_system.publish_event(
                    EventTypes.DAY_PASSED,
                    data={"day": current_day}
                )
        self._last_day = current_day

    def step(self, minutes: int = 1):
        """
        Advance simulation by specified minutes.

        Args:
            minutes: Number of simulation minutes to advance
        """
        self.update(float(minutes))

    def simulate_hours(self, hours: int):
        """Simulate N hours"""
        self.update(float(hours * 60))

    def simulate_days(self, days: int):
        """Simulate N days"""
        self.update(float(days * 24 * 60))

    def get_location(self, location_id: str) -> Optional[LivingLocation]:
        """Get location by ID"""
        return self.locations.get(location_id)

    def get_npc(self, npc_id: str) -> Optional[LivingNPC]:
        """Get NPC by ID"""
        return self.npcs.get(npc_id)

    def get_npcs_at_location(self, location_id: str) -> List[LivingNPC]:
        """Get all NPCs at a specific location"""
        return [npc for npc in self.npcs.values()
                if npc.current_location_id == location_id]

    def get_active_npcs(self) -> List[LivingNPC]:
        """Get all active NPCs"""
        return [npc for npc in self.npcs.values() if npc.active]

    def spawn_npc(self, location_id: str, professions: Optional[List[str]] = None,
                  race: Optional[str] = None) -> LivingNPC:
        """
        Spawn a new NPC at specified location.

        Args:
            location_id: Where to spawn
            professions: NPC professions
            race: NPC race

        Returns:
            New LivingNPC instance
        """
        # Generate NPC data
        npc_data = self.generator_adapter.spawn_npc(
            professions=professions,
            race=race,
            location_id=location_id
        )

        # Create living NPC
        npc = EntityFactory.create_npc(npc_data, self)

        # Add to world
        self.npcs[npc.id] = npc

        # Add to location
        if location_id in self.locations:
            self.locations[location_id].add_npc(npc.id)

        # Publish event
        self.event_system.publish_event(
            EventTypes.NPC_SPAWNED,
            source_id=npc.id,
            location_id=location_id,
            data={"npc_name": npc.get_name(), "profession": npc.get_profession()}
        )

        return npc

    def remove_npc(self, npc_id: str):
        """Remove NPC from world"""
        if npc_id in self.npcs:
            npc = self.npcs[npc_id]

            # Remove from location
            if npc.current_location_id and npc.current_location_id in self.locations:
                self.locations[npc.current_location_id].remove_npc(npc_id)

            # Remove from world
            del self.npcs[npc_id]

            # Publish event
            self.event_system.publish_event(
                EventTypes.NPC_DIED,
                source_id=npc_id,
                data={"npc_name": npc.get_name()}
            )

    def get_world_summary(self) -> Dict[str, Any]:
        """
        Get summary of world state.

        Returns:
            Dictionary with world statistics
        """
        return {
            "name": self.name,
            "time": self.time_manager.get_full_datetime_string(),
            "total_simulation_time": self.total_simulation_time,
            "locations": len(self.locations),
            "npcs": len(self.npcs),
            "active_npcs": len(self.get_active_npcs()),
            "events_in_queue": self.event_system.get_queue_size(),
            "recent_events": len(self.event_system.get_recent_events()),
        }

    def save(self, filename: str, format: str = "json", compressed: bool = True) -> str:
        """
        Save world state to file.

        Args:
            filename: Name of save file
            format: "json" or "pickle"
            compressed: Whether to compress

        Returns:
            Path to save file
        """
        world_state = self.to_dict()

        if format == "json":
            return self.state_manager.save_json(world_state, filename, compressed)
        elif format == "pickle":
            return self.state_manager.save_pickle(self, filename, compressed)
        else:
            raise ValueError(f"Unknown format: {format}")

    @classmethod
    def load(cls, filename: str, format: str = "json") -> 'World':
        """
        Load world state from file.

        Args:
            filename: Name of save file
            format: "json" or "pickle"

        Returns:
            World instance
        """
        state_manager = StateManager()

        if format == "json":
            world_state = state_manager.load_json(filename)
            return cls.from_dict(world_state)
        elif format == "pickle":
            return state_manager.load_pickle(filename)
        else:
            raise ValueError(f"Unknown format: {format}")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize world to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "seed": self.seed,
            "total_simulation_time": self.total_simulation_time,
            "time_manager": self.time_manager.to_dict(),
            "event_system": self.event_system.to_dict(),
            "locations": {
                loc_id: loc.to_dict()
                for loc_id, loc in self.locations.items()
            },
            "npcs": {
                npc_id: npc.to_dict()
                for npc_id, npc in self.npcs.items()
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'World':
        """Deserialize world from dictionary"""
        world = cls(seed=data.get("seed"))
        world.name = data.get("name", "Loaded World")
        world.description = data.get("description", "")
        world.total_simulation_time = data.get("total_simulation_time", 0)

        # Restore time manager
        world.time_manager = TimeManager.from_dict(data["time_manager"])

        # Restore locations
        for loc_id, loc_data in data.get("locations", {}).items():
            world.locations[loc_id] = LivingLocation.from_dict(loc_data, world)

        # Restore NPCs
        for npc_id, npc_data in data.get("npcs", {}).items():
            world.npcs[npc_id] = LivingNPC.from_dict(npc_data, world)

        return world

    def __repr__(self):
        return (f"World(name='{self.name}', locations={len(self.locations)}, "
                f"npcs={len(self.npcs)}, time={self.time_manager.get_time_string()})")
