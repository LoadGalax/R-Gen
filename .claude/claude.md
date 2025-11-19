# R-Gen: Random Game Content Generator

## Project Overview

R-Gen is a powerful Python-based dynamic game content generation engine for creating Items, NPCs, Locations, Worlds, Spells, Organizations, Quests, and more. The system features weighted probabilities, constraints, database integration, a web interface, and a comprehensive CLI.

**Project Type:** Game Development Tool / Procedural Content Generator
**Primary Language:** Python 3.7+
**Architecture:** Modular JSON-driven configuration system
**Interfaces:** Python API, CLI, Web UI (Flask)

## Core Philosophy

1. **Pure Python Core**: Core functionality uses only Python standard library
2. **JSON-Driven**: All content templates stored in modular JSON configuration files
3. **Weighted Randomness**: Realistic probability distributions (legendary items are actually rare)
4. **Cross-Referencing**: Smart relationships between content types (NPCs get appropriate inventory)
5. **Reproducibility**: Seed-based generation for consistent results
6. **Flexibility**: Multiple interfaces (API, CLI, Web) for different use cases

## Technology Stack

### Core Dependencies
- **Python**: 3.7+ (pure standard library for core features)
- **Required Modules**: `random`, `json`, `os`, `copy`, `datetime`, `uuid`, `argparse`

### Optional Dependencies
- **Flask** 3.0.0: Web interface
- **flask-cors** 4.0.0: CORS support for web API
- **psycopg2-binary** 2.9.9: PostgreSQL database support
- **pytest** 7.4.3: Testing framework
- **pytest-cov** 4.1.0: Code coverage

### Database Support
- **SQLite**: Built-in support (no additional dependencies)
- **PostgreSQL**: Optional (requires psycopg2-binary)

## Project Structure

```
R-Gen/
├── .claude/                  # Claude AI configuration
│   └── claude.md            # This file
├── data/                     # JSON configuration files
│   ├── adjectives.json      # Tactile and visual adjectives
│   ├── biomes.json          # Biome definitions and characteristics
│   ├── damage_types.json    # Combat damage types
│   ├── description_styles.json  # 10+ description style templates
│   ├── economy.json         # Pricing, trade goods, services
│   ├── environment_tags.json    # Location environment descriptors
│   ├── factions.json        # Faction definitions and relationships
│   ├── item_sets.json       # Predefined item collections
│   ├── item_templates.json  # Item type definitions
│   ├── locations.json       # Location templates and properties
│   ├── materials.json       # Crafting materials
│   ├── npc_traits.json      # Personality traits
│   ├── organizations.json   # Guild and organization types
│   ├── profession_levels.json   # Experience/skill tiers
│   ├── professions.json     # Detailed NPC professions
│   ├── quality.json         # Quality tiers with multipliers
│   ├── quests.json          # Quest templates and objectives
│   ├── races.json           # Character races and stats
│   ├── rarity.json          # Rarity tiers with weights
│   ├── spells.json          # Magic spell templates
│   ├── stats.json           # Available character stats
│   └── weather.json         # Weather patterns and effects
├── src/                      # Core Python modules
│   ├── content_generator.py # Main ContentGenerator class
│   └── database.py          # Database integration layer
├── cli.py                   # Command-line interface
├── web_app.py               # Flask web application
├── example.py               # Comprehensive demo script
├── requirements.txt         # Optional dependencies
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation

```

## Key Components

### 1. ContentGenerator (`src/content_generator.py`)

The core engine for all content generation. Approximately 3,000+ lines of code.

**Key Responsibilities:**
- Load and manage JSON configuration files
- Generate items, NPCs, locations, worlds, spells, quests, organizations
- Apply weighted probability distributions
- Handle constraint-based filtering
- Manage cross-references between content types
- Generate dynamic descriptions from templates
- Support seed-based reproducible generation
- Economic system (pricing, markets, trade)
- Weather and environmental systems
- NPC relationship networks
- Equipment systems
- Export to multiple formats (JSON, CSV, Markdown, XML, SQL)

**Key Methods:**
- `generate_item()`: Create items with quality, rarity, stats, materials
- `generate_npc()`: Create NPCs with stats, skills, inventory, dialogue
- `generate_location()`: Create locations with NPCs, items, connections
- `generate_world()`: Create interconnected world networks
- `generate_spell()`: Create magic spells with levels and schools
- `generate_quest_advanced()`: Create quests with chains and complications
- `generate_organization()`: Create guilds and factions
- `generate_market()`: Create economic marketplaces
- `generate_weather_detailed()`: Create weather with seasonal effects
- `generate_npc_network()`: Create social relationship networks
- `calculate_item_price()`: Dynamic pricing with supply/demand

### 2. DatabaseManager (`src/database.py`)

Handles persistence and retrieval of generated content.

**Key Responsibilities:**
- SQLite and PostgreSQL support
- Store items, NPCs, locations, quests, spells, organizations
- Generation history tracking
- Search and filtering
- Batch operations
- Schema management

**Key Methods:**
- `save_item()`, `save_npc()`, `save_location()`, etc.
- `get_item()`, `get_npc()`, `get_location()`, etc.
- `search_items()`, `search_npcs()`, etc.
- `get_history()`: Retrieve generation history

### 3. CLI (`cli.py`)

Command-line interface for quick generation.

**Key Commands:**
- `list-templates`: Show available templates
- `generate-item`: Create items
- `generate-npc`: Create NPCs
- `generate-location`: Create locations
- `generate-world`: Create worlds
- `generate-spell`: Create spells
- `generate-spellbook`: Create spell collections
- `generate-quest-advanced`: Create quests
- `generate-organization`: Create organizations
- `generate-market`: Create markets
- `generate-weather-detailed`: Create weather
- `generate-npc-network`: Create NPC networks
- `export`: Export to different formats

### 4. Web Interface (`web_app.py`)

Flask-based REST API and web UI.

**API Endpoints:**
- `GET /api/templates`: List templates
- `GET /api/attributes`: Get filterable attributes
- `POST /api/generate/item`: Generate items
- `POST /api/generate/npc`: Generate NPCs
- `POST /api/generate/location`: Generate locations
- `POST /api/generate/world`: Generate worlds
- `POST /api/generate/bulk`: Batch generation
- `GET /api/history`: Generation history
- `GET /api/search/items`: Search saved items

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone <repository-url>
cd R-Gen

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install optional dependencies for full features
pip install -r requirements.txt

# Core features work with no dependencies
python example.py
```

### Testing

```bash
# Run tests (when test suite exists)
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Running the Application

```bash
# Run web interface
python web_app.py
# Access at http://localhost:5000

# CLI examples
python cli.py generate-item --template weapon_melee
python cli.py generate-npc --archetype merchant
python cli.py generate-world --size 10

# Run demonstration
python example.py
```

## Coding Conventions

### Python Style
- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all public methods

### JSON Configuration Files
- Use 2 spaces for indentation
- Keep consistent structure across similar files
- Include comments where configuration is complex
- Use descriptive key names

### Documentation
- All public methods must have docstrings
- Include parameter types and return values
- Provide usage examples for complex features

### Error Handling
- Use try-except blocks for file operations
- Provide meaningful error messages
- Validate user inputs
- Handle missing configuration gracefully

## Content Generation System

### Weighted Probability System

All random selections use weighted probabilities defined in JSON files:

**Quality Levels** (quality.json):
- Poor: 25% (0.5x value multiplier)
- Standard: 35% (1.0x)
- Fine: 20% (1.5x)
- Excellent: 12% (2.0x)
- Masterwork: 6% (3.0x)
- Legendary: 2% (5.0x)

**Rarity Tiers** (rarity.json):
- Common: 40% (1.0x value multiplier)
- Uncommon: 30% (2.0x)
- Rare: 18% (3.0x)
- Epic: 8% (5.0x)
- Legendary: 3% (8.0x)
- Mythic: 1% (10.0x)

### Value Calculation

Final item value = base_value × quality_multiplier × rarity_multiplier

Example:
- Base sword: 100 gold
- Excellent quality: ×2.0
- Rare: ×3.0
- Final value: 100 × 2.0 × 3.0 = 600 gold

### Dynamic Descriptions

Templates use `{placeholder}` syntax:

```json
"description_templates": [
  "A {quality} {rarity} {material} {base_name}, which feels {tactile_adjective} to the touch."
]
```

Available placeholders:
- `{quality}`, `{rarity}`, `{material}`, `{base_name}`
- `{tactile_adjective}`, `{visual_adjective}`
- `{trait}`, `{title}` (for NPCs)
- `{environment_tag_1}`, `{environment_tag_2}`, etc.

### Cross-Referencing System

1. **NPCs → Items**: NPCs get inventory from `inventory_set`
2. **Locations → NPCs**: Locations spawn NPCs from `spawnable_npcs`
3. **Locations → Items**: Locations spawn items from `spawnable_items`
4. **Locations → Locations**: Locations connect via `can_connect_to`

## Common Development Tasks

### Adding a New Item Type

1. Edit `data/item_templates.json`
2. Add new template definition:
```json
"my_new_item": {
  "type": "weapon",
  "subtype": "special",
  "base_names": ["Blade", "Sword"],
  "has_material": true,
  "has_quality": true,
  "has_rarity": true,
  "stat_count": {"min": 1, "max": 3},
  "value_range": {"min": 100, "max": 1000},
  "description_templates": [
    "A {quality} {rarity} {material} {base_name}..."
  ]
}
```

### Adding a New NPC Archetype

1. Edit `data/professions.json`
2. Add new archetype definition
3. Create corresponding item set in `data/item_sets.json` if needed

### Adding a New Location Type

1. Edit `data/locations.json`
2. Define template with spawnable NPCs and items
3. Specify connection compatibility

### Adding New Attributes

Edit relevant files in `data/`:
- `materials.json`: Add new materials
- `stats.json`: Add new character stats
- `damage_types.json`: Add new damage types
- `environment_tags.json`: Add new environment descriptors

### Modifying Generation Logic

1. Locate relevant method in `src/content_generator.py`
2. Update logic while maintaining weighted probability system
3. Ensure backward compatibility with existing JSON configs
4. Test with various seeds to ensure randomness works

### Adding New Export Formats

1. Add export method to `ContentGenerator` class
2. Follow pattern of existing exports (JSON, CSV, Markdown, XML, SQL)
3. Update CLI to support new format
4. Update web API if needed

## Database Schema

### Items Table
- id, name, type, subtype, quality, rarity, material
- stats (JSON), value, description
- template, seed, created_at

### NPCs Table
- id, name, title, archetype
- stats (JSON), skills (JSON), dialogue, description
- inventory (JSON), location_id
- archetype, seed, created_at

### Locations Table
- id, name, type, environment_tags (JSON)
- description, connections (JSON)
- npcs (JSON), items (JSON)
- template, seed, created_at

### Generation History
- id, content_type, content_id
- template, seed, constraints (JSON)
- created_at

## Features by Category

### Content Types
- ✅ Items (weapons, armor, consumables, jewelry)
- ✅ NPCs (60+ professions with stats, skills, inventory)
- ✅ Locations (buildings, outdoor, underground)
- ✅ Worlds (interconnected location networks)
- ✅ Spells (9 levels, 8 schools)
- ✅ Quests (10 quest types, chains, complications)
- ✅ Organizations (guilds, factions, hierarchies)
- ✅ Markets (merchants, pricing, trade goods)

### Systems
- ✅ Weighted probability distributions
- ✅ Constraint-based filtering
- ✅ Seed-based reproducibility
- ✅ Cross-reference system
- ✅ Dynamic description engine
- ✅ Equipment system for NPCs
- ✅ Economic system (pricing, supply/demand)
- ✅ Weather system (seasons, moon phases, disasters)
- ✅ Relationship system (NPC networks)
- ✅ Export system (JSON, CSV, Markdown, XML, SQL)

### Interfaces
- ✅ Python API
- ✅ Command-line interface
- ✅ Web interface with REST API
- ✅ Database integration (SQLite, PostgreSQL)

## Best Practices

### When Generating Content

1. **Use Seeds for Testing**: Always use fixed seeds during development
2. **Validate Constraints**: Check constraint validity before generation
3. **Batch Operations**: Use bulk generation for large datasets
4. **Export Regularly**: Save important generations to JSON

### When Modifying Code

1. **Preserve Backward Compatibility**: Existing JSON configs must work
2. **Test with Multiple Seeds**: Ensure randomness is consistent
3. **Update Documentation**: Keep README.md synchronized
4. **Handle Edge Cases**: Empty lists, missing fields, invalid data

### When Working with JSON Configs

1. **Maintain Structure**: Follow existing patterns
2. **Test Changes**: Generate content after modifications
3. **Validate JSON**: Ensure files are valid JSON
4. **Document Complex Fields**: Add inline comments if needed

## Performance Considerations

### Optimization Tips

1. **Lazy Loading**: Load JSON files only when needed
2. **Caching**: Cache frequently accessed data
3. **Batch Generation**: Generate multiple items in one call
4. **Database Indexing**: Add indexes for search fields
5. **Connection Limits**: Limit location connection depth

### Scalability

- Single generation: < 0.1s per item/NPC
- Bulk generation: 100+ items/second
- World generation: 10 locations in ~1-2s
- Database: Tested with 10,000+ records

## Common Issues and Solutions

### Issue: Items always the same
**Solution**: Reset seed or use random seed: `ContentGenerator(seed=None)`

### Issue: No legendary items generated
**Solution**: Normal - they have 2% probability. Generate more items or use constraints.

### Issue: NPCs missing inventory
**Solution**: Ensure `inventory_set` exists in `item_sets.json`

### Issue: Locations not connecting
**Solution**: Check `can_connect_to` compatibility in templates

### Issue: Database errors
**Solution**: Ensure database schema is initialized: `db = DatabaseManager(db_path)`

## Future Enhancement Ideas

### Planned Features
- [ ] Character class system
- [ ] Equipment slot system (head, chest, legs, etc.)
- [ ] Crafting system
- [ ] Faction reputation system
- [ ] Dynamic quest generation based on world state
- [ ] Combat simulation
- [ ] Loot table system
- [ ] Difficulty scaling
- [ ] Procedural dialogue generation
- [ ] Save game support

### Possible Improvements
- [ ] Web UI improvements (React/Vue frontend)
- [ ] Real-time generation preview
- [ ] Visual world map generator
- [ ] Export to game engine formats (Unity, Godot)
- [ ] Integration with existing RPG systems (D&D, Pathfinder)
- [ ] Mobile app
- [ ] Multiplayer world sharing
- [ ] AI-generated descriptions (LLM integration)

## API Quick Reference

### ContentGenerator

```python
from src.content_generator import ContentGenerator

# Initialize
gen = ContentGenerator(seed=42)

# Generate content
item = gen.generate_item("weapon_melee", constraints={...})
npc = gen.generate_npc("blacksmith")
location = gen.generate_location("tavern")
world = gen.generate_world(num_locations=10)
spell = gen.generate_spell(spell_level=5, school="Evocation")
quest = gen.generate_quest_advanced(quest_type="rescue")
org = gen.generate_organization(org_type="thieves_guild")
market = gen.generate_market(wealth_level="wealthy")
weather = gen.generate_weather_detailed(season="winter")
network = gen.generate_npc_network(network_size=5)

# Export
gen.export_to_json(data, "output.json")
gen.export_to_markdown(data, "output.md", title="My Content")
gen.export_to_csv(data, "output.csv")
```

### DatabaseManager

```python
from src.database import DatabaseManager

# Initialize
db = DatabaseManager("game.db")

# Save
item_id = db.save_item(item, template="weapon_melee", seed=42)

# Retrieve
item = db.get_item(item_id)

# Search
items = db.search_items(filters={"rarity": "Legendary"})

# History
history = db.get_history(content_type="item", limit=100)
```

## Git Workflow

### Branch Strategy
- `main`: Stable releases
- `develop`: Development branch
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches

### Commit Messages
- Use present tense: "Add feature" not "Added feature"
- Be descriptive: Explain what and why
- Reference issues: "Fix #123: Issue description"

### Pull Requests
- Update README.md if adding features
- Include examples in description
- Test all affected functionality

## Resources

### Documentation
- README.md: User-facing documentation
- This file: Developer documentation
- Docstrings: Method-level documentation

### External Resources
- Python Docs: https://docs.python.org/3/
- Flask Docs: https://flask.palletsprojects.com/
- JSON Specification: https://www.json.org/

## Contact and Support

For issues, questions, or contributions:
- Open an issue on the repository
- Check existing documentation first
- Provide minimal reproducible examples
- Include Python version and dependencies

---

**Last Updated**: 2025-11-19
**Version**: 2.0
**Maintainer**: R-Gen Development Team
