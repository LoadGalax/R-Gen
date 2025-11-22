# GenerationEngine API Documentation

## Overview

The GenerationEngine (`ContentGenerator` class) is a procedural content generation system for fantasy RPG worlds. It generates items, NPCs, locations, quests, spells, and more with rich, dynamic properties.

## Installation & Setup

```python
from GenerationEngine.src.content_generator import ContentGenerator

# Initialize with default data directory
generator = ContentGenerator(data_dir="data")

# Initialize with specific seed for reproducible results
generator = ContentGenerator(data_dir="data", seed=12345)
```

## Core API Methods

### Item Generation

#### `generate_item(template_name=None, constraints=None)`
Generate a random item (weapons, armor, potions, jewelry, scrolls, etc.)

**Parameters:**
- `template_name` (str, optional): Specific template like "weapon_melee", "weapon_ranged", "armor", "potion", "jewelry", "scroll"
- `constraints` (dict, optional): Generation constraints
  - `min_quality`: Minimum quality ("Poor", "Average", "Good", "Excellent", "Masterwork", "Legendary")
  - `min_rarity`: Minimum rarity ("Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic")
  - `min_value`: Minimum gold value
  - `required_stats`: List of required stats (e.g., ["strength", "dexterity"])

**Example Output:**
```json
{
  "name": "Masterwork Steel Longsword of Fury",
  "type": "weapon",
  "subtype": "melee",
  "quality": "Masterwork",
  "rarity": "Rare",
  "value": 1250,
  "description": "A finely crafted longsword made of gleaming steel, radiating with magical fury.",
  "stats": {
    "Strength": 5,
    "Attack Power": 12
  },
  "properties": {
    "damage": "1d8+3",
    "material": "Steel",
    "weight": 3.5
  }
}
```

#### `generate_items_from_set(set_name, count=None, constraints=None)`
Generate items from a specific item set (matching theme/bonus)

**Parameters:**
- `set_name` (str): Name of the item set
- `count` (int, optional): Number of items to generate
- `constraints` (dict, optional): Same as generate_item

**Example Output:**
```json
[
  {"name": "Dragon Slayer Helm", "type": "armor", "subtype": "helmet", ...},
  {"name": "Dragon Slayer Gauntlets", "type": "armor", "subtype": "gloves", ...},
  {"name": "Dragon Slayer Boots", "type": "armor", "subtype": "boots", ...}
]
```

#### `generate_equipment(equipment_chance=0.7, equipment_set=None)`
Generate a full set of equipment for all slots

**Example Output:**
```json
{
  "chest": {"name": "Reinforced Leather Armor", ...},
  "helmet": {"name": "Iron Helm", ...},
  "gloves": {"name": "Studded Gloves", ...},
  "legs": {"name": "Chain Leggings", ...},
  "boots": {"name": "Leather Boots", ...},
  "belt": null,
  "ring1": {"name": "Ring of Protection", ...},
  "ring2": null,
  "earring1": null,
  "earring2": null,
  "collar": null
}
```

#### `generate_item_with_modifiers(template_name=None, num_modifiers=1, modifier_power=5)`
Generate an item with specific number of magical modifiers

### NPC Generation

#### `generate_npc(archetype_name=None, profession_names=None, race=None, faction=None, level=1)`
Generate a non-player character with stats, inventory, and personality

**Parameters:**
- `archetype_name` (str, optional): Deprecated, use profession_names instead
- `profession_names` (list, optional): List of profession names (e.g., ["Blacksmith", "Warrior"])
- `race` (str, optional): Race like "human", "elf", "dwarf", "orc"
- `faction` (str, optional): Faction affiliation
- `level` (int): Character level

**Example Output:**
```json
{
  "name": "Thorin Ironforge",
  "race": "dwarf",
  "professions": ["Blacksmith", "Warrior"],
  "level": 5,
  "description": "A sturdy dwarf with a thick beard, skilled in both forge and combat.",
  "stats": {
    "Strength": 16,
    "Constitution": 14,
    "Intelligence": 10,
    "Wisdom": 12,
    "Dexterity": 8,
    "Charisma": 10
  },
  "personality": {
    "traits": ["Gruff", "Loyal", "Perfectionist"],
    "motivation": "Master the art of legendary weaponsmithing"
  },
  "inventory": [...],
  "equipment": {...}
}
```

#### `generate_npc_network(central_npc, network_size=5)`
Generate a network of NPCs related to a central NPC (family, friends, rivals, etc.)

### Location Generation

#### `generate_location(template_name=None, biome=None, generate_connections=False, populate_npcs=True)`
Generate a location (town, dungeon, wilderness area, etc.)

**Parameters:**
- `template_name` (str, optional): Location template (e.g., "tavern", "dungeon", "town")
- `biome` (str, optional): Environmental biome
- `generate_connections` (bool): Whether to generate connected locations
- `populate_npcs` (bool): Whether to add NPCs to the location

**Example Output:**
```json
{
  "id": "loc_001",
  "name": "The Rusty Dragon Inn",
  "type": "settlement",
  "subtype": "tavern",
  "description": "A cozy tavern with a crackling fireplace and the smell of roasted meat.",
  "biome": "temperate_forest",
  "npcs": [
    {"name": "Barnabas", "role": "Innkeeper", ...}
  ],
  "items": [...],
  "connections": {
    "north": "Town Square",
    "east": "Blacksmith Shop"
  },
  "features": ["fireplace", "bar", "guest_rooms"]
}
```

#### `generate_world(num_locations=5)`
Generate an entire world with multiple interconnected locations

**Example Output:**
```json
{
  "name": "The Kingdom of Eldoria",
  "locations": {
    "loc_001": {...},
    "loc_002": {...},
    "loc_003": {...}
  },
  "factions": [...],
  "history": "Ancient kingdom founded...",
  "map_connections": {...}
}
```

### Quest Generation

#### `generate_quest(quest_type=None, difficulty=1, location=None)`
Generate a quest with objectives and rewards

**Parameters:**
- `quest_type` (str, optional): "fetch", "kill", "escort", "explore", "craft", "deliver"
- `difficulty` (int): 1-10 difficulty scale
- `location` (dict, optional): Starting location

**Example Output:**
```json
{
  "title": "The Missing Heirloom",
  "type": "fetch",
  "difficulty": 3,
  "description": "Recover the stolen family heirloom from the bandits' hideout.",
  "objectives": [
    "Travel to Darkwood Forest",
    "Locate the bandit camp",
    "Retrieve the golden amulet"
  ],
  "rewards": {
    "gold": 500,
    "experience": 1200,
    "items": [...]
  },
  "quest_giver": {"name": "Lady Morgana", ...}
}
```

#### `generate_quest_advanced(quest_type=None, difficulty=1, create_chain=False)`
Generate advanced quest with multiple stages and branching paths

### Combat & Encounters

#### `generate_encounter(party_level=1, biome=None, encounter_type=None, difficulty_modifier=1.0)`
Generate a combat encounter, social encounter, puzzle, or trap

**Parameters:**
- `party_level` (int): Average party level
- `biome` (str, optional): Environmental setting
- `encounter_type` (str, optional): "combat", "social", "puzzle", "trap"
- `difficulty_modifier` (float): Multiplier for difficulty

**Example Output:**
```json
{
  "type": "combat",
  "difficulty": "medium",
  "enemies": [
    {"name": "Goblin Warrior", "count": 3, "level": 2, ...},
    {"name": "Goblin Shaman", "count": 1, "level": 3, ...}
  ],
  "environment": "cave",
  "tactics": "Shaman stays back while warriors engage",
  "loot": {...}
}
```

#### `generate_loot_table(enemy_type="standard", difficulty=1, quantity=None)`
Generate loot drops for enemies

**Parameters:**
- `enemy_type` (str): "minion", "standard", "elite", "boss"
- `difficulty` (int): Enemy difficulty level
- `quantity` (int, optional): Number of items

### Magic & Spells

#### `generate_spell(spell_level=None, school=None, spell_type=None)`
Generate a spell with effects and requirements

**Parameters:**
- `spell_level` (int, optional): 0-9 (cantrip to 9th level)
- `school` (str, optional): "evocation", "abjuration", "conjuration", etc.
- `spell_type` (str, optional): "damage", "healing", "buff", "debuff", "utility"

**Example Output:**
```json
{
  "name": "Fireball",
  "level": 3,
  "school": "evocation",
  "type": "damage",
  "casting_time": "1 action",
  "range": "150 feet",
  "components": ["V", "S", "M"],
  "duration": "Instantaneous",
  "description": "A bright streak flashes from your pointing finger...",
  "damage": "8d6 fire",
  "area": "20-foot radius sphere"
}
```

#### `generate_spellbook(caster_level=1, school_preference=None)`
Generate a complete spellbook for a caster

### World Features

#### `generate_animal(category=None, species=None, biome=None)`
Generate animals and creatures

**Parameters:**
- `category` (str, optional): "wild_fauna", "pet", "livestock", "predator"
- `species` (str, optional): Specific species name
- `biome` (str, optional): Natural habitat

#### `generate_flora(category=None, species=None, biome=None)`
Generate plants, trees, and vegetation

**Parameters:**
- `category` (str, optional): "trees", "plants", "mushrooms", "crops", "vines"
- `species` (str, optional): Specific species name
- `biome` (str, optional): Natural habitat

#### `generate_weather_and_time(biome=None)`
Generate weather conditions and time of day

**Example Output:**
```json
{
  "time": "dusk",
  "weather": "light rain",
  "temperature": "cool",
  "visibility": "moderate",
  "wind": "gentle breeze"
}
```

#### `generate_weather_detailed(biome=None, season=None, hour=None)`
Generate detailed weather with atmospheric effects

**Parameters:**
- `season` (str, optional): "spring", "summer", "autumn", "winter"

### Economy & Trading

#### `generate_market(location=None, wealth_level="modest")`
Generate a marketplace with merchants and goods

**Parameters:**
- `wealth_level` (str): "destitute", "poor", "modest", "comfortable", "wealthy", "aristocratic"

**Example Output:**
```json
{
  "name": "Central Marketplace",
  "wealth_level": "comfortable",
  "merchants": [
    {"name": "Greta the Clothier", "inventory": [...], "haggle_difficulty": 12}
  ],
  "special_goods": [...],
  "market_mood": "bustling"
}
```

#### `generate_crafting_recipe(output_item=None, difficulty=1, profession=None)`
Generate crafting recipes with ingredients and requirements

### Organizations

#### `generate_organization(org_type=None, faction=None, size="medium")`
Generate guilds, factions, and organizations

**Example Output:**
```json
{
  "name": "The Silver Hand",
  "type": "guild",
  "specialty": "adventurers",
  "size": "large",
  "headquarters": "Goldshire",
  "leader": {"name": "Master Aldric", ...},
  "members": 150,
  "reputation": "honored",
  "services": ["quest_board", "training", "item_storage"]
}
```

### Utility Methods

#### `generate_procedural_name(race="human", gender="male")`
Generate procedurally created names

**Parameters:**
- `race` (str): "human", "elf", "dwarf", "orc", etc.
- `gender` (str): "male", "female"

#### `generate_description(content, content_type="item", style="standard")`
Generate enhanced descriptions for any content

**Parameters:**
- `content` (dict): The content object to describe
- `content_type` (str): "item", "npc", "location", "quest"
- `style` (str): "standard", "verbose", "terse", "poetic"

#### `generate_trap_or_puzzle(difficulty=1, trap_type=None)`
Generate traps and puzzles for dungeons

**Parameters:**
- `trap_type` (str, optional): "mechanical", "magical", "puzzle", "environmental"

#### `generate_batch_with_distribution(content_type="item", count=10, distribution=None)`
Generate multiple items with rarity distribution

**Parameters:**
- `content_type` (str): "item", "npc", "location"
- `count` (int): Number to generate
- `distribution` (dict, optional): Rarity distribution weights

#### `generate_item_set_collection(set_name=None, set_size=5, theme=None)`
Generate a themed collection of items with set bonuses

### Seed Management

#### `reset_seed(seed=None)`
Reset the random seed for reproducible generation

## Usage Examples

### Example 1: Generate a Dungeon with Enemies and Loot
```python
# Create a dungeon location
dungeon = generator.generate_location(template_name="dungeon", populate_npcs=True)

# Generate encounters for each room
for i in range(5):
    encounter = generator.generate_encounter(
        party_level=5,
        encounter_type="combat",
        difficulty_modifier=1.2
    )
    print(f"Room {i+1}: {encounter['enemies']}")

# Generate boss loot
boss_loot = generator.generate_loot_table(enemy_type="boss", difficulty=10)
```

### Example 2: Create a Merchant with Inventory
```python
# Generate merchant NPC
merchant = generator.generate_npc(
    profession_names=["Merchant"],
    level=8
)

# Generate their shop inventory
market = generator.generate_market(wealth_level="wealthy")

# Add some legendary items to their special stock
legendary_item = generator.generate_item(
    constraints={"min_rarity": "Legendary"}
)
```

### Example 3: Build a Quest Chain
```python
# Generate main quest
main_quest = generator.generate_quest_advanced(
    quest_type="explore",
    difficulty=7,
    create_chain=True
)

# Generate related NPCs
quest_giver = main_quest["quest_giver"]
npc_network = generator.generate_npc_network(quest_giver, network_size=3)
```

### Example 4: Create a Living World
```python
# Generate world
world = generator.generate_world(num_locations=10)

# Add weather system
for location in world["locations"].values():
    location["weather"] = generator.generate_weather_detailed(
        biome=location.get("biome"),
        season="spring"
    )

# Populate with wildlife
for location in world["locations"].values():
    if location["type"] == "wilderness":
        location["fauna"] = [
            generator.generate_animal(biome=location.get("biome"))
            for _ in range(3)
        ]
        location["flora"] = [
            generator.generate_flora(biome=location.get("biome"))
            for _ in range(5)
        ]
```

## Tips for AI Usage

1. **Always initialize with a seed** for reproducible results during testing
2. **Use constraints** to ensure generated content fits your requirements
3. **Cache the generator instance** - initialization loads all data files
4. **Combine methods** - NPCs can have inventories, locations can have NPCs, quests can reference locations
5. **Check the test file** (`tests/test_all_generation.py`) for comprehensive examples of every method

## Return Value Structure

All generation methods return Python dictionaries or lists of dictionaries. The structure is JSON-serializable, making it easy to save, transmit, or integrate with game engines.

Common fields across all content types:
- `name`: Human-readable name
- `description`: Narrative description
- `type` / `subtype`: Categorization
- Various type-specific fields (stats, inventory, connections, etc.)
