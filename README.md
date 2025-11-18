# ContentGenerator

A Python-based dynamic game content generation engine that creates Items, NPCs, and Locations by reading and interpreting structured JSON configuration files.

## Features

### Core Capabilities

- **Modular JSON Configuration**: Separate, specialized configuration files for easy maintenance
- **Dynamic Content Generation**: Randomly generates game elements with unique properties
- **Cross-Referencing**: Support for references between different content types
- **Dynamic Descriptions**: Template-based description system with variable substitution
- **World Building**: Generate interconnected locations with NPCs and items

### Content Types

1. **Items** (Gear/Consumables)
   - Weapons (melee and ranged)
   - Armor and shields
   - Potions and scrolls
   - Jewelry and accessories
   - Random quality, rarity, stats, and value
   - Material-based properties

2. **NPCs** (Non-Player Characters)
   - Multiple archetypes (Blacksmith, Guard, Merchant, Mage, etc.)
   - Randomized names and personalities
   - Skill sets and stat distributions
   - Dynamic dialogue hooks
   - Inventory based on archetype
   - Location associations

3. **Locations** (Areas/Rooms)
   - Various environment types (outdoor, underground, buildings)
   - Environment tags (Dark, Wet, Dangerous, etc.)
   - Connected location networks
   - Spawnable NPCs and items
   - Dynamic descriptions

## Project Structure

```
R-Gen/
├── data/                    # JSON configuration files
│   ├── attributes.json      # Global properties (quality, rarity, etc.)
│   ├── items.json          # Item templates and definitions
│   ├── npcs.json           # NPC archetypes and properties
│   └── locations.json      # Location templates
├── src/
│   └── content_generator.py # Main ContentGenerator class
├── cli.py                  # Command-line interface
├── example.py              # Demo script showing all features
└── README.md              # This file
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd R-Gen
```

2. Ensure you have Python 3.7+ installed:
```bash
python --version
```

3. No external dependencies required - uses only Python standard library!

## Quick Start

### Run the Demo

```bash
python example.py
```

This will demonstrate all features and export sample generated content to JSON files.

### Command-Line Interface (CLI)

R-Gen includes a powerful CLI for quick content generation:

#### List Available Templates

```bash
python cli.py list-templates
```

This shows all available item templates, NPC archetypes, location templates, and item sets.

#### Generate Items

```bash
# Generate a random item (text format)
python cli.py generate-item

# Generate a specific item type
python cli.py generate-item --template weapon_melee

# Generate multiple items
python cli.py generate-item --count 10

# Output as JSON
python cli.py generate-item --format json

# Save to file
python cli.py generate-item --count 5 --format json --output items.json
```

#### Generate NPCs

```bash
# Generate a random NPC
python cli.py generate-npc

# Generate a specific NPC archetype
python cli.py generate-npc --archetype blacksmith

# Generate multiple NPCs
python cli.py generate-npc --archetype merchant --count 3

# Save to file
python cli.py generate-npc --archetype guard --output guards.json
```

#### Generate Locations

```bash
# Generate a random location
python cli.py generate-location

# Generate a specific location type
python cli.py generate-location --template tavern

# Generate location with connections
python cli.py generate-location --template forge --connections

# Save to file
python cli.py generate-location --template cave --format json --output dungeon.json
```

#### Generate Worlds

```bash
# Generate a small world
python cli.py generate-world --size 5

# Generate a large world and save it
python cli.py generate-world --size 20 --format json --output my_world.json
```

#### CLI Options

- `--template <name>`: Specify item/location template
- `--archetype <name>`: Specify NPC archetype
- `--count <n>`: Generate multiple items/NPCs
- `--format <type>`: Output format (`text`, `json`, `pretty`)
- `--output <file>`: Save output to file
- `--connections`: Generate connected locations (for locations)
- `--size <n>`: Number of locations (for worlds)
- `--data-dir <path>`: Custom data directory path

### Basic Usage (Python API)

```python
from src.content_generator import ContentGenerator

# Initialize the generator
generator = ContentGenerator(data_dir="data")

# Generate a random item
item = generator.generate_item()
print(f"Generated: {item['name']}")
print(f"Description: {item['description']}")

# Generate a specific type of item
sword = generator.generate_item("weapon_melee")
potion = generator.generate_item("potion")

# Generate an NPC
npc = generator.generate_npc("blacksmith")
print(f"NPC: {npc['name']} - {npc['title']}")
print(f"Dialogue: {npc['dialogue']}")

# Generate a location
location = generator.generate_location("tavern")
print(f"Location: {location['name']}")
print(f"NPCs present: {len(location['npcs'])}")
print(f"Items available: {len(location['items'])}")

# Generate a full world
world = generator.generate_world(num_locations=5)
print(f"World created with {len(world['locations'])} locations")
```

## API Reference

### ContentGenerator Class

#### `__init__(data_dir="data")`
Initialize the content generator.

**Parameters:**
- `data_dir` (str): Path to directory containing JSON configuration files

#### `generate_item(template_name=None)`
Generate a random item.

**Parameters:**
- `template_name` (str, optional): Specific item template to use (e.g., "weapon_melee", "potion")

**Returns:**
- dict: Item object with properties:
  - `name`: Full item name
  - `type`: Item type
  - `subtype`: Item subtype
  - `quality`: Quality level
  - `rarity`: Rarity level
  - `stats`: Dictionary of stat modifiers
  - `value`: Gold value
  - `description`: Dynamic description
  - `properties`: Additional properties

**Example:**
```python
# Random item
item = generator.generate_item()

# Specific item type
sword = generator.generate_item("weapon_melee")
armor = generator.generate_item("armor")
potion = generator.generate_item("potion")
```

#### `generate_items_from_set(set_name, count=None)`
Generate multiple items from a predefined item set.

**Parameters:**
- `set_name` (str): Name of the item set (e.g., "blacksmith_inventory")
- `count` (int, optional): Number of items to generate

**Returns:**
- list: List of generated item dictionaries

**Example:**
```python
items = generator.generate_items_from_set("merchant_inventory", count=5)
```

#### `generate_npc(archetype_name=None, location_id=None)`
Generate a random NPC.

**Parameters:**
- `archetype_name` (str, optional): Specific archetype to use (e.g., "blacksmith", "guard")
- `location_id` (str, optional): ID of the location where this NPC resides

**Returns:**
- dict: NPC object with properties:
  - `name`: Full NPC name
  - `title`: NPC title/role
  - `archetype`: Base archetype
  - `stats`: Dictionary of stat values
  - `skills`: List of skills
  - `dialogue`: Random dialogue hook
  - `description`: Dynamic description
  - `inventory`: List of items
  - `location`: Location ID reference

**Example:**
```python
# Random NPC
npc = generator.generate_npc()

# Specific archetype
blacksmith = generator.generate_npc("blacksmith")
merchant = generator.generate_npc("merchant")
```

#### `generate_location(template_name=None, generate_connections=True, max_connections=3)`
Generate a random location.

**Parameters:**
- `template_name` (str, optional): Specific template to use (e.g., "tavern", "forest_clearing")
- `generate_connections` (bool): Whether to generate connected locations
- `max_connections` (int): Maximum number of connections to generate

**Returns:**
- dict: Location object with properties:
  - `id`: Unique location identifier
  - `name`: Location name
  - `type`: Location type
  - `environment_tags`: List of environment descriptors
  - `description`: Dynamic description
  - `connections`: Map of connected location IDs
  - `npcs`: List of NPCs in this location
  - `items`: List of items in this location

**Example:**
```python
# Random location
location = generator.generate_location()

# Specific location type
tavern = generator.generate_location("tavern")
forge = generator.generate_location("forge")

# Location without connections
standalone = generator.generate_location("cave", generate_connections=False)
```

#### `generate_world(num_locations=5)`
Generate a connected world with multiple locations.

**Parameters:**
- `num_locations` (int): Number of main locations to generate

**Returns:**
- dict: World object with:
  - `locations`: Dictionary of location_id to location data
  - `world_map`: Summary of connections

**Example:**
```python
world = generator.generate_world(num_locations=10)

# Access all locations
for loc_id, location in world['locations'].items():
    print(f"{location['name']}: {len(location['npcs'])} NPCs, {len(location['items'])} items")

# View world map
for loc_id, summary in world['world_map'].items():
    print(f"{summary['name']}: {len(summary['connections'])} connections")
```

#### `export_to_json(data, filename)`
Export generated content to a JSON file.

**Parameters:**
- `data`: Data to export
- `filename` (str): Output filename

**Example:**
```python
items = [generator.generate_item() for _ in range(10)]
generator.export_to_json(items, "my_items.json")
```

## Configuration Files

### attributes.json

Defines global properties used across all content types:

- `quality`: Quality levels (Poor, Standard, Fine, Excellent, Masterwork, Legendary)
- `rarity`: Rarity tiers (Common, Uncommon, Rare, Epic, Legendary, Mythic)
- `materials`: Material types for items (iron, steel, mithril, etc.)
- `damage_types`: Types of damage (Slashing, Fire, Ice, etc.)
- `environment_tags`: Location descriptors (Dark, Wet, Ancient, etc.)
- `stats`: Available stats with min/max ranges
- `npc_traits`: Personality traits for NPCs
- `tactile_adjectives`: Touch-based descriptors
- `visual_adjectives`: Sight-based descriptors

### items.json

Defines item templates and item sets:

**Template Structure:**
```json
{
  "templates": {
    "weapon_melee": {
      "type": "weapon",
      "subtype": "melee",
      "base_names": ["Sword", "Axe", "Mace"],
      "has_material": true,
      "has_quality": true,
      "has_rarity": true,
      "stat_count": {"min": 1, "max": 3},
      "value_range": {"min": 50, "max": 500},
      "description_templates": [
        "A {quality} {rarity} {material} {base_name}..."
      ],
      "damage_type_count": {"min": 1, "max": 2}
    }
  },
  "item_sets": {
    "blacksmith_inventory": ["weapon_melee", "armor"]
  }
}
```

### npcs.json

Defines NPC archetypes:

**Archetype Structure:**
```json
{
  "archetypes": {
    "blacksmith": {
      "title": "Blacksmith",
      "first_names": ["Thorin", "Bronn"],
      "last_names": ["Ironhammer", "Steelforge"],
      "skills": ["Smithing", "Metalworking"],
      "base_stats": {
        "Strength": 8,
        "Dexterity": 5
      },
      "dialogue_hooks": [
        "Need something repaired?"
      ],
      "description_templates": [
        "A {trait} {title} with..."
      ],
      "inventory_set": "blacksmith_inventory",
      "typical_locations": ["forge", "market"]
    }
  }
}
```

### locations.json

Defines location templates:

**Template Structure:**
```json
{
  "templates": {
    "tavern": {
      "name": "Tavern",
      "type": "building",
      "base_environment_tags": ["Bright", "Peaceful"],
      "additional_tags_count": {"min": 0, "max": 2},
      "description_templates": [
        "A {visual_adjective} tavern..."
      ],
      "can_connect_to": ["city_square", "market"],
      "spawnable_npcs": ["innkeeper", "merchant"],
      "spawnable_items": ["potion"],
      "item_spawn_count": {"min": 0, "max": 3},
      "npc_spawn_count": {"min": 1, "max": 3}
    }
  }
}
```

## Dynamic Description System

The engine uses a template-based system for generating unique descriptions:

### Template Syntax

Use `{placeholder}` syntax in description templates:

```json
"description_templates": [
  "A {quality} {rarity} {material} {base_name}, which feels {tactile_adjective} to the touch."
]
```

### Available Placeholders

- `{quality}`: Quality level (poor, standard, excellent, etc.)
- `{rarity}`: Rarity tier (common, rare, legendary, etc.)
- `{material}`: Material type (iron, steel, mithril, etc.)
- `{base_name}`: Base item/location name
- `{tactile_adjective}`: Touch-based descriptor (rough, smooth, cold, etc.)
- `{visual_adjective}`: Sight-based descriptor (weathered, pristine, ornate, etc.)
- `{trait}`: NPC personality trait (gruff, friendly, mysterious, etc.)
- `{title}`: NPC title/role
- `{environment_tag_1}`, `{environment_tag_2}`, etc.: Environment descriptors

### Cross-Referencing

The system supports cross-referencing between different content types:

1. **NPCs reference Item Sets**: NPCs have inventories based on item sets defined in items.json
2. **Locations reference NPCs**: Locations specify which NPC archetypes can spawn
3. **Locations reference Items**: Locations specify which item types can spawn
4. **Locations reference Locations**: Locations can connect to other location types

**Example:**
```python
# Generate a blacksmith NPC (automatically gets blacksmith_inventory items)
blacksmith = generator.generate_npc("blacksmith")
# blacksmith['inventory'] contains weapons and armor

# Generate a forge location (automatically spawns blacksmith NPCs)
forge = generator.generate_location("forge")
# forge['npcs'] contains blacksmith NPCs with their inventories
```

## Customization

### Adding New Content

#### Add a New Item Type

1. Edit `data/items.json`
2. Add a new template under `templates`:
```json
"my_new_item": {
  "type": "special",
  "subtype": "custom",
  "base_names": ["Widget", "Gadget"],
  "has_material": true,
  "has_quality": true,
  "has_rarity": true,
  "stat_count": {"min": 1, "max": 2},
  "value_range": {"min": 100, "max": 1000},
  "description_templates": [
    "A {quality} {material} {base_name}..."
  ]
}
```

#### Add a New NPC Archetype

1. Edit `data/npcs.json`
2. Add a new archetype under `archetypes`:
```json
"wizard": {
  "title": "Wizard",
  "first_names": ["Gandalf", "Merlin"],
  "last_names": ["the Grey", "the Wise"],
  "skills": ["Magic", "Lore"],
  "base_stats": {...},
  "dialogue_hooks": ["I have magic to sell..."],
  "description_templates": ["A {trait} {title}..."],
  "inventory_set": "mage_inventory"
}
```

#### Add a New Location Type

1. Edit `data/locations.json`
2. Add a new template under `templates`:
```json
"castle": {
  "name": "Castle",
  "type": "building",
  "base_environment_tags": ["Pristine", "Ancient"],
  "additional_tags_count": {"min": 1, "max": 2},
  "description_templates": ["A {visual_adjective} castle..."],
  "can_connect_to": ["city_square", "gate"],
  "spawnable_npcs": ["guard", "merchant"],
  "spawnable_items": ["weapon_melee", "armor"],
  "item_spawn_count": {"min": 5, "max": 15},
  "npc_spawn_count": {"min": 3, "max": 8}
}
```

### Modifying Attributes

Edit `data/attributes.json` to add new:
- Quality levels
- Rarity tiers
- Materials
- Damage types
- Environment tags
- Stats
- Descriptive adjectives

## Advanced Features

### Value Calculation

Item values are calculated based on:
- Base value range from template
- Quality multiplier (Poor: 0.5x to Legendary: 5.0x)
- Rarity multiplier (Common: 1.0x to Mythic: 10.0x)

### Stat Generation

- Stats are randomly selected from available stats in attributes.json
- Number of stats based on template's `stat_count`
- Stat values range from template-defined min/max
- Only non-zero stats are included

### NPC Stat Variation

- NPCs start with archetype's `base_stats`
- Random variation of ±1 applied to each stat
- Stats are clamped to minimum of 1

### Location Connections

- Locations can connect to types defined in `can_connect_to`
- 50% chance to reuse existing location vs. generating new one
- Prevents infinite recursion by limiting connection depth

## Examples

See `example.py` for comprehensive examples including:

1. Generating individual items of various types
2. Creating NPCs with full inventories
3. Building locations with spawned content
4. Generating interconnected worlds
5. Demonstrating cross-referencing
6. Exporting content to JSON

## License

MIT License - feel free to use and modify for your projects!

## Contributing

Contributions are welcome! Areas for improvement:
- Additional item types and templates
- More NPC archetypes
- New location types
- Enhanced description templates
- Procedural quest generation
- Loot table systems
- Difficulty scaling

## Support

For issues, questions, or suggestions, please open an issue on the repository.
