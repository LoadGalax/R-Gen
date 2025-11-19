# R-Gen: Procedural Fantasy World Generator & Simulator

**A two-engine system for creating and simulating rich fantasy worlds**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🌟 Overview

R-Gen is split into two powerful, independent engines:

### 🎲 Generation Engine
**Create** rich, diverse content using templates and procedural generation
- 80+ NPC professions
- 20+ location types
- Spells, quests, items, organizations, and more
- Seed-based reproducibility
- Weighted probability distributions

### 🌍 Simulation Engine
**Simulate** living worlds where content comes alive
- NPCs work, eat, sleep, socialize
- Time progression (day/night, seasons)
- Dynamic events and markets
- Save/load world state
- Event-driven architecture

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/LoadGalax/R-Gen.git
cd R-Gen

# Install GenerationEngine
cd GenerationEngine
pip install -e .

# Install SimulationEngine
cd ../SimulationEngine
pip install -e .
```

### Usage Examples

#### 1. Generation Only (Static Content)

```python
from GenerationEngine.src.content_generator import ContentGenerator

gen = ContentGenerator(seed=42)

# Generate items
weapon = gen.generate_item("weapon_melee")
print(f"{weapon['name']} - {weapon['quality']} quality")

# Generate NPCs
npc = gen.generate_npc("blacksmith")
print(f"{npc['name']} the {npc['title']}")

# Generate a world
world = gen.generate_world(num_locations=10)
print(f"Created world with {len(world['locations'])} locations")
```

#### 2. Full Simulation (Living World)

```python
from SimulationEngine.src.core.world import World
from SimulationEngine.src.simulation.simulator import WorldSimulator

# Create a living world
world = World.create_new(num_locations=10, seed=42, name="Fantasy Realm")

# Create simulator
simulator = WorldSimulator(world)

# Simulate one day
simulator.simulate_day()

# Check status
simulator.print_summary()
simulator.print_npc_status()
simulator.print_recent_events()

# Save world
world.save("my_world", format="json", compressed=True)
```

#### 3. Hybrid (Generation + Simulation)

```python
# Start with static generation
gen = ContentGenerator(seed=42)
quest = gen.generate_quest_advanced("fetch", difficulty=5)

# Create living world
world = World.create_new(num_locations=8, seed=42)

# Spawn NPCs dynamically during simulation
location_id = list(world.locations.keys())[0]
new_npc = world.spawn_npc(location_id, professions=["merchant"])

# Simulate
simulator = WorldSimulator(world)
simulator.simulate_hours(24)

# NPCs automatically craft items, travel, and interact!
```

## 📂 Project Structure

```
R-Gen/
├── GenerationEngine/          # Static content generation
│   ├── src/
│   │   ├── content_generator.py    # Core generator (2,823 lines)
│   │   └── database.py
│   ├── data/                       # 24 JSON config files
│   ├── cli.py                      # Command-line interface
│   ├── web_app.py                  # REST API
│   └── README.md
│
├── SimulationEngine/          # Living world simulation
│   ├── src/
│   │   ├── core/                   # World, Time, Events, State
│   │   ├── entities/               # Living NPCs, Locations
│   │   ├── integration/            # GenerationEngine bridge
│   │   └── simulation/             # Simulator
│   └── README.md
│
├── examples/                  # Usage examples
│   ├── 01_generation_only.py
│   ├── 02_full_simulation.py
│   └── 03_hybrid_usage.py
│
└── docs/                      # Documentation
    └── ARCHITECTURE.md
```

## 🎮 Features

### Generation Engine

✅ **Items** - 20+ types with quality/rarity/stats
✅ **NPCs** - 80+ professions with skills/equipment/dialogue
✅ **Locations** - 20+ templates with biomes/connections
✅ **Spells** - 8 schools, 9 levels
✅ **Quests** - 10 types with chains & complications
✅ **Organizations** - 11 types (guilds, orders, etc.)
✅ **Markets** - Dynamic pricing & supply/demand
✅ **Weather** - Seasons, time of day, moon phases
✅ **Animals & Flora** - Wild fauna and vegetation

### Simulation Engine

🌍 **Time System** - Day/night cycles, seasons, working hours
👥 **NPC Behaviors** - Work, eat, sleep, socialize, travel
⚡ **Events** - Pub/sub event bus with history tracking
🏪 **Dynamic Markets** - Open/close based on time
☁️ **Weather** - Updates periodically
🎨 **Crafting** - NPCs create items while working
💾 **Persistence** - Save/load world state (JSON/pickle)
📊 **Statistics** - Track simulation progress

## 🔧 CLI Usage

### Generation CLI

```bash
cd GenerationEngine

# Generate items
python cli.py generate-item --template weapon_melee --count 5

# Generate NPCs
python cli.py generate-npc --profession blacksmith --race dwarf

# Generate world
python cli.py generate-world --size 10

# List available templates
python cli.py list-templates
```

### Web API

```bash
cd GenerationEngine
python web_app.py

# API available at http://localhost:5000
# Interactive docs at http://localhost:5000/api/docs
```

## 📖 Examples

Run the included examples:

```bash
cd examples

# Example 1: Static generation only
python 01_generation_only.py

# Example 2: Full simulation
python 02_full_simulation.py

# Example 3: Hybrid usage
python 03_hybrid_usage.py
```

## 🎯 Use Cases

### Game Development
- Generate infinite unique content
- Populate open worlds
- Create dynamic NPCs with routines
- Simulate economies and factions

### Tabletop RPGs
- Generate towns, NPCs, quests
- Track time and events during sessions
- Persistent world between sessions
- Random encounters and loot

### Interactive Fiction
- Living, breathing worlds
- NPCs with daily routines
- Dynamic storytelling
- Save/load story state

### Procedural Content Systems
- Plugin for game engines
- Content pipeline for games
- Automated testing scenarios
- World generation research

## 🧪 Testing

```bash
# Test GenerationEngine
cd GenerationEngine
python test_all_generation.py

# Test SimulationEngine
cd SimulationEngine
python -m pytest tests/
```

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design & patterns
- **[GenerationEngine README](GenerationEngine/README.md)** - Generation API
- **[SimulationEngine README](SimulationEngine/README.md)** - Simulation API
- **[Examples](examples/)** - Code examples

## 🛠️ API Reference

### GenerationEngine

```python
gen = ContentGenerator(seed=42)

# Generate content
item = gen.generate_item(template, constraints={})
npc = gen.generate_npc(professions, race, faction)
location = gen.generate_location(template, biome)
world = gen.generate_world(num_locations)
spell = gen.generate_spell(level, school)
quest = gen.generate_quest_advanced(type, difficulty)
org = gen.generate_organization(type, faction)
market = gen.generate_market(location, wealth_level)
```

### SimulationEngine

```python
# Create world
world = World.create_new(num_locations=10, seed=42, name="My World")

# Simulate
world.step(minutes=60)
world.simulate_hours(24)
world.simulate_days(7)

# Query
npc = world.get_npc(npc_id)
location = world.get_location(location_id)
npcs_here = world.get_npcs_at_location(location_id)

# Spawn
new_npc = world.spawn_npc(location_id, professions=["merchant"])

# Persist
world.save("savefile")
loaded = World.load("savefile")

# Simulate with utilities
simulator = WorldSimulator(world)
simulator.simulate_day()
simulator.print_summary()
```

## 🎨 Configuration

All generation is driven by JSON templates in `GenerationEngine/data/`:

- `professions.json` - 80+ NPC professions (68 KB!)
- `locations.json` - 20+ location templates
- `item_templates.json` - Weapon, armor, consumable definitions
- `spells.json` - Magic system configuration
- `races.json` - 20+ playable races
- `factions.json` - Political factions
- `organizations.json` - Guilds, orders, companies
- And 17 more...

## 🔄 How It Works

```
┌─────────────────────────────────────┐
│   User Application                  │
│   (CLI, Web API, Game Engine)       │
└──────────┬─────────────────┬────────┘
           │                 │
           ▼                 ▼
┌──────────────────┐  ┌──────────────────┐
│ Generation       │  │ Simulation       │
│ Engine           │◄─┤ Engine           │
│                  │  │                  │
│ Creates content  │  │ Makes it alive   │
└──────────────────┘  └──────────────────┘
           │                 │
           ▼                 ▼
    Static Dicts      Living Entities
    (JSON data)       (Behaviors)
```

### Data Flow

1. **GenerationEngine** creates static data (dicts)
2. **SimulationEngine** converts to living entities (objects with behaviors)
3. **World.update()** simulates time progression
4. **Entities** act based on time, needs, profession
5. **Events** are published and logged
6. **GenerationEngine** can create new content during simulation

## 🚀 Performance

- **Recommended**: 30-60 minute simulation steps
- **Tested**: 100+ NPCs, 20+ locations
- **Save files**: ~100KB compressed JSON for medium world
- **Event processing**: 1000+ events/second

## 🗺️ Roadmap

### Current (v0.1.0)
- ✅ Generation Engine with 80+ professions
- ✅ Simulation Engine with time/events
- ✅ Basic NPC behaviors (work, eat, sleep)
- ✅ Save/load system
- ✅ Documentation & examples

### Near Future (v0.2.0)
- [ ] Combat system
- [ ] Advanced economy (supply/demand)
- [ ] Faction warfare & diplomacy
- [ ] Weather affecting NPC behavior
- [ ] Population growth/decline

### Long Term (v1.0.0)
- [ ] Advanced AI (behavior trees, GOAP)
- [ ] Multi-threading for large worlds
- [ ] Real-time visualization
- [ ] Game engine integrations (Unity, Godot)
- [ ] Multiplayer support

## 🤝 Contributing

Contributions welcome! Areas of interest:

- New NPC professions & behaviors
- Additional entity types (animals, monsters)
- Simulation systems (combat, economy, politics)
- Performance optimizations
- Game engine integrations
- Documentation improvements

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

Built with:
- Python 3.7+
- NumPy for random distributions
- Flask for web API (optional)

## 📧 Contact

- GitHub: [@LoadGalax](https://github.com/LoadGalax)
- Repository: [R-Gen](https://github.com/LoadGalax/R-Gen)

## 🌟 Star History

If you find R-Gen useful, consider giving it a star on GitHub!

---

**Made with ❤️ for game developers, dungeon masters, and world builders**
