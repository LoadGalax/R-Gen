# R-Gen Generation Engine

Procedural content generation system for fantasy worlds.

## Overview

The Generation Engine is responsible for creating static content including:
- **Items** (20+ types with quality/rarity/materials)
- **NPCs** (80+ professions with stats/skills/equipment)
- **Locations** (20+ types with environment/biomes)
- **Spells** (8 schools, 9 levels)
- **Organizations** (11 types)
- **Quests** (10 types with chains)
- **Markets** (dynamic pricing)
- **Animals & Flora**
- **Weather systems**

## Installation

```bash
# Basic installation
pip install -e .

# With all features
pip install -e ".[all]"

# Just database support
pip install -e ".[database]"

# Just web API support
pip install -e ".[web]"
```

## Quick Start

### Python API

```python
from GenerationEngine.src.content_generator import ContentGenerator

# Create generator
gen = ContentGenerator(seed=42)

# Generate content
item = gen.generate_item("weapon_melee")
npc = gen.generate_npc("blacksmith")
world = gen.generate_world(num_locations=10)

print(f"Item: {item['name']}")
print(f"NPC: {npc['name']} the {npc['title']}")
print(f"World has {len(world['locations'])} locations")
```

### CLI

```bash
# Generate items
python cli.py generate-item --template weapon_melee --count 5

# Generate NPCs
python cli.py generate-npc --profession blacksmith

# Generate a world
python cli.py generate-world --size 10
```

### Web API

```bash
# Start the server
python web_app.py

# Access API at http://localhost:5000
# Interactive docs at http://localhost:5000/api/docs
```

## Features

- **Seed-based reproducibility** - Same seed = same content
- **Weighted distributions** - Realistic rarity (legendary items are rare!)
- **Constraint-based generation** - Min quality, required stats, etc.
- **Template system** - 24 JSON configuration files
- **Multiple export formats** - JSON, Markdown, CSV
- **Database persistence** - SQLite & PostgreSQL support

## Configuration

All generation is driven by JSON templates in `data/`:

- `professions.json` - 80+ NPC professions
- `locations.json` - 20+ location templates
- `item_templates.json` - Item definitions
- `spells.json` - Magic system
- And 20 more...

## Architecture

```
GenerationEngine/
├── src/
│   ├── content_generator.py   # Core generation logic
│   └── database.py             # Persistence layer
├── data/                       # 24 JSON config files
├── cli.py                      # Command-line interface
├── web_app.py                  # Flask REST API
└── tests/                      # Test suite
```

## License

See main project LICENSE file.
