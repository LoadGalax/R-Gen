#!/usr/bin/env python3
"""
Comprehensive test suite for all R-Gen generation methods.
This script tests every generation feature to identify bugs and issues.
"""

import sys
import json
import traceback
from pathlib import Path
from typing import Dict, List, Any

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from content_generator import ContentGenerator


class TestRunner:
    """Test runner for comprehensive generation testing."""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []
        self.generator = None

    def log_error(self, test_name: str, error: Exception, details: str = ""):
        """Log an error during testing."""
        self.errors.append({
            "test": test_name,
            "error": str(error),
            "type": type(error).__name__,
            "details": details,
            "traceback": traceback.format_exc()
        })
        print(f"❌ FAILED: {test_name}")
        print(f"   Error: {error}")
        if details:
            print(f"   Details: {details}")

    def log_warning(self, test_name: str, warning: str):
        """Log a warning during testing."""
        self.warnings.append({
            "test": test_name,
            "warning": warning
        })
        print(f"⚠️  WARNING: {test_name}")
        print(f"   {warning}")

    def log_success(self, test_name: str):
        """Log a successful test."""
        self.passed.append(test_name)
        print(f"✅ PASSED: {test_name}")

    def validate_item(self, item: Dict[str, Any], test_name: str) -> bool:
        """Validate an item has required fields."""
        required_fields = ["name", "type", "subtype", "value", "description", "stats", "properties"]
        for field in required_fields:
            if field not in item:
                self.log_error(test_name, ValueError(f"Missing required field: {field}"),
                             f"Item: {item.get('name', 'Unknown')}")
                return False

        # Validate types
        if not isinstance(item["name"], str) or not item["name"]:
            self.log_error(test_name, ValueError("Invalid name"),
                         f"Name must be non-empty string, got: {item.get('name')}")
            return False

        if not isinstance(item["value"], int) or item["value"] < 0:
            self.log_warning(test_name, f"Item value should be non-negative int, got: {item['value']}")

        if not isinstance(item["stats"], dict):
            self.log_error(test_name, TypeError("stats must be dict"),
                         f"Got type: {type(item['stats'])}")
            return False

        return True

    def validate_npc(self, npc: Dict[str, Any], test_name: str) -> bool:
        """Validate an NPC has required fields."""
        required_fields = ["name", "description", "stats"]
        for field in required_fields:
            if field not in npc:
                self.log_error(test_name, ValueError(f"Missing required field: {field}"),
                             f"NPC: {npc.get('name', 'Unknown')}")
                return False

        if not isinstance(npc["name"], str) or not npc["name"]:
            self.log_error(test_name, ValueError("Invalid name"),
                         f"Name must be non-empty string, got: {npc.get('name')}")
            return False

        if not isinstance(npc["stats"], dict):
            self.log_error(test_name, TypeError("stats must be dict"),
                         f"Got type: {type(npc['stats'])}")
            return False

        # Check for professions field (should exist even if empty list)
        if "professions" not in npc and "archetype" not in npc:
            self.log_warning(test_name,
                           f"NPC '{npc['name']}' has neither 'professions' nor 'archetype' field")

        return True

    def validate_location(self, location: Dict[str, Any], test_name: str) -> bool:
        """Validate a location has required fields."""
        required_fields = ["id", "name", "type", "description"]
        for field in required_fields:
            if field not in location:
                self.log_error(test_name, ValueError(f"Missing required field: {field}"),
                             f"Location: {location.get('name', 'Unknown')}")
                return False

        if "npcs" in location and not isinstance(location["npcs"], list):
            self.log_error(test_name, TypeError("npcs must be a list"),
                         f"Got type: {type(location['npcs'])}")
            return False

        if "items" in location and not isinstance(location["items"], list):
            self.log_error(test_name, TypeError("items must be a list"),
                         f"Got type: {type(location['items'])}")
            return False

        return True

    def validate_animal(self, animal: Dict[str, Any], test_name: str) -> bool:
        """Validate an animal has required fields."""
        required_fields = ["name", "species", "category", "description"]
        for field in required_fields:
            if field not in animal:
                self.log_error(test_name, ValueError(f"Missing required field: {field}"),
                             f"Animal: {animal.get('name', 'Unknown')}")
                return False
        return True

    def validate_flora(self, flora: Dict[str, Any], test_name: str) -> bool:
        """Validate flora has required fields."""
        required_fields = ["name", "species", "category", "description"]
        for field in required_fields:
            if field not in flora:
                self.log_error(test_name, ValueError(f"Missing required field: {field}"),
                             f"Flora: {flora.get('name', 'Unknown')}")
                return False
        return True

    def run_all_tests(self):
        """Run all generation tests."""
        print("="*80)
        print("R-Gen Comprehensive Test Suite")
        print("="*80)
        print()

        try:
            self.generator = ContentGenerator(data_dir="data", seed=12345)
            print("✅ ContentGenerator initialized successfully")
            print()
        except Exception as e:
            print(f"❌ CRITICAL: Failed to initialize ContentGenerator: {e}")
            traceback.print_exc()
            return

        # Run test categories
        self.test_basic_item_generation()
        self.test_item_constraints()
        self.test_item_sets()
        self.test_equipment_generation()
        self.test_npc_generation()
        self.test_location_generation()
        self.test_world_generation()
        self.test_animal_generation()
        self.test_flora_generation()
        self.test_loot_generation()
        self.test_quest_generation()
        self.test_crafting_recipes()
        self.test_encounters()
        self.test_procedural_names()
        self.test_item_modifiers()
        self.test_item_set_collections()
        self.test_batch_generation()
        self.test_weather_generation()
        self.test_traps_and_puzzles()
        self.test_spell_generation()
        self.test_spellbook_generation()
        self.test_organization_generation()
        self.test_weather_detailed()
        self.test_market_generation()
        self.test_quest_advanced()
        self.test_npc_network()
        self.test_description_generation()

        # Print summary
        self.print_summary()

    def test_basic_item_generation(self):
        """Test basic item generation."""
        print("\n" + "="*80)
        print("Testing Basic Item Generation")
        print("="*80)

        # Test random item
        try:
            item = self.generator.generate_item()
            if self.validate_item(item, "Generate random item"):
                self.log_success("Generate random item")
        except Exception as e:
            self.log_error("Generate random item", e)

        # Test specific templates (only test templates that exist)
        templates = ["weapon_melee", "weapon_ranged", "armor", "potion",
                    "jewelry", "scroll"]

        for template in templates:
            try:
                item = self.generator.generate_item(template)
                if self.validate_item(item, f"Generate {template}"):
                    self.log_success(f"Generate {template}")
            except Exception as e:
                self.log_error(f"Generate {template}", e)

        # Test with invalid template
        try:
            item = self.generator.generate_item("invalid_template_xyz")
            self.log_warning("Generate invalid template",
                           "Should have raised an error for invalid template")
        except KeyError:
            self.log_success("Invalid template rejection")
        except Exception as e:
            self.log_error("Invalid template handling", e)

    def test_item_constraints(self):
        """Test item generation with constraints."""
        print("\n" + "="*80)
        print("Testing Item Constraints")
        print("="*80)

        # Test quality constraints
        try:
            item = self.generator.generate_item(constraints={"min_quality": "Excellent"})
            if item["quality"] in ["Excellent", "Masterwork", "Legendary"]:
                self.log_success("Quality constraint (min)")
            else:
                self.log_error("Quality constraint (min)",
                             ValueError(f"Got quality: {item['quality']}"))
        except Exception as e:
            self.log_error("Quality constraint (min)", e)

        # Test rarity constraints
        try:
            item = self.generator.generate_item(constraints={"min_rarity": "Rare"})
            if item["rarity"] in ["Rare", "Epic", "Legendary", "Mythic"]:
                self.log_success("Rarity constraint (min)")
            else:
                self.log_error("Rarity constraint (min)",
                             ValueError(f"Got rarity: {item['rarity']}"))
        except Exception as e:
            self.log_error("Rarity constraint (min)", e)

        # Test value constraints
        try:
            item = self.generator.generate_item(constraints={"min_value": 1000})
            if item["value"] >= 1000:
                self.log_success("Value constraint (min)")
            else:
                self.log_error("Value constraint (min)",
                             ValueError(f"Got value: {item['value']}"))
        except Exception as e:
            self.log_error("Value constraint (min)", e)

        # Test required stats (case-insensitive)
        try:
            item = self.generator.generate_item(constraints={"required_stats": ["strength", "dexterity"]})
            # Check for stats case-insensitively
            stat_keys_lower = [k.lower() for k in item["stats"].keys()]
            if "strength" in stat_keys_lower and "dexterity" in stat_keys_lower:
                self.log_success("Required stats constraint")
            else:
                self.log_error("Required stats constraint",
                             ValueError(f"Missing required stats. Got stats: {list(item['stats'].keys())}"))
        except Exception as e:
            self.log_error("Required stats constraint", e)

    def test_item_sets(self):
        """Test item set generation."""
        print("\n" + "="*80)
        print("Testing Item Sets")
        print("="*80)

        # Get available item sets
        item_sets = list(self.generator.item_sets.keys()) if hasattr(self.generator, 'item_sets') else []

        if not item_sets:
            self.log_warning("Item sets test", "No item sets found in configuration")
            return

        for set_name in item_sets[:5]:  # Test first 5 sets
            try:
                items = self.generator.generate_items_from_set(set_name, count=3)
                if isinstance(items, list) and len(items) == 3:
                    all_valid = True
                    for item in items:
                        if not self.validate_item(item, f"Item set '{set_name}' item"):
                            all_valid = False
                            break
                    if all_valid:
                        self.log_success(f"Generate item set '{set_name}'")
                else:
                    self.log_error(f"Generate item set '{set_name}'",
                                 ValueError(f"Expected 3 items, got {len(items) if isinstance(items, list) else 'non-list'}"))
            except Exception as e:
                self.log_error(f"Generate item set '{set_name}'", e)

    def test_equipment_generation(self):
        """Test equipment generation."""
        print("\n" + "="*80)
        print("Testing Equipment Generation")
        print("="*80)

        try:
            equipment = self.generator.generate_equipment(equipment_chance=0.5)
            if not isinstance(equipment, dict):
                self.log_error("Generate equipment", TypeError("Expected dict"))
                return

            expected_slots = ["chest", "helmet", "gloves", "legs", "boots", "belt",
                            "ring1", "ring2", "earring1", "earring2", "collar"]

            for slot in expected_slots:
                if slot not in equipment:
                    self.log_error("Generate equipment",
                                 ValueError(f"Missing slot: {slot}"))
                    return

            self.log_success("Generate equipment")
        except Exception as e:
            self.log_error("Generate equipment", e)

    def test_npc_generation(self):
        """Test NPC generation."""
        print("\n" + "="*80)
        print("Testing NPC Generation")
        print("="*80)

        # Test random NPC
        try:
            npc = self.generator.generate_npc()
            if self.validate_npc(npc, "Generate random NPC"):
                self.log_success("Generate random NPC")
        except Exception as e:
            self.log_error("Generate random NPC", e)

        # Test specific professions
        professions = list(self.generator.professions.keys())[:5]  # Test first 5

        for profession in professions:
            try:
                npc = self.generator.generate_npc(profession_names=[profession])
                if self.validate_npc(npc, f"Generate NPC with profession '{profession}'"):
                    # Verify profession is in the list
                    if "professions" in npc and profession in npc["professions"]:
                        self.log_success(f"Generate NPC with profession '{profession}'")
                    elif "archetype" in npc and npc["archetype"] == profession:
                        self.log_success(f"Generate NPC with profession '{profession}' (legacy)")
                    else:
                        self.log_warning(f"Generate NPC with profession '{profession}'",
                                       f"Profession not found in NPC data. Got: {npc.get('professions', npc.get('archetype'))}")
            except Exception as e:
                self.log_error(f"Generate NPC with profession '{profession}'", e)

        # Test NPC with no profession
        try:
            npc = self.generator.generate_npc(profession_names=[])
            if self.validate_npc(npc, "Generate NPC with no profession"):
                if "professions" in npc and len(npc["professions"]) == 0:
                    self.log_success("Generate NPC with no profession")
                else:
                    self.log_warning("Generate NPC with no profession",
                                   f"Expected empty professions list, got: {npc.get('professions')}")
        except Exception as e:
            self.log_error("Generate NPC with no profession", e)

        # Test NPC with multiple professions
        try:
            if len(professions) >= 2:
                npc = self.generator.generate_npc(profession_names=professions[:2])
                if self.validate_npc(npc, "Generate NPC with multiple professions"):
                    self.log_success("Generate NPC with multiple professions")
        except Exception as e:
            self.log_error("Generate NPC with multiple professions", e)

        # Test NPC with specific race
        try:
            races = list(self.generator.races_config.get("races", {}).keys())
            if races:
                npc = self.generator.generate_npc(race=races[0])
                if self.validate_npc(npc, f"Generate NPC with race '{races[0]}'"):
                    if npc.get("race") == races[0]:
                        self.log_success(f"Generate NPC with race '{races[0]}'")
                    else:
                        self.log_warning(f"Generate NPC with race '{races[0]}'",
                                       f"Expected race '{races[0]}', got '{npc.get('race')}'")
        except Exception as e:
            self.log_error("Generate NPC with specific race", e)

        # Test NPC with specific faction
        try:
            factions = list(self.generator.factions_config.get("factions", {}).keys())
            if factions:
                npc = self.generator.generate_npc(faction=factions[0])
                if self.validate_npc(npc, f"Generate NPC with faction '{factions[0]}'"):
                    self.log_success(f"Generate NPC with faction '{factions[0]}'")
        except Exception as e:
            self.log_error("Generate NPC with specific faction", e)

    def test_location_generation(self):
        """Test location generation."""
        print("\n" + "="*80)
        print("Testing Location Generation")
        print("="*80)

        # Test random location
        try:
            location = self.generator.generate_location()
            if self.validate_location(location, "Generate random location"):
                self.log_success("Generate random location")
        except Exception as e:
            self.log_error("Generate random location", e)

        # Test specific location templates
        templates = list(self.generator.locations_config.get("templates", {}).keys())[:5]

        for template in templates:
            try:
                location = self.generator.generate_location(template_name=template)
                if self.validate_location(location, f"Generate location '{template}'"):
                    self.log_success(f"Generate location '{template}'")
            except Exception as e:
                self.log_error(f"Generate location '{template}'", e)

        # Test location with connections
        try:
            location = self.generator.generate_location(generate_connections=True)
            if self.validate_location(location, "Generate location with connections"):
                if "connections" in location and isinstance(location["connections"], dict):
                    self.log_success("Generate location with connections")
                else:
                    self.log_warning("Generate location with connections",
                                   "Location missing connections dict")
        except Exception as e:
            self.log_error("Generate location with connections", e)

        # Test location with specific biome
        try:
            biomes = list(self.generator.biomes_config.get("biomes", {}).keys())
            if biomes:
                location = self.generator.generate_location(biome=biomes[0])
                if self.validate_location(location, f"Generate location in biome '{biomes[0]}'"):
                    self.log_success(f"Generate location in biome '{biomes[0]}'")
        except Exception as e:
            self.log_error("Generate location with specific biome", e)

    def test_world_generation(self):
        """Test world generation."""
        print("\n" + "="*80)
        print("Testing World Generation")
        print("="*80)

        try:
            world = self.generator.generate_world(num_locations=5)

            if not isinstance(world, dict):
                self.log_error("Generate world", TypeError("Expected dict"))
                return

            if "locations" not in world:
                self.log_error("Generate world", ValueError("Missing 'locations' field"))
                return

            locations = world["locations"]
            if isinstance(locations, dict):
                locations = list(locations.values())

            if len(locations) != 5:
                self.log_warning("Generate world",
                               f"Expected 5 locations, got {len(locations)}")

            # Validate each location
            all_valid = True
            for loc in locations:
                if not self.validate_location(loc, "World location"):
                    all_valid = False
                    break

            if all_valid:
                self.log_success("Generate world (5 locations)")
        except Exception as e:
            self.log_error("Generate world", e)

        # Test small world
        try:
            world = self.generator.generate_world(num_locations=2)
            self.log_success("Generate small world (2 locations)")
        except Exception as e:
            self.log_error("Generate small world", e)

    def test_animal_generation(self):
        """Test animal generation."""
        print("\n" + "="*80)
        print("Testing Animal Generation")
        print("="*80)

        # Test random animal
        try:
            animal = self.generator.generate_animal()
            if self.validate_animal(animal, "Generate random animal"):
                self.log_success("Generate random animal")
        except Exception as e:
            self.log_error("Generate random animal", e)

        # Test specific categories
        categories = ["wild_fauna", "pet"]
        for category in categories:
            try:
                animal = self.generator.generate_animal(category=category)
                if self.validate_animal(animal, f"Generate {category} animal"):
                    if animal.get("category") == category:
                        self.log_success(f"Generate {category} animal")
                    else:
                        self.log_warning(f"Generate {category} animal",
                                       f"Expected category '{category}', got '{animal.get('category')}'")
            except Exception as e:
                self.log_error(f"Generate {category} animal", e)

        # Test specific species
        try:
            species_data = self.generator.animal_species.get("species", {})
            if species_data:
                species_name = list(species_data.keys())[0]
                animal = self.generator.generate_animal(species=species_name)
                if self.validate_animal(animal, f"Generate animal species '{species_name}'"):
                    self.log_success(f"Generate animal species '{species_name}'")
        except Exception as e:
            self.log_error("Generate animal with specific species", e)

    def test_flora_generation(self):
        """Test flora generation."""
        print("\n" + "="*80)
        print("Testing Flora Generation")
        print("="*80)

        # Test random flora
        try:
            flora = self.generator.generate_flora()
            if self.validate_flora(flora, "Generate random flora"):
                self.log_success("Generate random flora")
        except Exception as e:
            self.log_error("Generate random flora", e)

        # Test specific categories
        categories = ["trees", "plants", "mushrooms", "crops", "vines"]
        for category in categories:
            try:
                flora = self.generator.generate_flora(category=category)
                if self.validate_flora(flora, f"Generate {category} flora"):
                    if flora.get("category") == category:
                        self.log_success(f"Generate {category} flora")
                    else:
                        self.log_warning(f"Generate {category} flora",
                                       f"Expected category '{category}', got '{flora.get('category')}'")
            except Exception as e:
                self.log_error(f"Generate {category} flora", e)

        # Test specific species
        try:
            species_data = self.generator.flora_species.get("species", {})
            if species_data:
                species_name = list(species_data.keys())[0]
                flora = self.generator.generate_flora(species=species_name)
                if self.validate_flora(flora, f"Generate flora species '{species_name}'"):
                    self.log_success(f"Generate flora species '{species_name}'")
        except Exception as e:
            self.log_error("Generate flora with specific species", e)

    def test_loot_generation(self):
        """Test loot table generation."""
        print("\n" + "="*80)
        print("Testing Loot Generation")
        print("="*80)

        enemy_types = ["minion", "standard", "elite", "boss"]
        for enemy_type in enemy_types:
            try:
                loot = self.generator.generate_loot_table(enemy_type=enemy_type, difficulty=5)
                if isinstance(loot, dict) and "items" in loot:
                    self.log_success(f"Generate loot for {enemy_type}")
                else:
                    self.log_error(f"Generate loot for {enemy_type}",
                                 ValueError("Expected dict with 'items' field"))
            except Exception as e:
                self.log_error(f"Generate loot for {enemy_type}", e)

    def test_quest_generation(self):
        """Test quest generation."""
        print("\n" + "="*80)
        print("Testing Quest Generation")
        print("="*80)

        # Test random quest
        try:
            quest = self.generator.generate_quest()
            if isinstance(quest, dict) and "title" in quest and "description" in quest:
                self.log_success("Generate random quest")
            else:
                self.log_error("Generate random quest",
                             ValueError("Quest missing required fields"))
        except Exception as e:
            self.log_error("Generate random quest", e)

        # Test specific quest types
        quest_types = ["fetch", "kill", "escort", "explore", "craft", "deliver"]
        for quest_type in quest_types:
            try:
                quest = self.generator.generate_quest(quest_type=quest_type, difficulty=3)
                if isinstance(quest, dict):
                    self.log_success(f"Generate {quest_type} quest")
                else:
                    self.log_error(f"Generate {quest_type} quest",
                                 TypeError("Expected dict"))
            except Exception as e:
                self.log_error(f"Generate {quest_type} quest", e)

    def test_crafting_recipes(self):
        """Test crafting recipe generation."""
        print("\n" + "="*80)
        print("Testing Crafting Recipes")
        print("="*80)

        try:
            recipe = self.generator.generate_crafting_recipe()
            if isinstance(recipe, dict) and "output" in recipe and "ingredients" in recipe:
                self.log_success("Generate random crafting recipe")
            else:
                self.log_error("Generate random crafting recipe",
                             ValueError("Recipe missing required fields"))
        except Exception as e:
            self.log_error("Generate random crafting recipe", e)

        # Test recipe with specific output item
        try:
            item = self.generator.generate_item("weapon_melee")
            recipe = self.generator.generate_crafting_recipe(output_item=item, difficulty=5)
            if isinstance(recipe, dict):
                self.log_success("Generate recipe for specific item")
        except Exception as e:
            self.log_error("Generate recipe for specific item", e)

    def test_encounters(self):
        """Test encounter generation."""
        print("\n" + "="*80)
        print("Testing Encounters")
        print("="*80)

        encounter_types = ["combat", "social", "puzzle", "trap"]
        for enc_type in encounter_types:
            try:
                encounter = self.generator.generate_encounter(
                    party_level=5,
                    encounter_type=enc_type
                )
                if isinstance(encounter, dict):
                    self.log_success(f"Generate {enc_type} encounter")
                else:
                    self.log_error(f"Generate {enc_type} encounter",
                                 TypeError("Expected dict"))
            except Exception as e:
                self.log_error(f"Generate {enc_type} encounter", e)

    def test_procedural_names(self):
        """Test procedural name generation."""
        print("\n" + "="*80)
        print("Testing Procedural Names")
        print("="*80)

        races = ["human", "elf", "dwarf", "orc"]
        genders = ["male", "female"]

        for race in races:
            for gender in genders:
                try:
                    name = self.generator.generate_procedural_name(race=race, gender=gender)
                    if isinstance(name, str) and len(name) > 0:
                        self.log_success(f"Generate {race} {gender} name: {name}")
                    else:
                        self.log_error(f"Generate {race} {gender} name",
                                     ValueError("Name must be non-empty string"))
                except Exception as e:
                    self.log_error(f"Generate {race} {gender} name", e)

    def test_item_modifiers(self):
        """Test item generation with modifiers."""
        print("\n" + "="*80)
        print("Testing Item Modifiers")
        print("="*80)

        for num_mods in [0, 1, 2]:
            try:
                item = self.generator.generate_item_with_modifiers(
                    template_name="weapon_melee",
                    num_modifiers=num_mods
                )
                if self.validate_item(item, f"Generate item with {num_mods} modifiers"):
                    self.log_success(f"Generate item with {num_mods} modifiers")
            except Exception as e:
                self.log_error(f"Generate item with {num_mods} modifiers", e)

    def test_item_set_collections(self):
        """Test item set collection generation."""
        print("\n" + "="*80)
        print("Testing Item Set Collections")
        print("="*80)

        try:
            item_set = self.generator.generate_item_set_collection(set_size=5)
            if isinstance(item_set, dict) and "items" in item_set:
                self.log_success("Generate item set collection")
            else:
                self.log_error("Generate item set collection",
                             ValueError("Expected dict with 'items' field"))
        except Exception as e:
            self.log_error("Generate item set collection", e)

    def test_batch_generation(self):
        """Test batch generation with distribution."""
        print("\n" + "="*80)
        print("Testing Batch Generation")
        print("="*80)

        content_types = ["item", "npc", "location"]
        for content_type in content_types:
            try:
                batch = self.generator.generate_batch_with_distribution(
                    content_type=content_type,
                    count=10
                )
                if isinstance(batch, list) and len(batch) == 10:
                    self.log_success(f"Generate batch of {content_type}s")
                else:
                    self.log_error(f"Generate batch of {content_type}s",
                                 ValueError(f"Expected list of 10, got {len(batch) if isinstance(batch, list) else 'non-list'}"))
            except Exception as e:
                self.log_error(f"Generate batch of {content_type}s", e)

    def test_weather_generation(self):
        """Test weather and time generation."""
        print("\n" + "="*80)
        print("Testing Weather Generation")
        print("="*80)

        try:
            weather = self.generator.generate_weather_and_time()
            if isinstance(weather, dict):
                self.log_success("Generate weather and time")
            else:
                self.log_error("Generate weather and time",
                             TypeError("Expected dict"))
        except Exception as e:
            self.log_error("Generate weather and time", e)

    def test_traps_and_puzzles(self):
        """Test trap and puzzle generation."""
        print("\n" + "="*80)
        print("Testing Traps and Puzzles")
        print("="*80)

        trap_types = ["mechanical", "magical", "puzzle", "environmental"]
        for trap_type in trap_types:
            try:
                trap = self.generator.generate_trap_or_puzzle(
                    difficulty=5,
                    trap_type=trap_type
                )
                if isinstance(trap, dict):
                    self.log_success(f"Generate {trap_type} trap/puzzle")
                else:
                    self.log_error(f"Generate {trap_type} trap/puzzle",
                                 TypeError("Expected dict"))
            except Exception as e:
                self.log_error(f"Generate {trap_type} trap/puzzle", e)

    def test_spell_generation(self):
        """Test spell generation."""
        print("\n" + "="*80)
        print("Testing Spell Generation")
        print("="*80)

        # Test spells of different levels
        for spell_level in range(0, 10):
            try:
                spell = self.generator.generate_spell(spell_level=spell_level)
                if isinstance(spell, dict) and "name" in spell:
                    self.log_success(f"Generate level {spell_level} spell")
                else:
                    self.log_error(f"Generate level {spell_level} spell",
                                 ValueError("Spell missing required fields"))
            except Exception as e:
                self.log_error(f"Generate level {spell_level} spell", e)

    def test_spellbook_generation(self):
        """Test spellbook generation."""
        print("\n" + "="*80)
        print("Testing Spellbook Generation")
        print("="*80)

        try:
            spellbook = self.generator.generate_spellbook(caster_level=10)
            if isinstance(spellbook, dict) and "spells" in spellbook:
                self.log_success("Generate spellbook")
            else:
                self.log_error("Generate spellbook",
                             ValueError("Spellbook missing 'spells' field"))
        except Exception as e:
            self.log_error("Generate spellbook", e)

    def test_organization_generation(self):
        """Test organization generation."""
        print("\n" + "="*80)
        print("Testing Organization Generation")
        print("="*80)

        try:
            org = self.generator.generate_organization()
            if isinstance(org, dict) and "name" in org:
                self.log_success("Generate organization")
            else:
                self.log_error("Generate organization",
                             ValueError("Organization missing required fields"))
        except Exception as e:
            self.log_error("Generate organization", e)

    def test_weather_detailed(self):
        """Test detailed weather generation."""
        print("\n" + "="*80)
        print("Testing Detailed Weather")
        print("="*80)

        seasons = ["spring", "summer", "autumn", "winter"]
        for season in seasons:
            try:
                weather = self.generator.generate_weather_detailed(season=season)
                if isinstance(weather, dict):
                    self.log_success(f"Generate {season} weather")
                else:
                    self.log_error(f"Generate {season} weather",
                                 TypeError("Expected dict"))
            except Exception as e:
                self.log_error(f"Generate {season} weather", e)

    def test_market_generation(self):
        """Test market generation."""
        print("\n" + "="*80)
        print("Testing Market Generation")
        print("="*80)

        wealth_levels = ["destitute", "poor", "modest", "comfortable", "wealthy", "aristocratic"]
        for wealth in wealth_levels:
            try:
                market = self.generator.generate_market(wealth_level=wealth)
                if isinstance(market, dict) and "merchants" in market:
                    self.log_success(f"Generate {wealth} market")
                else:
                    self.log_error(f"Generate {wealth} market",
                                 ValueError("Market missing required fields"))
            except Exception as e:
                self.log_error(f"Generate {wealth} market", e)

    def test_quest_advanced(self):
        """Test advanced quest generation."""
        print("\n" + "="*80)
        print("Testing Advanced Quests")
        print("="*80)

        try:
            quest = self.generator.generate_quest_advanced(difficulty=5)
            if isinstance(quest, dict) and "title" in quest:
                self.log_success("Generate advanced quest")
            else:
                self.log_error("Generate advanced quest",
                             ValueError("Quest missing required fields"))
        except Exception as e:
            self.log_error("Generate advanced quest", e)

        # Test quest chain
        try:
            quest = self.generator.generate_quest_advanced(difficulty=3, create_chain=True)
            if isinstance(quest, dict):
                self.log_success("Generate quest chain")
        except Exception as e:
            self.log_error("Generate quest chain", e)

    def test_npc_network(self):
        """Test NPC network generation."""
        print("\n" + "="*80)
        print("Testing NPC Networks")
        print("="*80)

        try:
            central_npc = self.generator.generate_npc()
            network = self.generator.generate_npc_network(central_npc, network_size=5)
            if isinstance(network, list) and len(network) > 0:
                self.log_success("Generate NPC network")
            else:
                self.log_error("Generate NPC network",
                             ValueError("Network must be non-empty list"))
        except Exception as e:
            self.log_error("Generate NPC network", e)

    def test_description_generation(self):
        """Test description generation."""
        print("\n" + "="*80)
        print("Testing Description Generation")
        print("="*80)

        # Test item description
        try:
            item = self.generator.generate_item()
            desc = self.generator.generate_description(item, content_type="item")
            if isinstance(desc, str) and len(desc) > 0:
                self.log_success("Generate item description")
            else:
                self.log_error("Generate item description",
                             ValueError("Description must be non-empty string"))
        except Exception as e:
            self.log_error("Generate item description", e)

        # Test NPC description
        try:
            npc = self.generator.generate_npc()
            desc = self.generator.generate_description(npc, content_type="npc")
            if isinstance(desc, str) and len(desc) > 0:
                self.log_success("Generate NPC description")
            else:
                self.log_error("Generate NPC description",
                             ValueError("Description must be non-empty string"))
        except Exception as e:
            self.log_error("Generate NPC description", e)

    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*80)
        print("Test Summary")
        print("="*80)
        print(f"\n✅ Passed: {len(self.passed)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Failed: {len(self.errors)}")
        print()

        if self.warnings:
            print("\nWarnings:")
            print("-" * 80)
            for warning in self.warnings:
                print(f"\n⚠️  {warning['test']}")
                print(f"   {warning['warning']}")

        if self.errors:
            print("\n\nErrors:")
            print("=" * 80)
            for error in self.errors:
                print(f"\n❌ {error['test']}")
                print(f"   Type: {error['type']}")
                print(f"   Error: {error['error']}")
                if error['details']:
                    print(f"   Details: {error['details']}")
                print(f"\n   Traceback:")
                print(f"   {error['traceback'][:500]}...")  # Truncate long tracebacks

        # Write detailed report to file
        report_file = "test_report.json"
        report = {
            "passed": self.passed,
            "warnings": self.warnings,
            "errors": self.errors,
            "summary": {
                "total_passed": len(self.passed),
                "total_warnings": len(self.warnings),
                "total_errors": len(self.errors)
            }
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n\n📄 Detailed report saved to: {report_file}")

        if len(self.errors) == 0:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print(f"\n⚠️  {len(self.errors)} tests failed. Please review the errors above.")
            return 1


def main():
    """Main entry point."""
    runner = TestRunner()
    exit_code = runner.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
