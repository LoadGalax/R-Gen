## R-Gen Simulation Engine

Living world simulation system built on top of R-Gen Generation Engine.

## Overview

The Simulation Engine brings generated content to life by adding:
- **Time Progression** - Day/night cycles, seasons, working hours
- **Entity Behaviors** - NPCs work, eat, sleep, socialize, travel
- **Dynamic Events** - Markets open/close, items crafted, relationships change
- **State Management** - Save/load world state
- **Event System** - Pub/sub event bus for entity interactions
- **Real-time Simulation** - World evolves over time

## Architecture

```
SimulationEngine/
├── src/
│   ├── core/              # Core systems
│   │   ├── world.py              # Main world container
│   │   ├── time_manager.py       # Time progression
│   │   ├── event_system.py       # Event pub/sub
│   │   └── state_manager.py      # Save/load
│   │
│   ├── entities/          # Living entities
│   │   ├── base_entity.py        # Abstract entity
│   │   ├── npc.py                # NPCs with behaviors
│   │   └── location.py           # Dynamic locations
│   │
│   ├── integration/       # GenerationEngine bridge
│   │   ├── generator_adapter.py  # Wraps ContentGenerator
│   │   └── entity_factory.py     # Converts data to entities
│   │
│   └── simulation/        # Simulation control
│       └── simulator.py          # High-level simulator
│
├── config/                # Simulation configuration
├── tests/                 # Test suite
└── examples/              # Usage examples
```

## Installation

```bash
# First install GenerationEngine
cd ../GenerationEngine
pip install -e .

# Then install SimulationEngine
cd ../SimulationEngine
pip install -e .
```

## Quick Start

### Basic Simulation

```python
from SimulationEngine.src.core.world import World
from SimulationEngine.src.simulation.simulator import WorldSimulator

# Create a new world (uses GenerationEngine internally)
world = World.create_new(num_locations=10, seed=42, name="My World")

# Create simulator
simulator = WorldSimulator(world)

# Simulate 24 hours
simulator.simulate_day(minutes_per_step=60)

# Check status
simulator.print_summary()
simulator.print_npc_status()
simulator.print_recent_events()
```

### Save and Load

```python
# Save world
world.save("my_world", format="json", compressed=True)

# Load world
loaded_world = World.load("my_world", format="json")

# Continue simulation
simulator = WorldSimulator(loaded_world)
simulator.simulate_hours(12)
```

### Dynamic Content Generation

```python
# Spawn new NPC during simulation
location_id = list(world.locations.keys())[0]
new_npc = world.spawn_npc(location_id, professions=["merchant"])

# Generate content on-demand
quest = world.generator_adapter.generate_quest(difficulty=5)
item = world.generator_adapter.spawn_item("weapon_melee")
```

## Key Features

### Time System
- 360-day year (12 months × 30 days)
- 24-hour days with time periods (night, dawn, morning, etc.)
- 4 seasons
- Time-based events and scheduling

### NPC Behaviors
- **Daily Routines**: Work, eat, sleep based on time of day
- **Needs System**: Energy, hunger, mood affect behavior
- **Profession Activities**: Blacksmiths craft, merchants trade, guards patrol
- **Movement**: NPCs can travel between locations
- **Crafting**: NPCs create items while working
- **Social**: NPCs socialize and build relationships

### Location Dynamics
- **Market Hours**: Markets open/close based on time
- **Weather**: Dynamic weather that changes periodically
- **Population**: Track NPCs present at each location
- **Events**: Location-specific events and activities

### Event System
- Pub/sub event bus
- Event history tracking
- Common events: NPC movement, item crafting, market changes, etc.
- Custom event types supported

### State Persistence
- JSON format (human-readable)
- Pickle format (faster, supports complex objects)
- Compression support
- Autosave functionality
- Version tracking

## Examples

See the `../examples/` directory for complete examples:

1. **01_generation_only.py** - Using GenerationEngine only
2. **02_full_simulation.py** - Complete world simulation
3. **03_hybrid_usage.py** - Combining both engines

Run an example:

```bash
cd examples
python 02_full_simulation.py
```

## API Reference

### World

```python
# Create new world
world = World.create_new(num_locations=10, seed=42, name="My World")

# Step simulation
world.step(minutes=60)  # Advance 1 hour
world.simulate_hours(24)  # Advance 24 hours
world.simulate_days(7)  # Advance 7 days

# Query entities
npc = world.get_npc(npc_id)
location = world.get_location(location_id)
npcs_here = world.get_npcs_at_location(location_id)

# Spawn entities
new_npc = world.spawn_npc(location_id, professions=["blacksmith"])

# Save/load
world.save("savefile")
loaded = World.load("savefile")
```

### WorldSimulator

```python
simulator = WorldSimulator(world)

# Simulate
simulator.step(minutes=1)
simulator.simulate_hours(hours=24)
simulator.simulate_days(days=7)
simulator.simulate_day()  # One full day

# Status
simulator.print_summary()
simulator.print_npc_status(limit=10)
simulator.print_location_status(limit=10)
simulator.print_recent_events(limit=20)

# Callbacks
def on_tick(world):
    print(f"Time: {world.time_manager.get_time_string()}")

simulator.add_callback(on_tick)
```

### TimeManager

```python
tm = world.time_manager

# Current state
print(tm.current_year)
print(tm.current_day)  # Day of year (1-360)
print(tm.current_hour)  # 0-23
print(tm.current_time_of_day)  # night, dawn, morning, etc.
print(tm.current_season)  # Spring, Summer, Fall, Winter

# Checks
if tm.is_daytime:
    print("It's daytime!")
if tm.is_working_hours:
    print("Shops are open!")

# Formatted output
print(tm.get_full_datetime_string())
```

### EventSystem

```python
events = world.event_system

# Subscribe to events
def on_npc_move(event):
    print(f"NPC {event.source_id} moved!")

events.subscribe("npc_moved", on_npc_move)

# Publish events
events.publish_event(
    "custom_event",
    source_id="npc_123",
    location_id="tavern_456",
    data={"message": "Hello!"}
)

# Query history
recent = events.get_recent_events(limit=10)
npc_events = events.get_events_by_source("npc_123")
location_events = events.get_events_by_location("tavern_456")
```

## How It Works

### Static Generation → Living Simulation

1. **Generation Phase**
   ```python
   # GenerationEngine creates static data
   world_data = generator.generate_world(10)
   # Returns: {"locations": {...}, "world_map": {...}}
   ```

2. **Conversion Phase**
   ```python
   # EntityFactory converts to living entities
   living_world = World.create_new(10)
   # NPCs become LivingNPC with behaviors
   # Locations become LivingLocation with state
   ```

3. **Simulation Phase**
   ```python
   # World.update() called each tick
   for npc in npcs:
       npc.update(delta_time, world)  # NPCs act
   for location in locations:
       location.update(delta_time, world)  # Locations update
   event_system.process_events()  # Events processed
   ```

### NPC Behavior Example

```python
# NPC's update() method (simplified)
def update(self, delta_time, world):
    # Update needs
    self.energy -= delta_time * 0.1
    self.hunger += delta_time * 0.1

    # Decide action
    if self.energy < 20:
        self.start_sleeping()
    elif self.hunger > 80:
        self.start_eating()
    elif world.time_manager.is_working_hours:
        if "blacksmith" in self.professions:
            self.start_working()
            # Randomly craft items
            if random() < 0.01:
                item = world.generator_adapter.spawn_item("weapon_melee")
                self.inventory.append(item)
```

## Extending the Simulation

### Custom NPC Behaviors

Subclass `LivingNPC`:

```python
from SimulationEngine.src.entities.npc import LivingNPC

class MageNPC(LivingNPC):
    def update(self, delta_time, world):
        super().update(delta_time, world)

        # Custom mage behavior
        if self.energy > 50 and random() < 0.05:
            self.cast_spell()

    def cast_spell(self):
        spell = self.world.generator_adapter.generate_spell()
        self.world.event_system.publish_event(
            "spell_cast",
            source_id=self.id,
            data={"spell": spell}
        )
```

### Custom Events

```python
# Define event types
CUSTOM_EVENT = "guild_formed"

# Subscribe
def on_guild_formed(event):
    print(f"New guild: {event.data['guild_name']}")

world.event_system.subscribe(CUSTOM_EVENT, on_guild_formed)

# Publish
world.event_system.publish_event(
    CUSTOM_EVENT,
    data={"guild_name": "Adventurers Guild"}
)
```

## Performance

- **Recommended**: 1-60 minute steps for real-time feel
- **Fast simulation**: 60-1440 minute steps (1 hour to 1 day)
- **Entities**: Tested with 100+ NPCs, 20+ locations
- **Events**: Event queue processes all queued events each tick
- **Save files**: Compressed JSON ~100KB for medium world

## Roadmap

- [ ] Combat system
- [ ] Economy simulation with supply/demand
- [ ] Faction warfare and diplomacy
- [ ] Weather affecting NPC behavior
- [ ] Population growth/decline
- [ ] Advanced AI with behavior trees
- [ ] Quest system integration
- [ ] Multi-threading for large worlds

## License

See main project LICENSE file.
