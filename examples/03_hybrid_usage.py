#!/usr/bin/env python3
"""
Example 3: Hybrid Usage

This example shows how to use GenerationEngine and SimulationEngine together,
generating content on-demand during simulation.
"""

import sys
from pathlib import Path

# Add both engines to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "GenerationEngine"))
sys.path.insert(0, str(project_root / "SimulationEngine"))

# Import from engines
from src.content_generator import ContentGenerator
from src.core.world import World
from src.simulation.simulator import WorldSimulator


def main():
    print("="*60)
    print("EXAMPLE 3: Hybrid Usage")
    print("="*60)

    # First, use GenerationEngine to create initial content
    print("\nPhase 1: Static Generation")
    print("-"*40)

    gen = ContentGenerator(seed=42)

    # Generate some starting items
    starting_weapons = [gen.generate_item("weapon_melee") for _ in range(3)]
    starting_potions = [gen.generate_item("consumable") for _ in range(5)]

    print(f"Pre-generated {len(starting_weapons)} weapons and {len(starting_potions)} potions")

    # Generate initial NPCs
    starting_npcs = [
        gen.generate_npc("blacksmith"),
        gen.generate_npc("merchant"),
        gen.generate_npc("innkeeper"),
    ]

    print(f"Pre-generated {len(starting_npcs)} NPCs")

    # Now create a simulation world
    print("\nPhase 2: Create Simulation World")
    print("-"*40)

    world = World.create_new(num_locations=6, seed=42, name="Hybrid World")
    simulator = WorldSimulator(world)

    print(f"Created world with {len(world.locations)} locations and {len(world.npcs)} NPCs")

    # Simulate for a while
    print("\nPhase 3: Initial Simulation")
    print("-"*40)

    simulator.simulate_hours(2, minutes_per_step=30)
    simulator.print_summary()

    # During simulation, generate content on-demand
    print("\nPhase 4: Dynamic Content Generation During Simulation")
    print("-"*40)

    # Find a blacksmith NPC
    blacksmith = None
    for npc in world.npcs.values():
        if "blacksmith" in npc.get_profession().lower():
            blacksmith = npc
            break

    if blacksmith:
        print(f"\nFound blacksmith: {blacksmith.get_name()}")
        print(f"Current inventory: {len(blacksmith.data.get('inventory', []))} items")

        # Blacksmith crafts items during simulation (happens automatically in update)
        # But we can also manually generate items and add them
        print("\nManually crafting a legendary weapon...")
        legendary_weapon = gen.generate_item(
            "weapon_melee",
            constraints={"quality_min": "Legendary"}
        )

        blacksmith.data.setdefault("inventory", []).append(legendary_weapon)
        print(f"Crafted: {legendary_weapon['name']}")
        print(f"  Quality: {legendary_weapon['quality']}")
        print(f"  Rarity: {legendary_weapon['rarity']}")
        print(f"  Value: {legendary_weapon['value']} gold")

    # Generate a quest on-the-fly
    print("\nGenerating quest during simulation...")
    quest = gen.generate_quest_advanced(quest_type="fetch", difficulty=3)

    print(f"\nNew Quest: {quest['title']}")
    print(f"  Type: {quest['quest_type']}")
    print(f"  Difficulty: {quest['difficulty']}")
    print(f"  Objective: {quest['objective'][:80]}...")

    # Spawn new NPC dynamically
    print("\nSpawning new NPC during simulation...")
    location_id = list(world.locations.keys())[0]
    new_npc = world.spawn_npc(location_id, professions=["alchemist"])

    print(f"Spawned: {new_npc.get_name()}")

    # Continue simulation
    print("\nPhase 5: Continue Simulation")
    print("-"*40)

    simulator.simulate_hours(4, minutes_per_step=60)

    # Final summary
    print("\n" + "="*60)
    print("FINAL STATE")
    print("="*60)

    simulator.print_summary()
    simulator.print_npc_status(limit=6)
    simulator.print_recent_events(limit=10)

    print("\n" + "="*60)
    print("HYBRID USAGE DEMONSTRATED!")
    print("="*60)
    print("\nWhat we did:")
    print("  1. Used GenerationEngine to create initial static content")
    print("  2. Created SimulationEngine world from generated data")
    print("  3. Ran simulation with time, events, and NPC behaviors")
    print("  4. Generated NEW content during simulation (quest, items)")
    print("  5. Dynamically spawned NPCs during simulation")
    print("  6. NPCs automatically crafted items while working")
    print("\nThis hybrid approach gives you:")
    print("  - Rich procedural content (GenerationEngine)")
    print("  - Living, dynamic world (SimulationEngine)")
    print("  - On-demand content generation")
    print("  - Seamless integration between static and dynamic")
    print("="*60)


if __name__ == "__main__":
    main()
