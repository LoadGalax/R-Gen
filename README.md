# R-Gen: Random Game Content Generator

A powerful Python-based dynamic game content generation engine that creates Items, NPCs, Locations, Worlds, Spells, Organizations, Quests, and much more with advanced features including weighted probabilities, constraints, database integration, and a web interface.

## 🚀 Latest Major Updates

### NEW: Magic & Spell System
- ✨ **Spell Generation**: 9 spell levels (0-9) across 8 magic schools
- 📚 **Spellbooks**: Automatically generated spell collections
- 🎯 **Spell Components**: Verbal, somatic, material, and focus requirements
- 🔮 **Spell Effects**: Damage, healing, buffs, debuffs, summons, and utility spells
- 🌟 **Spell Rarity**: Common to Mythic spells with appropriate value scaling

### NEW: Organizations & Guilds
- 🏛️ **10+ Organization Types**: Guilds, thieves guilds, mages circles, religious orders, mercenary companies, etc.
- 👑 **Leadership Hierarchies**: Dynamic leadership structures with ranked NPCs
- 💰 **Economic Resources**: Wealth tracking, benefits, and membership requirements
- 🤝 **Relationships**: Allied, neutral, rival, and enemy relationships between organizations
- 🎭 **Activities**: Each organization has specific activities and purposes

### NEW: Advanced Quest System
- 📜 **10 Quest Types**: Fetch, Kill, Escort, Rescue, Investigate, Diplomacy, Craft, Exploration, Defense, Heist
- 🔗 **Quest Chains**: Automatically generated multi-quest storylines
- 🎲 **Complications**: Random complications and moral dilemmas
- 🎁 **Reward System**: Gold, items, reputation, and experience scaling with difficulty
- 🎯 **Secondary Objectives**: Optional objectives for bonus rewards

### NEW: Economic System
- 💹 **Dynamic Pricing**: Supply & demand, location-based pricing modifiers
- 🏪 **Market Generation**: Complete markets with merchants, goods, and services
- 💰 **Wealth Levels**: 7 economic tiers from destitute to royal
- 📊 **Trade Goods**: Extensive catalog of food, materials, and magical components
- ⚖️ **Services**: Lodging, meals, transport, professional services, and more

### NEW: Enhanced Weather & Environment
- 🌦️ **Detailed Weather System**: 11 weather patterns with gameplay effects
- 🗓️ **Seasonal System**: Four seasons with temperature and weather variations
- 🌙 **Moon Phases**: 8 moon phases affecting visibility and magic
- ⛈️ **Natural Disasters**: Earthquakes, floods, tornadoes, volcanic eruptions, and more
- ⏰ **Time of Day**: 6 time periods with visibility and mood effects

### NEW: Relationship System
- 🤝 **NPC Relationships**: Friends, rivals, enemies, family, romantic partners, mentors
- 🕸️ **Social Networks**: Generate interconnected groups of NPCs
- 💖 **Reputation Tracking**: Quantified relationship values
- 👨‍👩‍👧‍👦 **Family Trees**: Support for familial relationships

### NEW: Enhanced Description System
- 📖 **10 Description Styles**: Technical, Poetic, Brief, Detailed, Historical, Dramatic, Mysterious, Humorous, Ominous, Scholarly, Noir
- 🎨 **Context-Aware**: Descriptions adapt to location, weather, time, and mood
- 🌍 **Location-Based Modifiers**: Volcanic, arctic, forest, underground, desert, coastal, urban, ruins
- 🎭 **Mood-Based**: Peaceful, tense, hostile, melancholic atmospheres

### NEW: Export Formats
- 📝 **Markdown Export**: Beautiful formatted documents
- 📊 **Enhanced CSV Export**: Spreadsheet-compatible data
- 📄 **Existing Formats**: JSON, XML, SQL still supported

### NEW: Validation & Error Handling
- ✅ **Constraint Validation**: Validate generation parameters before use
- 🛡️ **Type Checking**: Better error messages and input validation
- 🔍 **Thematic Consistency**: Check if items fit their biome/environment

## ✨ Core Features

### Advanced Features
- 🎯 **Seed-based Generation**: Reproducible content generation with random seeds
- ⚖️ **Weighted Probabilities**: Realistic rarity distribution (legendary items are actually rare!)
- 🎛️ **Generation Constraints**: Filter by quality, rarity, value, materials, and more
- 💾 **Database Integration**: SQLite and PostgreSQL support with full history tracking
- 🌐 **Web Interface**: Beautiful Flask-powered web UI for easy content generation
- 🔧 **Config-Driven Multipliers**: All value calculations now configurable via JSON
- 🔄 **Bidirectional Connections**: Fixed location connections (now work both ways!)

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

## Key Features & Highlights

### 🎲 Smart Randomization
- **Intelligent Value Calculation**: Item values automatically scale based on quality (Poor to Legendary: 0.5x to 5.0x) and rarity (Common to Mythic: 1.0x to 10.0x)
- **Stat Variation**: NPCs get randomized stat variations (±1) from their archetype base stats
- **Dynamic Properties**: Every item, NPC, and location is unique with randomized properties

### 🔗 Cross-Referencing System
- **Smart Inventories**: NPCs automatically receive appropriate items based on their archetype (e.g., blacksmiths get weapons and armor)
- **Location-aware NPCs**: NPCs know which location they're in and spawn in appropriate places
- **Connected Worlds**: Locations intelligently connect to compatible location types with 50% reuse of existing locations
- **Item Sets**: Predefined item sets ensure thematic consistency (blacksmith_inventory, merchant_inventory, etc.)

### 📝 Dynamic Description Engine
- **Template-based System**: Use `{placeholder}` syntax for infinite description variations
- **Context-aware**: Descriptions automatically include quality, rarity, materials, and environmental details
- **Adjective Libraries**: Built-in tactile and visual adjective banks for rich descriptions

### ⚡ Multiple Interfaces
- **Python API**: Full programmatic control for integration into games or tools
- **CLI Tool**: Quick command-line generation with text, JSON, or pretty-print output
- **Batch Export**: Generate hundreds of items and export to JSON for game databases

### 🎯 Zero Dependencies
- Pure Python 3.7+ standard library
- No external packages required
- Easy deployment and integration

## Project Structure

```
R-Gen/
├── data/                    # JSON configuration files
│   ├── attributes.json      # Global properties (quality, rarity, weighted probabilities)
│   ├── items.json          # Item templates and definitions
│   ├── npcs.json           # NPC archetypes and properties
│   └── locations.json      # Location templates
├── src/
│   ├── content_generator.py # Main ContentGenerator class
│   └── database.py          # Database integration layer
├── templates/
│   └── index.html          # Web interface template
├── cli.py                  # Command-line interface
├── web_app.py              # Flask web application
├── example.py              # Demo script showing all features
├── requirements.txt        # Optional dependencies
└── README.md              # This file
```

## Installation

### Basic Installation (Core Features Only)

1. Clone the repository:
```bash
git clone <repository-url>
cd R-Gen
```

2. Ensure you have Python 3.7+ installed:
```bash
python --version
```

3. No external dependencies required for core features - uses only Python standard library!

### Full Installation (With Web Interface & Database)

For web interface and database features, install optional dependencies:

```bash
pip install -r requirements.txt
```

Optional dependencies:
- `flask` and `flask-cors` - For web interface
- `psycopg2-binary` - For PostgreSQL support (SQLite works out of the box)

## Quick Start

### Option 1: Web Interface (Recommended)

Launch the web interface for the easiest experience:

```bash
python web_app.py
```

Then open your browser to `http://localhost:5000`

Features:
- Interactive content generation
- Real-time preview
- Constraint configuration
- Database integration
- History tracking
- Bulk generation

### Option 2: Command Line

Generate content quickly from the terminal:

```bash
# === Basic Content Generation ===

# Generate a weapon with seed for reproducibility
python cli.py generate-item --template weapon_melee --seed 42

# Generate 10 high-quality items
python cli.py generate-item --count 10

# Generate an NPC merchant
python cli.py generate-npc --archetype merchant

# Generate a complete world
python cli.py generate-world --size 10

# === NEW: Spell Generation ===

# Generate a random spell
python cli.py generate-spell

# Generate a level 5 Evocation spell
python cli.py generate-spell --spell-level 5 --school Evocation

# Generate a healing spell
python cli.py generate-spell --spell-template healing

# Generate a complete spellbook for a level 10 caster
python cli.py generate-spellbook --caster-level 10 --school-preference Necromancy

# === NEW: Organization Generation ===

# Generate a random organization
python cli.py generate-organization

# Generate a large thieves guild
python cli.py generate-organization --org-type thieves_guild --size large

# Generate a mages circle aligned with a faction
python cli.py generate-organization --org-type mages_circle --faction arcane_council

# === NEW: Advanced Quest System ===

# Generate a random quest
python cli.py generate-quest-advanced

# Generate a difficult rescue quest
python cli.py generate-quest-advanced --quest-type rescue --difficulty 7

# Generate a quest chain
python cli.py generate-quest-advanced --quest-type investigation --create-chain

# === NEW: Economic System ===

# Generate a market in a wealthy area
python cli.py generate-market --wealth-level wealthy

# Generate a market in a poor settlement
python cli.py generate-market --wealth-level poor

# === NEW: Enhanced Weather ===

# Generate detailed weather
python cli.py generate-weather-detailed

# Generate winter weather at night
python cli.py generate-weather-detailed --season winter --time-of-day night

# Generate desert weather in summer
python cli.py generate-weather-detailed --biome desert --season summer

# === NEW: NPC Social Networks ===

# Generate an NPC with 5 connected relationships
python cli.py generate-npc-network --network-size 5

# Generate a network for a specific faction
python cli.py generate-npc-network --network-size 10 --faction merchants_guild

# === Export to Different Formats ===

# Export to Markdown
python cli.py generate-item --count 5 --output items.json
python cli.py export --input items.json --output items.md --export-format markdown --title "Epic Items"

# Export to CSV
python cli.py export --input items.json --output items.csv --export-format csv
```

### Option 3: Python API

Use R-Gen in your own Python code:

```python
from src.content_generator import ContentGenerator

# Initialize with seed for reproducible generation
generator = ContentGenerator(seed=42)

# === Basic Content Generation ===

# Generate item with constraints
item = generator.generate_item(
    template="weapon_melee",
    constraints={
        "min_quality": "Excellent",
        "min_rarity": "Rare",
        "min_value": 500,
        "required_stats": ["Strength"]
    }
)
print(f"Generated: {item['name']} - {item['value']} gold")

# === NEW: Generate Spells ===

# Generate a random spell
spell = generator.generate_spell()
print(f"Spell: {spell['name']} (Level {spell['level']} {spell['school']})")

# Generate a specific type of spell
fireball = generator.generate_spell(
    spell_level=3,
    school="Evocation",
    spell_template="damage_area"
)

# Generate a spellbook
spellbook = generator.generate_spellbook(
    caster_level=10,
    school_preference="Necromancy"
)
print(f"Spellbook with {len(spellbook['spells'])} spells")

# === NEW: Generate Organizations ===

# Create a thieves guild
guild = generator.generate_organization(
    org_type="thieves_guild",
    faction="shadow_syndicate",
    size="large"
)
print(f"Organization: {guild['name']} with {guild['member_count']} members")

# === NEW: Generate Advanced Quests ===

# Generate a quest with chain
quest = generator.generate_quest_advanced(
    quest_type="rescue",
    difficulty=5,
    faction="kingdom_of_valor",
    create_chain=True
)
print(f"Quest: {quest['name']} - Reward: {quest['rewards']['gold']} gold")

# === NEW: Generate Markets ===

# Create a wealthy market
market = generator.generate_market(
    wealth_level="wealthy"
)
print(f"Market with {len(market['merchants'])} merchants and {len(market['available_goods'])} goods")

# Calculate dynamic pricing
pricing = generator.calculate_item_price(
    item=item,
    supply="scarce",
    demand="high"
)
print(f"Price: {pricing['final_price']} gold (normally {pricing['base_value']})")

# === NEW: Generate Detailed Weather ===

# Generate weather with all details
weather = generator.generate_weather_detailed(
    season="winter",
    time_of_day="night",
    biome="mountains"
)
print(f"Weather: {weather['description']}")

# === NEW: NPC Relationships ===

# Create an NPC with a social network
central_npc = generator.generate_npc()
network = generator.generate_npc_network(
    central_npc=central_npc,
    network_size=5
)
print(f"Network of {len(network)} NPCs with relationships")

# Add custom relationships
npc1 = generator.generate_npc()
npc2 = generator.generate_npc()
generator.add_relationship(npc1, npc2, relationship_type="rival")

# === NEW: Enhanced Descriptions ===

# Generate descriptions in different styles
poetic_desc = generator.generate_description(
    content=item,
    content_type="item",
    style="poetic"
)

technical_desc = generator.generate_description(
    content=item,
    content_type="item",
    style="technical"
)

# Context-aware descriptions
context = {
    "location": "volcanic",
    "weather": "storm",
    "mood": "hostile"
}
dramatic_desc = generator.generate_description(
    content=item,
    content_type="item",
    style="dramatic",
    context=context
)

# === NEW: Export to Different Formats ===

# Export to Markdown
data = [item, spell, quest]
generator.export_to_markdown(data, "content.md", title="Epic Game Content")

# Export to JSON
generator.export_to_json(data, "content.json")
```

### Run the Demo

```bash
python example.py
```

This will demonstrate all features and export sample generated content to JSON files.

### Quick Examples

Generate content in seconds with simple commands:

```bash
# Generate a random sword
python cli.py generate-item --template weapon_melee

# Create a merchant NPC with inventory
python cli.py generate-npc --archetype merchant

# Build a tavern with NPCs and items
python cli.py generate-location --template tavern

# Generate a complete world with 10 locations
python cli.py generate-world --size 10
```

**Example Output:**
```
📦 Excellent Steel Sword
   Type: weapon (melee)
   Quality: Excellent | Rarity: Rare
   Material: steel
   Value: 750 gold
   Stats: Strength+3, Dexterity+2
   Damage Types: Slashing, Fire
   Description: An excellent rare steel sword, which feels cold to the touch.
```

## Common Use Cases

R-Gen is perfect for:

- **🎮 Game Development**: Generate loot tables, NPC shops, quest rewards, and dungeon layouts
- **📚 Tabletop RPGs**: Create random encounters, treasure hoards, and town NPCs on-the-fly
- **✍️ World Building**: Populate your fantasy world with detailed locations and inhabitants
- **🧪 Procedural Generation**: Build roguelikes, random dungeons, or exploration-based games
- **📊 Game Databases**: Batch-generate hundreds of items and NPCs for your game's content database
- **🎲 D&D Sessions**: Quickly generate merchants, blacksmiths, and locations when players go off-script

## What You Can Build

With R-Gen, you can create:

- **Loot Systems**: Random treasure drops, chest contents, enemy loot tables
- **Shop Systems**: Dynamic merchant inventories that change each visit
- **Quest Generators**: Randomized quest objectives with appropriate rewards
- **Dungeon Crawlers**: Procedurally generated dungeons with unique rooms and encounters
- **Town Populators**: Fill your towns with unique NPCs, each with their own inventory and dialogue
- **World Explorers**: Generate vast interconnected worlds for exploration games
- **Character Creators**: Generate starting equipment and NPCs for character backstories
- **Encounter Tables**: Random encounter generators for tabletop RPG sessions

## Getting Started Tutorial

### Your First Item (CLI)

```bash
# 1. List available item templates
python cli.py list-templates

# 2. Generate a weapon
python cli.py generate-item --template weapon_melee

# 3. Generate 5 potions and save to file
python cli.py generate-item --template potion --count 5 --output my_potions.json
```

### Your First Item (Python)

```python
# 1. Import the generator
from src.content_generator import ContentGenerator

# 2. Create an instance
generator = ContentGenerator()

# 3. Generate your first item
sword = generator.generate_item("weapon_melee")

# 4. Display the results
print(f"You found: {sword['name']}")
print(f"Value: {sword['value']} gold")
print(f"Stats: {sword['stats']}")
print(f"Description: {sword['description']}")
```

### Your First NPC with Inventory

```python
from src.content_generator import ContentGenerator

generator = ContentGenerator()

# Generate a merchant with inventory
merchant = generator.generate_npc("merchant")

print(f"Meet {merchant['name']}, the {merchant['title']}")
print(f'"{merchant["dialogue"]}"')
print(f"\nInventory ({len(merchant['inventory'])} items):")

# Show the merchant's wares
for item in merchant['inventory']:
    print(f"  - {item['name']}: {item['value']} gold")
```

### Your First World

```python
from src.content_generator import ContentGenerator

generator = ContentGenerator()

# Generate a small world
world = generator.generate_world(num_locations=5)

print(f"World created with {len(world['locations'])} locations")

# Explore the world
for loc_id, location in world['locations'].items():
    print(f"\n{location['name']}:")
    print(f"  NPCs: {len(location['npcs'])}")
    print(f"  Items: {len(location['items'])}")
    print(f"  Connections: {len(location['connections'])}")

# Export for later use
generator.export_to_json(world, "my_world.json")
```

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

#### CLI Examples with Different Formats

**Text Format (Default - Human Readable):**
```bash
python cli.py generate-npc --archetype blacksmith
```
Output:
```
👤 Thorin Ironhammer
   Title: Blacksmith
   Archetype: blacksmith
   Stats: Strength: 9, Dexterity: 5, Constitution: 7
   Skills: Smithing, Metalworking, Repair
   Description: A gruff blacksmith with calloused hands and a determined expression.
   Dialogue: "Need something repaired? Or perhaps a new blade?"
   Inventory (4 items):
      📦 Fine Steel Sword (450 gold)
      📦 Standard Iron Axe (120 gold)
```

**JSON Format (For Game Integration):**
```bash
python cli.py generate-item --template weapon_melee --format json
```
Output:
```json
{
  "name": "Masterwork Mithril Sword",
  "type": "weapon",
  "subtype": "melee",
  "quality": "Masterwork",
  "rarity": "Epic",
  "stats": {
    "Strength": 5,
    "Dexterity": 3,
    "Attack": 8
  },
  "value": 4800,
  "description": "A masterwork epic mithril sword, which feels smooth to the touch.",
  "material": "mithril",
  "damage_types": ["Slashing", "Lightning"]
}
```

**Save to File:**
```bash
# Generate 20 weapons and save to file
python cli.py generate-item --template weapon_melee --count 20 --format json --output weapons.json

# Generate a complete world and save
python cli.py generate-world --size 15 --format json --output my_world.json

# Generate merchant inventory
python cli.py generate-npc --archetype merchant --count 5 --output merchants.json
```

**Advanced Combinations:**
```bash
# Generate multiple random items
python cli.py generate-item --count 10

# Generate a connected dungeon area
python cli.py generate-location --template cave --connections

# List all available templates
python cli.py list-templates
```

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

## Practical Examples

### Use Case 1: Quest Reward Generator

Generate random loot for quest rewards:

```python
from src.content_generator import ContentGenerator

generator = ContentGenerator()

# Generate quest rewards based on difficulty
def generate_quest_rewards(difficulty="normal"):
    if difficulty == "easy":
        items = [generator.generate_item("potion") for _ in range(2)]
        gold = 50
    elif difficulty == "normal":
        items = [
            generator.generate_item("weapon_melee"),
            generator.generate_item("potion")
        ]
        gold = 150
    else:  # hard
        items = [
            generator.generate_item("weapon_melee"),
            generator.generate_item("armor"),
            generator.generate_item("jewelry")
        ]
        gold = 500

    return {"items": items, "gold": gold}

rewards = generate_quest_rewards("hard")
print(f"Quest Complete! You earned {rewards['gold']} gold and {len(rewards['items'])} items!")
```

### Use Case 2: Shop Inventory System

Create dynamic shop inventories based on merchant type:

```python
from src.content_generator import ContentGenerator

generator = ContentGenerator()

# Generate a blacksmith's shop
blacksmith = generator.generate_npc("blacksmith")
print(f"\n{blacksmith['name']}'s Forge")
print(f'"{blacksmith["dialogue"]}"')
print("\nItems for sale:")

for item in blacksmith['inventory']:
    print(f"  {item['name']}: {item['value']} gold")
    if item['stats']:
        stats_str = ', '.join([f"{k}+{v}" for k, v in item['stats'].items()])
        print(f"    Stats: {stats_str}")
```

**Example Output:**
```
Thorin Ironhammer's Forge
"Need something repaired? Or perhaps a new blade?"

Items for sale:
  Masterwork Steel Sword: 1200 gold
    Stats: Strength+4, Dexterity+2
  Fine Iron Axe: 450 gold
    Stats: Strength+3
  Excellent Steel Armor: 2500 gold
    Stats: Constitution+5, Defense+8
```

### Use Case 3: Dungeon Generator

Create a multi-room dungeon with enemies and loot:

```python
from src.content_generator import ContentGenerator

generator = ContentGenerator()

def generate_dungeon(num_rooms=5):
    """Generate a dungeon with connected rooms"""
    world = generator.generate_world(num_locations=num_rooms)

    print(f"🏰 Dungeon Generated: {len(world['locations'])} rooms")
    print("\nDungeon Map:")

    for loc_id, location in world['locations'].items():
        print(f"\n📍 {location['name']}")
        print(f"   Environment: {', '.join(location['environment_tags'])}")
        print(f"   Enemies: {len(location['npcs'])}")
        print(f"   Loot items: {len(location['items'])}")
        print(f"   Exits: {len(location['connections'])}")

        # Show total loot value
        total_value = sum(item['value'] for item in location['items'])
        print(f"   Total loot value: {total_value} gold")

dungeon = generate_dungeon(5)
```

### Use Case 4: Random Encounter Generator

Generate random encounters for exploration:

```python
from src.content_generator import ContentGenerator
import random

generator = ContentGenerator()

def random_encounter():
    """Generate a random encounter"""
    encounter_type = random.choice(["combat", "merchant", "treasure"])

    if encounter_type == "combat":
        enemy = generator.generate_npc("guard")  # or any combat archetype
        print(f"\n⚔️  Combat Encounter!")
        print(f"   {enemy['name']} blocks your path!")
        print(f'   "{enemy["dialogue"]}"')
        print(f"   Stats: {enemy['stats']}")

    elif encounter_type == "merchant":
        merchant = generator.generate_npc("merchant")
        print(f"\n💰 You encounter a traveling merchant!")
        print(f"   {merchant['name']}: \"{merchant['dialogue']}\"")
        print(f"   Items available: {len(merchant['inventory'])}")

    else:  # treasure
        treasure_count = random.randint(1, 3)
        treasures = [generator.generate_item() for _ in range(treasure_count)]
        print(f"\n💎 You found a treasure chest!")
        print(f"   Contents ({treasure_count} items):")
        for item in treasures:
            print(f"   - {item['name']} ({item['value']} gold)")

# Generate 3 random encounters
for i in range(3):
    random_encounter()
```

### Use Case 5: Character Starting Equipment

Generate starting equipment based on character class:

```python
from src.content_generator import ContentGenerator

generator = ContentGenerator()

def generate_starting_gear(character_class):
    """Generate appropriate starting gear for a character class"""

    gear_templates = {
        "warrior": ["weapon_melee", "armor", "shield"],
        "mage": ["weapon_ranged", "scroll", "potion"],
        "rogue": ["weapon_melee", "jewelry", "potion"],
        "cleric": ["weapon_melee", "armor", "potion"]
    }

    templates = gear_templates.get(character_class, ["weapon_melee", "armor"])
    starting_gear = [generator.generate_item(template) for template in templates]

    print(f"\n🎒 Starting Equipment for {character_class.title()}:")
    for item in starting_gear:
        print(f"   {item['name']}")
        if item['stats']:
            stats_str = ', '.join([f"{k}+{v}" for k, v in item['stats'].items()])
            print(f"      Stats: {stats_str}")
        print(f"      Value: {item['value']} gold")

    return starting_gear

# Generate starting gear for a warrior
warrior_gear = generate_starting_gear("warrior")
```

### Use Case 6: Batch Content Generation for Game Database

Generate large amounts of content and export to JSON:

```python
from src.content_generator import ContentGenerator

generator = ContentGenerator()

# Generate a complete game database
print("Generating game content database...")

# Generate 100 weapons
weapons = [generator.generate_item("weapon_melee") for _ in range(50)]
weapons += [generator.generate_item("weapon_ranged") for _ in range(50)]

# Generate 50 armor pieces
armors = [generator.generate_item("armor") for _ in range(50)]

# Generate 30 NPCs of each archetype
npcs = []
archetypes = ["blacksmith", "merchant", "guard", "mage", "innkeeper"]
for archetype in archetypes:
    npcs += [generator.generate_npc(archetype) for _ in range(30)]

# Generate 20 complete locations
locations = [generator.generate_location(generate_connections=False) for _ in range(20)]

# Export everything
generator.export_to_json(weapons, "game_database_weapons.json")
generator.export_to_json(armors, "game_database_armors.json")
generator.export_to_json(npcs, "game_database_npcs.json")
generator.export_to_json(locations, "game_database_locations.json")

print(f"✅ Generated:")
print(f"   {len(weapons)} weapons")
print(f"   {len(armors)} armor pieces")
print(f"   {len(npcs)} NPCs")
print(f"   {len(locations)} locations")
```

### Use Case 7: Dynamic World Events

Generate dynamic world events with context:

```python
from src.content_generator import ContentGenerator
import random

generator = ContentGenerator()

def generate_world_event():
    """Generate a random world event"""
    event_types = [
        "market_day",
        "monster_attack",
        "traveling_caravan",
        "festival"
    ]

    event = random.choice(event_types)

    if event == "market_day":
        market = generator.generate_location("market", generate_connections=False)
        print(f"\n🎪 Market Day at {market['name']}!")
        print(f"   Merchants present: {len(market['npcs'])}")
        print(f"   Special items available: {len(market['items'])}")

        # Show some special items
        rare_items = [item for item in market['items']
                     if item.get('rarity') in ['Rare', 'Epic', 'Legendary']]
        if rare_items:
            print("\n   ✨ Rare items today:")
            for item in rare_items[:3]:
                print(f"      {item['name']} - {item['value']} gold")

    elif event == "traveling_caravan":
        merchants = [generator.generate_npc("merchant") for _ in range(3)]
        print(f"\n🐫 A traveling caravan arrives!")
        print(f"   {len(merchants)} merchants with exotic goods")

        total_items = sum(len(m['inventory']) for m in merchants)
        print(f"   Total items for sale: {total_items}")

generate_world_event()
```

## Advanced Features

### Seed-Based Generation

Generate reproducible content using seeds:

```python
from src.content_generator import ContentGenerator

# Create generator with fixed seed
generator = ContentGenerator(seed=12345)

# Generate items - will always be the same with this seed
item1 = generator.generate_item("weapon_melee")
item2 = generator.generate_item("armor")

# Reset to regenerate the same sequence
generator.reset_seed(12345)
item3 = generator.generate_item("weapon_melee")
# item1 and item3 are identical!
```

### Generation Constraints

Filter generated content to meet specific requirements:

```python
# Generate only high-quality legendary weapons
legendary_weapon = generator.generate_item(
    template="weapon_melee",
    constraints={
        "min_quality": "Masterwork",
        "min_rarity": "Legendary",
        "min_value": 1000,
        "required_stats": ["Strength", "Dexterity"]
    }
)

# Generate items excluding certain materials
no_wood_items = generator.generate_item(
    template="weapon_melee",
    constraints={
        "exclude_materials": ["wood", "bone"]
    }
)
```

### Database Integration

Store and retrieve generated content with full history tracking:

```python
from src.database import DatabaseManager
from src.content_generator import ContentGenerator

# Initialize database (SQLite)
db = DatabaseManager("my_game.db")

# Or use PostgreSQL
# db = DatabaseManager("postgresql://user:password@localhost/dbname", db_type="postgresql")

generator = ContentGenerator(seed=42)

# Generate and save
item = generator.generate_item("weapon_melee")
item_id = db.save_item(item, template="weapon_melee", seed=42)

# Retrieve later
retrieved_item = db.get_item(item_id)

# Search items
legendary_items = db.search_items(filters={
    "rarity": "Legendary",
    "min_value": 1000
}, limit=50)

# View generation history
history = db.get_history(content_type="item", limit=100)
```

### Weighted Probabilities

R-Gen now uses realistic probability distributions. In `data/attributes.json`:

```json
{
  "quality": {
    "Poor": {"weight": 0.25, "multiplier": 0.5},
    "Standard": {"weight": 0.35, "multiplier": 1.0},
    "Fine": {"weight": 0.20, "multiplier": 1.5},
    "Excellent": {"weight": 0.12, "multiplier": 2.0},
    "Masterwork": {"weight": 0.06, "multiplier": 3.0},
    "Legendary": {"weight": 0.02, "multiplier": 5.0}
  }
}
```

This means:
- 25% of items are Poor quality
- 35% are Standard
- Only 2% are Legendary (actually rare!)
- Value multipliers are configurable

### Web API Endpoints

When running the web interface (`python web_app.py`), the following REST API endpoints are available:

#### GET `/api/templates`
List all available templates

#### GET `/api/attributes`
Get all filterable attributes (quality levels, rarities, materials, etc.)

#### POST `/api/generate/item`
Generate an item
```json
{
  "template": "weapon_melee",
  "seed": 42,
  "save": true,
  "min_quality": "Excellent",
  "min_rarity": "Rare",
  "min_value": 500
}
```

#### POST `/api/generate/npc`
Generate an NPC
```json
{
  "archetype": "blacksmith",
  "seed": 42,
  "save": true
}
```

#### POST `/api/generate/location`
Generate a location
```json
{
  "template": "tavern",
  "connections": true,
  "seed": 42,
  "save": true
}
```

#### POST `/api/generate/world`
Generate a world
```json
{
  "size": 10,
  "seed": 42,
  "save": true,
  "name": "My Fantasy World"
}
```

#### POST `/api/generate/bulk`
Generate multiple items in bulk
```json
{
  "type": "item",
  "count": 100,
  "template": "weapon_melee",
  "seed": 42,
  "save": true
}
```

#### GET `/api/history?type=item&limit=50`
Get generation history

#### GET `/api/search/items?quality=Legendary&min_value=1000`
Search saved items

## API Reference

### ContentGenerator Class

#### `__init__(data_dir="data", seed=None)`
Initialize the content generator.

**Parameters:**
- `data_dir` (str): Path to directory containing JSON configuration files
- `seed` (int, optional): Random seed for reproducible generation

**Example:**
```python
# Create generator with seed for reproducible results
generator = ContentGenerator(seed=42)
item1 = generator.generate_item("weapon_melee")

# Reset with same seed to get identical results
generator.reset_seed(42)
item2 = generator.generate_item("weapon_melee")
# item1 and item2 will be identical
```

#### `generate_item(template_name=None, constraints=None)`
Generate a random item with optional constraints.

**Parameters:**
- `template_name` (str, optional): Specific item template to use (e.g., "weapon_melee", "potion")
- `constraints` (dict, optional): Generation constraints:
  - `min_quality`: Minimum quality level (e.g., "Fine", "Excellent")
  - `max_quality`: Maximum quality level
  - `min_rarity`: Minimum rarity level (e.g., "Rare", "Epic")
  - `max_rarity`: Maximum rarity level
  - `min_value`: Minimum gold value
  - `max_value`: Maximum gold value
  - `exclude_materials`: List of materials to exclude
  - `required_stats`: List of required stat names

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

## Running the Built-in Examples

The repository includes `example.py` with 6 comprehensive demonstrations:

```bash
python example.py
```

This will run through:

1. **Example 1 - Generating Items**: Shows various item types (weapons, armor, potions, jewelry)
2. **Example 2 - Generating NPCs**: Creates NPCs from different archetypes with inventories
3. **Example 3 - Generating Locations**: Builds locations with NPCs and items
4. **Example 4 - Generating Worlds**: Creates interconnected world with multiple locations
5. **Example 5 - Cross-Referencing**: Demonstrates relationships between content types
6. **Example 6 - Exporting Content**: Shows how to export generated content to JSON files

**Output Files Created:**
- `output_items.json` - 5 randomly generated items
- `output_npcs.json` - 3 randomly generated NPCs
- `output_world.json` - Complete world with all locations, NPCs, and items

See the [Practical Examples](#practical-examples) section above for real-world use cases like quest rewards, shop systems, dungeon generators, and more!

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
