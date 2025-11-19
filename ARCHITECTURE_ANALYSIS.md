# R-Gen Architecture Analysis: Adding Animals and Flora Systems

## Executive Summary

R-Gen is a modular, JSON-driven game content generator with a clean separation between:
- **Core Generation Engine**: `src/content_generator.py` (3000+ lines)
- **Data Layer**: `data/*.json` configuration files (22 JSON files)
- **CLI Interface**: `cli.py` (1200+ lines)
- **Database Layer**: `src/database.py` (600+ lines)

This document provides a comprehensive guide for adding new entity types (Animals and Flora).

---

## Part 1: Current NPC Structure and Definition

### 1.1 NPC Data Model

NPCs in R-Gen are defined with the following key properties:

```python
NPC = {
    "name": str,                          # Generated from profession's name lists
    "title": str,                         # Profession title
    "professions": List[str],             # Can have multiple professions (new)
    "profession_level": str,              # novice, apprentice, journeyman, expert, master, grandmaster
    "race": str,                          # human, dwarf, elf, etc.
    "faction": Optional[str],             # Faction allegiance
    "location": Optional[str],            # Location ID
    "stats": Dict[str, int],              # Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma
    "skills": List[str],                  # Skill names from profession
    "dialogue": str,                      # Random dialogue hook
    "description": str,                   # Dynamic description
    "inventory": List[Item],              # Generated from inventory_set
    "equipment": Dict[str, Item],         # Equipment slots (11 slots)
    "challenge_rating": int,              # Calculated from stats and level
    "relationships": Optional[Dict],      # NPC relationships (from network system)
}
```

### 1.2 Profession Definition Structure

Located in: **`data/professions.json`**

Each profession entry contains:

```json
{
  "profession_name": {
    "title": "Display Title",
    "use_race_names": true,
    "possible_races": ["human", "dwarf"],
    "possible_factions": ["kingdom_of_valor"],
    "first_names": ["Name1", "Name2"],
    "last_names": ["Lastname1", "Lastname2"],
    "skills": ["Skill1", "Skill2"],
    "base_stats": {
      "Strength": 8,
      "Dexterity": 5,
      "Constitution": 7,
      "Intelligence": 4,
      "Wisdom": 5,
      "Charisma": 3
    },
    "dialogue_hooks": ["Dialogue 1", "Dialogue 2"],
    "description_templates": [
      "A {trait} {race} {title} with {feature}."
    ],
    "inventory_set": "profession_inventory_set_name",
    "typical_locations": ["tavern", "market"]
  }
}
```

### 1.3 Key NPC Generation Code

Location: `src/content_generator.py`, method: `generate_npc()` (lines 426-710)

**Key highlights:**

```python
def generate_npc(self, 
                 archetype_name: Optional[str] = None,
                 location_id: Optional[str] = None,
                 race: Optional[str] = None,
                 faction: Optional[str] = None,
                 profession_names: Optional[List[str]] = None,
                 profession_level: Optional[str] = None) -> Dict[str, Any]:
    """
    Core NPC generation with:
    - Multi-profession support
    - Race/faction selection
    - Stat averaging and leveling
    - Skill combining
    - Inventory building
    - Challenge rating calculation
    """
```

**Generation flow:**
1. Validate profession names
2. Select race (from profession's possible_races)
3. Generate name (potentially using race-specific names)
4. Select profession level with weighted distribution
5. Combine and average stats from all professions
6. Apply racial modifiers
7. Add random stat variation
8. Combine skills from all professions
9. Generate inventory from inventory_set
10. Generate dialogue from dialogue_hooks
11. Fill description templates with dynamic values

---

## Part 2: Existing JSON Schemas and Data Structures

### 2.1 Core Attribute Files

#### **stats.json**
Defines available character stats and their value ranges:

```json
{
  "Strength": {"min": 1, "max": 20},
  "Dexterity": {"min": 1, "max": 20},
  "Constitution": {"min": 1, "max": 20},
  "Intelligence": {"min": 1, "max": 20},
  "Wisdom": {"min": 1, "max": 20},
  "Charisma": {"min": 1, "max": 20}
}
```

#### **materials.json**
Defines craftable/findable materials for items:

```json
[
  "iron", "steel", "wood", "leather", "copper", "silver", "gold", 
  "mithril", "adamantite", "bronze", "platinum", "obsidian", etc.
]
```

#### **quality.json**
Quality tiers with probability weights and value multipliers:

```json
{
  "Poor": {"weight": 0.25, "multiplier": 0.5},
  "Standard": {"weight": 0.35, "multiplier": 1.0},
  "Fine": {"weight": 0.20, "multiplier": 1.5},
  "Excellent": {"weight": 0.12, "multiplier": 2.0},
  "Masterwork": {"weight": 0.06, "multiplier": 3.0},
  "Legendary": {"weight": 0.02, "multiplier": 5.0}
}
```

#### **rarity.json**
Rarity distribution for items:

```json
{
  "Common": {"weight": 0.40, "multiplier": 1.0},
  "Uncommon": {"weight": 0.30, "multiplier": 2.0},
  "Rare": {"weight": 0.18, "multiplier": 3.0},
  "Epic": {"weight": 0.08, "multiplier": 5.0},
  "Legendary": {"weight": 0.03, "multiplier": 8.0},
  "Mythic": {"weight": 0.01, "multiplier": 10.0}
}
```

#### **adjectives.json**
Descriptive words for dynamic descriptions:

```json
{
  "visual": ["beautiful", "striking", "dull", "vibrant", ...],
  "tactile": ["soft", "rough", "smooth", "cold", ...]
}
```

#### **environment_tags.json**
Tags for describing locations:

```json
[
  "Dark", "Dangerous", "Overgrown", "Ancient", "Humid", "Cold",
  "Peaceful", "Tense", "Hostile", "Wet", "Dry", "Magical", ...
]
```

### 2.2 Entity Template Files

#### **item_templates.json**
Defines item types and generation parameters:

```json
{
  "weapon_melee": {
    "type": "weapon",
    "subtype": "melee",
    "base_names": ["Sword", "Axe", "Mace"],
    "has_material": true,
    "has_quality": true,
    "has_rarity": true,
    "stat_count": {"min": 1, "max": 3},
    "value_range": {"min": 50, "max": 500},
    "description_templates": ["A {quality} {rarity} {material} {base_name}..."],
    "damage_type_count": {"min": 1, "max": 2}
  }
}
```

#### **locations.json**
Defines location templates with spawning rules:

```json
{
  "templates": {
    "tavern": {
      "name": "Tavern",
      "type": "building",
      "suitable_biomes": ["urban", "plains", "coastal"],
      "base_environment_tags": ["Warm", "Social"],
      "additional_tags_count": {"min": 1, "max": 3},
      "can_connect_to": ["blacksmith", "market", "inn"],
      "spawnable_npcs": ["barkeep", "merchant", "guard"],
      "spawnable_items": ["weapon_melee", "potion"],
      "npc_spawn_count": {"min": 2, "max": 5},
      "item_spawn_count": {"min": 1, "max": 3}
    }
  }
}
```

#### **races.json**
Race definitions with stat modifiers and naming conventions:

```json
{
  "races": {
    "human": {
      "name": "Human",
      "size": "medium",
      "stat_modifiers": {"all": 1},
      "lifespan": {"min": 50, "max": 90},
      "first_names_male": ["Aldric", ...],
      "first_names_female": ["Aria", ...],
      "last_names": ["Ashford", ...]
    }
  }
}
```

#### **organizations.json**
Guild and organization definitions:

```json
{
  "organization_types": {
    "guild": {
      "description": "Professional association",
      "typical_size": {"min": 50, "max": 500},
      "hierarchy_levels": ["Apprentice", "Journeyman", "Master"],
      "common_activities": ["trade", "crafting", "training"]
    }
  }
}
```

### 2.3 Item Sets

Located in: **`data/item_sets.json`**

Predefined collections of items that NPCs can carry:

```json
{
  "blacksmith_inventory": {
    "guaranteed": ["hammer", "tongs"],
    "optional": [
      {"template": "weapon_melee", "count": 2},
      {"template": "armor", "count": 1}
    ]
  }
}
```

### 2.4 Biomes

Located in: **`data/biomes.json`**

Defines environmental characteristics:

```json
{
  "biomes": {
    "temperate_forest": {
      "name": "Temperate Forest",
      "climate": "temperate",
      "terrain": "forest",
      "spawnable_creatures": ["deer", "wolf"],
      "common_materials": ["wood", "leather"],
      "suitable_locations": ["forest_clearing", "cave"]
    }
  }
}
```

---

## Part 3: CLI Implementation and Entity Type Handling

### 3.1 CLI Architecture

Location: **`cli.py`** (1200+ lines)

**Key structure:**
1. Main parser setup (lines 774-815)
2. Subparsers for each command (lines 815-1115)
3. Command handlers: `cmd_*` functions (lines 271-771)
4. Main execution loop (lines 1115-1210)

### 3.2 How CLI Handles Different Entity Types

#### **Pattern 1: Single Entity Generation**

```python
def cmd_generate_item(args, generator, db=None):
    """Generate item(s)"""
    constraints = {}
    # ... build constraints from args ...
    
    if count == 1:
        item = generator.generate_item(args.template, constraints)
        if args.save and db:
            item_id = db.save_item(item, args.template, constraints, args.seed)
        output_data(item, args.format, args.output)
    else:
        items = [generator.generate_item(args.template, constraints) 
                 for _ in range(count)]
        # ... save and output ...
```

**Commands following this pattern:**
- `generate-item`
- `generate-npc`
- `generate-location`
- `generate-spell`

#### **Pattern 2: Complex Entity Generation**

```python
def cmd_generate_quest_advanced(args, generator):
    """Generate advanced quest with branching"""
    quest = generator.generate_quest_advanced(
        quest_type=args.quest_type,
        difficulty=args.difficulty,
        faction=args.faction,
        create_chain=args.create_chain
    )
    output_data(quest, args.format, args.output)
```

**Commands following this pattern:**
- `generate-quest-advanced`
- `generate-organization`
- `generate-market`
- `generate-weather-detailed`
- `generate-npc-network`

#### **Pattern 3: Data Retrieval**

```python
def cmd_get_item(args, db):
    """Get item by ID"""
    item = db.get_item(args.id)
    if item:
        output_data(item, args.format, None)
    else:
        print(f"Item with ID {args.id} not found")
```

### 3.3 Output Formatting

Location: **`cli.py`**, functions: `output_data()`, `format_npc()`, `format_item()`, etc.

**Output modes:**
- `text`: Human-readable with emoji and formatting
- `json`: Raw JSON output
- `pretty`: Formatted JSON

**Entity detection logic (lines 234-259):**

```python
if isinstance(data, list):
    if 'archetype' in data[0] or 'professions' in data[0]:
        output = "\n\n".join([format_npc(npc) for npc in data])
    elif 'environment_tags' in data[0]:
        output = "\n\n".join([format_location(loc) for loc in data])
    else:
        output = "\n\n".join([format_item(item) for item in data])
```

### 3.4 Database Integration

For entities that support `--save`:
1. Initialize `DatabaseManager`
2. Call appropriate `save_*` method
3. Return database ID

```python
if args.command in ['generate-item', 'generate-npc', ...] and args.save:
    db = DatabaseManager(args.db)
    item_id = db.save_item(item, template, constraints, seed)
```

---

## Part 4: Where New Entity Types (Animals, Flora) Should Be Added

### 4.1 File Structure for New Entity Types

Create parallel structures to existing entities:

```
data/
├── animal_types.json          # NEW: Animal type definitions
├── animal_species.json        # NEW: Specific animal species
├── flora_types.json           # NEW: Flora/plant type definitions
├── flora_species.json         # NEW: Specific flora species
├── biome_fauna_flora.json     # NEW: What animals/plants spawn in biomes
└── ... (existing files)
```

### 4.2 Data Schema Design for Animals

**File: `data/animal_types.json`**

```json
{
  "animal_categories": {
    "wild_fauna": {
      "description": "Wild animals found in nature",
      "typical_size": "varies",
      "base_stats": {
        "Strength": 6,
        "Dexterity": 7,
        "Constitution": 6,
        "Intelligence": 2,
        "Wisdom": 5,
        "Charisma": 2
      },
      "traits": ["wild", "untamed", "instinctual"]
    },
    "domesticated_pets": {
      "description": "Tamed animals kept as companions",
      "typical_size": "small_to_medium",
      "base_stats": {
        "Strength": 4,
        "Dexterity": 6,
        "Constitution": 5,
        "Intelligence": 3,
        "Wisdom": 6,
        "Charisma": 5
      },
      "traits": ["tame", "trained", "loyal"]
    }
  }
}
```

**File: `data/animal_species.json`**

```json
{
  "wolf": {
    "category": "wild_fauna",
    "name": "Wolf",
    "description": "A carnivorous predator found in forests and mountains",
    "size": "medium",
    "biome_affinity": ["temperate_forest", "tundra", "mountains"],
    "base_stats": {
      "Strength": 8,
      "Dexterity": 8,
      "Constitution": 7,
      "Intelligence": 3,
      "Wisdom": 6,
      "Charisma": 2
    },
    "skills": ["hunting", "tracking", "pack_tactics"],
    "abilities": ["bite", "sharp_claws", "keen_senses"],
    "behavior_types": ["aggressive", "territorial", "pack_hunter"],
    "rarity_distribution": {
      "Common": 0.60,
      "Uncommon": 0.30,
      "Rare": 0.08,
      "Epic": 0.02
    },
    "value_range": {
      "hide": {"min": 10, "max": 50},
      "tamed": {"min": 100, "max": 500}
    }
  },
  "dog": {
    "category": "domesticated_pets",
    "name": "Dog",
    "description": "A loyal canine companion",
    "size": "small_to_medium",
    "biome_affinity": ["urban", "plains"],
    "base_stats": {
      "Strength": 5,
      "Dexterity": 6,
      "Constitution": 6,
      "Intelligence": 4,
      "Wisdom": 7,
      "Charisma": 6
    },
    "skills": ["loyalty", "obedience", "companionship"],
    "abilities": ["bite", "keen_senses"],
    "behavior_types": ["friendly", "protective", "trainable"],
    "owner_types": ["blacksmith", "guard", "merchant"]
  }
}
```

### 4.3 Data Schema Design for Flora

**File: `data/flora_types.json`**

```json
{
  "flora_categories": {
    "wild_plants": {
      "description": "Plants growing naturally",
      "harvestable": true,
      "regrowth_time": "seasonal"
    },
    "cultivated_crops": {
      "description": "Plants grown for food or materials",
      "harvestable": true,
      "yield": "high"
    },
    "magical_plants": {
      "description": "Plants with magical properties",
      "harvestable": true,
      "rarity": "rare"
    },
    "decorative_plants": {
      "description": "Ornamental plants for gardens",
      "harvestable": false,
      "purpose": "aesthetic"
    }
  }
}
```

**File: `data/flora_species.json`**

```json
{
  "oak_tree": {
    "category": "wild_plants",
    "name": "Oak Tree",
    "description": "A mighty oak providing shelter and sustenance",
    "size": "large",
    "biome_affinity": ["temperate_forest", "plains"],
    "growth_stage": ["seed", "sapling", "mature", "ancient"],
    "harvest_products": ["wood", "acorns", "bark"],
    "value": {"wood": 20, "acorns": 5},
    "rarity_distribution": {
      "Common": 0.70,
      "Uncommon": 0.20,
      "Rare": 0.08,
      "Epic": 0.02
    }
  },
  "moonflower": {
    "category": "magical_plants",
    "name": "Moonflower",
    "description": "A luminescent flower that blooms at night",
    "size": "small",
    "biome_affinity": ["magical", "temperate_forest", "jungle"],
    "magical_properties": ["illumination", "healing", "magical_enhancement"],
    "harvest_products": ["petals", "essence", "seeds"],
    "value": {"petals": 50, "essence": 200},
    "rarity_distribution": {
      "Common": 0.10,
      "Uncommon": 0.20,
      "Rare": 0.40,
      "Epic": 0.25,
      "Legendary": 0.05
    }
  }
}
```

### 4.4 Biome-to-Creature/Flora Mapping

**File: `data/biome_fauna_flora.json`** (NEW)

```json
{
  "temperate_forest": {
    "spawnable_animals": ["wolf", "deer", "bear"],
    "spawnable_flora": ["oak_tree", "mushroom", "wildflower"],
    "rare_animals": ["griffin"],
    "rare_flora": ["moonflower"]
  },
  "mountains": {
    "spawnable_animals": ["eagle", "mountain_goat", "snow_leopard"],
    "spawnable_flora": ["pine_tree", "mountain_herb"],
    "rare_animals": ["phoenix"],
    "rare_flora": ["crystal_flower"]
  }
}
```

### 4.5 Location Integration

Update **`data/locations.json`** to spawn animals and flora:

```json
{
  "forest_clearing": {
    "spawnable_animals": ["wolf", "deer"],
    "animal_spawn_count": {"min": 0, "max": 3},
    "spawnable_flora": ["oak_tree", "mushroom"],
    "flora_spawn_count": {"min": 2, "max": 5}
  }
}
```

---

## Part 5: How Entities Are Generated and Stored

### 5.1 Entity Generation Flow

#### **Step 1: Initialization**
```python
generator = ContentGenerator(data_dir="data", seed=42)
```

**What happens:**
- Loads all JSON configuration files
- Sets up RNG with seed for reproducibility
- Initializes caches for locations, NPCs, organizations

#### **Step 2: Generation Method Call**

For items:
```python
item = generator.generate_item(template_name=None, constraints=None)
```

For NPCs:
```python
npc = generator.generate_npc(profession_names=["blacksmith"], race="dwarf")
```

#### **Step 3: Core Generation Logic**

General pattern (from `src/content_generator.py`):

```python
def generate_entity(self, template_name=None, filters=None):
    """
    1. Select template (random if None)
    2. Select subcomponents (quality, rarity, material, etc.)
    3. Apply constraints/filters
    4. Generate description from templates
    5. Build final entity dict
    6. Return entity
    """
    
    # Select template
    if template_name is None:
        template_name = self.rng.choice(list(self.templates.keys()))
    
    template = self.templates[template_name]
    
    # Generate properties with weighted choices
    quality = self._weighted_choice(self.quality)
    rarity = self._weighted_choice(self.rarity)
    
    # Apply filters
    if not self._check_constraints(quality, rarity, filters):
        return self.generate_entity(template_name, filters)  # Retry
    
    # Fill description template
    description = self._fill_template(template["description_templates"], values)
    
    # Build entity
    entity = {
        "name": name,
        "type": template["type"],
        "quality": quality,
        "description": description,
        # ... other properties
    }
    
    return entity
```

### 5.2 Item Generation Details

Location: `src/content_generator.py`, method: `generate_item()` (lines 162-345)

**Full flow:**

```
1. Select template (weapon_melee, armor, potion, etc.)
   └─ Weighted random from all templates
   
2. Generate basic properties
   ├─ Select base name from template.base_names
   ├─ Generate quality (if has_quality)
   ├─ Generate rarity (if has_rarity)
   ├─ Select material (if has_material)
   └─ Generate random stats
   
3. Apply constraints
   ├─ Check min/max quality
   ├─ Check min/max rarity
   ├─ Check min/max value
   ├─ Check required stats
   └─ Verify material not excluded
   
4. Calculate value
   └─ base_value × quality_multiplier × rarity_multiplier
   
5. Generate description
   ├─ Select description template
   ├─ Fill placeholders (quality, rarity, material, adjectives)
   └─ Return filled description
   
6. Return completed item dict
```

### 5.3 NPC Generation Details

Location: `src/content_generator.py`, method: `generate_npc()` (lines 426-710)

**Full flow:**

```
1. Validate profession(s)
   └─ Load profession data from professions.json
   
2. Select race
   ├─ From profession.possible_races OR
   └─ Random from all races
   
3. Generate name
   ├─ If use_race_names: Use race-specific names
   └─ Else: Use profession names
   
4. Select profession level
   └─ Weighted distribution (novice > master > grandmaster)
   
5. Combine profession stats
   ├─ Average stats from all professions
   ├─ Apply level multiplier
   ├─ Apply racial modifiers
   └─ Add random variation (-1 to +1)
   
6. Combine skills
   └─ Deduplicate from all professions
   
7. Generate inventory
   ├─ Load inventory_set from professions
   ├─ Generate items from item_sets
   └─ Apply equipment system
   
8. Generate dialogue
   └─ Random from profession.dialogue_hooks
   
9. Generate description
   ├─ Select from profession.description_templates
   ├─ Fill trait, race, title, adjectives
   └─ Return filled description
   
10. Calculate challenge_rating
    └─ Based on stats and profession level
    
11. Return completed NPC dict
```

### 5.4 Location Generation Details

Location: `src/content_generator.py`, method: `generate_location()` (lines 770-901)

**Full flow:**

```
1. Select template (tavern, cave, forge, etc.)
   └─ From locations.json templates
   
2. Select biome
   ├─ From template.suitable_biomes OR
   └─ Random from all biomes
   
3. Generate unique location ID
   └─ Format: {template_name}_{random_number}
   
4. Generate environment tags
   ├─ Start with template.base_environment_tags
   ├─ Add random additional tags
   └─ Limit by additional_tags_count
   
5. Generate description
   ├─ Select from template.description_templates
   ├─ Fill visual/tactile adjectives
   ├─ Fill environment tags
   └─ Return filled description
   
6. Generate NPCs
   ├─ Count from template.npc_spawn_count
   ├─ Select archetypes from template.spawnable_npcs
   └─ Call generate_npc() for each
   
7. Generate items
   ├─ Count from template.item_spawn_count
   ├─ Select templates from template.spawnable_items
   └─ Call generate_item() for each
   
8. Generate connections
   ├─ Get compatible location types from template.can_connect_to
   ├─ Either reuse existing location (50% chance)
   └─ Or generate new connected location
   
9. Return completed location dict
```

### 5.5 Storage in Database

Location: `src/database.py`

#### **Database Schema**

```sql
-- Items table
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    name TEXT,
    type TEXT,
    subtype TEXT,
    quality TEXT,
    rarity TEXT,
    material TEXT,
    value INTEGER,
    data TEXT (JSON),      -- Full item dict
    created_at TIMESTAMP,
    seed INTEGER
);

-- NPCs table
CREATE TABLE npcs (
    id INTEGER PRIMARY KEY,
    name TEXT,
    title TEXT,
    archetype TEXT,
    data TEXT (JSON),      -- Full NPC dict
    created_at TIMESTAMP,
    seed INTEGER
);

-- Locations table
CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    location_id TEXT UNIQUE,
    name TEXT,
    type TEXT,
    data TEXT (JSON),      -- Full location dict
    created_at TIMESTAMP,
    seed INTEGER
);

-- Generation history
CREATE TABLE generation_history (
    id INTEGER PRIMARY KEY,
    content_type TEXT,
    content_id INTEGER,
    template_name TEXT,
    constraints TEXT (JSON),
    created_at TIMESTAMP,
    seed INTEGER
);
```

#### **Save Process**

```python
def save_item(self, item: Dict, template_name=None, constraints=None, seed=None):
    """
    1. Serialize item dict to JSON string
    2. INSERT into items table with fields:
       - name, type, subtype, quality, rarity, material, value
       - data (full JSON), created_at, seed
    3. INSERT history record with:
       - content_type="item", content_id=item_id
       - template_name, constraints (JSON), seed
    4. COMMIT transaction
    5. Return item_id
    """
```

#### **Retrieval Process**

```python
def get_item(self, item_id: int):
    """
    1. SELECT data from items WHERE id = item_id
    2. Parse JSON string back to dict
    3. Return item dict
    """
```

### 5.6 Weighted Probability System

All random selections use weighted probabilities:

```python
def _weighted_choice(self, weighted_dict: Dict[str, Dict]) -> str:
    """
    weighted_dict = {
        "Common": {"weight": 0.40, ...},
        "Uncommon": {"weight": 0.30, ...},
        "Rare": {"weight": 0.18, ...},
        ...
    }
    
    Returns key based on weights using rng.choices()
    """
    items = list(weighted_dict.keys())
    weights = [weighted_dict[item].get("weight", 1.0) for item in items]
    return self.rng.choices(items, weights=weights, k=1)[0]
```

### 5.7 Description Template System

Templates use `{placeholder}` syntax that gets filled at generation time:

```python
def _fill_template(self, template: str, values: Dict[str, Any]) -> str:
    """
    template = "A {quality} {rarity} {material} {base_name}, which feels {tactile_adjective}."
    values = {
        "quality": "Excellent",
        "rarity": "Rare",
        "material": "iron",
        "base_name": "Sword",
        "tactile_adjective": "smooth"
    }
    
    Returns: "A Excellent Rare iron Sword, which feels smooth."
    """
    result = template
    for key, value in values.items():
        result = result.replace(f"{{{key}}}", str(value))
    # Remove any unfilled placeholders
    result = re.sub(r'\{[^}]+\}', '', result)
    return result
```

---

## Part 6: Implementation Recommendations

### 6.1 For Animals System

1. **Create new generation method:** `generate_animal(category, species, biome)`
2. **Add CLI command:** `generate-animal --category wild_fauna --species wolf`
3. **Extend locations:** Add `spawnable_animals` to location templates
4. **Database support:** Add animals table for persistence
5. **Formatting:** Add `format_animal()` function in CLI

### 6.2 For Flora System

1. **Create new generation method:** `generate_flora(category, species, biome)`
2. **Add CLI command:** `generate-flora --category wild_plants --species oak_tree`
3. **Extend locations:** Add `spawnable_flora` to location templates
4. **Database support:** Add flora table for persistence
5. **Formatting:** Add `format_flora()` function in CLI

### 6.3 Integration Points

- Update **`data/biomes.json`** to include spawnable_animals and spawnable_flora
- Update **`data/locations.json`** templates to spawn animals/flora
- Add animals/flora as discoverable items in locations
- Support in world generation (interconnected wildlife systems)
- Support in NPC networks (NPCs interacting with animals)

---

## Quick Reference: Adding a New Entity Type

### Template (example: Magical Artifact)

1. **Create data file:** `data/magical_artifacts.json`
2. **Create generation method:** `generate_magical_artifact(rarity, school)`
3. **Create CLI command:** `generate-artifact --rarity Epic --school Evocation`
4. **Create formatter:** `format_artifact()` in `cli.py`
5. **Add to database:** `save_artifact()`, `get_artifact()` in `database.py`
6. **Update CLI main:** Add case for new command in `main()`

### File Modifications

| File | Change |
|------|--------|
| `data/magical_artifacts.json` | Add new (create new file) |
| `src/content_generator.py` | Add `generate_magical_artifact()` method |
| `cli.py` | Add `cmd_generate_artifact()` and formatter |
| `src/database.py` | Add `save_artifact()`, `get_artifact()` |

---

This comprehensive analysis provides the foundation for adding Animals and Flora systems to R-Gen!
