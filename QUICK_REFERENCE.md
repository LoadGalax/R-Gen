# Quick Reference: GenerationEngine & Game Integration

## Key Facts at a Glance

### ContentGenerator Status
- **File**: `/home/user/R-Gen/GenerationEngine/src/content_generator.py` (2,823 lines)
- **Import**: Used in `Game/game_server.py` (line 25)
- **Dependency on Game**: NONE - completely independent library
- **Methods**: 40+ generation functions

### JSON Configuration
- **Location**: `/home/user/R-Gen/GenerationEngine/data/`
- **Count**: 24 JSON files
- **Load Time**: On server startup (ContentGenerator.__init__)
- **Hot Reload**: Not currently supported

### Critical Files for Integration

| File | Purpose | Lines | Key Classes |
|------|---------|-------|------------|
| `GenerationEngine/src/content_generator.py` | Content generation | 2,823 | ContentGenerator |
| `Game/game_server.py` | Flask API server | 2,087 | Flask app, endpoints |
| `Game/game_database.py` | Persistent storage | 486 | GameDatabase |
| `SimulationEngine/src/integration/generator_adapter.py` | Adapter | 150+ | GeneratorAdapter |
| `SimulationEngine/src/integration/entity_factory.py` | Entity conversion | 100+ | EntityFactory |

### Database Tables (SQLite)
```
game_server.db
├── players (user accounts)
├── player_stats (character stats)
├── player_inventory (items owned)
├── player_professions (skills/crafting)
├── player_recipes (discovered recipes)
└── generated_items (standalone items)
```

### API Endpoints Using ContentGenerator

| Endpoint | Method | Generator Call | JSON Used |
|----------|--------|-----------------|-----------|
| `/api/master/items/generate` | POST | `generator.generate_item()` | item_templates, quality, rarity, materials, stats |
| `/api/master/professions` | GET | `generator.professions` | professions, profession_levels |
| `/api/master/loot_tables` | GET/POST/PATCH | `generator.generate_loot_table()` | quality, item_templates, biomes |
| World creation | (SimulationEngine) | `generator.generate_world()` | locations, biomes, npcs, professions |

### JSON File Categories

```
Attribute Configs (8)
├── quality.json (item quality tiers)
├── rarity.json (item rarity levels)
├── materials.json (material properties)
├── damage_types.json (weapon damage)
├── environment_tags.json (location tags)
├── stats.json (stat ranges)
├── npc_traits.json (character traits)
└── adjectives.json (description words)

Item Configs (2)
├── item_templates.json (10+ item types)
└── item_sets.json (item collections)

NPC Configs (2)
├── professions.json (20+ professions)
└── profession_levels.json (progression)

World Configs (4)
├── locations.json (location types)
├── biomes.json (biome definitions)
├── factions.json (faction definitions)
└── races.json (playable races)

Feature Configs (5)
├── spells.json (9 levels, 8 schools)
├── organizations.json (guilds, orders)
├── weather.json (weather patterns)
├── economy.json (pricing, trade goods)
└── quests.json (quest templates)

Other (3)
├── description_styles.json (10 styles)
├── animal_species.json (wildlife)
└── flora_species.json (plants)
```

### Data Flow

```
Request to GameServer
    ↓
API Endpoint Handler
    ↓
ContentGenerator method (uses JSONs)
    ↓
Generate Dict
    ↓
Save to DB (optional) / Return to Client
```

### No Direct Dependencies
- ContentGenerator does NOT know about Flask/GameServer
- ContentGenerator does NOT know about GameDatabase
- ContentGenerator does NOT import anything from Game folder
- ContentGenerator only depends on Python standard library

### Seeding & Reproducibility
- All generation is seeded: `ContentGenerator(seed=42)`
- Same seed = same content (deterministic)
- Used in SimulationEngine for world generation

### What's Currently Persisted
- ✅ Player data (GameDatabase)
- ✅ Player inventory items (GameDatabase)
- ✅ Player professions (GameDatabase)
- ❌ Generated NPCs (memory only)
- ❌ Generated Locations (memory only)
- ❌ Loot Tables (memory only)
- ❌ Quests (generation only)
- ❌ Markets (on-demand generation)

### Current Limitations for JSONs Detachment

1. **Hardcoded paths**: JSONs assumed to be in `data_dir/filename`
2. **Hardcoded filenames**: 24 exact filenames in `__init__`
3. **No validation**: No check if JSON exists before use
4. **Tight coupling**: Methods assume all JSONs are loaded
5. **No config inheritance**: Can't share config across methods

### Dependencies Graph

```
Game Server (Flask)
    ↓
ContentGenerator (independent library)
    ↓
24 JSON Config Files
    
SimulationEngine
    ↓
GeneratorAdapter → ContentGenerator
    ↓
EntityFactory → Dict → LivingNPC/LivingLocation
```

### Key Integration Points

1. **Profession System**: JSON → Game → Database → Player
2. **Item Generation**: JSON → Game → Database → Player Inventory
3. **Loot Tables**: JSON → Game → Memory (World object)
4. **World Simulation**: JSON → SimulationEngine → Living World

### Future Detachment Strategy

To detach JSONs from GenerationEngine:
1. Create JSON loader abstraction (not hardcoded)
2. Make ContentGenerator accept config dict instead of loading JSONs
3. Create config validator to ensure required JSONs exist
4. Update all imports to use new config system
5. Update Game/SimulationEngine to manage JSON paths

