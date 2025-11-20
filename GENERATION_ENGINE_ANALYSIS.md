# R-Gen GenerationEngine Architecture & Profession/Crafting System Analysis

## Overview

The GenerationEngine is a dynamic content generation system that creates game elements (items, NPCs, locations, quests, encounters) using modular JSON configuration files and Python templates. It follows a **configuration-driven generation pattern** with constraint support and random seeding.

## Key Architecture Components

### 1. Core Generator Pattern

**File:** `src/content_generator.py` (2,823 lines)

**Core Class:** `ContentGenerator`
- **Initialization:** Loads ~20+ JSON configuration files from `data/` directory
- **Random Seeding:** Supports reproducible generation via `seed` parameter
- **Template System:** Uses `_fill_template()` method for dynamic text generation

```python
def __init__(self, data_dir: str = "data", seed: Optional[int] = None):
    # Loads all configuration files
    self.quality = self._load_json("quality.json")
    self.rarity = self._load_json("rarity.json")
    self.materials = self._load_json("materials.json")
    self.item_templates = self._load_json("item_templates.json")
    self.professions = self._load_json("professions.json")
    self.profession_levels = self._load_json("profession_levels.json")
    # ... and more
```

### 2. Generation Methods (Key Methods)

#### **Item Generation**
```python
def generate_item(self, template_name: Optional[str] = None, 
                 constraints: Optional[Dict[str, Any]] = None) -> Dict
```

- Selects a random or specified item template (e.g., "weapon_melee", "armor")
- Applies constraints (quality, rarity, stats, value)
- Generates: name, type, quality, rarity, material, stats, value, description
- **Key Feature:** Template-based with weighted random choices

#### **NPC Generation**
```python
def generate_npc(self, profession_names: Optional[List[str]] = None,
                race: Optional[str] = None, faction: Optional[str] = None,
                profession_level: Optional[str] = None) -> Dict
```

- Supports multiple professions per NPC
- 35+ profession archetypes (blacksmith, merchant, mage, carpenter, etc.)
- 6-level profession hierarchy (Novice → Grandmaster)
- Combines stats/skills from all professions with level multiplier
- Generates equipment based on profession level

#### **Location Generation**
```python
def generate_location(self, template_name: Optional[str] = None,
                     biome: Optional[str] = None) -> Dict
```

- Templates with biome-specific variations
- Auto-spawns NPCs and items based on location type
- Supports location connections/relationships
- Description templates with adjective injection

#### **Crafting Recipe Generation** ⭐
```python
def generate_crafting_recipe(self, output_item: Optional[Dict] = None,
                           difficulty: int = 1) -> Dict
```

- **Already Exists!** Returns recipe with:
  - `ingredients` (material + quantity)
  - `required_tools` (forge, anvil, hammer, etc.)
  - `skill_requirements` (Crafting, Smithing, Alchemy, Jewelcrafting)
  - `crafting_time` (difficulty * 10 minutes)
  - `success_rate` (0.5 - 1.0 based on difficulty)

---

## Template System Architecture

### Template Files (JSON Configuration)

**Location:** `data/` directory

#### **1. Item Templates** (`item_templates.json`)
```json
{
  "weapon_melee": {
    "type": "weapon",
    "subtype": "melee",
    "base_names": ["Sword", "Axe", "Mace", ...],
    "has_material": true,
    "has_quality": true,
    "has_rarity": true,
    "stat_count": { "min": 1, "max": 3 },
    "value_range": { "min": 50, "max": 500 },
    "description_templates": [
      "A {quality} {rarity} {material} {base_name}, which feels {tactile_adjective} to the touch.",
      ...
    ]
  }
}
```

**Key Fields:**
- `base_names`: List of item base names to randomly select
- `has_material`, `has_quality`, `has_rarity`: Boolean flags
- `stat_count`: Range for how many stats to generate
- `value_range`: Gold value multiplied by quality/rarity multipliers
- `description_templates`: Template strings with `{placeholder}` markers

#### **2. Profession Templates** (`professions.json`)
```json
{
  "blacksmith": {
    "title": "Blacksmith",
    "use_race_names": true,
    "possible_races": ["human", "dwarf", "half_orc", "dragonborn"],
    "possible_factions": ["merchants_guild", "kingdom_of_valor", ...],
    "first_names": ["Thorin", "Bronn", "Grimm", ...],
    "last_names": ["Ironhammer", "Steelforge", ...],
    "skills": ["Smithing", "Metalworking", "Weapon Repair", "Armor Crafting"],
    "base_stats": {
      "Strength": 8,
      "Dexterity": 5,
      "Constitution": 7,
      ...
    },
    "dialogue_hooks": ["Need something repaired?", ...],
    "description_templates": [
      "A {trait} {race} {title} with soot-covered hands and a {tactile_adjective} demeanor.",
      ...
    ],
    "inventory_set": "blacksmith_inventory",
    "typical_locations": ["forge", "workshop", "market"]
  }
}
```

**All 35 Professions:** blacksmith, guard, merchant, mage, innkeeper, hermit, alchemist, cleric, druid, bard, thief, assassin, carpenter, tailor, jeweler, farmer, fisherman, hunter, scholar, scribe, healer, knight, soldier, archer, smuggler, necromancer, ranger, paladin, warlock, monk, barbarian, engineer, cartographer, baker, brewer, miner, spy, navigator, diplomat, gladiator, fortune_teller, sailor, pirate

#### **3. Profession Levels** (`profession_levels.json`)
```json
{
  "novice": { "rank": 1, "stat_multiplier": 0.7, "skill_bonus": 0, ... },
  "apprentice": { "rank": 2, "stat_multiplier": 0.85, "skill_bonus": 1, ... },
  "journeyman": { "rank": 3, "stat_multiplier": 1.0, "skill_bonus": 2, ... },
  "expert": { "rank": 4, "stat_multiplier": 1.15, "skill_bonus": 3, ... },
  "master": { "rank": 5, "stat_multiplier": 1.3, "skill_bonus": 4, ... },
  "grandmaster": { "rank": 6, "stat_multiplier": 1.5, "skill_bonus": 5, ... }
}
```

#### **4. Location Templates** (`locations.json`)
```json
{
  "templates": {
    "forest_clearing": {
      "type": "outdoor",
      "suitable_biomes": ["temperate_forest", "jungle"],
      "base_environment_tags": ["Traversable", "Overgrown"],
      "spawnable_npcs": ["hermit", "mage"],
      "spawnable_items": ["potion", "scroll"]
    }
  }
}
```

#### **5. Material & Attribute Lists**
- `materials.json`: ["iron", "steel", "bronze", "silver", "mithril", "wood", "leather", "bone"]
- `quality.json`: Weighted quality levels with multipliers
- `rarity.json`: Weighted rarity levels (common, uncommon, rare, legendary)
- `stats.json`: Stat definitions with value ranges
- `item_sets.json`: Pre-defined item collections for professions/factions

---

## Template Placeholder System

The `_fill_template()` method supports flexible template substitution:

```python
def _fill_template(self, template: str, values: Dict[str, Any]) -> str:
    # Replaces {placeholder} markers with corresponding values
    result = template
    for key, value in values.items():
        pattern = f"{{{key}}}"
        result = result.replace(pattern, str(value))
    return result
```

**Placeholder Types:**

| Type | Example | Used In |
|------|---------|---------|
| **Quality** | `{quality}` | Items, descriptions |
| **Rarity** | `{rarity}` | Items, descriptions |
| **Material** | `{material}` | Items, descriptions |
| **Adjectives** | `{visual_adjective}`, `{tactile_adjective}` | Descriptions |
| **Indexed Tags** | `{environment_tag_1}`, `{environment_tag_2}` | Location descriptions |
| **Trait** | `{trait}` | NPC descriptions |
| **Race** | `{race}` | NPC names, descriptions |
| **Title** | `{title}` | NPC descriptions |

**Example Template:**
```
"A {quality} {rarity} {material} {base_name}, which feels {tactile_adjective} to the touch."
```

Becomes: `"A fine rare bronze sword, which feels smooth to the touch."`

---

## Database Integration

**File:** `src/database.py`

**DatabaseManager** supports both SQLite and PostgreSQL:

```python
class DatabaseManager:
    def __init__(self, db_path: str = "r_gen.db", db_type: str = "sqlite"):
        # Creates tables for items, NPCs, locations, encounters, quests
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT,
                quality TEXT,
                rarity TEXT,
                value INTEGER,
                created_at TIMESTAMP
            )
        """)
```

**Storage Pattern:**
- Each generated content type has a corresponding table
- JSON properties stored as TEXT (serialized)
- Timestamps track generation time
- Supports history and playback

---

## Existing Profession/Crafting Data

### ✅ What Already Exists:

1. **35 Professions with Full Data:**
   - Skills (unique to each profession)
   - Base stats (distributed across 6 stats)
   - Dialogue hooks
   - Description templates
   - Inventory sets

2. **6-Level Profession Hierarchy:**
   - Novice (0.7x stats) → Grandmaster (1.5x stats)
   - Skill bonuses and title prefixes
   - Stat multipliers for progression

3. **Recipe Generation:**
   - `generate_crafting_recipe()` exists!
   - Returns: ingredients, tools, skill requirements, crafting time, success rate

4. **Profession-linked NPCs:**
   - NPCs can have multiple professions
   - Profession level affects stats and equipment

### ❌ What's Missing:

1. **Recipe Database:** Specific recipes for each profession
2. **Ingredient System:** Links between profession skills and material requirements
3. **Crafting Constraints:** Profession level requirements for recipes
4. **Recipe Collection System:** Player learning/unlocking recipes
5. **API Endpoints:** No `/api/craft/` endpoints in game_server.py
6. **Frontend Integration:** Game UI has craft tabs but no backend connection

---

## Pattern for Adding New Generation Capabilities

### Step 1: Create Configuration File

Create `data/new_feature.json`:
```json
{
  "templates": {
    "template_name": {
      "base_names": ["Name1", "Name2"],
      "properties": [...],
      "description_templates": ["Template with {placeholder}"]
    }
  }
}
```

### Step 2: Load in ContentGenerator.__init__()

```python
def __init__(self, data_dir: str = "data", seed: Optional[int] = None):
    # ... existing loads ...
    self.new_feature = self._load_json("new_feature.json")
```

### Step 3: Create Generation Method

```python
def generate_new_feature(self, template_name: Optional[str] = None) -> Dict:
    """
    Generate a new feature.
    
    Returns:
        Dictionary with feature properties
    """
    if template_name is None:
        template_name = self.rng.choice(list(self.new_feature["templates"].keys()))
    
    template = self.new_feature["templates"][template_name]
    
    # Use _weighted_choice() for weighted selections
    # Use _fill_template() for description generation
    # Use _get_random_stats() for stat generation
    
    return {
        "name": selected_name,
        "type": "new_feature",
        "description": filled_description,
        # ... other properties
    }
```

### Step 4: Add Database Table (if needed)

```python
# In DatabaseManager._init_sqlite()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS new_features (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT,
        data JSON,
        created_at TIMESTAMP
    )
""")
```

### Step 5: Add API Endpoint (if needed)

```python
@app.route('/api/new-feature', methods=['GET', 'POST'])
def handle_new_feature():
    if request.method == 'POST':
        feature = generator.generate_new_feature()
        return jsonify(feature)
```

### Step 6: Add Frontend UI (if needed)

Update `Client/game.js` or `Client/index.html`:
```javascript
showNewFeature() {
    const feature = await fetch('/api/new-feature').then(r => r.json());
    // Render feature to UI
}
```

---

## Implementation Recommendations for Profession/Crafting System

### Phase 1: Create Recipe Database

Create `data/recipes.json`:
```json
{
  "blacksmith": [
    {
      "name": "Iron Sword",
      "profession": "blacksmith",
      "min_level": "apprentice",
      "ingredients": [
        { "material": "iron", "quantity": 5 },
        { "material": "wood", "quantity": 1 }
      ],
      "tools": ["forge", "anvil"],
      "time": 60,
      "skill": "Smithing"
    }
  ]
}
```

### Phase 2: Create Recipe Generation Method

```python
def get_profession_recipes(self, profession: str, 
                          level: str = "novice") -> List[Dict]:
    """Get recipes available to a profession at a given level."""
    # Returns recipes filtered by profession and level requirement
```

### Phase 3: Add Crafting Endpoints

```python
@app.route('/api/player/recipes', methods=['GET'])
def get_player_recipes():
    # Return recipes player can craft based on professions

@app.route('/api/player/craft', methods=['POST'])
def craft_item():
    # Execute crafting, consume ingredients, produce item
```

### Phase 4: Frontend Integration

Link the existing craft UI in `game.js` (lines 1292-1410) to backend endpoints

---

## Key Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| `src/content_generator.py` | Core generation engine | 2,823 |
| `src/database.py` | Data persistence | ~600 |
| `data/professions.json` | 35 profession definitions | 3,150+ |
| `data/profession_levels.json` | 6-level hierarchy | 50 |
| `data/item_templates.json` | Item templates | ~1,500 |
| `data/materials.json` | Material list | 11 |
| `data/locations.json` | Location templates | ~1,000 |
| `game_server.py` | REST API server | 650+ |
| `Client/game.js` | Game UI logic | 1,600+ |

---

## Summary

The GenerationEngine is a robust, template-driven system that:
- ✅ Has a strong foundation for professions (35 complete)
- ✅ Already generates crafting recipes
- ✅ Supports profession levels and skill progression
- ✅ Uses flexible template placeholders
- ❌ Lacks recipe database linking professions to items
- ❌ Missing crafting API endpoints
- ❌ Frontend craft UI not connected to backend

The pattern is consistent and scalable. Adding profession-specific recipes is straightforward using the existing architecture.
