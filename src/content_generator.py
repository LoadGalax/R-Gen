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

        # Load separated attribute configuration files
        self.quality = self._load_json("quality.json")
        self.rarity = self._load_json("rarity.json")
        self.materials = self._load_json("materials.json")
        self.damage_types = self._load_json("damage_types.json")
        self.environment_tags = self._load_json("environment_tags.json")
        self.stats = self._load_json("stats.json")
        self.npc_traits = self._load_json("npc_traits.json")
        self.adjectives = self._load_json("adjectives.json")

        # Load separated item configuration files
        self.item_templates = self._load_json("item_templates.json")
        self.item_sets = self._load_json("item_sets.json")

        # Load separated NPC configuration files
        self.professions = self._load_json("professions.json")
        self.profession_levels = self._load_json("profession_levels.json")

        # Load other configuration files
        self.locations_config = self._load_json("locations.json")
        self.biomes_config = self._load_json("biomes.json")
        self.factions_config = self._load_json("factions.json")
        self.races_config = self._load_json("races.json")

        # Load enhanced feature configuration files
        self.spells_config = self._load_json("spells.json")
        self.organizations_config = self._load_json("organizations.json")
        self.weather_config = self._load_json("weather.json")
        self.economy_config = self._load_json("economy.json")
        self.quests_config = self._load_json("quests.json")
        self.description_styles_config = self._load_json("description_styles.json")

        # Cache for generated locations to support cross-referencing
        self.generated_locations = {}

        # Cache for generated NPCs to support relationship building
        self.generated_npcs = []

        # Cache for generated organizations
        self.generated_organizations = []

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
        available_stats = list(self.stats.keys())
        selected_stats = self.rng.sample(available_stats, min(count, len(available_stats)))

        for stat_name in selected_stats:
            stat_range = self.stats[stat_name]
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
                template_name = self.rng.choice(list(self.item_templates.keys()))

            template = self.item_templates[template_name]

            # Generate basic properties with constraints
            base_name = self.rng.choice(template["base_names"])

            # Generate quality with weighted probability
            if template["has_quality"]:
                quality = self._weighted_choice(self.quality)
            else:
                quality = None

            # Generate rarity with weighted probability
            if template["has_rarity"]:
                rarity = self._weighted_choice(self.rarity)
            else:
                rarity = None

            # Generate material with constraints
            if template.get("has_material", False):
                available_materials = [m for m in self.materials
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
                    if req_stat not in stats and req_stat in self.stats:
                        stat_range = self.stats[req_stat]
                        stats[req_stat] = self.rng.randint(stat_range["min"], stat_range["max"])

            # Generate value (influenced by quality and rarity)
            base_value = self.rng.randint(
                template["value_range"]["min"],
                template["value_range"]["max"]
            )

            # Get multipliers from config
            quality_multiplier = self.quality.get(quality, {}).get("multiplier", 1.0) if quality else 1.0
            rarity_multiplier = self.rarity.get(rarity, {}).get("multiplier", 1.0) if rarity else 1.0

            value = int(base_value * quality_multiplier * rarity_multiplier)

            # Check constraints
            quality_order = list(self.quality.keys())
            rarity_order = list(self.rarity.keys())

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
                    self.damage_types,
                    min(damage_count, len(self.damage_types))
                )

            # Generate dynamic description
            description_template = self.rng.choice(template["description_templates"])
            description_values = {
                "quality": quality.lower() if quality else "",
                "rarity": rarity.lower() if rarity else "",
                "material": material if material else "",
                "base_name": base_name.lower(),
                "tactile_adjective": self.rng.choice(self.adjectives["tactile"]),
                "visual_adjective": self.rng.choice(self.adjectives["visual"])
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
        if set_name not in self.item_sets:
            raise ValueError(f"Unknown item set: {set_name}")

        template_list = self.item_sets[set_name]
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
                    profession_names: Optional[List[str]] = None,
                    profession_level: Optional[str] = None) -> Dict[str, Any]:
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
            profession_level: Specific profession level (novice, apprentice, journeyman, expert, master, grandmaster).
                            If None, selects random level.

        Returns:
            Dictionary containing NPC properties including:
            - name: Full NPC name
            - title: NPC title/role (based on professions)
            - professions: List of profession names
            - profession_level: Profession level data
            - race: NPC race
            - faction: NPC faction (optional)
            - stats: Stat values (averaged from all professions with level multiplier)
            - skills: Combined list of skills from all professions
            - dialogue: Random dialogue hook
            - description: Dynamic description
            - inventory: Combined items from all professions
            - location: Location ID reference (optional)
            - challenge_rating: Calculated power level
        """
        # Handle backward compatibility with archetype_name
        if profession_names is None:
            if archetype_name is not None:
                profession_names = [archetype_name]
            else:
                # Random single profession by default
                profession_names = [self.rng.choice(list(self.professions.keys()))]

        # profession_names can be an empty list for NPCs with no profession
        professions = []
        for prof_name in profession_names:
            if prof_name in self.professions:
                professions.append(self.professions[prof_name])
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

        # Select profession level
        if profession_level is None:
            # Weighted selection favoring middle levels
            level_weights = {
                "novice": 0.15,
                "apprentice": 0.25,
                "journeyman": 0.30,
                "expert": 0.20,
                "master": 0.08,
                "grandmaster": 0.02
            }
            profession_level = self.rng.choices(
                list(level_weights.keys()),
                weights=list(level_weights.values()),
                k=1
            )[0]

        level_data = self.profession_levels[profession_level]

        # Combine stats from all professions (average them)
        combined_stats = {}
        for prof in professions:
            for stat, value in prof["base_stats"].items():
                if stat not in combined_stats:
                    combined_stats[stat] = []
                combined_stats[stat].append(value)

        # Average the stats and apply profession level multiplier
        stats = {}
        for stat, values in combined_stats.items():
            base_stat = sum(values) // len(values)
            stats[stat] = int(base_stat * level_data["stat_multiplier"])

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

        # Generate title based on professions and level
        if len(professions) == 1:
            title = f"{level_data['title_prefix']} {professions[0]['title']}"
        else:
            # Combine profession titles with level prefix
            profession_titles = [prof["title"] for prof in professions]
            title = f"{level_data['title_prefix']} {' / '.join(profession_titles)}"

        # Generate description
        description_template = self.rng.choice(primary_profession["description_templates"])
        description_values = {
            "trait": self.rng.choice(self.npc_traits),
            "title": title.lower(),
            "race": race_data["name"],
            "tactile_adjective": self.rng.choice(self.adjectives["tactile"]),
            "visual_adjective": self.rng.choice(self.adjectives["visual"])
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

        # Calculate challenge rating (power level)
        challenge_rating = self._calculate_challenge_rating(stats, skills, inventory, level_data["rank"])

        # Build NPC object
        npc = {
            "name": full_name,
            "title": title,
            "professions": profession_names,  # Store as list
            "profession_level": profession_level,
            "race": race,
            "stats": stats,
            "skills": skills,
            "dialogue": dialogue,
            "description": description,
            "inventory": inventory,
            "challenge_rating": challenge_rating
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
        trait = self.rng.choice(self.npc_traits)
        tactile = self.rng.choice(self.adjectives["tactile"])
        visual = self.rng.choice(self.adjectives["visual"])
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
        available_tags = [tag for tag in self.environment_tags
                         if tag not in environment_tags]
        additional_tags = self.rng.sample(
            available_tags,
            min(additional_tag_count, len(available_tags))
        )
        environment_tags.extend(additional_tags)

        # Generate description
        description_template = self.rng.choice(template["description_templates"])
        description_values = {
            "visual_adjective": self.rng.choice(self.adjectives["visual"]),
            "tactile_adjective": self.rng.choice(self.adjectives["tactile"]),
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

    def _calculate_challenge_rating(self, stats: Dict[str, int], skills: List[str],
                                    inventory: List[Dict], profession_rank: int) -> float:
        """
        Calculate NPC power level (challenge rating).

        Args:
            stats: NPC stats
            skills: NPC skills
            inventory: NPC inventory
            profession_rank: Rank from profession level (1-6)

        Returns:
            Challenge rating as a float
        """
        # Base CR from average stats
        stat_avg = sum(stats.values()) / len(stats) if stats else 1
        base_cr = stat_avg / 2.0

        # Add skill bonus
        skill_bonus = len(skills) * 0.2

        # Add equipment bonus
        equipment_value = sum(item.get("value", 0) for item in inventory)
        equipment_bonus = equipment_value / 1000.0

        # Add profession rank bonus
        rank_bonus = profession_rank * 0.5

        total_cr = base_cr + skill_bonus + equipment_bonus + rank_bonus
        return round(total_cr, 2)

    def generate_loot_table(self, enemy_type: str = "standard", difficulty: int = 1,
                           quantity_range: tuple = (1, 3), biome: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a loot table for enemies or treasure chests.

        Args:
            enemy_type: Type of enemy (standard, boss, elite, minion)
            difficulty: Difficulty level (1-10)
            quantity_range: Min and max number of items
            biome: Biome type to filter materials

        Returns:
            Loot table with items and gold
        """
        multipliers = {
            "minion": 0.5,
            "standard": 1.0,
            "elite": 2.0,
            "boss": 5.0
        }

        multiplier = multipliers.get(enemy_type, 1.0)
        item_count = self.rng.randint(quantity_range[0], quantity_range[1])

        # Adjust quality/rarity based on difficulty
        quality_constraints = {}
        if difficulty >= 7:
            quality_constraints["min_quality"] = "Excellent"
        elif difficulty >= 4:
            quality_constraints["min_quality"] = "Fine"

        # Generate items
        items = []
        for _ in range(item_count):
            template = self.rng.choice(list(self.item_templates.keys()))

            # Filter materials by biome if provided
            constraints = quality_constraints.copy()
            if biome and biome in self.biomes_config["biomes"]:
                biome_data = self.biomes_config["biomes"][biome]
                # Allow common and rare materials from biome
                allowed_materials = biome_data.get("common_materials", []) + biome_data.get("rare_materials", [])
                if allowed_materials:
                    # Don't exclude, just note for thematic generation
                    pass

            try:
                item = self.generate_item(template, constraints=constraints)
                items.append(item)
            except ValueError:
                # If constraints too strict, generate without them
                item = self.generate_item(template)
                items.append(item)

        # Calculate gold reward
        base_gold = difficulty * 50
        gold = int(base_gold * multiplier * self.rng.uniform(0.8, 1.2))

        return {
            "enemy_type": enemy_type,
            "difficulty": difficulty,
            "items": items,
            "gold": gold,
            "total_value": sum(item.get("value", 0) for item in items) + gold
        }

    def generate_quest(self, quest_type: Optional[str] = None, difficulty: int = 1,
                      faction: Optional[str] = None, location_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a quest template.

        Args:
            quest_type: Type of quest (fetch, kill, escort, explore, craft)
            difficulty: Quest difficulty (1-10)
            faction: Faction offering the quest
            location_id: Location where quest starts

        Returns:
            Quest data with objectives, rewards, and quest giver
        """
        quest_types = ["fetch", "kill", "escort", "explore", "craft", "deliver"]
        if quest_type is None:
            quest_type = self.rng.choice(quest_types)

        # Generate quest giver NPC
        quest_giver = self.generate_npc(faction=faction, location_id=location_id)

        # Generate rewards based on difficulty
        reward_gold = difficulty * 100 * self.rng.randint(1, 3)
        reward_items = []

        reward_count = min(difficulty // 2, 3)
        for _ in range(max(1, reward_count)):
            reward_items.append(self.generate_item())

        # Quest-type specific objectives
        objectives = {
            "fetch": f"Retrieve {self.rng.randint(1, 5)} {self.rng.choice(['ancient artifacts', 'rare herbs', 'lost documents', 'magical crystals'])}",
            "kill": f"Defeat {self.rng.randint(3, 10)} {self.rng.choice(['bandits', 'monsters', 'corrupted creatures', 'undead'])}",
            "escort": f"Escort {self.rng.choice(['merchant', 'noble', 'scholar', 'pilgrim'])} safely to their destination",
            "explore": f"Explore and map the {self.rng.choice(['ancient ruins', 'dark cavern', 'forgotten temple', 'mysterious forest'])}",
            "craft": f"Craft a {self.rng.choice(['legendary weapon', 'powerful artifact', 'magical item', 'rare potion'])}",
            "deliver": f"Deliver {self.rng.choice(['urgent message', 'valuable package', 'secret documents', 'rare goods'])} to the destination"
        }

        quest_name = f"{self.rng.choice(['The', 'A'])} {self.rng.choice(['Dangerous', 'Urgent', 'Secret', 'Ancient', 'Lost', 'Forbidden'])} {quest_type.capitalize()}"

        return {
            "name": quest_name,
            "type": quest_type,
            "difficulty": difficulty,
            "objective": objectives.get(quest_type, "Complete the objective"),
            "quest_giver": quest_giver,
            "rewards": {
                "gold": reward_gold,
                "items": reward_items,
                "experience": difficulty * 100
            },
            "faction": faction,
            "location": location_id,
            "status": "available"
        }

    def generate_crafting_recipe(self, output_item: Optional[Dict[str, Any]] = None,
                                 difficulty: int = 1) -> Dict[str, Any]:
        """
        Generate a crafting recipe for an item.

        Args:
            output_item: The item to craft (if None, generates random item)
            difficulty: Recipe difficulty (1-10)

        Returns:
            Crafting recipe with materials, tools, and skill requirements
        """
        if output_item is None:
            output_item = self.generate_item()

        # Determine materials needed based on item properties
        materials_needed = []

        if "material" in output_item:
            material = output_item["material"]
            quantity = self.rng.randint(2, 5) * difficulty
            materials_needed.append({
                "material": material,
                "quantity": quantity
            })

        # Add additional materials
        additional_count = min(difficulty // 2, 4)
        for _ in range(additional_count):
            mat = self.rng.choice(self.materials)
            materials_needed.append({
                "material": mat,
                "quantity": self.rng.randint(1, 3)
            })

        # Determine required tools
        tools = []
        item_type = output_item.get("type", "")
        if item_type == "weapon" or item_type == "armor":
            tools = ["forge", "anvil", "hammer"]
        elif item_type == "consumable":
            tools = ["alchemy_station", "mortar_and_pestle"]
        elif item_type == "accessory":
            tools = ["jeweler_tools", "crafting_table"]
        else:
            tools = ["crafting_table"]

        # Skill requirements
        skill_level = max(1, difficulty * 10)

        return {
            "output_item": output_item,
            "materials": materials_needed,
            "required_tools": tools,
            "skill_requirements": {
                "skill": self.rng.choice(["Crafting", "Smithing", "Alchemy", "Jewelcrafting"]),
                "level": skill_level
            },
            "crafting_time": difficulty * 10,  # minutes
            "difficulty": difficulty,
            "success_rate": max(0.5, 1.0 - (difficulty * 0.05))
        }

    def generate_encounter(self, party_level: int = 1, biome: Optional[str] = None,
                          faction: Optional[str] = None, encounter_type: str = "combat") -> Dict[str, Any]:
        """
        Generate an encounter for party.

        Args:
            party_level: Average party level (1-20)
            biome: Biome where encounter occurs
            faction: Faction involved in encounter
            encounter_type: Type (combat, social, puzzle, trap)

        Returns:
            Encounter data with enemies/NPCs, difficulty, and rewards
        """
        # Determine number of enemies based on party level
        enemy_count = self.rng.randint(max(1, party_level // 3), max(2, party_level // 2) + 2)

        if encounter_type == "combat":
            # Generate enemies
            enemies = []
            for i in range(enemy_count):
                # Mix of enemy types
                if i == 0 and self.rng.random() < 0.3:  # 30% chance of boss
                    enemy_type = "elite"
                else:
                    enemy_type = "standard"

                # Generate NPC as enemy
                enemy_profession = self.rng.choice(["guard", "soldier", "thief", "mage", "barbarian"])
                enemy = self.generate_npc(
                    archetype_name=enemy_profession,
                    faction=faction,
                    profession_level=self._get_level_for_party(party_level)
                )
                enemy["enemy_type"] = enemy_type
                enemies.append(enemy)

            # Calculate total CR
            total_cr = sum(e.get("challenge_rating", 1.0) for e in enemies)

            # Generate loot
            loot = self.generate_loot_table(
                enemy_type="standard" if total_cr < party_level * 2 else "elite",
                difficulty=party_level,
                quantity_range=(1, max(2, enemy_count // 2)),
                biome=biome
            )

            return {
                "type": "combat",
                "enemies": enemies,
                "total_challenge_rating": round(total_cr, 2),
                "difficulty": "easy" if total_cr < party_level else "medium" if total_cr < party_level * 1.5 else "hard",
                "loot": loot,
                "biome": biome,
                "faction": faction
            }

        elif encounter_type == "social":
            # Generate NPCs for social encounter
            npcs = []
            for _ in range(self.rng.randint(1, 3)):
                npc = self.generate_npc(faction=faction)
                npcs.append(npc)

            return {
                "type": "social",
                "npcs": npcs,
                "objective": self.rng.choice([
                    "Negotiate a deal",
                    "Gather information",
                    "Persuade the NPCs",
                    "Mediate a conflict"
                ]),
                "difficulty": party_level,
                "faction": faction
            }

        return {"type": encounter_type, "message": f"{encounter_type} encounter generated"}

    def _get_level_for_party(self, party_level: int) -> str:
        """Get appropriate profession level for party level."""
        if party_level <= 3:
            return "novice"
        elif party_level <= 7:
            return "apprentice"
        elif party_level <= 12:
            return "journeyman"
        elif party_level <= 16:
            return "expert"
        elif party_level <= 19:
            return "master"
        else:
            return "grandmaster"

    def generate_procedural_name(self, race: str = "human", gender: str = "male") -> str:
        """
        Generate a procedural name using syllable combination.

        Args:
            race: Race type for name generation
            gender: Gender for name generation

        Returns:
            Procedurally generated name
        """
        syllables = {
            "human": {
                "first": ["Al", "Bren", "Ced", "Da", "El", "Finn", "Gar", "Har", "Iv", "Jas"],
                "middle": ["dri", "nan", "ric", "mi", "en", "na", "eth", "ugh", "an", "per"],
                "last": ["c", "n", "k", "en", "a", "s", "th", "on", "or", "er"]
            },
            "elf": {
                "first": ["Ae", "Cal", "El", "Fae", "Gal", "Il", "Lor", "Nae", "Syl", "Vae"],
                "middle": ["la", "ad", "io", "la", "a", "li", "e", "ri", "va", "li"],
                "last": ["r", "n", "rel", "lyn", "don", "an", "ei", "s", "ra", "s"]
            },
            "dwarf": {
                "first": ["Thor", "Brom", "Grim", "Dur", "Bal", "Krag", "Mor", "Thar", "Gor", "Bor"],
                "middle": ["in", "on", "ak", "ek", "ik", "im", "um", "ar", "or", "an"],
                "last": ["", "", "n", "d", "k", "r", "m", "g", "t", "s"]
            }
        }

        # Default to human if race not found
        race_syllables = syllables.get(race, syllables["human"])

        first_name = (
            self.rng.choice(race_syllables["first"]) +
            self.rng.choice(race_syllables["middle"]) +
            self.rng.choice(race_syllables["last"])
        )

        return first_name

    def generate_item_with_modifiers(self, template_name: Optional[str] = None,
                                    num_modifiers: int = 0) -> Dict[str, Any]:
        """
        Generate item with procedural prefix/suffix modifiers.

        Args:
            template_name: Item template to use
            num_modifiers: Number of modifiers to apply (0-2)

        Returns:
            Item with modifiers applied
        """
        item = self.generate_item(template_name)

        if num_modifiers > 0:
            prefixes = ["Flaming", "Frozen", "Shocking", "Vampiric", "Holy", "Shadow", "Vorpal", "Keen", "Mighty", "Swift"]
            suffixes = ["of Giants", "of the Bear", "of the Eagle", "of Protection", "of Warding", "of Power", "of Speed", "of the Phoenix", "of the Dragon", "of the Ancients"]

            modifiers_applied = []
            bonus_value = 0

            if num_modifiers >= 1 and self.rng.random() < 0.7:
                prefix = self.rng.choice(prefixes)
                item["name"] = f"{prefix} {item['name']}"
                modifiers_applied.append(prefix)

                # Add bonus based on prefix
                if prefix in ["Flaming", "Frozen", "Shocking"]:
                    item.setdefault("damage_types", []).append(prefix.replace("ing", "e") if prefix == "Flaming" else prefix.replace("ing", ""))

                bonus_value += item["value"] * 0.3

            if num_modifiers >= 2 and self.rng.random() < 0.5:
                suffix = self.rng.choice(suffixes)
                item["name"] = f"{item['name']} {suffix}"
                modifiers_applied.append(suffix)

                # Add stat bonus based on suffix
                if "of Giants" in suffix:
                    item["stats"]["Strength"] = item["stats"].get("Strength", 0) + 2
                elif "of the Bear" in suffix:
                    item["stats"]["Constitution"] = item["stats"].get("Constitution", 0) + 2
                elif "of Speed" in suffix or "Swift" in modifiers_applied:
                    item["stats"]["Dexterity"] = item["stats"].get("Dexterity", 0) + 2

                bonus_value += item["value"] * 0.5

            item["value"] = int(item["value"] + bonus_value)
            item["modifiers"] = modifiers_applied

        return item

    def validate_thematic_consistency(self, item: Dict[str, Any], biome: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate if item fits thematically with biome.

        Args:
            item: Item to validate
            biome: Biome to check against

        Returns:
            Validation result with warnings
        """
        warnings = []

        if biome and biome in self.biomes_config["biomes"]:
            biome_data = self.biomes_config["biomes"][biome]

            # Check material consistency
            if "material" in item:
                allowed_materials = biome_data.get("common_materials", []) + biome_data.get("rare_materials", [])
                if allowed_materials and item["material"] not in allowed_materials:
                    warnings.append(f"Material '{item['material']}' is unusual for {biome} biome")

            # Check damage type vs biome
            if "damage_types" in item:
                biome_env_tags = biome_data.get("environment_tags", [])
                for damage_type in item["damage_types"]:
                    if damage_type == "Fire" and "Cold" in biome_env_tags:
                        warnings.append(f"Fire damage item in cold {biome} biome may be thematically inconsistent")
                    elif damage_type == "Ice" and "Hot" in biome_env_tags:
                        warnings.append(f"Ice damage item in hot {biome} biome may be thematically inconsistent")

        return {
            "valid": len(warnings) == 0,
            "warnings": warnings,
            "item": item
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

    def export_to_xml(self, data: Any, filename: str) -> None:
        """
        Export generated content to XML format.

        Args:
            data: Data to export
            filename: Output filename
        """
        import xml.etree.ElementTree as ET

        def dict_to_xml(tag, d):
            elem = ET.Element(tag)
            if isinstance(d, dict):
                for key, val in d.items():
                    child = dict_to_xml(key, val)
                    elem.append(child)
            elif isinstance(d, list):
                for item in d:
                    child = dict_to_xml("item", item)
                    elem.append(child)
            else:
                elem.text = str(d)
            return elem

        root = dict_to_xml("data", data)
        tree = ET.ElementTree(root)
        output_path = Path(filename)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        print(f"Exported to {output_path}")

    def export_to_csv(self, data: Any, filename: str) -> None:
        """
        Export generated content to CSV format (works best for lists of items/NPCs).

        Args:
            data: Data to export (should be list of dicts)
            filename: Output filename
        """
        import csv

        output_path = Path(filename)

        if isinstance(data, list) and len(data) > 0:
            # Get all possible keys
            all_keys = set()
            for item in data:
                if isinstance(item, dict):
                    all_keys.update(item.keys())

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                for item in data:
                    if isinstance(item, dict):
                        # Convert nested structures to strings
                        row = {}
                        for k, v in item.items():
                            if isinstance(v, (dict, list)):
                                row[k] = json.dumps(v)
                            else:
                                row[k] = v
                        writer.writerow(row)
            print(f"Exported to {output_path}")
        else:
            print("CSV export requires a list of dictionaries")

    def export_to_sql(self, data: Any, filename: str, table_name: str = "game_content") -> None:
        """
        Export generated content to SQL INSERT statements.

        Args:
            data: Data to export (should be list of dicts)
            filename: Output filename
            table_name: SQL table name
        """
        output_path = Path(filename)

        if isinstance(data, list) and len(data) > 0:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Get all possible columns
                all_keys = set()
                for item in data:
                    if isinstance(item, dict):
                        all_keys.update(item.keys())

                columns = sorted(all_keys)

                for item in data:
                    if isinstance(item, dict):
                        values = []
                        for col in columns:
                            val = item.get(col, None)
                            if val is None:
                                values.append("NULL")
                            elif isinstance(val, (dict, list)):
                                escaped_json = json.dumps(val).replace("'", "''")
                                values.append(f"'{escaped_json}'")
                            elif isinstance(val, str):
                                escaped_str = val.replace("'", "''")
                                values.append(f"'{escaped_str}'")
                            else:
                                values.append(str(val))

                        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
                        f.write(sql)

            print(f"Exported to {output_path}")
        else:
            print("SQL export requires a list of dictionaries")

    def generate_item_set_collection(self, set_name: Optional[str] = None,
                                     set_size: int = 5) -> Dict[str, Any]:
        """
        Generate a themed item set collection (e.g., "Dragon Slayer Set").

        Args:
            set_name: Name of the set
            set_size: Number of items in the set

        Returns:
            Item set with bonuses
        """
        if set_name is None:
            themes = ["Dragon Slayer", "Shadow", "Holy", "Infernal", "Frost", "Storm", "Ancient", "Ethereal"]
            theme = self.rng.choice(themes)
            set_name = f"{theme} Set"

        # Generate complementary items
        set_templates = ["weapon_melee", "armor", "armor", "jewelry", "jewelry"]
        items = []

        for template in set_templates[:set_size]:
            item = self.generate_item_with_modifiers(template, num_modifiers=1)
            # Add set identifier
            item["set"] = set_name
            items.append(item)

        # Define set bonuses
        set_bonuses = {
            2: {"description": "2-piece bonus: +10% damage", "stats": {"Strength": 1}},
            3: {"description": "3-piece bonus: +15% defense", "stats": {"Constitution": 2}},
            4: {"description": "4-piece bonus: +20% critical chance", "stats": {"Dexterity": 2}},
            5: {"description": "5-piece bonus: +25% all stats", "stats": {"Strength": 2, "Dexterity": 2, "Constitution": 2}}
        }

        return {
            "name": set_name,
            "items": items,
            "set_bonuses": set_bonuses,
            "total_value": sum(item.get("value", 0) for item in items)
        }

    def generate_batch_with_distribution(self, content_type: str = "item",
                                        count: int = 100,
                                        distribution: Optional[Dict[str, float]] = None,
                                        **kwargs) -> List[Dict[str, Any]]:
        """
        Generate batch content with specific rarity distribution.

        Args:
            content_type: Type to generate (item, npc, location)
            count: Total number to generate
            distribution: Rarity distribution (e.g., {"Common": 0.5, "Rare": 0.3, "Epic": 0.2})
            **kwargs: Additional arguments for generation functions

        Returns:
            List of generated content matching distribution
        """
        if distribution is None:
            # Default distribution
            if content_type == "item":
                distribution = {
                    "Common": 0.45,
                    "Uncommon": 0.28,
                    "Rare": 0.15,
                    "Epic": 0.08,
                    "Legendary": 0.03,
                    "Mythic": 0.01
                }

        results = []

        # Calculate counts per rarity
        for rarity, percentage in distribution.items():
            rarity_count = int(count * percentage)

            for _ in range(rarity_count):
                if content_type == "item":
                    constraints = kwargs.get("constraints", {})
                    constraints["min_rarity"] = rarity
                    constraints["max_rarity"] = rarity
                    try:
                        item = self.generate_item(
                            template_name=kwargs.get("template_name"),
                            constraints=constraints
                        )
                        results.append(item)
                    except ValueError:
                        # If constraints too strict, skip
                        pass

                elif content_type == "npc":
                    # Map rarity to profession level
                    rarity_to_level = {
                        "Common": "novice",
                        "Uncommon": "apprentice",
                        "Rare": "journeyman",
                        "Epic": "expert",
                        "Legendary": "master",
                        "Mythic": "grandmaster"
                    }
                    npc = self.generate_npc(
                        profession_level=rarity_to_level.get(rarity, "journeyman"),
                        **kwargs
                    )
                    results.append(npc)

                elif content_type == "location":
                    location = self.generate_location(**kwargs)
                    results.append(location)

        return results

    def generate_weather_and_time(self, biome: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate weather and time-of-day conditions.

        Args:
            biome: Biome type (affects weather possibilities)

        Returns:
            Weather and time data with gameplay modifiers
        """
        times_of_day = {
            "dawn": {"hour": 6, "light_level": 0.5, "visibility": "moderate"},
            "morning": {"hour": 9, "light_level": 1.0, "visibility": "clear"},
            "noon": {"hour": 12, "light_level": 1.0, "visibility": "clear"},
            "afternoon": {"hour": 15, "light_level": 0.9, "visibility": "clear"},
            "dusk": {"hour": 18, "light_level": 0.4, "visibility": "dim"},
            "evening": {"hour": 20, "light_level": 0.2, "visibility": "dark"},
            "midnight": {"hour": 0, "light_level": 0.0, "visibility": "very_dark"},
            "late_night": {"hour": 3, "light_level": 0.0, "visibility": "very_dark"}
        }

        # Weather conditions
        weather_conditions = {
            "clear": {"visibility_modifier": 1.0, "movement_modifier": 1.0, "description": "Clear skies"},
            "cloudy": {"visibility_modifier": 0.9, "movement_modifier": 1.0, "description": "Overcast"},
            "rain": {"visibility_modifier": 0.7, "movement_modifier": 0.9, "description": "Rainfall"},
            "heavy_rain": {"visibility_modifier": 0.5, "movement_modifier": 0.7, "description": "Heavy rainfall"},
            "fog": {"visibility_modifier": 0.4, "movement_modifier": 0.8, "description": "Dense fog"},
            "snow": {"visibility_modifier": 0.6, "movement_modifier": 0.7, "description": "Snowfall"},
            "storm": {"visibility_modifier": 0.3, "movement_modifier": 0.6, "description": "Thunderstorm"},
            "blizzard": {"visibility_modifier": 0.2, "movement_modifier": 0.4, "description": "Blizzard"}
        }

        # Biome-specific weather probabilities
        biome_weather = {
            "desert": ["clear", "clear", "clear", "cloudy"],
            "swamp": ["fog", "rain", "cloudy", "heavy_rain"],
            "tundra": ["snow", "blizzard", "cloudy", "clear"],
            "coastal": ["rain", "cloudy", "clear", "storm"],
            "mountains": ["snow", "cloudy", "clear", "fog"],
            "jungle": ["rain", "heavy_rain", "cloudy", "fog"],
            "volcanic": ["cloudy", "storm", "clear", "fog"]
        }

        time_key = self.rng.choice(list(times_of_day.keys()))
        time_data = times_of_day[time_key].copy()
        time_data["period"] = time_key

        # Select weather based on biome
        if biome and biome in biome_weather:
            weather_key = self.rng.choice(biome_weather[biome])
        else:
            weather_key = self.rng.choice(["clear", "cloudy", "rain"])

        weather_data = weather_conditions[weather_key].copy()
        weather_data["condition"] = weather_key

        # Calculate combined modifiers
        final_visibility = time_data["light_level"] * weather_data["visibility_modifier"]

        return {
            "time": time_data,
            "weather": weather_data,
            "combined_modifiers": {
                "visibility": round(final_visibility, 2),
                "movement_speed": weather_data["movement_modifier"],
                "stealth_bonus": round((1.0 - final_visibility) * 0.5, 2)  # Darkness helps stealth
            },
            "description": f"{time_data['period'].capitalize()}, {weather_data['description'].lower()}"
        }

    def generate_trap_or_puzzle(self, difficulty: int = 1, trap_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a trap or puzzle encounter.

        Args:
            difficulty: Difficulty level (1-10)
            trap_type: Type of trap (mechanical, magical, puzzle)

        Returns:
            Trap/puzzle data with detection, disarm mechanics
        """
        trap_types_list = ["mechanical", "magical", "puzzle", "environmental"]
        if trap_type is None:
            trap_type = self.rng.choice(trap_types_list)

        if trap_type == "mechanical":
            traps = [
                {"name": "Spike Pit", "damage": "2d6 piercing", "trigger": "pressure plate"},
                {"name": "Poison Dart", "damage": "1d4 piercing + poison", "trigger": "tripwire"},
                {"name": "Swinging Blade", "damage": "3d6 slashing", "trigger": "door"},
                {"name": "Crushing Walls", "damage": "4d6 bludgeoning", "trigger": "entering room"},
                {"name": "Arrow Volley", "damage": "2d6 piercing", "trigger": "chest opening"}
            ]
            trap_data = self.rng.choice(traps)

        elif trap_type == "magical":
            traps = [
                {"name": "Glyph of Warding", "damage": "3d8 force", "trigger": "crossing threshold"},
                {"name": "Lightning Rune", "damage": "4d6 lightning", "trigger": "touching object"},
                {"name": "Fireball Trap", "damage": "6d6 fire", "trigger": "opening container"},
                {"name": "Charm Trap", "damage": "none (charm effect)", "trigger": "reading text"},
                {"name": "Teleportation Circle", "damage": "none (teleport)", "trigger": "stepping on"}
            ]
            trap_data = self.rng.choice(traps)

        elif trap_type == "puzzle":
            puzzles = [
                {"name": "Riddle Door", "solution_type": "intelligence check", "hint": "speaks in riddles"},
                {"name": "Color Sequence", "solution_type": "pattern recognition", "hint": "colored tiles"},
                {"name": "Weight Balance", "solution_type": "logic puzzle", "hint": "scales and weights"},
                {"name": "Rotating Statues", "solution_type": "spatial reasoning", "hint": "directional statues"},
                {"name": "Musical Notes", "solution_type": "memory/hearing", "hint": "sequence of sounds"}
            ]
            trap_data = self.rng.choice(puzzles)

        else:  # environmental
            traps = [
                {"name": "Collapsing Ceiling", "damage": "5d6 bludgeoning", "trigger": "structural weakness"},
                {"name": "Flooding Room", "damage": "drowning risk", "trigger": "time-based"},
                {"name": "Gas Release", "damage": "poison/sleep", "trigger": "air disturbance"},
                {"name": "Lava Flow", "damage": "10d6 fire", "trigger": "floor mechanism"},
                {"name": "Rockslide", "damage": "4d8 bludgeoning", "trigger": "vibration"}
            ]
            trap_data = self.rng.choice(traps)

        # Calculate DC based on difficulty
        detection_dc = 10 + (difficulty * 2)
        disarm_dc = 12 + (difficulty * 2)

        return {
            "type": trap_type,
            "name": trap_data["name"],
            "difficulty": difficulty,
            "detection_dc": detection_dc,
            "disarm_dc": disarm_dc if trap_type != "puzzle" else None,
            "solve_dc": disarm_dc if trap_type == "puzzle" else None,
            "damage": trap_data.get("damage", "varies"),
            "trigger": trap_data.get("trigger", "unknown"),
            "solution_type": trap_data.get("solution_type"),
            "hint": trap_data.get("hint"),
            "rewards_on_bypass": {
                "experience": difficulty * 50,
                "possible_treasure": self.rng.random() > 0.5
            }
        }

    # ========== NEW FEATURES: Spell Generation ==========

    def generate_spell(self, spell_level: Optional[int] = None, school: Optional[str] = None,
                      spell_template: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a spell with components, effects, and flavor.

        Args:
            spell_level: Spell level (0-9, where 0 is cantrip)
            school: Magic school (Evocation, Necromancy, etc.)
            spell_template: Specific spell template (damage_single, damage_area, healing, etc.)

        Returns:
            Dict containing spell properties
        """
        # Select spell level
        if spell_level is None:
            # Weighted toward lower levels
            level_weights = [0.2, 0.18, 0.15, 0.12, 0.10, 0.08, 0.07, 0.05, 0.03, 0.02]
            spell_level = self.rng.choices(range(10), weights=level_weights, k=1)[0]

        level_name = "cantrip" if spell_level == 0 else f"{spell_level}{'st' if spell_level == 1 else 'nd' if spell_level == 2 else 'rd' if spell_level == 3 else 'th'}"
        level_data = self.spells_config["spell_levels"][level_name]

        # Select school
        if school is None:
            school = self.rng.choice(list(self.spells_config["magic_schools"].keys()))

        school_data = self.spells_config["magic_schools"][school]

        # Select template
        if spell_template is None:
            spell_template = self.rng.choice(list(self.spells_config["spell_templates"].keys()))

        template = self.spells_config["spell_templates"][spell_template]

        # Generate spell name
        name_pattern = self.rng.choice(template["name_patterns"])
        spell_variables = self.spells_config["spell_variables"]
        name_values = {
            "element": self.rng.choice(spell_variables.get("element", ["Energy"])),
            "intensity": self.rng.choice(spell_variables.get("intensity", ["Lesser"])),
            "adjective": self.rng.choice(spell_variables.get("adjective", ["Arcane"])),
            "shape": self.rng.choice(spell_variables.get("shape", ["Blast"])),
            "quality": self.rng.choice(spell_variables.get("quality", ["Power"])),
            "severity": self.rng.choice(spell_variables.get("severity", ["Wounds"])),
            "affliction": self.rng.choice(spell_variables.get("affliction", ["Weakness"])),
            "creature": self.rng.choice(spell_variables.get("creature", ["Elemental"])),
            "action": self.rng.choice(spell_variables.get("action", ["Flight"])),
            "stat": self.rng.choice(["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"])
        }
        spell_name = self._fill_template(name_pattern, name_values)

        # Calculate power based on level
        power_multiplier = level_data["power_multiplier"]

        # Generate effect values
        effect_data = {}
        if template["effect_type"] == "damage":
            base_damage = self.rng.randint(template["base_damage_range"]["min"], template["base_damage_range"]["max"])
            scaling = self.rng.randint(template["scaling_per_level"]["min"], template["scaling_per_level"]["max"])
            effect_data["damage"] = int(base_damage * power_multiplier)
            effect_data["scaling_per_level"] = scaling
            if template["target"] == "area":
                effect_data["area_size"] = self.rng.randint(template["area_size"]["min"], template["area_size"]["max"])

        elif template["effect_type"] == "healing":
            base_healing = self.rng.randint(template["base_healing_range"]["min"], template["base_healing_range"]["max"])
            scaling = self.rng.randint(template["scaling_per_level"]["min"], template["scaling_per_level"]["max"])
            effect_data["healing"] = int(base_healing * power_multiplier)
            effect_data["scaling_per_level"] = scaling

        elif template["effect_type"] in ["buff", "debuff"]:
            if template["effect_type"] == "buff":
                bonus = self.rng.randint(template["stat_bonus_range"]["min"], template["stat_bonus_range"]["max"])
                effect_data["bonus"] = int(bonus * power_multiplier)
            else:
                penalty = self.rng.randint(template["stat_penalty_range"]["min"], template["stat_penalty_range"]["max"])
                effect_data["penalty"] = int(penalty * power_multiplier)

            effect_data["duration"] = self.rng.randint(template["duration_range"]["min"], template["duration_range"]["max"])
            effect_data["stat"] = name_values["stat"]

        elif template["effect_type"] == "summon":
            duration = self.rng.randint(template["summon_duration_range"]["min"], template["summon_duration_range"]["max"])
            power = self.rng.randint(template["summon_power_range"]["min"], template["summon_power_range"]["max"])
            effect_data["duration"] = duration
            effect_data["power"] = int(power * power_multiplier)
            effect_data["creature"] = name_values["creature"]
            effect_data["plane"] = self.rng.choice(spell_variables.get("plane", ["Astral Plane"]))

        elif template["effect_type"] == "utility":
            duration = self.rng.randint(template["duration_range"]["min"], template["duration_range"]["max"])
            effect_data["duration"] = duration
            effect_data["utility_effect"] = self.rng.choice(spell_variables.get("utility_effect", ["see in darkness"]))

        # Mana cost
        base_cost = self.rng.randint(template["mana_cost_range"]["min"], template["mana_cost_range"]["max"])
        mana_cost = int(base_cost * level_data["mana_cost_multiplier"]) if spell_level > 0 else 0

        # Components
        components = []
        if self.spells_config["spell_components"]["verbal"]["required"]:
            components.append("Verbal")
        if self.spells_config["spell_components"]["somatic"]["required"]:
            components.append("Somatic")
        if self.rng.random() < 0.3:  # 30% chance of material component
            material_component = self.rng.choice(self.spells_config["spell_components"]["material"]["component_examples"])
            components.append(f"Material ({material_component})")

        # Casting time and range
        casting_time = self.rng.choice(template["casting_time"])
        spell_range = self.rng.choice(template["range"])

        # Generate description
        description_template = self.rng.choice(template["description_templates"])
        desc_values = {**name_values, **effect_data}
        description = self._fill_template(description_template, desc_values)

        # Rarity
        rarity = self._weighted_choice(self.spells_config["spell_rarity"])

        # Value (for scrolls/spellbooks)
        base_value = (spell_level + 1) * 100
        rarity_mult = self.spells_config["spell_rarity"][rarity]["value_multiplier"]
        value = int(base_value * rarity_mult)

        spell = {
            "name": spell_name,
            "level": spell_level,
            "school": school,
            "effect_type": template["effect_type"],
            "target": template["target"],
            "casting_time": casting_time,
            "range": spell_range,
            "components": components,
            "mana_cost": mana_cost,
            "description": description,
            "effect_data": effect_data,
            "rarity": rarity,
            "value": value
        }

        return spell

    def generate_spellbook(self, caster_level: int = 1, school_preference: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a spellbook with multiple spells.

        Args:
            caster_level: Caster's level (determines max spell level)
            school_preference: Preferred school of magic

        Returns:
            Spellbook with collection of spells
        """
        max_spell_level = min(9, (caster_level + 1) // 2)
        spell_count = self.rng.randint(caster_level, caster_level * 2 + 5)

        spells = []
        for _ in range(spell_count):
            spell_level = self.rng.randint(0, max_spell_level)
            school = school_preference if school_preference and self.rng.random() < 0.6 else None
            spell = self.generate_spell(spell_level=spell_level, school=school)
            spells.append(spell)

        total_value = sum(s.get("value", 0) for s in spells)

        return {
            "type": "spellbook",
            "caster_level": caster_level,
            "school_preference": school_preference,
            "spell_count": len(spells),
            "spells": spells,
            "total_value": total_value + 500  # Add book value
        }

    # ========== NEW FEATURES: Organization & Guild Generation ==========

    def generate_organization(self, org_type: Optional[str] = None, faction: Optional[str] = None,
                             size: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an organization or guild.

        Args:
            org_type: Type of organization (guild, thieves_guild, mages_circle, etc.)
            faction: Associated faction
            size: Organization size (small, medium, large)

        Returns:
            Organization data with structure, resources, and members
        """
        # Select organization type
        if org_type is None:
            org_type = self.rng.choice(list(self.organizations_config["organization_types"].keys()))

        org_template = self.organizations_config["organization_types"][org_type]

        # Generate organization name
        name_pattern = self.rng.choice(self.organizations_config["organization_templates"][0]["name_patterns"])
        org_variables = self.organizations_config["organization_variables"]
        name_values = {
            "adjective": self.rng.choice(org_variables["adjective"]),
            "type": self.rng.choice(org_variables["type"]),
            "symbol": self.rng.choice(org_variables["symbol"]),
            "city": self.rng.choice(org_variables["city"]),
            "founder": self.rng.choice(["Aldric", "Morgana", "Thalion", "Ravenna", "Godric"])
        }
        org_name = self._fill_template(name_pattern, name_values)

        # Determine size
        if size is None:
            size_options = ["small", "medium", "large"]
            size = self.rng.choices(size_options, weights=[0.4, 0.4, 0.2], k=1)[0]

        size_multipliers = {"small": 0.5, "medium": 1.0, "large": 2.0}
        member_count = int(self.rng.randint(org_template["typical_size"]["min"],
                                           org_template["typical_size"]["max"]) * size_multipliers[size])

        # Wealth
        wealth_level = org_template.get("wealth_level", "moderate")
        if wealth_level in self.organizations_config["organization_resources"]["wealth"]:
            wealth_range = self.organizations_config["organization_resources"]["wealth"][wealth_level]
            wealth = self.rng.randint(wealth_range["min"], wealth_range["max"])
        else:
            wealth = 10000

        # Generate leadership NPCs
        hierarchy = org_template["hierarchy_levels"]
        leaders = []
        for rank in hierarchy[-2:]:  # Top 2 ranks
            leader = self.generate_npc(faction=faction)
            leader["org_rank"] = rank
            leaders.append(leader)

        # Benefits
        benefits = self.organizations_config["organization_templates"][0]["benefits"].get(org_type, [])

        # Relationships with other organizations
        relationship_type = self.rng.choice(["allied", "neutral", "rival", "enemy"])
        relationships = {
            "type": relationship_type,
            "description": self.organizations_config["organization_relationships"][relationship_type]["description"]
        }

        organization = {
            "name": org_name,
            "type": org_type,
            "description": org_template["description"],
            "size": size,
            "member_count": member_count,
            "hierarchy": hierarchy,
            "leaders": leaders,
            "wealth": wealth,
            "faction": faction,
            "activities": org_template["common_activities"],
            "benefits": benefits,
            "relationships": relationships,
            "secrecy": org_template.get("secrecy", "none"),
            "requirements": org_template.get("requirements", [])
        }

        self.generated_organizations.append(organization)
        return organization

    # ========== NEW FEATURES: Enhanced Weather & Environment ==========

    def generate_weather_detailed(self, biome: Optional[str] = None, season: Optional[str] = None,
                                  time_of_day: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate detailed weather with natural disasters and moon phases.

        Args:
            biome: Biome type
            season: Season (spring, summer, autumn, winter)
            time_of_day: Specific time (dawn, morning, noon, afternoon, dusk, night)

        Returns:
            Detailed weather data with all environmental factors
        """
        # Select season
        if season is None:
            season = self.rng.choice(list(self.weather_config["seasons"].keys()))

        season_data = self.weather_config["seasons"][season]

        # Select time of day
        if time_of_day is None:
            time_of_day = self.rng.choice(list(self.weather_config["time_of_day"].keys()))

        time_data = self.weather_config["time_of_day"][time_of_day]

        # Select weather pattern
        if season in ["winter"]:
            available_weather = [w for w, data in self.weather_config["weather_patterns"].items()
                               if data.get("season_required") in [None, season]]
        else:
            available_weather = [w for w, data in self.weather_config["weather_patterns"].items()
                               if data.get("season_required") is None or data.get("season_required") == season]

        # Weighted selection
        weather_weights = [self.weather_config["weather_patterns"][w]["weight"] for w in available_weather]
        weather_type = self.rng.choices(available_weather, weights=weather_weights, k=1)[0]
        weather_data = self.weather_config["weather_patterns"][weather_type]

        # Calculate temperature
        base_temp = season_data["base_temperature"] + weather_data["temperature_modifier"]
        variation = self.rng.randint(-season_data["temperature_variation"], season_data["temperature_variation"])
        temperature = base_temp + variation

        # Moon phase
        moon_phase = self.rng.choice(list(self.weather_config["moon_phases"].keys()))
        moon_data = self.weather_config["moon_phases"][moon_phase]

        # Calculate combined visibility
        base_visibility = time_data["visibility_modifier"]
        moon_bonus = moon_data["light_bonus"] if time_of_day == "night" else 0
        final_visibility = min(1.0, base_visibility + moon_bonus)

        # Natural disaster chance (very rare)
        disaster = None
        if self.rng.random() < 0.01:  # 1% chance
            disaster_type = self.rng.choice(list(self.weather_config["natural_disasters"].keys()))
            disaster_info = self.weather_config["natural_disasters"][disaster_type]
            severity = self.rng.choice(list(disaster_info["severity_levels"].keys()))
            disaster = {
                "type": disaster_type,
                "severity": severity,
                "description": disaster_info["description"],
                "effects": disaster_info["severity_levels"][severity]["effects"]
            }

        return {
            "season": season,
            "time_of_day": time_of_day,
            "weather_type": weather_type,
            "temperature": temperature,
            "visibility": final_visibility,
            "mood": weather_data["mood"],
            "effects": weather_data["effects"],
            "travel_speed_modifier": weather_data["travel_speed_modifier"],
            "combat_modifier": weather_data["combat_modifier"],
            "moon_phase": moon_phase,
            "moon_effects": moon_data["effects"],
            "natural_disaster": disaster,
            "description": f"{season.capitalize()}, {time_of_day}, {weather_data['description'].lower()}. Temperature: {temperature}°C. {moon_phase.replace('_', ' ').title()}"
        }

    # ========== NEW FEATURES: Economic System ==========

    def calculate_item_price(self, item: Dict[str, Any], location: Optional[Dict[str, Any]] = None,
                            supply: str = "normal", demand: str = "normal") -> Dict[str, Any]:
        """
        Calculate dynamic item price based on economic factors.

        Args:
            item: Item to price
            location: Location where item is sold (affects distance modifiers)
            supply: Supply level (abundant, normal, scarce, rare)
            demand: Demand level (low, normal, high, desperate)

        Returns:
            Pricing information with modifiers
        """
        base_value = item.get("value", 100)

        # Get economic modifiers
        supply_modifier = self.economy_config["price_factors"]["supply"][supply]["modifier"]
        demand_modifier = self.economy_config["price_factors"]["demand"][demand]["modifier"]

        # Location modifier (simplified - could use actual trade routes)
        location_modifier = 1.0
        if location:
            location_type = location.get("type", "")
            if "market" in location_type.lower():
                location_modifier = 0.9  # Markets have better prices
            elif "remote" in location_type.lower():
                location_modifier = 1.5

        # Quality and condition modifiers already in base_value
        # Calculate final price
        final_price = int(base_value * supply_modifier * demand_modifier * location_modifier)

        return {
            "base_value": base_value,
            "final_price": final_price,
            "modifiers": {
                "supply": supply_modifier,
                "demand": demand_modifier,
                "location": location_modifier
            },
            "supply_status": supply,
            "demand_status": demand
        }

    def generate_market(self, location: Optional[Dict[str, Any]] = None, wealth_level: str = "modest") -> Dict[str, Any]:
        """
        Generate a market with goods, services, and dynamic pricing.

        Args:
            location: Location of market
            wealth_level: Economic level (destitute, poor, modest, comfortable, wealthy, aristocratic)

        Returns:
            Market data with available goods and services
        """
        # Number of merchants based on wealth
        merchant_count = {"destitute": 2, "poor": 5, "modest": 10, "comfortable": 15,
                         "wealthy": 25, "aristocratic": 40}.get(wealth_level, 10)

        merchants = []
        for _ in range(merchant_count):
            merchant = self.generate_npc(archetype_name="merchant", location_id=location.get("id") if location else None)
            merchants.append(merchant)

        # Available goods (mix of item types)
        goods = []
        for _ in range(merchant_count * 3):
            item = self.generate_item()
            supply = self.rng.choice(["abundant", "normal", "normal", "scarce"])
            demand = self.rng.choice(["low", "normal", "normal", "high"])
            pricing = self.calculate_item_price(item, location, supply, demand)

            goods.append({
                "item": item,
                "pricing": pricing,
                "merchant_index": self.rng.randint(0, merchant_count - 1)
            })

        # Services
        services = []
        service_types = ["lodging", "meals", "transport", "professional"]
        for stype in service_types:
            if stype in self.economy_config["services"]:
                for service_name, service_data in self.economy_config["services"][stype].items():
                    services.append({
                        "type": stype,
                        "name": service_name.replace("_", " ").title(),
                        "base_price": service_data.get("price", service_data.get("price_per_night", service_data.get("price_per_service", 10))),
                        "description": service_data.get("description", "")
                    })

        return {
            "location": location.get("name") if location else "Generic Market",
            "wealth_level": wealth_level,
            "merchant_count": merchant_count,
            "merchants": merchants,
            "available_goods": goods,
            "available_services": services,
            "market_conditions": "normal",  # Could be dynamic
            "taxes": {
                "sales_tax": self.economy_config["taxation"]["sales_tax"]["typical_rate"],
                "tariff": self.economy_config["taxation"]["tariff"]["typical_rate"]
            }
        }

    # ========== NEW FEATURES: Enhanced Quest System ==========

    def generate_quest_advanced(self, quest_type: Optional[str] = None, difficulty: int = 1,
                               faction: Optional[str] = None, create_chain: bool = False) -> Dict[str, Any]:
        """
        Generate advanced quest with branching objectives and complications.

        Args:
            quest_type: Quest type from quests.json
            difficulty: Difficulty (1-10)
            faction: Faction offering quest
            create_chain: Whether to create a quest chain

        Returns:
            Advanced quest data
        """
        # Select quest type
        if quest_type is None:
            quest_type = self.rng.choice(list(self.quests_config["quest_types"].keys()))

        quest_template = self.quests_config["quest_types"][quest_type]

        # Generate quest name and objective
        objective_template = self.rng.choice(quest_template["common_objectives"])
        quest_variables = self.quests_config["quest_variables"]

        obj_values = {key: self.rng.choice(values) for key, values in quest_variables.items()}
        obj_values["number"] = str(self.rng.randint(3, 10))

        objective = self._fill_template(objective_template, obj_values)

        # Quest giver
        giver_type = self.rng.choice(list(self.quests_config["quest_givers"].keys()))
        giver_data = self.quests_config["quest_givers"][giver_type]
        giver_profession = self.rng.choice(giver_data["types"])
        quest_giver = self.generate_npc(faction=faction)

        # Generate rewards
        reward_gold_data = self.quests_config["quest_rewards"]["gold"]["base_by_difficulty"][str(difficulty)]
        reward_gold = self.rng.randint(reward_gold_data["min"], reward_gold_data["max"])

        reward_items = []
        for _ in range(min(3, max(1, difficulty // 3))):
            reward_items.append(self.generate_item())

        reputation_points = self.quests_config["quest_rewards"]["reputation"]["points_by_difficulty"][str(difficulty)]
        experience_points = self.quests_config["quest_rewards"]["experience"]["points_by_difficulty"][str(difficulty)]

        # Complications
        complication = self.rng.choice(quest_template["complications"]) if self.rng.random() < 0.4 else None

        # Secondary objectives
        secondary_objectives = []
        if self.rng.random() < 0.5:
            secondary_obj = self.rng.choice(self.quests_config["quest_objectives"]["secondary"]["examples"])
            secondary_objectives.append(secondary_obj)

        # Quest chain (if requested)
        next_quest = None
        if create_chain and self.rng.random() < 0.7:
            next_quest = self.generate_quest_advanced(difficulty=difficulty + 1, faction=faction, create_chain=False)

        quest = {
            "name": f"The {self.rng.choice(['Ancient', 'Forgotten', 'Lost', 'Hidden', 'Dangerous'])} {quest_type.title()}",
            "type": quest_type,
            "difficulty": difficulty,
            "primary_objective": objective,
            "secondary_objectives": secondary_objectives,
            "quest_giver": quest_giver,
            "quest_giver_type": giver_type,
            "complication": complication,
            "rewards": {
                "gold": reward_gold,
                "items": reward_items,
                "reputation": reputation_points,
                "experience": experience_points,
                "faction": faction
            },
            "failure_consequences": quest_template["failure_consequences"],
            "status": "available",
            "next_in_chain": next_quest
        }

        return quest

    # ========== NEW FEATURES: Relationship System ==========

    def add_relationship(self, npc1: Dict[str, Any], npc2: Dict[str, Any],
                        relationship_type: str = "neutral") -> None:
        """
        Add a relationship between two NPCs.

        Args:
            npc1: First NPC
            npc2: Second NPC
            relationship_type: Type (friend, rival, enemy, family, romantic, mentor)
        """
        if "relationships" not in npc1:
            npc1["relationships"] = []
        if "relationships" not in npc2:
            npc2["relationships"] = []

        npc1["relationships"].append({
            "npc_name": npc2["name"],
            "type": relationship_type,
            "reputation": self._get_relationship_reputation(relationship_type)
        })

        npc2["relationships"].append({
            "npc_name": npc1["name"],
            "type": relationship_type,
            "reputation": self._get_relationship_reputation(relationship_type)
        })

    def _get_relationship_reputation(self, rel_type: str) -> int:
        """Get reputation value for relationship type."""
        values = {
            "enemy": -100,
            "rival": -50,
            "neutral": 0,
            "acquaintance": 25,
            "friend": 75,
            "close_friend": 100,
            "family": 150,
            "romantic": 125,
            "mentor": 80,
            "apprentice": 60
        }
        return values.get(rel_type, 0)

    def generate_npc_network(self, central_npc: Dict[str, Any], network_size: int = 5) -> List[Dict[str, Any]]:
        """
        Generate a social network around an NPC.

        Args:
            central_npc: NPC at center of network
            network_size: Number of connected NPCs

        Returns:
            List of NPCs with relationships
        """
        network = [central_npc]

        for _ in range(network_size):
            new_npc = self.generate_npc(faction=central_npc.get("faction"))

            # Determine relationship
            rel_types = ["friend", "rival", "acquaintance", "family", "colleague"]
            rel_type = self.rng.choice(rel_types)

            self.add_relationship(central_npc, new_npc, rel_type)
            network.append(new_npc)

        return network

    # ========== NEW FEATURES: Enhanced Description System ==========

    def generate_description(self, content: Dict[str, Any], content_type: str = "item",
                           style: str = "detailed", context: Optional[Dict[str, str]] = None) -> str:
        """
        Generate context-aware description with multiple styles.

        Args:
            content: Content to describe (item, npc, location, spell)
            content_type: Type of content
            style: Description style (technical, poetic, brief, detailed, historical, dramatic, mysterious, etc.)
            context: Context dict with keys like location, weather, time_of_day, mood

        Returns:
            Generated description
        """
        if style not in self.description_styles_config["description_styles"]:
            style = "detailed"

        style_data = self.description_styles_config["description_styles"][style]

        # Get template for content type
        if content_type not in style_data["templates"]:
            # Fallback to brief description
            return content.get("description", f"A {content_type}")

        template = style_data["templates"][content_type]

        # Build values dict from content
        values = dict(content)

        # Add style-specific vocabulary
        if "vocabulary" in style_data:
            values["adjective"] = self.rng.choice(style_data["vocabulary"][:3])

        # Add context-aware modifiers
        if context:
            context_mods = self.description_styles_config.get("context_aware_modifiers", {})

            if "location" in context and "location_based" in context_mods:
                if context["location"] in context_mods["location_based"]:
                    loc_mods = context_mods["location_based"][context["location"]]
                    values["imagery"] = self.rng.choice(loc_mods.get("imagery", ["the surrounding area"]))
                    values["atmosphere"] = loc_mods.get("atmosphere", "")

            if "weather" in context and "weather_based" in context_mods:
                if context["weather"] in context_mods["weather_based"]:
                    weather_mods = context_mods["weather_based"][context["weather"]]
                    values.update(weather_mods.get("sensory", {}))

        # Fill template
        description = self._fill_template(template, values)

        return description

    # ========== NEW FEATURES: Export Formats ==========

    def export_to_markdown(self, data: Any, filename: str, title: str = "Generated Content") -> None:
        """
        Export content to Markdown format.

        Args:
            data: Data to export
            filename: Output filename
            title: Document title
        """
        output_path = Path(filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")

            if isinstance(data, dict):
                self._write_dict_to_markdown(f, data)
            elif isinstance(data, list):
                for idx, item in enumerate(data, 1):
                    f.write(f"## Entry {idx}\n\n")
                    if isinstance(item, dict):
                        self._write_dict_to_markdown(f, item)
                    else:
                        f.write(f"{item}\n\n")
            else:
                f.write(f"{data}\n\n")

        print(f"Exported to {output_path}")

    def _write_dict_to_markdown(self, f, d: Dict, level: int = 3) -> None:
        """Helper to write dict to markdown."""
        for key, value in d.items():
            heading = "#" * level
            key_formatted = key.replace("_", " ").title()

            if isinstance(value, dict):
                f.write(f"{heading} {key_formatted}\n\n")
                self._write_dict_to_markdown(f, value, level + 1)
            elif isinstance(value, list):
                f.write(f"{heading} {key_formatted}\n\n")
                for item in value:
                    if isinstance(item, dict):
                        f.write(f"- ")
                        for k, v in item.items():
                            f.write(f"**{k}**: {v}, ")
                        f.write("\n")
                    else:
                        f.write(f"- {item}\n")
                f.write("\n")
            else:
                f.write(f"**{key_formatted}**: {value}\n\n")

    # ========== NEW FEATURES: Validation & Error Handling ==========

    def validate_item_constraints(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate item generation constraints.

        Args:
            constraints: Constraints dict to validate

        Returns:
            Validation result with any errors
        """
        errors = []
        warnings = []

        valid_qualities = list(self.quality.keys())
        valid_rarities = list(self.rarity.keys())

        if "min_quality" in constraints and constraints["min_quality"] not in valid_qualities:
            errors.append(f"Invalid min_quality: {constraints['min_quality']}. Valid: {valid_qualities}")

        if "max_quality" in constraints and constraints["max_quality"] not in valid_qualities:
            errors.append(f"Invalid max_quality: {constraints['max_quality']}. Valid: {valid_qualities}")

        if "min_rarity" in constraints and constraints["min_rarity"] not in valid_rarities:
            errors.append(f"Invalid min_rarity: {constraints['min_rarity']}. Valid: {valid_rarities}")

        if "exclude_materials" in constraints:
            invalid_mats = [m for m in constraints["exclude_materials"] if m not in self.materials]
            if invalid_mats:
                warnings.append(f"Unknown materials in exclude list: {invalid_mats}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
