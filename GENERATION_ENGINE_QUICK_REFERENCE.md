# GenerationEngine Quick Reference

## How ContentGenerator Works

1. **JSON Configuration Files** (in `data/`) define templates
2. **ContentGenerator loads them** in `__init__()`
3. **Generation methods** read templates and create random content
4. **Template placeholders** (`{quality}`, `{material}`, etc.) are filled by `_fill_template()`
5. **Constraints** (min/max quality, rarity, etc.) filter generated content

## Key Generation Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `generate_item(template_name, constraints)` | Random item | Dict with name, type, stats, value |
| `generate_npc(profession_names, level)` | Random NPC | Dict with name, skills, equipment, stats |
| `generate_location(template_name, biome)` | Random location | Dict with description, NPCs, items |
| `generate_crafting_recipe(item, difficulty)` | Random recipe | Dict with ingredients, tools, time, success_rate |

## Template Structure Example

```json
{
  "weapon_melee": {
    "base_names": ["Sword", "Axe"],          // Random selection
    "has_material": true,                      // Quality modifiers
    "has_quality": true,
    "has_rarity": true,
    "stat_count": { "min": 1, "max": 3 },     // Random count
    "description_templates": [
      "A {quality} {material} {base_name}"    // Placeholders
    ]
  }
}
```

## How Items Are Generated

1. Select random template (e.g., "weapon_melee")
2. Pick random base_name ("Sword")
3. Generate quality/rarity/material (weighted random)
4. Generate 1-3 random stats
5. Calculate value (base × quality_multiplier × rarity_multiplier)
6. Fill description: "A fine steel sword"

## Profession System

- **35 professions** fully defined (blacksmith, mage, merchant, etc.)
- **6 levels** of progression (Novice → Grandmaster)
- **Stat multipliers** scale 0.7x to 1.5x based on level
- **Skills** unique to each profession
- **Inventory sets** (e.g., blacksmith_inventory) define what NPCs carry

## Database Integration

- `DatabaseManager` creates tables for each content type
- Stores generated content with metadata
- Supports SQLite (default) or PostgreSQL

## Adding New Features: 3-Step Process

### 1. Create Configuration
```json
// data/my_feature.json
{
  "templates": {
    "my_template": {
      "base_names": [],
      "description_templates": []
    }
  }
}
```

### 2. Load in ContentGenerator
```python
# src/content_generator.py line 67
self.my_feature = self._load_json("my_feature.json")
```

### 3. Create Generation Method
```python
def generate_my_feature(self, template_name: Optional[str] = None) -> Dict:
    if template_name is None:
        template_name = self.rng.choice(list(self.my_feature["templates"].keys()))
    template = self.my_feature["templates"][template_name]
    # ... generate content using template ...
    return result
```

## Profession/Crafting Status

### Already Implemented
- 35 complete profession definitions
- Profession level system (6 levels)
- NPC stat/skill combination from professions
- Recipe generation method exists

### Still Needed
- Recipe database linking professions to specific recipes
- Player recipe discovery/unlocking system
- Crafting API endpoints
- Frontend connection to backend

## Template Placeholder Reference

| Placeholder | Used For | Example |
|-------------|----------|---------|
| `{quality}` | Item quality | "fine", "masterwork" |
| `{rarity}` | Item rarity | "common", "legendary" |
| `{material}` | Item material | "steel", "leather" |
| `{visual_adjective}` | Description adjective | "shimmering", "ancient" |
| `{tactile_adjective}` | Feel/texture | "smooth", "rough" |
| `{trait}` | NPC trait | "wise", "grumpy" |
| `{race}` | Character race | "dwarf", "human" |
| `{title}` | NPC title | "Blacksmith", "Guard" |
| `{environment_tag_N}` | Location descriptor | "dark", "dangerous" |
| `{base_name}` | Base item/location name | "sword", "forest" |

## Key Files

- **Generation Logic:** `/home/user/R-Gen/src/content_generator.py` (2,823 lines)
- **Professions:** `/home/user/R-Gen/data/professions.json` (3,150+ lines)
- **Items:** `/home/user/R-Gen/data/item_templates.json`
- **Levels:** `/home/user/R-Gen/data/profession_levels.json`
- **Database:** `/home/user/R-Gen/src/database.py`
- **Server:** `/home/user/R-Gen/game_server.py`
- **Frontend:** `/home/user/R-Gen/Client/game.js`
