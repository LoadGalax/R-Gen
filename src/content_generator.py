"""
ContentGenerator: A dynamic game content generation engine.

This module provides the ContentGenerator class which reads structured JSON
configuration files and generates game elements like Items, NPCs, and Locations
with randomized properties and dynamic descriptions.
"""

import json
import random
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class ContentGenerator:
    """
    Main engine for generating dynamic game content.

    Reads modular JSON configuration files and generates randomized
    Items, NPCs, and Locations with cross-referencing support.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the ContentGenerator.

        Args:
            data_dir: Path to directory containing JSON configuration files
        """
        self.data_dir = Path(data_dir)
        self.attributes = self._load_json("attributes.json")
        self.items_config = self._load_json("items.json")
        self.npcs_config = self._load_json("npcs.json")
        self.locations_config = self._load_json("locations.json")

        # Cache for generated locations to support cross-referencing
        self.generated_locations = {}

    def _load_json(self, filename: str) -> Dict:
        """Load and parse a JSON file."""
        file_path = self.data_dir / filename
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")

    def _fill_template(self, template: str, values: Dict[str, Any]) -> str:
        """
        Fill a description template with values.

        Replaces {placeholder} markers with corresponding values.
        Handles both simple replacements and indexed environment tags.

        Args:
            template: Template string with {placeholder} markers
            values: Dictionary of placeholder names to values

        Returns:
            Filled template string
        """
        result = template

        # Replace all placeholders
        for key, value in values.items():
            pattern = f"{{{key}}}"
            result = result.replace(pattern, str(value))

        # Handle any remaining unfilled placeholders by removing them
        result = re.sub(r'\{[^}]+\}', '', result)

        return result

    def _get_random_stats(self, count: int) -> Dict[str, int]:
        """
        Generate random stat modifiers.

        Args:
            count: Number of stats to generate

        Returns:
            Dictionary of stat names to values
        """
        stats = {}
        available_stats = list(self.attributes["stats"].keys())
        selected_stats = random.sample(available_stats, min(count, len(available_stats)))

        for stat_name in selected_stats:
            stat_range = self.attributes["stats"][stat_name]
            value = random.randint(stat_range["min"], stat_range["max"])
            if value != 0:  # Only include non-zero stats
                stats[stat_name] = value

        return stats

    def generate_item(self, template_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a random item based on a template.

        Args:
            template_name: Specific template to use (e.g., "weapon_melee").
                          If None, selects random template.

        Returns:
            Dictionary containing item properties including:
            - name: Full item name
            - type: Item type
            - subtype: Item subtype
            - quality: Quality level
            - rarity: Rarity level
            - stats: Stat modifiers
            - value: Gold value
            - description: Dynamic description
            - properties: Additional properties
        """
        # Select template
        if template_name is None:
            template_name = random.choice(list(self.items_config["templates"].keys()))

        template = self.items_config["templates"][template_name]

        # Generate basic properties
        base_name = random.choice(template["base_names"])
        quality = random.choice(self.attributes["quality"]) if template["has_quality"] else None
        rarity = random.choice(self.attributes["rarity"]) if template["has_rarity"] else None
        material = random.choice(self.attributes["materials"]) if template.get("has_material", False) else None

        # Generate stats
        stat_count = random.randint(
            template["stat_count"]["min"],
            template["stat_count"]["max"]
        )
        stats = self._get_random_stats(stat_count)

        # Generate value (influenced by quality and rarity)
        base_value = random.randint(
            template["value_range"]["min"],
            template["value_range"]["max"]
        )

        # Value multipliers based on quality and rarity
        quality_multipliers = {
            "Poor": 0.5, "Standard": 1.0, "Fine": 1.5,
            "Excellent": 2.0, "Masterwork": 3.0, "Legendary": 5.0
        }
        rarity_multipliers = {
            "Common": 1.0, "Uncommon": 1.5, "Rare": 2.5,
            "Epic": 4.0, "Legendary": 6.0, "Mythic": 10.0
        }

        value = int(base_value *
                   quality_multipliers.get(quality, 1.0) *
                   rarity_multipliers.get(rarity, 1.0))

        # Build full name
        name_parts = []
        if quality:
            name_parts.append(quality)
        if material:
            name_parts.append(material.capitalize())
        name_parts.append(base_name)

        full_name = " ".join(name_parts)

        # Generate damage types if applicable
        damage_types = []
        if "damage_type_count" in template:
            damage_count = random.randint(
                template["damage_type_count"]["min"],
                template["damage_type_count"]["max"]
            )
            damage_types = random.sample(
                self.attributes["damage_types"],
                min(damage_count, len(self.attributes["damage_types"]))
            )

        # Generate dynamic description
        description_template = random.choice(template["description_templates"])
        description_values = {
            "quality": quality.lower() if quality else "",
            "rarity": rarity.lower() if rarity else "",
            "material": material if material else "",
            "base_name": base_name.lower(),
            "tactile_adjective": random.choice(self.attributes["tactile_adjectives"]),
            "visual_adjective": random.choice(self.attributes["visual_adjectives"])
        }
        description = self._fill_template(description_template, description_values)

        # Build item object
        item = {
            "name": full_name,
            "type": template["type"],
            "subtype": template["subtype"],
            "quality": quality,
            "rarity": rarity,
            "stats": stats,
            "value": value,
            "description": description,
            "properties": {}
        }

        # Add optional properties
        if material:
            item["material"] = material
        if damage_types:
            item["damage_types"] = damage_types
        if template.get("consumable", False):
            item["properties"]["consumable"] = True
        if template.get("single_use", False):
            item["properties"]["single_use"] = True
        if template.get("provides_defense", False):
            item["properties"]["provides_defense"] = True

        return item

    def generate_items_from_set(self, set_name: str, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate multiple items from a predefined item set.

        Args:
            set_name: Name of the item set (e.g., "blacksmith_inventory")
            count: Number of items to generate. If None, generates 1-5 items.

        Returns:
            List of generated item dictionaries
        """
        if set_name not in self.items_config["item_sets"]:
            raise ValueError(f"Unknown item set: {set_name}")

        template_list = self.items_config["item_sets"][set_name]
        if count is None:
            count = random.randint(1, 5)

        items = []
        for _ in range(count):
            template = random.choice(template_list)
            items.append(self.generate_item(template))

        return items

    def generate_npc(self, archetype_name: Optional[str] = None,
                    location_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a random NPC based on an archetype.

        Args:
            archetype_name: Specific archetype to use (e.g., "blacksmith").
                           If None, selects random archetype.
            location_id: ID of the location where this NPC resides.

        Returns:
            Dictionary containing NPC properties including:
            - name: Full NPC name
            - title: NPC title/role
            - archetype: Base archetype
            - stats: Stat values
            - skills: List of skills
            - dialogue: Random dialogue hook
            - description: Dynamic description
            - inventory: List of items
            - location: Location ID reference
        """
        # Select archetype
        if archetype_name is None:
            archetype_name = random.choice(list(self.npcs_config["archetypes"].keys()))

        archetype = self.npcs_config["archetypes"][archetype_name]

        # Generate name
        first_name = random.choice(archetype["first_names"])
        last_name = random.choice(archetype["last_names"])
        full_name = f"{first_name} {last_name}"

        # Get base stats (could add random variation)
        stats = archetype["base_stats"].copy()

        # Add some random variation to stats (-1 to +1)
        for stat in stats:
            variation = random.randint(-1, 1)
            stats[stat] = max(1, stats[stat] + variation)

        # Select dialogue hook
        dialogue = random.choice(archetype["dialogue_hooks"])

        # Generate description
        description_template = random.choice(archetype["description_templates"])
        description_values = {
            "trait": random.choice(self.attributes["npc_traits"]),
            "title": archetype["title"].lower(),
            "tactile_adjective": random.choice(self.attributes["tactile_adjectives"]),
            "visual_adjective": random.choice(self.attributes["visual_adjectives"])
        }
        description = self._fill_template(description_template, description_values)

        # Generate inventory based on inventory set
        inventory = []
        if "inventory_set" in archetype:
            inventory = self.generate_items_from_set(
                archetype["inventory_set"],
                count=random.randint(2, 6)
            )

        # Build NPC object
        npc = {
            "name": full_name,
            "title": archetype["title"],
            "archetype": archetype_name,
            "stats": stats,
            "skills": archetype["skills"].copy(),
            "dialogue": dialogue,
            "description": description,
            "inventory": inventory
        }

        # Add location reference if provided
        if location_id:
            npc["location"] = location_id

        return npc

    def generate_location(self, template_name: Optional[str] = None,
                         generate_connections: bool = True,
                         max_connections: int = 3) -> Dict[str, Any]:
        """
        Generate a random location based on a template.

        Args:
            template_name: Specific template to use (e.g., "forest_clearing").
                          If None, selects random template.
            generate_connections: Whether to generate connected locations.
            max_connections: Maximum number of connections to generate.

        Returns:
            Dictionary containing location properties including:
            - id: Unique location identifier
            - name: Location name
            - type: Location type
            - environment_tags: List of environment descriptors
            - description: Dynamic description
            - connections: Map of connected location IDs
            - npcs: List of NPCs in this location
            - items: List of items in this location
        """
        # Select template
        if template_name is None:
            template_name = random.choice(list(self.locations_config["templates"].keys()))

        template = self.locations_config["templates"][template_name]

        # Generate unique ID
        location_id = f"{template_name}_{random.randint(1000, 9999)}"

        # Generate environment tags
        environment_tags = template["base_environment_tags"].copy()
        additional_tag_count = random.randint(
            template["additional_tags_count"]["min"],
            template["additional_tags_count"]["max"]
        )

        # Add random additional tags
        available_tags = [tag for tag in self.attributes["environment_tags"]
                         if tag not in environment_tags]
        additional_tags = random.sample(
            available_tags,
            min(additional_tag_count, len(available_tags))
        )
        environment_tags.extend(additional_tags)

        # Generate description
        description_template = random.choice(template["description_templates"])
        description_values = {
            "visual_adjective": random.choice(self.attributes["visual_adjectives"]),
            "tactile_adjective": random.choice(self.attributes["tactile_adjectives"]),
        }

        # Add indexed environment tags for template
        for i, tag in enumerate(environment_tags[:3], 1):
            description_values[f"environment_tag_{i}"] = tag.lower()

        description = self._fill_template(description_template, description_values)

        # Generate NPCs
        npc_count = random.randint(
            template["npc_spawn_count"]["min"],
            template["npc_spawn_count"]["max"]
        )
        npcs = []
        for _ in range(npc_count):
            npc_archetype = random.choice(template["spawnable_npcs"])
            npc = self.generate_npc(npc_archetype, location_id)
            npcs.append(npc)

        # Generate items
        item_count = random.randint(
            template["item_spawn_count"]["min"],
            template["item_spawn_count"]["max"]
        )
        items = []
        for _ in range(item_count):
            item_template = random.choice(template["spawnable_items"])
            item = self.generate_item(item_template)
            items.append(item)

        # Build location object
        location = {
            "id": location_id,
            "name": template["name"],
            "type": template["type"],
            "environment_tags": environment_tags,
            "description": description,
            "npcs": npcs,
            "items": items,
            "connections": {}
        }

        # Store in cache
        self.generated_locations[location_id] = location

        # Generate connections if requested
        if generate_connections:
            connection_count = random.randint(1, min(max_connections, len(template["can_connect_to"])))
            connection_types = random.sample(template["can_connect_to"], connection_count)

            for conn_type in connection_types:
                # Check if we already have a generated location of this type
                existing = [loc for loc in self.generated_locations.values()
                          if conn_type in loc["id"]]

                if existing and random.random() > 0.5:  # 50% chance to reuse existing
                    connected_loc = random.choice(existing)
                    location["connections"][conn_type] = connected_loc["id"]
                else:
                    # Generate new connected location (without further connections to avoid recursion)
                    connected_loc = self.generate_location(conn_type, generate_connections=False)
                    location["connections"][conn_type] = connected_loc["id"]

        return location

    def generate_world(self, num_locations: int = 5) -> Dict[str, Any]:
        """
        Generate a connected world with multiple locations.

        Args:
            num_locations: Number of main locations to generate

        Returns:
            Dictionary containing:
            - locations: Dict of location_id to location data
            - world_map: Summary of connections
        """
        # Clear location cache
        self.generated_locations = {}

        # Generate main locations
        main_locations = []
        for _ in range(num_locations):
            loc = self.generate_location(generate_connections=True, max_connections=2)
            main_locations.append(loc)

        # Build world map summary
        world_map = {}
        for loc_id, loc_data in self.generated_locations.items():
            world_map[loc_id] = {
                "name": loc_data["name"],
                "type": loc_data["type"],
                "connections": list(loc_data["connections"].values()),
                "npc_count": len(loc_data["npcs"]),
                "item_count": len(loc_data["items"])
            }

        return {
            "locations": self.generated_locations,
            "world_map": world_map
        }

    def export_to_json(self, data: Any, filename: str) -> None:
        """
        Export generated content to a JSON file.

        Args:
            data: Data to export
            filename: Output filename
        """
        output_path = Path(filename)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Exported to {output_path}")
