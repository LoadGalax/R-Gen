# Game Data Directory

This directory contains the JSON configuration files used by the game server for content generation. These files have been **copied** from the GenerationEngine and serve as the base configuration for this specific game instance.

## Purpose

The game server uses these JSON files to generate dynamic content such as:
- **Items** (weapons, armor, consumables, etc.)
- **NPCs** (professions, traits, dialogue)
- **Locations** (biomes, settlements, dungeons)
- **Quests** (objectives, rewards, storylines)
- **World elements** (weather, economy, factions)

## Fully Detached from GenerationEngine

This game instance is **completely independent** from the GenerationEngine module:

✅ **JSON files are independent copies** - Customize without affecting the original engine
✅ **ContentGenerator source is local** - Located in `Game/src/content_generator.py`
✅ **No module dependencies** - Game runs without requiring GenerationEngine installation
✅ **Self-contained** - All generation logic and data is in the Game folder
✅ **Multiple games can coexist** - Each with different configurations and customizations

## File Categories

### Attributes (7 files)
- `quality.json` - Item quality levels (common, rare, epic, etc.)
- `rarity.json` - Item rarity definitions
- `materials.json` - Crafting and item materials
- `damage_types.json` - Combat damage types
- `environment_tags.json` - Location/biome tags
- `stats.json` - Character and NPC statistics
- `adjectives.json` - Descriptive adjectives for generation

### Items (2 files)
- `item_templates.json` - Item type definitions and generation rules
- `item_sets.json` - Predefined item collections

### NPCs (3 files)
- `professions.json` - NPC profession definitions (skills, inventory, etc.)
- `profession_levels.json` - Profession progression system
- `npc_traits.json` - Character personality and behavior traits

### World (4 files)
- `locations.json` - Location templates and generation rules
- `biomes.json` - Biome definitions and characteristics
- `factions.json` - Political and social factions
- `races.json` - Playable and NPC races

### Features (5 files)
- `spells.json` - Magic system and spell definitions
- `organizations.json` - Guilds, orders, and institutions
- `weather.json` - Weather patterns and effects
- `economy.json` - Economic systems and trading
- `quests.json` - Quest templates and generation rules

### Content (3 files)
- `description_styles.json` - Narrative style templates
- `animal_species.json` - Wildlife and creature definitions
- `flora_species.json` - Plant and vegetation types

## Customization

To customize your game:

1. **Edit JSON files directly** - Modify the values, add new entries, or remove existing ones
2. **Test your changes** - Restart the game server to load the updated configurations
3. **Backup important changes** - Consider version controlling your custom configurations
4. **Document modifications** - Add comments in this README about major customizations

## Migration from Original Structure

Previously, the game server pointed directly to `GenerationEngine/data/`. Now it uses this directory (`Game/data/`) which contains independent copies. This allows for:

- **Game-specific content** without modifying the original GenerationEngine library
- **Easier deployment** - the Game folder is self-contained
- **Better organization** - each game instance has its own configuration

## Regenerating from GenerationEngine

If you want to reset to the original GenerationEngine defaults:

```bash
# From the R-Gen root directory
cp -r GenerationEngine/data/*.json Game/data/
```

⚠️ **Warning**: This will overwrite any customizations you've made!

## Integration

The game server (`game_server.py`) uses a local copy of ContentGenerator:

```python
# Import from local src module (not GenerationEngine)
from src import ContentGenerator

# Load data from local data directory
data_dir = project_root / "Game" / "data"
generator = ContentGenerator(data_dir=str(data_dir))
```

The ContentGenerator source code is located in `Game/src/content_generator.py`, making the game completely self-contained.

Any changes to these JSON files require a server restart to take effect.

---

**Last Updated**: 2025-11-21
**Structure Version**: 1.0 (Detached from GenerationEngine)
