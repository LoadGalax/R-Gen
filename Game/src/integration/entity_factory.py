"""
Entity Factory

Converts generated data from GenerationEngine into living simulation entities.
"""

from typing import Dict, Any, Optional
from ..entities.npc import LivingNPC
from ..entities.location import LivingLocation


class EntityFactory:
    """
    Factory for creating living entities from generated data.

    Converts static dictionaries from GenerationEngine into
    dynamic entity objects with behaviors and state.
    """

    @staticmethod
    def create_npc(npc_data: Dict[str, Any], world_context: Any,
                   entity_id: Optional[str] = None) -> LivingNPC:
        """
        Convert generated NPC data to LivingNPC instance.

        Args:
            npc_data: NPC dictionary from GenerationEngine
            world_context: Reference to World instance
            entity_id: Optional custom entity ID

        Returns:
            LivingNPC instance
        """
        return LivingNPC(
            entity_id=entity_id or npc_data.get("id"),
            data=npc_data,
            world_context=world_context
        )

    @staticmethod
    def create_location(location_data: Dict[str, Any], world_context: Any,
                       entity_id: Optional[str] = None) -> LivingLocation:
        """
        Convert generated location data to LivingLocation instance.

        Args:
            location_data: Location dictionary from GenerationEngine
            world_context: Reference to World instance
            entity_id: Optional custom entity ID

        Returns:
            LivingLocation instance
        """
        return LivingLocation(
            entity_id=entity_id or location_data.get("id"),
            data=location_data,
            world_context=world_context
        )

    @staticmethod
    def create_world_from_generated(world_data: Dict[str, Any], world_context: Any):
        """
        Convert entire generated world to living entities.

        Args:
            world_data: World dictionary from GenerationEngine
            world_context: Reference to World instance

        Returns:
            Dictionary with locations and npcs
        """
        locations = {}
        npcs = []

        # Convert all locations
        for loc_id, loc_data in world_data.get("locations", {}).items():
            living_loc = EntityFactory.create_location(
                loc_data,
                world_context,
                entity_id=loc_id
            )
            locations[loc_id] = living_loc

            # Convert NPCs within location
            for npc_data in loc_data.get("npcs", []):
                npc_data["location"] = loc_id  # Ensure location is set
                living_npc = EntityFactory.create_npc(npc_data, world_context)
                npcs.append(living_npc)

                # Add NPC to location
                living_loc.add_npc(living_npc.id)

        return {
            "locations": locations,
            "npcs": npcs
        }
