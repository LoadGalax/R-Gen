"""
Generator Adapter

Bridge between SimulationEngine and GenerationEngine.
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add GenerationEngine to path
gen_engine_path = Path(__file__).parent.parent.parent.parent / "GenerationEngine"
if str(gen_engine_path) not in sys.path:
    sys.path.insert(0, str(gen_engine_path))

# Import ContentGenerator - try multiple import strategies
try:
    from src.content_generator import ContentGenerator
except ModuleNotFoundError:
    # Fallback: direct module import
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "content_generator",
        gen_engine_path / "src" / "content_generator.py"
    )
    content_generator_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(content_generator_module)
    ContentGenerator = content_generator_module.ContentGenerator


class GeneratorAdapter:
    """
    Adapter to use GenerationEngine within SimulationEngine.

    This class wraps the ContentGenerator and provides a clean interface
    for the simulation to request new content on-demand.
    """

    def __init__(self, seed: Optional[int] = None, data_dir: Optional[str] = None):
        """
        Initialize the generator adapter.

        Args:
            seed: Random seed for reproducibility
            data_dir: Path to data directory (defaults to GenerationEngine/data)
        """
        if data_dir is None:
            data_dir = str(gen_engine_path / "data")

        self.generator = ContentGenerator(seed=seed, data_dir=data_dir)
        self.seed = seed

    def create_initial_world(self, num_locations: int = 10) -> Dict[str, Any]:
        """
        Generate initial world data.

        Args:
            num_locations: Number of locations to generate

        Returns:
            World data dictionary
        """
        return self.generator.generate_world(num_locations=num_locations)

    def spawn_npc(self, professions: Optional[List[str]] = None,
                  race: Optional[str] = None,
                  faction: Optional[str] = None,
                  level: Optional[str] = None,
                  location_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a new NPC on-demand.

        Args:
            professions: List of professions (or None for random)
            race: Race name (or None for random)
            faction: Faction name (or None for random)
            level: Profession level (or None for random)
            location_id: Location where NPC spawns

        Returns:
            NPC data dictionary
        """
        npc = self.generator.generate_npc(
            professions=professions,
            race=race,
            faction=faction,
            profession_level=level
        )

        if location_id:
            npc["location"] = location_id

        return npc

    def spawn_item(self, template: str,
                   quality_min: Optional[str] = None,
                   rarity_min: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a new item on-demand.

        Args:
            template: Item template name
            quality_min: Minimum quality tier
            rarity_min: Minimum rarity tier

        Returns:
            Item data dictionary
        """
        constraints = {}
        if quality_min:
            constraints["quality_min"] = quality_min
        if rarity_min:
            constraints["rarity_min"] = rarity_min

        return self.generator.generate_item(template, constraints=constraints)

    def spawn_location(self, template: Optional[str] = None,
                      biome: Optional[str] = None,
                      num_connections: int = 2) -> Dict[str, Any]:
        """
        Generate a new location on-demand.

        Args:
            template: Location template name (or None for random)
            biome: Biome type
            num_connections: Number of connections to generate

        Returns:
            Location data dictionary
        """
        return self.generator.generate_location(
            template=template,
            num_connections=num_connections,
            biome=biome
        )

    def generate_quest(self, quest_type: Optional[str] = None,
                      difficulty: int = 1,
                      create_chain: bool = False) -> Dict[str, Any]:
        """
        Generate a quest.

        Args:
            quest_type: Type of quest (or None for random)
            difficulty: Quest difficulty (1-10)
            create_chain: Whether to create a quest chain

        Returns:
            Quest data dictionary
        """
        return self.generator.generate_quest_advanced(
            quest_type=quest_type,
            difficulty=difficulty,
            create_chain=create_chain
        )

    def generate_encounter(self, party_level: int,
                          biome: Optional[str] = None,
                          encounter_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a random encounter.

        Args:
            party_level: Level of the party
            biome: Biome where encounter occurs
            encounter_type: Type of encounter

        Returns:
            Encounter data dictionary
        """
        return self.generator.generate_encounter(
            party_level=party_level,
            biome=biome,
            encounter_type=encounter_type
        )

    def generate_organization(self, org_type: Optional[str] = None,
                            faction: Optional[str] = None,
                            size: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Generate an organization.

        Args:
            org_type: Type of organization
            faction: Faction affiliation
            size: (min, max) size tuple

        Returns:
            Organization data dictionary
        """
        return self.generator.generate_organization(
            org_type=org_type,
            faction=faction,
            size=size
        )

    def generate_weather(self, biome: Optional[str] = None,
                        season: Optional[str] = None,
                        time_of_day: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate weather conditions.

        Args:
            biome: Biome type
            season: Current season
            time_of_day: Time of day

        Returns:
            Weather data dictionary
        """
        return self.generator.generate_weather_detailed(
            biome=biome,
            season=season,
            time_of_day=time_of_day
        )

    def generate_animal(self, category: Optional[str] = None,
                       species: Optional[str] = None,
                       owner: Optional[str] = None,
                       habitat: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an animal.

        Args:
            category: Animal category
            species: Specific species
            owner: Owner name (for pets)
            habitat: Animal's habitat

        Returns:
            Animal data dictionary
        """
        return self.generator.generate_animal(
            category=category,
            species=species,
            owner=owner,
            habitat=habitat
        )

    def generate_flora(self, category: Optional[str] = None,
                      species: Optional[str] = None,
                      habitat: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate flora.

        Args:
            category: Flora category
            species: Specific species
            habitat: Flora's habitat

        Returns:
            Flora data dictionary
        """
        return self.generator.generate_flora(
            category=category,
            species=species,
            habitat=habitat
        )

    def generate_market(self, location_id: str,
                       wealth_level: str = "moderate") -> Dict[str, Any]:
        """
        Generate a market.

        Args:
            location_id: Location where market exists
            wealth_level: Economic wealth level

        Returns:
            Market data dictionary
        """
        return self.generator.generate_market(
            location=location_id,
            wealth_level=wealth_level
        )

    def generate_spell(self, level: Optional[int] = None,
                      school: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a spell.

        Args:
            level: Spell level (0-9)
            school: Magic school

        Returns:
            Spell data dictionary
        """
        return self.generator.generate_spell(level=level, school=school)

    def reset_seed(self, seed: Optional[int] = None):
        """
        Reset the random seed.

        Args:
            seed: New seed (or None to use original)
        """
        self.generator.reset_seed(seed if seed is not None else self.seed)

    def get_available_templates(self, category: str) -> List[str]:
        """
        Get list of available templates for a category.

        Args:
            category: Template category (items, locations, etc.)

        Returns:
            List of template names
        """
        if category == "items":
            return list(self.generator.item_templates.keys())
        elif category == "locations":
            return list(self.generator.locations.keys())
        elif category == "professions":
            return list(self.generator.professions.keys())
        elif category == "organizations":
            return list(self.generator.organizations.keys())
        elif category == "quests":
            return list(self.generator.quests.keys())
        elif category == "races":
            return list(self.generator.races.keys())
        elif category == "factions":
            return list(self.generator.factions.keys())
        else:
            return []
