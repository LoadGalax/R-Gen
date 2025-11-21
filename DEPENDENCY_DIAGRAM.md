# Dependency & Data Flow Diagram

## 1. Import Dependencies

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROOT LEVEL                                   │
│  cli.py ────────────┐                                            │
│  web_app.py ────────┼──────────────────────────────────────────┐ │
└─────────────────────┼────────────────────────────────────────────┤─┘
                      │                                            │
            ┌─────────▼──────────────────┐    ┌──────────────────▼─┐
            │ GenerationEngine            │    │ SimulationEngine   │
            │ (ContentGenerator)          │    │                   │
            │                             │    │ generator_adapter. │
            │ ✓ Independent library       │    │ py (wraps CG)     │
            │ ✓ No Game imports           │    │                   │
            │ ✓ No DB imports             │    │ entity_factory.py  │
            │ ✓ Only stdlib deps          │    │ (converts data)    │
            └────────┬────────────────────┘    └──────────┬────────┘
                     │                                    │
                     │                                    │
           ┌─────────▼────────────────────────────────────┘
           │
    ┌──────▼──────────────────┐
    │ Game/game_server.py      │
    │                          │
    │ Line 25: Import CG       │
    │ Lines 37-39: Init CG     │
    │ Lines 671+: Use CG       │
    │                          │
    │ Flask REST API           │
    │ WebSocket endpoints      │
    └──────┬─────────┬─────────┘
           │         │
      ┌────▼──┐  ┌───▼────────────────────┐
      │ CG    │  │ Game/game_database.py  │
      │ (in   │  │                        │
      │memory)│  │ SQLite: game_server.db │
      └───────┘  └────────────────────────┘
```

## 2. Data Flow - Item Generation Pipeline

```
CLIENT (JavaScript)
    │
    │ POST /api/master/items/generate
    │ { template: "weapon_melee", count: 5 }
    ▼
┌─────────────────────────────────┐
│ game_server.py endpoint handler │
│ generate_items()                │
└────────────┬────────────────────┘
             │
             │ for i in range(count):
             ▼
┌────────────────────────────────────────────┐
│ ContentGenerator.generate_item()           │
│                                            │
│ Uses these loaded JSONs:                  │
│  • item_templates.json (get template)     │
│  • quality.json (get quality tier)        │
│  • rarity.json (get rarity tier)          │
│  • materials.json (get material)          │
│  • stats.json (get random stats)          │
│  • adjectives.json (get descriptions)     │
└────────────┬────────────────────────────────┘
             │
             │ returns Dict with:
             │ {name, type, quality, rarity,
             │  material, stats, value, description}
             ▼
┌───────────────────────────┐
│ Dict representation       │
│ of generated item         │
└──────────┬────────────────┘
           │
           ├─→ Return to client as JSON response
           │
           └─→ Save to GameDatabase
                   │
                   ▼
              generated_items table
              (item_data column is JSON)
```

## 3. NPC Generation & Storage

```
ContentGenerator.generate_npc()
    │
    ├─ Uses: professions.json
    ├─ Uses: profession_levels.json
    ├─ Uses: races.json
    ├─ Uses: npc_traits.json
    ├─ Uses: stats.json
    └─ Uses: item_sets.json (for inventory)
    │
    ▼
Returns Dict with:
{id, name, profession, race, level, stats,
 traits, equipment, dialogue_hooks, background}
    │
    ├─→ To SimulationEngine World object
    │   └─→ becomes LivingNPC entity
    │       └─→ has behaviors, state, mood
    │
    └─→ To game_server API response
        └─→ directly to client as JSON
```

## 4. Profession Validation Flow

```
Client request: "Create profession X"
    │
    ▼
game_server.py endpoint
    │
    ├─ Check: is X in generator.professions?
    │ (Line 741 of game_server.py)
    │ (generator.professions loaded from professions.json)
    │
    ├─ YES: Get config from JSON
    │ │
    │ ├─ profession_levels.json (for level info)
    │ ├─ item_sets.json (for starting items)
    │ │
    │ └─→ Store in GameDatabase
    │     └─→ player_professions table
    │
    └─ NO: Return error (profession not in config)
```

## 5. Loot Table Generation

```
game_server.py: POST /api/master/loot_table
    │
    ├─ enemy_type: "boss"
    ├─ difficulty: 8
    └─ biome: "volcanic"
    │
    ▼
ContentGenerator.generate_loot_table()
    │
    ├─ Calculate difficulty constraints
    │ └─→ if difficulty >= 7, min_quality = "Excellent"
    │
    ├─ Get items (using generate_item)
    │ └─ Uses quality.json, item_templates.json
    │
    ├─ Filter by biome
    │ └─ Uses biomes.json (common_materials, rare_materials)
    │
    └─ Calculate gold reward
       └─ difficulty * 50 * multiplier[boss]
           multiplier from hardcoded dict: boss=5.0
    │
    ▼
Return Dict:
{
  enemy_type: "boss",
  difficulty: 8,
  items: [...], 
  gold: 2000,
  total_value: 5432
}
    │
    ▼
Stored in World object (in memory)
NOT persisted to game_server.db
```

## 6. Complete Request-Response Cycle

```
┌──────────────────────────────────────────────────────────────┐
│ CLIENT (JavaScript)                                          │
│ master.js: Generate 10 magical swords                        │
└────┬─────────────────────────────────────────────────────────┘
     │
     │ HTTP POST /api/master/items/generate
     │ { template: "weapon_melee", count: 10,
     │   constraints: { min_rarity: "Rare" } }
     │
     ▼
┌────────────────────────────────────────────────────────────────┐
│ GAME SERVER (Flask)                                            │
│ game_server.py line 1362                                       │
│                                                                │
│ @app.route('/api/master/items/generate', methods=['POST'])    │
│ def generate_items():                                          │
│     template = "weapon_melee"                                  │
│     constraints = { min_rarity: "Rare" }                       │
│                                                                │
│     for i in range(10):                                        │
│         item = generator.generate_item(template, constraints)  │
│         generated_items.append(item)                           │
│                                                                │
│     return jsonify({'items': generated_items})                 │
└────┬─────────────────────────────────────────────────────────┘
     │
     │ Uses ContentGenerator instance
     │ (initialized at startup with GenerationEngine/data)
     │
     ▼
┌────────────────────────────────────────────────────────────────┐
│ GENERATION ENGINE (Content Generator)                          │
│ content_generator.py                                           │
│                                                                │
│ For each item:                                                 │
│   1. Load item_templates.json → get "weapon_melee" template   │
│   2. Load quality.json → choose quality tier                   │
│   3. Load rarity.json → choose "Rare" (constrained)          │
│   4. Load materials.json → choose material                     │
│   5. Load stats.json → generate 1-3 random stats              │
│   6. Load adjectives.json → generate description              │
│   7. Calculate value from quality + rarity multipliers        │
│   8. Return complete item dict                                │
└────┬────────────────────────────────────────────────────────┘
     │
     │ Item Dict: {
     │   name: "Rare Iron Sword of Strength",
     │   type: "weapon",
     │   subtype: "melee",
     │   quality: "Fine",
     │   rarity: "Rare",
     │   material: "iron",
     │   stats: {Strength: 5, Dexterity: 2},
     │   value: 450,
     │   description: "A fine iron sword..."
     │ }
     │
     ▼
┌────────────────────────────────────────────────────────────────┐
│ STORAGE DECISION (in game_server.py)                          │
│                                                                │
│ Option 1: Return directly                                      │
│ → Client gets items immediately                                │
│                                                                │
│ Option 2: Save to database                                     │
│ → INSERT INTO generated_items                                  │
│    (item_name, item_type, item_data)                           │
│    values ("Rare Iron Sword...", "weapon", JSON_STRING)       │
│                                                                │
│ Option 3: Add to player inventory                              │
│ → INSERT INTO player_inventory                                 │
│    (player_id, item_name, item_type, data)                    │
└────┬────────────────────────────────────────────────────────┘
     │
     │ HTTP 200 OK
     │ { success: true, items: [...10 items...], count: 10 }
     │
     ▼
┌────────────────────────────────────────────────────────────────┐
│ CLIENT RECEIVES RESPONSE                                       │
│ JavaScript processes items                                     │
│ - Display in UI                                                │
│ - Apply rarity color from config.js                            │
│ - Show in master control panel                                 │
└────────────────────────────────────────────────────────────────┘
```

## 7. JSON Loading Sequence (Server Startup)

```
game_server.py starts
    │
    ▼
Line 25: from GenerationEngine import ContentGenerator
    │
    ▼
Line 37-39: 
    data_dir = Path("GenerationEngine/data")
    generator = ContentGenerator(data_dir=str(data_dir))
    │
    ▼
ContentGenerator.__init__ executes:
    │
    ├─→ self.quality = _load_json("quality.json") ✓
    ├─→ self.rarity = _load_json("rarity.json") ✓
    ├─→ self.materials = _load_json("materials.json") ✓
    ├─→ self.damage_types = _load_json("damage_types.json") ✓
    ├─→ self.environment_tags = _load_json("environment_tags.json") ✓
    ├─→ self.stats = _load_json("stats.json") ✓
    ├─→ self.npc_traits = _load_json("npc_traits.json") ✓
    ├─→ self.adjectives = _load_json("adjectives.json") ✓
    ├─→ self.item_templates = _load_json("item_templates.json") ✓
    ├─→ self.item_sets = _load_json("item_sets.json") ✓
    ├─→ self.professions = _load_json("professions.json") ✓
    ├─→ self.profession_levels = _load_json("profession_levels.json") ✓
    ├─→ self.locations_config = _load_json("locations.json") ✓
    ├─→ self.biomes_config = _load_json("biomes.json") ✓
    ├─→ self.factions_config = _load_json("factions.json") ✓
    ├─→ self.races_config = _load_json("races.json") ✓
    ├─→ self.spells_config = _load_json("spells.json") ✓
    ├─→ self.organizations_config = _load_json("organizations.json") ✓
    ├─→ self.weather_config = _load_json("weather.json") ✓
    ├─→ self.economy_config = _load_json("economy.json") ✓
    ├─→ self.quests_config = _load_json("quests.json") ✓
    ├─→ self.description_styles_config = _load_json("description_styles.json") ✓
    ├─→ self.animal_species = _load_json("animal_species.json") ✓
    └─→ self.flora_species = _load_json("flora_species.json") ✓
    │
    ▼
All 24 JSONs now in memory
    │
    ▼
Server ready to handle requests
All generator methods can now use any loaded JSON
```

## 8. SimulationEngine Integration

```
SimulationEngine needs initial world:
    │
    ▼
GeneratorAdapter.__init__():
    data_dir = "GenerationEngine/data"
    self.generator = ContentGenerator(seed=42, data_dir=data_dir)
    │
    ▼
World.create_new(num_locations=10):
    │
    ▼
adapter.create_initial_world(num_locations=10)
    │
    ▼
generator.generate_world(num_locations=10)
    │
    ├─ Uses: locations.json, biomes.json, races.json,
    │        professions.json, item_templates.json
    │
    └─ Returns Dict:
       {
         locations: {...},
         npcs: [...],
         world_name: "Fantasy Realm"
       }
    │
    ▼
EntityFactory.create_world_from_generated(world_dict):
    │
    ├─ Converts location dicts → LivingLocation objects
    ├─ Converts npc dicts → LivingNPC objects
    └─ Adds behavior/state to entities
    │
    ▼
World object created with:
    - locations: {id: LivingLocation}
    - npcs: {id: LivingNPC}
    - event_system
    - time_manager
    │
    ▼
Simulation runs with living entities
(not just static dicts from JSON)
```

