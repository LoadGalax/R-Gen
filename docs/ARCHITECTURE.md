# R-Gen Architecture Documentation

## System Overview

R-Gen is split into two independent but integrated engines:

```
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                            │
│         (CLI, Web API, Game Engines, Custom Tools)              │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐    ┌──────────────────┐
│  GENERATION      │    │  SIMULATION      │
│  ENGINE          │◄───│  ENGINE          │
│                  │    │                  │
│  Static Content  │    │  Living World    │
│  Creation        │    │  Simulation      │
└──────────────────┘    └──────────────────┘
```

## 1. Generation Engine

**Purpose**: Create rich, diverse, static content

**Location**: `GenerationEngine/`

**Key Components**:
- `ContentGenerator` - Core generation logic (2,823 lines)
- 24 JSON configuration files (~260 KB)
- Template-based generation system
- Weighted probability distributions
- Seed-based reproducibility

**What It Generates**:
- Items (20+ types)
- NPCs (80+ professions)
- Locations (20+ templates)
- Spells, quests, organizations
- Markets, animals, flora
- Weather systems

**Independence**: Can be used standalone without SimulationEngine

## 2. Simulation Engine

**Purpose**: Bring generated content to life

**Location**: `SimulationEngine/`

**Key Components**:

### Core Systems (`src/core/`)
- **World** - Main container, entity management
- **TimeManager** - Time progression, scheduling
- **EventSystem** - Pub/sub event bus
- **StateManager** - Save/load world state

### Entities (`src/entities/`)
- **BaseEntity** - Abstract base class
- **LivingNPC** - NPCs with behaviors and needs
- **LivingLocation** - Dynamic locations with state

### Integration (`src/integration/`)
- **GeneratorAdapter** - Bridge to GenerationEngine
- **EntityFactory** - Converts static data to living entities

### Simulation (`src/simulation/`)
- **WorldSimulator** - High-level simulation interface

**Dependencies**: Requires GenerationEngine

## Data Flow

### Initial World Creation

```
1. User Request
   ↓
2. World.create_new(num_locations=10)
   ↓
3. GeneratorAdapter.create_initial_world(10)
   ↓
4. ContentGenerator.generate_world(10)
   ↓
5. Returns static world data (dicts)
   ↓
6. EntityFactory.create_world_from_generated(data)
   ↓
7. Converts each location → LivingLocation
   Converts each NPC → LivingNPC
   ↓
8. World.locations = {id: LivingLocation}
   World.npcs = {id: LivingNPC}
   ↓
9. Return living World instance
```

### Simulation Loop

```
1. WorldSimulator.step(minutes=60)
   ↓
2. World.update(60.0)
   ↓
3. TimeManager.advance_minutes(60)
   ├─ Check for hour/day/season transitions
   └─ Trigger time-based scheduled events
   ↓
4. For each location in World.locations:
   ├─ location.update(60, world)
   ├─ Update weather (hourly)
   ├─ Update market status
   └─ Publish events
   ↓
5. For each NPC in World.npcs:
   ├─ npc.update(60, world)
   ├─ Update needs (energy, hunger, mood)
   ├─ Handle urgent needs (sleep if tired)
   ├─ Decide activity (work, eat, travel, etc.)
   ├─ Execute activity behavior
   └─ Publish events (moved, crafted item, etc.)
   ↓
6. EventSystem.process_events()
   ├─ Call all subscribers for each event
   └─ Add events to history
   ↓
7. Return to step 1 or finish
```

### Dynamic Content Generation

```
During Simulation:
  ↓
NPC decides to craft item
  ↓
npc._craft_item()
  ↓
world.generator_adapter.spawn_item("weapon_melee")
  ↓
ContentGenerator.generate_item("weapon_melee")
  ↓
Returns new item dict
  ↓
npc.inventory.append(item)
  ↓
EventSystem.publish_event("item_crafted")
```

## Class Hierarchy

### Entities

```
BaseEntity (abstract)
├── LivingNPC
│   ├── Properties: energy, hunger, mood, activity
│   ├── Methods: update(), start_working(), move_to_location()
│   └── Data: Wraps generated NPC dict
│
└── LivingLocation
    ├── Properties: npc_ids, market_open, current_weather
    ├── Methods: update(), add_npc(), remove_npc()
    └── Data: Wraps generated location dict
```

### Core Systems

```
World
├── Manages: locations, npcs, time, events
├── Systems: TimeManager, EventSystem, StateManager
├── Integration: GeneratorAdapter
└── Methods: create_new(), update(), save(), load()

WorldSimulator
├── Wraps: World instance
├── Controls: simulation stepping, callbacks
└── Utilities: print_summary(), print_npc_status()
```

## File Organization

```
R-Gen/
│
├── GenerationEngine/              # Content generation
│   ├── src/
│   │   ├── content_generator.py   # 2,823 lines - core logic
│   │   └── database.py            # Persistence
│   ├── data/                      # 24 JSON configs
│   │   ├── professions.json       # 80+ professions (68 KB)
│   │   ├── locations.json         # 20+ location templates
│   │   ├── item_templates.json
│   │   └── ...
│   ├── cli.py                     # Command-line interface
│   ├── web_app.py                 # Flask REST API
│   ├── setup.py                   # Package config
│   └── README.md
│
├── SimulationEngine/              # World simulation
│   ├── src/
│   │   ├── core/                  # Core systems
│   │   │   ├── world.py           # Main world class
│   │   │   ├── time_manager.py    # Time progression
│   │   │   ├── event_system.py    # Event bus
│   │   │   └── state_manager.py   # Save/load
│   │   │
│   │   ├── entities/              # Living entities
│   │   │   ├── base_entity.py
│   │   │   ├── npc.py             # NPCs with behaviors
│   │   │   └── location.py        # Dynamic locations
│   │   │
│   │   ├── integration/           # GenerationEngine bridge
│   │   │   ├── generator_adapter.py
│   │   │   └── entity_factory.py
│   │   │
│   │   └── simulation/            # Simulation control
│   │       └── simulator.py
│   │
│   ├── config/                    # Sim configuration
│   ├── tests/
│   ├── setup.py
│   └── README.md
│
├── examples/                      # Usage examples
│   ├── 01_generation_only.py
│   ├── 02_full_simulation.py
│   └── 03_hybrid_usage.py
│
├── docs/                          # Documentation
│   └── ARCHITECTURE.md (this file)
│
└── README.md                      # Main project README
```

## Design Patterns

### 1. Adapter Pattern
**GeneratorAdapter** adapts ContentGenerator for use by SimulationEngine
- Provides clean interface
- Handles path configuration
- Wraps generation methods

### 2. Factory Pattern
**EntityFactory** creates living entities from static data
- `create_npc(data, world)` → LivingNPC
- `create_location(data, world)` → LivingLocation
- `create_world_from_generated(data, world)` → Full world

### 3. Observer Pattern
**EventSystem** implements pub/sub
- Entities publish events
- Systems subscribe to events
- Decoupled communication

### 4. Strategy Pattern
**Entity behaviors** can be customized
- NPCs have different behaviors based on profession
- Easy to extend with new entity types

### 5. Template Method Pattern
**BaseEntity.update()** defines lifecycle
- Subclasses implement specific update logic
- Consistent interface for all entities

## Key Interfaces

### GenerationEngine → SimulationEngine

```python
# GeneratorAdapter provides:
- create_initial_world(num_locations) → dict
- spawn_npc(professions, race, ...) → dict
- spawn_item(template, constraints) → dict
- spawn_location(template, biome, ...) → dict
- generate_quest(...) → dict
- generate_weather(...) → dict
```

### SimulationEngine → User

```python
# World provides:
- create_new(num_locations, seed, name) → World
- step(minutes)
- simulate_hours(hours)
- simulate_days(days)
- save(filename, format)
- load(filename, format) → World
- spawn_npc(location, professions) → LivingNPC
- get_npc(id) → LivingNPC
- get_location(id) → LivingLocation

# WorldSimulator provides:
- simulate_day()
- simulate_hours(hours)
- print_summary()
- print_npc_status()
- print_location_status()
- print_recent_events()
- add_callback(function)
```

## State Management

### World State Structure

```python
{
    "name": "World Name",
    "seed": 42,
    "total_simulation_time": 1440,  # minutes
    "time_manager": {
        "current_year": 1,
        "current_day": 15,
        "current_hour": 14,
        "current_minute": 30,
        "total_minutes": 21270
    },
    "event_system": {
        "queue_size": 0,
        "history_size": 247,
        "recent_events": [...]
    },
    "locations": {
        "loc_id_1": {
            "id": "loc_id_1",
            "data": {...},  # Generated location data
            "npc_ids": ["npc_1", "npc_2"],
            "market_open": true,
            "current_weather": {...}
        }
    },
    "npcs": {
        "npc_id_1": {
            "id": "npc_id_1",
            "data": {...},  # Generated NPC data
            "current_location_id": "loc_id_1",
            "current_activity": "working",
            "energy": 72.5,
            "hunger": 35.2,
            "mood": 68.3,
            ...
        }
    }
}
```

### Serialization Flow

```
Save:
World → to_dict() → StateManager.save_json() → File

Load:
File → StateManager.load_json() → World.from_dict() → World
```

## Extension Points

### Adding New Entity Types

1. Create class extending `BaseEntity`
2. Implement `update(delta_time, world)`
3. Implement `to_dict()` and `from_dict()`
4. Add to `EntityFactory`
5. Add to `World` storage

Example:
```python
class LivingOrganization(BaseEntity):
    def update(self, delta_time, world):
        # Organization behavior
        self.recruit_members()
        self.manage_resources()
```

### Adding New Systems

1. Create system class
2. Add to `World.__init__()`
3. Call from `World.update()`
4. Subscribe to relevant events

Example:
```python
class EconomySystem:
    def __init__(self, world):
        self.world = world
        world.event_system.subscribe("item_traded", self.on_trade)

    def update(self, delta_time):
        self.update_prices()
        self.simulate_trade()
```

### Adding New Behaviors

1. Add methods to existing entity classes
2. Call from `update()` based on conditions
3. Publish events for observability

Example:
```python
class LivingNPC(BaseEntity):
    def start_trading(self):
        self.current_activity = "trading"
        # Trading logic...
```

## Performance Considerations

### Time Complexity

- **World.update()**: O(N + M) where N=NPCs, M=Locations
- **Event processing**: O(E × S) where E=Events, S=Subscribers
- **NPC pathfinding**: O(1) (simple linear travel)

### Space Complexity

- **World state**: O(N + M + E) for entities and event history
- **Event history**: Capped at configurable limit (default 1000)

### Optimization Strategies

1. **Larger time steps** - Update every 30-60 minutes instead of 1
2. **Event batching** - Process events in batches
3. **Spatial partitioning** - Only update nearby entities (future)
4. **Lazy loading** - Load entity data on-demand (future)

## Testing Strategy

### Unit Tests
- Test each system independently
- Mock dependencies
- Test edge cases (time transitions, empty inventories, etc.)

### Integration Tests
- Test GeneratorAdapter ↔ ContentGenerator
- Test EntityFactory conversions
- Test World ↔ Systems interaction

### Simulation Tests
- Run multi-day simulations
- Verify state consistency
- Check for memory leaks
- Performance benchmarking

## Future Enhancements

### Short Term
- [ ] Combat system
- [ ] Economy with supply/demand
- [ ] Advanced AI (behavior trees)
- [ ] More entity types (animals, organizations)

### Medium Term
- [ ] Faction warfare
- [ ] Quest system integration
- [ ] Weather affecting behavior
- [ ] Population dynamics

### Long Term
- [ ] Distributed simulation (multi-threading)
- [ ] Real-time multiplayer support
- [ ] 3D visualization integration
- [ ] Machine learning for NPC AI

## Conclusion

This architecture provides:
- **Clean separation** between generation and simulation
- **Easy extension** via well-defined interfaces
- **Reusability** of both engines independently
- **Scalability** for large worlds
- **Maintainability** through modular design

The two-engine approach allows for:
- Using just GenerationEngine for static content
- Using both for living worlds
- Swapping out either engine independently
- Clear testing boundaries
