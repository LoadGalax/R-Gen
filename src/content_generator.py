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

    def __init__(self, data_dir: str = "data", seed: Optional[int] = None):
        """
        Initialize the ContentGenerator.

        Args:
            data_dir: Path to directory containing JSON configuration files
            seed: Random seed for reproducible generation. If None, uses system random.
        """
        self.data_dir = Path(data_dir)
        self.seed = seed
        self.rng = random.Random(seed)  # Dedicated random number generator

        self.attributes = self._load_json("attributes.json")
        self.items_config = self._load_json("items.json")
        self.npcs_config = self._load_json("npcs.json")
        self.locations_config = self._load_json("locations.json")

        # Load new configuration files
        self.biomes_config = self._load_json("biomes.json")
        self.factions_config = self._load_json("factions.json")
        self.races_config = self._load_json("races.json")

        # Cache for generated locations to support cross-referencing
        self.generated_locations = {}

    def reset_seed(self, seed: Optional[int] = None):
        """
        Reset the random seed for reproducible generation.

        Args:
            seed: New random seed. If None, uses the original seed.
        """
        if seed is not None:
            self.seed = seed
        self.rng = random.Random(self.seed)
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

    def _weighted_choice(self, weighted_dict: Dict[str, Dict]) -> str:
        """
        Make a weighted random choice from a dictionary.

        Args:
            weighted_dict: Dictionary with items containing 'weight' keys

        Returns:
            Randomly selected key based on weights
        """
        items = list(weighted_dict.keys())
        weights = [weighted_dict[item].get("weight", 1.0) for item in items]
        return self.rng.choices(items, weights=weights, k=1)[0]

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
        selected_stats = self.rng.sample(available_stats, min(count, len(available_stats)))

        for stat_name in selected_stats:
            stat_range = self.attributes["stats"][stat_name]
            value = self.rng.randint(stat_range["min"], stat_range["max"])
            if value != 0:  # Only include non-zero stats
                stats[stat_name] = value

        return stats

    def generate_item(self, template_name: Optional[str] = None, constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a random item based on a template.

        Args:
            template_name: Specific template to use (e.g., "weapon_melee").
                          If None, selects random template.
            constraints: Optional constraints for generation:
                - min_quality: Minimum quality level
                - max_quality: Maximum quality level
                - min_rarity: Minimum rarity level
                - max_rarity: Maximum rarity level
                - required_stats: List of required stat names
                - exclude_materials: List of materials to exclude
                - min_value: Minimum item value
                - max_value: Maximum item value

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
        constraints = constraints or {}
        max_attempts = 100  # Prevent infinite loops

        for attempt in range(max_attempts):
            # Select template
            if template_name is None:
                template_name = self.rng.choice(list(self.items_config["templates"].keys()))

            template = self.items_config["templates"][template_name]

            # Generate basic properties with constraints
            base_name = self.rng.choice(template["base_names"])

            # Generate quality with weighted probability
            if template["has_quality"]:
                quality = self._weighted_choice(self.attributes["quality"])
            else:
                quality = None

            # Generate rarity with weighted probability
            if template["has_rarity"]:
                rarity = self._weighted_choice(self.attributes["rarity"])
            else:
                rarity = None

            # Generate material with constraints
            if template.get("has_material", False):
                available_materials = [m for m in self.attributes["materials"]
                                     if m not in constraints.get("exclude_materials", [])]
                if available_materials:
                    material = self.rng.choice(available_materials)
                else:
                    material = None
            else:
                material = None

            # Generate stats
            stat_count = self.rng.randint(
                template["stat_count"]["min"],
                template["stat_count"]["max"]
            )
            stats = self._get_random_stats(stat_count)

            # Add required stats if specified
            if "required_stats" in constraints:
                for req_stat in constraints["required_stats"]:
                    if req_stat not in stats and req_stat in self.attributes["stats"]:
                        stat_range = self.attributes["stats"][req_stat]
                        stats[req_stat] = self.rng.randint(stat_range["min"], stat_range["max"])

            # Generate value (influenced by quality and rarity)
            base_value = self.rng.randint(
                template["value_range"]["min"],
                template["value_range"]["max"]
            )

            # Get multipliers from config
            quality_multiplier = self.attributes["quality"].get(quality, {}).get("multiplier", 1.0) if quality else 1.0
            rarity_multiplier = self.attributes["rarity"].get(rarity, {}).get("multiplier", 1.0) if rarity else 1.0

            value = int(base_value * quality_multiplier * rarity_multiplier)

            # Check constraints
            quality_order = list(self.attributes["quality"].keys())
            rarity_order = list(self.attributes["rarity"].keys())

            # Check quality constraints
            if "min_quality" in constraints:
                min_idx = quality_order.index(constraints["min_quality"])
                if quality and quality_order.index(quality) < min_idx:
                    continue

            if "max_quality" in constraints:
                max_idx = quality_order.index(constraints["max_quality"])
                if quality and quality_order.index(quality) > max_idx:
                    continue

            # Check rarity constraints
            if "min_rarity" in constraints:
                min_idx = rarity_order.index(constraints["min_rarity"])
                if rarity and rarity_order.index(rarity) < min_idx:
                    continue

            if "max_rarity" in constraints:
                max_idx = rarity_order.index(constraints["max_rarity"])
                if rarity and rarity_order.index(rarity) > max_idx:
                    continue

            # Check value constraints
            if "min_value" in constraints and value < constraints["min_value"]:
                continue
            if "max_value" in constraints and value > constraints["max_value"]:
                continue

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
                damage_count = self.rng.randint(
                    template["damage_type_count"]["min"],
                    template["damage_type_count"]["max"]
                )
                damage_types = self.rng.sample(
                    self.attributes["damage_types"],
                    min(damage_count, len(self.attributes["damage_types"]))
                )

            # Generate dynamic description
            description_template = self.rng.choice(template["description_templates"])
            description_values = {
                "quality": quality.lower() if quality else "",
                "rarity": rarity.lower() if rarity else "",
                "material": material if material else "",
                "base_name": base_name.lower(),
                "tactile_adjective": self.rng.choice(self.attributes["tactile_adjectives"]),
                "visual_adjective": self.rng.choice(self.attributes["visual_adjectives"])
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

        # If we couldn't generate a valid item after max_attempts, return without constraints
        raise ValueError(f"Could not generate item matching constraints after {max_attempts} attempts")

    def generate_items_from_set(self, set_name: str, count: Optional[int] = None, constraints: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Generate multiple items from a predefined item set.

        Args:
            set_name: Name of the item set (e.g., "blacksmith_inventory")
            count: Number of items to generate. If None, generates 1-5 items.
            constraints: Optional constraints passed to generate_item

        Returns:
            List of generated item dictionaries
        """
        if set_name not in self.items_config["item_sets"]:
            raise ValueError(f"Unknown item set: {set_name}")

        template_list = self.items_config["item_sets"][set_name]
        if count is None:
            count = self.rng.randint(1, 5)

        items = []
        for _ in range(count):
            template = self.rng.choice(template_list)
            items.append(self.generate_item(template, constraints=constraints))

        return items

    def generate_npc(self, archetype_name: Optional[str] = None,
                    location_id: Optional[str] = None,
                    race: Optional[str] = None,
                    faction: Optional[str] = None,
                    profession_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a random NPC based on profession(s).

        Args:
            archetype_name: DEPRECATED - Use profession_names instead. Single profession for backward compatibility.
            profession_names: List of professions (e.g., ["blacksmith", "merchant"]).
                            If None and archetype_name is None, generates NPC with random single profession.
                            If empty list [], generates NPC with no professions.
            location_id: ID of the location where this NPC resides.
            race: Specific race to use. If None, selects from profession's possible_races or random.
            faction: Specific faction to use. If None, selects from profession's possible_factions.

        Returns:
            Dictionary containing NPC properties including:
            - name: Full NPC name
            - title: NPC title/role (based on professions)
            - professions: List of profession names
            - race: NPC race
            - faction: NPC faction (optional)
            - stats: Stat values (averaged from all professions)
            - skills: Combined list of skills from all professions
            - dialogue: Random dialogue hook
            - description: Dynamic description
            - inventory: Combined items from all professions
            - location: Location ID reference (optional)
        """
        # Handle backward compatibility with archetype_name
        if profession_names is None:
            if archetype_name is not None:
                profession_names = [archetype_name]
            else:
                # Random single profession by default
                profession_names = [self.rng.choice(list(self.npcs_config["archetypes"].keys()))]

        # profession_names can be an empty list for NPCs with no profession
        professions = []
        for prof_name in profession_names:
            if prof_name in self.npcs_config["archetypes"]:
                professions.append(self.npcs_config["archetypes"][prof_name])
            else:
                raise ValueError(f"Unknown profession: {prof_name}")

        # If no professions, use generic NPC generation
        if len(professions) == 0:
            return self._generate_npc_no_profession(race, faction, location_id)

        # Use first profession as primary for certain attributes
        primary_profession = professions[0]

        # Select race - check all professions for possible races
        if race is None:
            all_possible_races = []
            for prof in professions:
                if "possible_races" in prof:
                    all_possible_races.extend(prof["possible_races"])
            if all_possible_races:
                race = self.rng.choice(all_possible_races)
            else:
                race = "human"  # Default fallback

        # Select faction - check all professions for possible factions
        if faction is None:
            all_possible_factions = []
            for prof in professions:
                if "possible_factions" in prof:
                    all_possible_factions.extend(prof["possible_factions"])
            if all_possible_factions:
                faction = self.rng.choice(all_possible_factions)

        # Get race data
        race_data = self.races_config["races"].get(race, self.races_config["races"]["human"])

        # Generate name (use race-specific names if primary profession requests it)
        if primary_profession.get("use_race_names", False) and race in self.races_config["races"]:
            # Use race-specific names
            gender = self.rng.choice(["male", "female"])
            if gender == "male" and "first_names_male" in race_data:
                first_name = self.rng.choice(race_data["first_names_male"])
            elif gender == "female" and "first_names_female" in race_data:
                first_name = self.rng.choice(race_data["first_names_female"])
            else:
                first_name = self.rng.choice(primary_profession["first_names"])

            if "last_names" in race_data:
                last_name = self.rng.choice(race_data["last_names"])
            else:
                last_name = self.rng.choice(primary_profession["last_names"])
        else:
            # Use primary profession names
            first_name = self.rng.choice(primary_profession["first_names"])
            last_name = self.rng.choice(primary_profession["last_names"])

        full_name = f"{first_name} {last_name}"

        # Combine stats from all professions (average them)
        combined_stats = {}
        for prof in professions:
            for stat, value in prof["base_stats"].items():
                if stat not in combined_stats:
                    combined_stats[stat] = []
                combined_stats[stat].append(value)

        # Average the stats
        stats = {}
        for stat, values in combined_stats.items():
            stats[stat] = sum(values) // len(values)

        # Apply racial stat modifiers
        if "stat_modifiers" in race_data:
            for stat, modifier in race_data["stat_modifiers"].items():
                if stat != "any_two":  # Handle general modifiers
                    if stat in stats:
                        stats[stat] += modifier
                    else:
                        stats[stat] = modifier

        # Add some random variation to stats (-1 to +1)
        for stat in stats:
            variation = self.rng.randint(-1, 1)
            stats[stat] = max(1, stats[stat] + variation)

        # Combine skills from all professions (unique skills)
        all_skills = []
        for prof in professions:
            all_skills.extend(prof["skills"])
        skills = list(set(all_skills))  # Remove duplicates

        # Select dialogue hook from random profession
        dialogue_profession = self.rng.choice(professions)
        dialogue = self.rng.choice(dialogue_profession["dialogue_hooks"])

        # Generate title based on professions
        if len(professions) == 1:
            title = professions[0]["title"]
        else:
            # Combine profession titles
            profession_titles = [prof["title"] for prof in professions]
            title = " / ".join(profession_titles)

        # Generate description
        description_template = self.rng.choice(primary_profession["description_templates"])
        description_values = {
            "trait": self.rng.choice(self.attributes["npc_traits"]),
            "title": title.lower(),
            "race": race_data["name"],
            "tactile_adjective": self.rng.choice(self.attributes["tactile_adjectives"]),
            "visual_adjective": self.rng.choice(self.attributes["visual_adjectives"])
        }
        description = self._fill_template(description_template, description_values)

        # Combine inventory from all professions
        inventory = []
        for prof in professions:
            if "inventory_set" in prof:
                items_from_prof = self.generate_items_from_set(
                    prof["inventory_set"],
                    count=self.rng.randint(1, 3)  # Fewer items per profession
                )
                inventory.extend(items_from_prof)

        # Build NPC object
        npc = {
            "name": full_name,
            "title": title,
            "professions": profession_names,  # Store as list
            "race": race,
            "stats": stats,
            "skills": skills,
            "dialogue": dialogue,
            "description": description,
            "inventory": inventory
        }

        # Add faction if assigned
        if faction:
            npc["faction"] = faction

        # Add location reference if provided
        if location_id:
            npc["location"] = location_id

        return npc

    def _generate_npc_no_profession(self, race: Optional[str] = None,
                                     faction: Optional[str] = None,
                                     location_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a generic NPC with no specific profession.

        Args:
            race: Specific race to use. If None, selects random race.
            faction: Specific faction to use.
            location_id: ID of the location where this NPC resides.

        Returns:
            Dictionary containing NPC properties without profession-specific attributes.
        """
        # Select random race if not specified
        if race is None:
            race = self.rng.choice(list(self.races_config["races"].keys()))

        # Get race data
        race_data = self.races_config["races"].get(race, self.races_config["races"]["human"])

        # Generate name using race-specific names
        gender = self.rng.choice(["male", "female"])
        if gender == "male" and "first_names_male" in race_data:
            first_name = self.rng.choice(race_data["first_names_male"])
        elif gender == "female" and "first_names_female" in race_data:
            first_name = self.rng.choice(race_data["first_names_female"])
        else:
            # Fallback to generic names
            first_name = self.rng.choice(["Alex", "Sam", "Jordan", "Morgan", "Taylor"])

        if "last_names" in race_data:
            last_name = self.rng.choice(race_data["last_names"])
        else:
            last_name = self.rng.choice(["Smith", "Jones", "Brown", "Wilson", "Moore"])

        full_name = f"{first_name} {last_name}"

        # Generate basic stats (average values)
        stats = {
            "Strength": 5,
            "Dexterity": 5,
            "Constitution": 5,
            "Intelligence": 5,
            "Wisdom": 5,
            "Charisma": 5
        }

        # Apply racial stat modifiers
        if "stat_modifiers" in race_data:
            for stat, modifier in race_data["stat_modifiers"].items():
                if stat != "any_two":
                    if stat in stats:
                        stats[stat] += modifier
                    else:
                        stats[stat] = modifier

        # Add random variation to stats (-2 to +2)
        for stat in stats:
            variation = self.rng.randint(-2, 2)
            stats[stat] = max(1, stats[stat] + variation)

        # Generic skills
        generic_skills = ["Perception", "Survival", "Athletics", "Persuasion", "Insight"]
        skills = self.rng.sample(generic_skills, k=min(3, len(generic_skills)))

        # Generic dialogue
        generic_dialogues = [
            "Hello there, traveler.",
            "Can I help you with something?",
            "Good day to you.",
            "What brings you here?",
            "I haven't seen you around before."
        ]
        dialogue = self.rng.choice(generic_dialogues)

        # Generic description
        trait = self.rng.choice(self.attributes["npc_traits"])
        tactile = self.rng.choice(self.attributes["tactile_adjectives"])
        visual = self.rng.choice(self.attributes["visual_adjectives"])
        description = f"A {trait} {race_data['name']} with {tactile} features and a {visual} appearance."

        # Minimal inventory
        inventory = []

        # Build NPC object
        npc = {
            "name": full_name,
            "title": "Commoner",
            "professions": [],  # Empty list for no professions
            "race": race,
            "stats": stats,
            "skills": skills,
            "dialogue": dialogue,
            "description": description,
            "inventory": inventory
        }

        # Add faction if assigned
        if faction:
            npc["faction"] = faction

        # Add location reference if provided
        if location_id:
            npc["location"] = location_id

        return npc

    def generate_location(self, template_name: Optional[str] = None,
                         generate_connections: bool = True,
                         max_connections: int = 3,
                         biome: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a random location based on a template.

        Args:
            template_name: Specific template to use (e.g., "forest_clearing").
                          If None, selects random template.
            generate_connections: Whether to generate connected locations.
            max_connections: Maximum number of connections to generate.
            biome: Specific biome for this location. If None, selects random suitable biome.

        Returns:
            Dictionary containing location properties including:
            - id: Unique location identifier
            - name: Location name
            - type: Location type
            - biome: Biome type
            - environment_tags: List of environment descriptors
            - description: Dynamic description
            - connections: Map of connected location IDs
            - npcs: List of NPCs in this location
            - items: List of items in this location
        """
        # Select template
        if template_name is None:
            template_name = self.rng.choice(list(self.locations_config["templates"].keys()))

        template = self.locations_config["templates"][template_name]

        # Select biome
        if biome is None and "suitable_biomes" in template:
            biome = self.rng.choice(template["suitable_biomes"])
        elif biome is None:
            biome = "temperate_forest"  # Default fallback

        # Generate unique ID
        location_id = f"{template_name}_{self.rng.randint(1000, 9999)}"

        # Generate environment tags
        environment_tags = template["base_environment_tags"].copy()
        additional_tag_count = self.rng.randint(
            template["additional_tags_count"]["min"],
            template["additional_tags_count"]["max"]
        )

        # Add random additional tags
        available_tags = [tag for tag in self.attributes["environment_tags"]
                         if tag not in environment_tags]
        additional_tags = self.rng.sample(
            available_tags,
            min(additional_tag_count, len(available_tags))
        )
        environment_tags.extend(additional_tags)

        # Generate description
        description_template = self.rng.choice(template["description_templates"])
        description_values = {
            "visual_adjective": self.rng.choice(self.attributes["visual_adjectives"]),
            "tactile_adjective": self.rng.choice(self.attributes["tactile_adjectives"]),
        }

        # Add indexed environment tags for template
        for i, tag in enumerate(environment_tags[:3], 1):
            description_values[f"environment_tag_{i}"] = tag.lower()

        description = self._fill_template(description_template, description_values)

        # Generate NPCs
        npc_count = self.rng.randint(
            template["npc_spawn_count"]["min"],
            template["npc_spawn_count"]["max"]
        )
        npcs = []
        for _ in range(npc_count):
            npc_archetype = self.rng.choice(template["spawnable_npcs"])
            npc = self.generate_npc(npc_archetype, location_id)
            npcs.append(npc)

        # Generate items
        item_count = self.rng.randint(
            template["item_spawn_count"]["min"],
            template["item_spawn_count"]["max"]
        )
        items = []
        for _ in range(item_count):
            item_template = self.rng.choice(template["spawnable_items"])
            item = self.generate_item(item_template)
            items.append(item)

        # Build location object
        location = {
            "id": location_id,
            "name": template["name"],
            "type": template["type"],
            "biome": biome,
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
            connection_count = self.rng.randint(1, min(max_connections, len(template["can_connect_to"])))
            connection_types = self.rng.sample(template["can_connect_to"], connection_count)

            for conn_type in connection_types:
                # Check if we already have a generated location of this type
                existing = [loc for loc in self.generated_locations.values()
                          if conn_type in loc["id"] and loc["id"] != location_id]

                if existing and self.rng.random() > 0.5:  # 50% chance to reuse existing
                    connected_loc = self.rng.choice(existing)
                    location["connections"][conn_type] = connected_loc["id"]
                    # Fix: Add bidirectional connection
                    connected_loc["connections"][template_name] = location_id
                else:
                    # Generate new connected location (without further connections to avoid recursion)
                    connected_loc = self.generate_location(conn_type, generate_connections=False)
                    location["connections"][conn_type] = connected_loc["id"]
                    # Fix: Add bidirectional connection
                    connected_loc["connections"][template_name] = location_id

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
