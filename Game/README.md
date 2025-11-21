# R-Gen Game Server

A self-contained game server instance, completely detached from the GenerationEngine module.

## Overview

This game server runs independently with its own copy of:
- **Content generation logic** (`src/content_generator.py`)
- **JSON configuration files** (`data/*.json`)
- **Game database** (`game_database.py`)
- **Flask server** (`game_server.py`)

## Architecture

```
Game/
├── src/
│   ├── __init__.py                 # Module initialization
│   └── content_generator.py        # Content generation engine (118KB)
├── data/
│   ├── README.md                   # Data directory documentation
│   └── *.json                      # 24 JSON configuration files
├── game_server.py                  # Flask + SocketIO server
├── game_database.py                # SQLite database layer
└── requirements_game.txt           # Python dependencies
```

## Complete Independence

This game instance does **NOT** require the GenerationEngine module:

✅ All content generation logic is local (`src/content_generator.py`)
✅ All configuration data is local (`data/*.json`)
✅ No imports from GenerationEngine
✅ Can be deployed standalone

## Running the Server

```bash
cd Game
python3 game_server.py
```

The server will start on `http://localhost:5000`

## Dependencies

Install required packages:

```bash
pip install -r requirements_game.txt
```

Dependencies:
- Flask
- Flask-CORS
- Flask-SocketIO
- werkzeug

## Content Generation

The game uses a local `ContentGenerator` class to generate dynamic content:

```python
from src import ContentGenerator

# Initialize with local data directory
generator = ContentGenerator(data_dir="data")

# Generate items, NPCs, locations, etc.
item = generator.generate_item("weapon_melee")
npc = generator.generate_npc()
location = generator.generate_location("settlement")
```

## Customization

### Modify JSON Configurations

Edit files in `data/` to customize:
- Item generation rules (`item_templates.json`)
- NPC professions (`professions.json`)
- World biomes (`biomes.json`)
- Quest templates (`quests.json`)
- And 20 more configuration files

See `data/README.md` for complete documentation.

### Modify Generation Logic

The content generation algorithm is in `src/content_generator.py`. You can:
- Add new generation methods
- Modify existing algorithms
- Change randomization logic
- Add new content types

Since this is a local copy, changes won't affect the original GenerationEngine.

## Database

The game uses SQLite for persistent storage:

Tables:
- `players` - Player accounts and characters
- `player_stats` - Character statistics
- `player_inventory` - Player items and equipment
- `player_professions` - Player profession levels
- `generated_items` - Saved generated items

See `game_database.py` for schema and operations.

## API Endpoints

### Player Management
- `POST /api/player/register` - Create new account
- `POST /api/player/login` - Login
- `GET /api/player/me` - Get current player data

### World
- `GET /api/world/info` - Get world information
- `GET /api/locations` - List all locations
- `GET /api/npcs` - List all NPCs

### Master Admin Panel
- `GET /master` - Admin control panel
- `GET /api/master/npcs` - Manage NPCs
- `GET /api/master/locations` - Manage locations
- `POST /api/master/items/generate` - Generate items

See `game_server.py` for complete API documentation.

## WebSocket Events

Real-time updates via SocketIO:
- `connect` - Client connection established
- `world_update` - World state changes
- `player_moved` - Player movement events

## Deployment

Since this is a self-contained game instance:

1. Copy the entire `Game/` folder
2. Install dependencies from `requirements_game.txt`
3. Run `python3 game_server.py`

No need to install or configure GenerationEngine!

## Development

### Adding New Content Types

1. Edit `src/content_generator.py` to add generation methods
2. Create/modify JSON files in `data/` for configuration
3. Update `game_server.py` to expose via API
4. Restart the server

### Testing

```bash
# Test ContentGenerator import
python3 -c "from src import ContentGenerator; print('OK')"

# Test data loading
python3 -c "from src import ContentGenerator; g = ContentGenerator('data'); print(f'Loaded {len(g.professions)} professions')"
```

## Migration Notes

This game was detached from GenerationEngine on 2025-11-21:

**Before:**
```python
from GenerationEngine import ContentGenerator  # Module dependency
data_dir = "../GenerationEngine/data"          # External data
```

**After:**
```python
from src import ContentGenerator               # Local copy
data_dir = "data"                              # Local data
```

## Updating from Original Engine

If you want to pull updates from the original GenerationEngine:

```bash
# Update ContentGenerator source
cp ../GenerationEngine/src/content_generator.py src/

# Update JSON configs (⚠️ overwrites customizations!)
cp ../GenerationEngine/data/*.json data/
```

## License

This is a self-contained copy derived from the R-Gen GenerationEngine.

---

**Version**: 1.0 (Fully Detached)
**Last Updated**: 2025-11-21
**Original Engine**: GenerationEngine v1.0
