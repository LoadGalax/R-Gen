# R-Gen Architecture Overview: GenerationEngine & Game Integration

## Project Structure

```
R-Gen/
├── GenerationEngine/          # Content generation engine (PYTHON)
│   ├── src/
│   │   ├── content_generator.py  # Main ContentGenerator class (2,823 lines)
│   │   ├── database.py           # Database manager
│   │   └── __init__.py
│   ├── data/                      # 24 JSON configuration files
│   │   ├── item_templates.json
│   │   ├── professions.json
│   │   ├── locations.json
│   │   ├── spells.json
│   │   ├── quests.json
│   │   ├── loot_tables.json (implied)
│   │   └── ... (21 more)
│   ├── tests/
│   ├── cli.py
│   └── web_app.py
│
├── Game/                      # Game Server (Flask + WebSocket)
│   ├── game_server.py        # Flask API & WebSocket endpoints (2,087 lines)
│   ├── game_database.py      # SQLite game state database (486 lines)
│   └── requirements_game.txt
│
├── SimulationEngine/          # Simulation & World Management
│   ├── src/
│   │   ├── core/              # World, event system, state management
│   │   ├── simulation/
│   │   ├── integration/
│   │   │   ├── generator_adapter.py  # Bridges to GenerationEngine
│   │   │   └── entity_factory.py
│   │   └── entities/          # LivingNPC, LivingLocation
│   └── setup.py
│
├── Client/                    # Web Client (JavaScript)
│   ├── index.html
│   ├── game.js               # Game client (WebSocket, API calls)
│   ├── master.html           # Admin panel
│   ├── master.js
│   ├── config.js
│   └── master.css
│
└── Root level
    ├── cli.py                # Root CLI
    ├── web_app.py
    └── README.md
```

---

## 1. GenerationEngine Class (ContentGenerator) - Current Architecture

### Location
`/home/user/R-Gen/GenerationEngine/src/content_generator.py`

### Core Design
The **ContentGenerator** is the main class (2,823 lines) that handles ALL procedural content generation in the system.

### Initialization & JSON Loading

```python
class ContentGenerator:
    def __init__(self, data_dir: str = "data", seed: Optional[int] = None):
        self.data_dir = Path(data_dir)
        self.seed = seed
        self.rng = random.Random(seed)  # Dedicated RNG for reproducibility
        
        # Loads 24 JSON files automatically during initialization:
        # Attribute configs (quality, rarity, materials, damage_types, etc.)
        # Item configs (item_templates, item_sets)
        # NPC configs (professions, profession_levels, npc_traits)
        # Location configs (locations, biomes, factions, races)
        # Feature configs (spells, organizations, weather, economy, quests)
        # Wildlife configs (animal_species, flora_species)
```

### Key Methods (40+ generation methods)

**Content Generation:**
- `generate_item()` - Items with quality, rarity, stats, value
- `generate_items_from_set()` - Multiple items from a set
- `generate_equipment()` - Character equipment loadouts
- `generate_npc()` - NPCs with professions, stats, dialogue
- `generate_location()` - Locations with NPCs, connections, features
- `generate_world()` - Complete worlds (5+ locations)
- `generate_loot_table()` - Enemy/treasure loot tables
- `generate_quest()` - Quests with objectives and rewards
- `generate_spell()` - Spells across 9 levels and 8 schools
- `generate_organization()` - Guilds, orders, companies
- `generate_encounter()` - Combat encounters with loot
- `generate_market()` - Dynamic markets with pricing

**Utility Methods:**
- `_load_json()` - Load configuration files
- `_weighted_choice()` - Weighted random selection
- `_fill_template()` - Description template substitution
- `_get_random_stats()` - Generate stat modifiers
- `calculate_item_price()` - Dynamic pricing with modifiers
- `validate_thematic_consistency()` - Check item/biome fit
- `export_to_*()` - Export in JSON, XML, CSV, SQL formats

### Current Dependencies on Game Class

**NO DIRECT DEPENDENCY CURRENTLY EXISTS.**

The ContentGenerator is designed as a **completely independent library**:
- It does NOT import or reference anything from `Game/game_server.py` or `game_database.py`
- It has NO knowledge of the Flask app, database, or player data
- It generates pure data dictionaries

### How Game Server Uses ContentGenerator

In `/home/user/R-Gen/Game/game_server.py`:

```python
# Line 25: Import
from GenerationEngine import ContentGenerator

# Line 37-39: Initialization
data_dir = project_root / "GenerationEngine" / "data"
generator = ContentGenerator(data_dir=str(data_dir))

# Usage locations:
# 1. Line 671: generator.professions (read-only access to profession configs)
# 2. Line 711-712: generator.professions (validate profession exists)
# 3. Line 1378: generator.generate_item() (generate items on-demand)
```

The game_server acts as a **thin wrapper** around ContentGenerator.

---

## 2. JSON Configuration Files (24 Total)

### Location
`/home/user/R-Gen/GenerationEngine/data/`

### Complete List & Purpose

#### **Attribute Configuration (8 files)**
1. **quality.json** - Quality tiers with multipliers (Broken, Poor, Fair, Fine, Excellent)
2. **rarity.json** - Rarity tiers (Common, Uncommon, Rare, Legendary, Mythic)
3. **materials.json** - Material properties (iron, steel, leather, silk, etc.)
4. **damage_types.json** - Damage types for weapons (slashing, piercing, bludgeoning, fire, etc.)
5. **environment_tags.json** - Location environmental tags
6. **stats.json** - Stat modifiers with min/max ranges
7. **npc_traits.json** - Character traits and personality descriptors
8. **adjectives.json** - Adjectives for descriptions (visual, tactile)

#### **Item Configuration (2 files)**
9. **item_templates.json** - Item templates: weapon_melee, weapon_ranged, armor, potion, scroll, jewelry, etc.
   - Includes: base_names, quality/rarity settings, stat ranges, value ranges, description templates
10. **item_sets.json** - Pre-defined item collections (e.g., "blacksmith_inventory", "wizard_spellbook")

#### **NPC Configuration (2 files)**
11. **professions.json** - 20+ profession archetypes (Blacksmith, Merchant, Guard, Wizard, Bard, etc.)
    - Each includes: title, names, skills, stats, dialogue hooks, inventory sets, locations
12. **profession_levels.json** - Profession progression (Level 1-10 requirements)

#### **World Configuration (4 files)**
13. **locations.json** - Location templates (village, fortress, tavern, forest, shrine, etc.)
    - Features, NPCs, connections, biome connections
14. **biomes.json** - Biome types with materials, weather, animals
15. **factions.json** - Faction definitions with alignment and purpose
16. **races.json** - Playable and non-playable races

#### **Feature Configuration (5 files)**
17. **spells.json** - Magic spells across 9 levels and 8 schools (Evocation, Transmutation, etc.)
18. **organizations.json** - 10+ organization types (Guilds, Thieves Guilds, Mages Circles, etc.)
19. **weather.json** - Weather patterns and effects
20. **economy.json** - Economic tiers, trade goods, services, pricing
21. **quests.json** - Quest templates and complications

#### **Description & Content (4 files)**
22. **description_styles.json** - 10 narrative styles (Technical, Poetic, Brief, Detailed, Noir, etc.)
23. **animal_species.json** - Wildlife species and behaviors
24. **flora_species.json** - Plant species and properties

### JSON Structure Example (item_templates.json)

```json
{
  "weapon_melee": {
    "type": "weapon",
    "subtype": "melee",
    "base_names": ["Sword", "Axe", "Mace", ...],
    "has_material": true,
    "has_quality": true,
    "has_rarity": true,
    "stat_count": {"min": 1, "max": 3},
    "value_range": {"min": 50, "max": 500},
    "description_templates": [
      "A {quality} {rarity} {material} {base_name}...",
      ...
    ]
  }
}
```

---

## 3. GameDatabase Structure & Storage

### Location
`/home/user/R-Gen/Game/game_database.py`

### SQLite Database Tables

The game maintains a **separate SQLite database** (`game_server.db`) for runtime game state:

#### **Core Tables**

1. **players**
   - id, username, password_hash, email
   - character_name, race, class
   - level, experience, gold
   - current_location_id, created_at, last_login

2. **player_stats**
   - player_id, health, max_health, mana, max_mana, energy, max_energy
   - strength, dexterity, intelligence, constitution, wisdom, charisma
   - updated_at

3. **player_inventory**
   - id, player_id, item_name, item_type
   - quantity, equipped, data (JSON), acquired_at

4. **player_professions**
   - id, player_id, profession_id
   - level (1-10), experience, created_at, updated_at

5. **player_recipes**
   - id, player_id, recipe_id
   - discovered_at

6. **generated_items**
   - id, item_name, item_type
   - item_data (full item JSON), created_at

### Data Flow: JSONs → Generation → Database

```
GenerationEngine/data/*.json
    ↓
ContentGenerator.generate_item/npc/location()
    ↓ (returns Dict)
GameDatabase methods
    ↓
game_server.py API endpoints
    ↓
SQLite database or direct return to client
```

---

## 4. How Game Currently Loads & Uses JSONs

### Step 1: Server Startup

```python
# game_server.py, lines 37-39
data_dir = project_root / "GenerationEngine" / "data"
generator = ContentGenerator(data_dir=str(data_dir))
# ContentGenerator loads all 24 JSONs into memory
```

### Step 2: On-Demand Generation

#### API Endpoint Example: Generate Items
```python
# game_server.py, line 1362
@app.route('/api/master/items/generate', methods=['POST'])
def generate_items():
    template = data.get('template', 'weapon_melee')  # From item_templates.json
    constraints = data.get('constraints', {})
    
    for _ in range(count):
        item = generator.generate_item(template, constraints)
        # ContentGenerator uses all relevant JSONs:
        # - item_templates.json
        # - quality.json
        # - rarity.json
        # - materials.json
        # - stats.json
        # - adjectives.json
        # Returns fully-formed item dict
```

#### API Endpoint Example: Professions
```python
# game_server.py, line 670
professions_data = generator.professions  # Direct JSON access
# Returns dict from professions.json + profession_levels.json

# Verify profession exists:
if profession_id not in generator.professions:
    return error
```

#### API Endpoint Example: Loot Tables
```python
# game_server.py, line 1011 in ContentGenerator
def generate_loot_table(self, enemy_type="standard", difficulty=1):
    # Uses quality_constraints from quality.json
    # Filters by biome from biomes.json
    # Generates items using generate_item()
    # Calculates gold based on difficulty
    return {"items": items, "gold": gold}
```

### Step 3: Storage

Generated content can be:
1. **Returned directly to client** (API responses)
2. **Stored in game_database.py** (player inventories, generated items)
3. **Stored in SimulationEngine World** (NPCs, locations for simulation)

---

## 5. GenerationEngine References Throughout Codebase

### File: `/home/user/R-Gen/Game/game_server.py` (2,087 lines)
- **Line 25**: Import ContentGenerator
- **Lines 37-39**: Initialize generator with data_dir
- **Lines 670-763**: Profession endpoints (read from generator.professions)
- **Line 1378**: Item generation via generator.generate_item()
- **Comments**: Multiple TODOs for future GenerationEngine integration

### File: `/home/user/R-Gen/SimulationEngine/src/integration/generator_adapter.py`
- **Wrapper class**: GeneratorAdapter
- **Methods**: 
  - `create_initial_world()` → generator.generate_world()
  - `spawn_npc()` → generator.generate_npc()
  - `spawn_item()` → generator.generate_item()
  - `spawn_location()` → generator.generate_location()
  - `generate_quest()` → generator.generate_quest()
- **Purpose**: Bridge between SimulationEngine and GenerationEngine

### File: `/home/user/R-Gen/SimulationEngine/src/integration/entity_factory.py`
- Converts GenerationEngine output (dicts) to SimulationEngine entities
- `create_npc()`: Dict → LivingNPC
- `create_location()`: Dict → LivingLocation
- `create_world_from_generated()`: World dict → living entities

### File: `/home/user/R-Gen/SimulationEngine/src/core/world.py`
- Comments reference GenerationEngine for world creation

### Root Level Files
- `/home/user/R-Gen/cli.py` - Uses ContentGenerator for CLI generation
- `/home/user/R-Gen/web_app.py` - Uses ContentGenerator for web interface
- `/home/user/R-Gen/GenerationEngine/example.py` - Demo usage

---

## 6. Current Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  (JavaScript: index.html, game.js, master.html, master.js)      │
│                    WebSocket & REST API                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    GAME SERVER (Flask)                          │
│                  game_server.py (2,087 lines)                  │
├─────────────────────────────────────────────────────────────────┤
│  REST API Endpoints:                                            │
│  - /api/world/info                                              │
│  - /api/locations, /api/npcs                                    │
│  - /api/master/items/generate ──────┐                           │
│  - /api/master/professions          │                           │
│  - /api/master/loot_tables          │                           │
└──────────────────────────┬───────────┼──────────────────────────┘
                           │           │
            ┌──────────────┼───────────┘
            │              │
       ┌────▼──────────────▼─────┐  ┌─────────────────────────────┐
       │  ContentGenerator        │  │   GameDatabase              │
       │  (GenerationEngine)      │  │   (SQLite)                  │
       │                          │  │                             │
       │  - generate_item()       │  │  Tables:                    │
       │  - generate_npc()        │  │  - players                  │
       │  - generate_location()   │  │  - player_stats             │
       │  - generate_world()      │  │  - player_inventory         │
       │  - generate_loot_table() │  │  - player_professions       │
       │  - generate_quest()      │  │  - generated_items          │
       │  - generate_spell()      │  │  - loot tables (in memory)  │
       │  - generate_market()     │  └─────────────────────────────┘
       └────┬─────────────────────┘
            │
       ┌────▼──────────────────┐
       │   24 JSON Config Files │
       ├────────────────────────┤
       │ - item_templates       │
       │ - professions          │
       │ - locations            │
       │ - spells               │
       │ - quests               │
       │ - quality, rarity      │
       │ - materials            │
       │ - stats, traits        │
       │ - (17 more...)         │
       └────────────────────────┘
             
       ┌──────────────────────────┐
       │  SimulationEngine        │
       │  (Optional/Future)       │
       │  - GeneratorAdapter      │
       │  - World simulation      │
       │  - NPC behaviors         │
       └──────────────────────────┘
```

---

## 7. Key Integration Points

### 1. **Profession System**
- JSON: `professions.json` (in GenerationEngine)
- Database: `player_professions` table (in GameDatabase)
- API: `/api/master/professions` endpoints
- Flow: Profession data read from JSON → validated against generator.professions → stored in DB

### 2. **Item Generation & Storage**
- JSON: `item_templates.json`, `item_sets.json`, `quality.json`, `rarity.json`, etc.
- Database: `player_inventory` and `generated_items` tables
- API: `/api/master/items/generate` → saves to `generated_items` table
- Flow: ContentGenerator.generate_item() → returns dict → saved to DB

### 3. **Loot Tables**
- Method: `ContentGenerator.generate_loot_table()`
- Storage: In-memory on World object (not persisted to DB currently)
- API: `/api/master/loot_tables` endpoints
- Uses: quality.json, item_templates.json for thematic generation

### 4. **Locations & NPCs**
- Generation: ContentGenerator.generate_location(), generate_npc()
- Storage: SimulationEngine.World.locations, World.npcs (not in game DB)
- Integration: SimulationEngine.GeneratorAdapter wraps ContentGenerator

---

## 8. Important Notes

### What's NOT Currently Persisted to Game Database
- Generated NPCs (stored in SimulationEngine memory)
- Generated Locations (stored in SimulationEngine memory)
- Loot tables (stored in World object)
- Quests (only generation template exists)
- Market data (generated on-demand)

### Why Separation Exists
1. **GenerationEngine** = Stateless content generator (pure data)
2. **GameDatabase** = Persistent game state (player, inventory data)
3. **SimulationEngine** = Live world simulation (NPCs with behaviors)
4. **Game Server** = Orchestrates between all three

### Current Limitations for Detachment
If detaching JSONs from GenerationEngine:
- ContentGenerator hardcodes 24 JSON filenames in `__init__`
- No abstraction layer for loading configurations
- Each method assumes its required JSONs are loaded
- No validation that required JSONs exist before use

---

## 9. Methods Using Each JSON File

| JSON File | Methods Using It |
|-----------|-----------------|
| item_templates.json | generate_item, generate_items_from_set, generate_loot_table, generate_equipment, generate_encounter |
| quality.json | generate_item, generate_loot_table, calculate_item_price |
| rarity.json | generate_item, generate_loot_table |
| materials.json | generate_item, generate_item_with_modifiers |
| professions.json | generate_npc, _generate_npc_no_profession |
| profession_levels.json | generate_npc (for level generation) |
| stats.json | _get_random_stats, generate_npc, generate_item |
| npc_traits.json | generate_npc |
| locations.json | generate_location, generate_world |
| biomes.json | generate_location, generate_encounter, generate_loot_table |
| spells.json | generate_spell, generate_spellbook |
| quests.json | generate_quest, generate_quest_advanced |
| organizations.json | generate_organization |
| races.json | generate_npc, generate_procedural_name |
| adjectives.json | Description generation in multiple methods |
| factions.json | generate_npc, generate_organization |
| animal_species.json | generate_encounter, location generation |
| flora_species.json | location generation |
| weather.json | generate_weather_and_time, generate_weather_detailed |
| economy.json | calculate_item_price, generate_market |
| description_styles.json | Dynamic description generation |
| environment_tags.json | Location generation |
| damage_types.json | Weapon generation |
| item_sets.json | generate_items_from_set |

---

## Summary

The **R-Gen system** separates concerns cleanly:

1. **GenerationEngine** (ContentGenerator): Pure, configurable, seed-based content factory
2. **JSONs**: Modular, game-balancing configuration files
3. **GameDatabase**: Persistent game state storage
4. **GameServer**: REST API orchestrator
5. **SimulationEngine**: Optional living world simulation
6. **Client**: Web-based frontend

**Current State**: ContentGenerator is completely independent and could be detached with proper abstraction of JSON loading and configuration management.

