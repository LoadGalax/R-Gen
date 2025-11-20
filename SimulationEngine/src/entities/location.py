"""
Living Location Entity

Locations with dynamic state and spawning.
"""

from typing import Optional, Dict, Any, List, Set
from .base_entity import BaseEntity


class LivingLocation(BaseEntity):
    """
    Location with dynamic state.

    Features:
    - Track NPCs present
    - Track items present
    - Dynamic weather
    - Market state (if applicable)
    - Events/activities
    """

    def __init__(self, entity_id: Optional[str] = None,
                 data: Optional[Dict[str, Any]] = None,
                 world_context: Any = None):
        """
        Initialize living location.

        Args:
            entity_id: Unique ID
            data: Generated location data from GenerationEngine
            world_context: Reference to world
        """
        super().__init__(entity_id, data)
        self.world = world_context

        # Dynamic state
        self.npc_ids: Set[str] = set()  # NPCs currently at this location
        self.item_ids: Set[str] = set()  # Items at this location
        self.current_weather = None
        self.market_open = False
        self.last_spawn_check = 0

    def update(self, delta_time: float, world_context: Any):
        """
        Update location state.

        Args:
            delta_time: Minutes elapsed
            world_context: Reference to world
        """
        if not self.active:
            return

        self.world = world_context
        self.last_update += delta_time

        # Update weather periodically
        if self.last_update % 60 < delta_time:  # Every hour
            self._update_weather()

        # Update market status
        self._update_market()

    def _update_weather(self):
        """Update weather conditions"""
        if self.world and self.world.generator_adapter:
            biome = self.data.get("biome", "temperate_forest")
            season = self.world.time_manager.current_season
            time_of_day = self.world.time_manager.current_time_of_day

            # Convert season to lowercase and map "Fall" to "autumn"
            season_map = {
                "Spring": "spring",
                "Summer": "summer",
                "Fall": "autumn",
                "Winter": "winter"
            }
            season_lower = season_map.get(season, season.lower())

            self.current_weather = self.world.generator_adapter.generate_weather(
                biome=biome,
                season=season_lower,
                time_of_day=time_of_day
            )

    def _update_market(self):
        """Update market status based on time"""
        if not self.world:
            return

        location_type = self.data.get("type", "")

        # Markets are open during working hours
        if location_type in ["building", "market"]:
            should_be_open = self.world.time_manager.is_working_hours

            if should_be_open and not self.market_open:
                self.market_open = True
                self.world.event_system.publish_event(
                    "market_opened",
                    location_id=self.id,
                    data={"location_name": self.get_name()}
                )
            elif not should_be_open and self.market_open:
                self.market_open = False
                self.world.event_system.publish_event(
                    "market_closed",
                    location_id=self.id,
                    data={"location_name": self.get_name()}
                )

    def add_npc(self, npc_id: str):
        """
        Add NPC to location.

        Args:
            npc_id: NPC entity ID
        """
        self.npc_ids.add(npc_id)

        if self.world:
            self.world.event_system.publish_event(
                "npc_entered_location",
                source_id=npc_id,
                location_id=self.id,
                data={"location_name": self.get_name()}
            )

    def remove_npc(self, npc_id: str):
        """
        Remove NPC from location.

        Args:
            npc_id: NPC entity ID
        """
        self.npc_ids.discard(npc_id)

        if self.world:
            self.world.event_system.publish_event(
                "npc_exited_location",
                source_id=npc_id,
                location_id=self.id,
                data={"location_name": self.get_name()}
            )

    def add_item(self, item_id: str):
        """Add item to location"""
        self.item_ids.add(item_id)

    def remove_item(self, item_id: str):
        """Remove item from location"""
        self.item_ids.discard(item_id)

    def get_npc_count(self) -> int:
        """Get number of NPCs at location"""
        return len(self.npc_ids)

    def get_name(self) -> str:
        """Get location name"""
        return self.data.get("name", "Unknown Location") if self.data else "Unknown Location"

    def get_type(self) -> str:
        """Get location type"""
        return self.data.get("type", "unknown") if self.data else "unknown"

    def get_biome(self) -> str:
        """Get location biome"""
        return self.data.get("biome", "temperate_forest") if self.data else "temperate_forest"

    def get_connections(self) -> Dict[str, str]:
        """Get connected location IDs"""
        return self.data.get("connections", {}) if self.data else {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize location to dictionary"""
        return {
            "id": self.id,
            "data": self.data,
            "npc_ids": list(self.npc_ids),
            "item_ids": list(self.item_ids),
            "current_weather": self.current_weather,
            "market_open": self.market_open,
            "last_spawn_check": self.last_spawn_check,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], world_context: Any) -> 'LivingLocation':
        """Deserialize location from dictionary"""
        location = cls(
            entity_id=data["id"],
            data=data["data"],
            world_context=world_context
        )

        location.npc_ids = set(data.get("npc_ids", []))
        location.item_ids = set(data.get("item_ids", []))
        location.current_weather = data.get("current_weather")
        location.market_open = data.get("market_open", False)
        location.last_spawn_check = data.get("last_spawn_check", 0)
        location.active = data.get("active", True)

        return location
