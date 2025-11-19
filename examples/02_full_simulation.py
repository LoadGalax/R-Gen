#!/usr/bin/env python3
"""
Example 2: Full World Simulation

This example shows how to use the SimulationEngine to create and run
a living, breathing world with dynamic NPCs and events.
"""

import sys
from pathlib import Path

# Add both engines to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "GenerationEngine"))
sys.path.insert(0, str(project_root / "SimulationEngine"))

from src.core.world import World
from src.simulation.simulator import WorldSimulator


def main():
    print("="*60)
    print("EXAMPLE 2: Full World Simulation")
    print("="*60)

    # Create a new world
    print("\nCreating new world...")
    world = World.create_new(num_locations=8, seed=42, name="Fantasy Realm")

    # Create simulator
    simulator = WorldSimulator(world)

    # Print initial state
    print("\n" + "-"*60)
    print("INITIAL STATE")
    print("-"*60)
    simulator.print_summary()
    simulator.print_npc_status(limit=5)
    simulator.print_location_status(limit=5)

    # Simulate a few hours
    print("\n" + "="*60)
    print("SIMULATING 4 HOURS...")
    print("="*60)

    simulator.simulate_hours(4, minutes_per_step=30)

    # Print state after simulation
    print("\n" + "-"*60)
    print("STATE AFTER 4 HOURS")
    print("-"*60)
    simulator.print_summary()
    simulator.print_npc_status(limit=5)
    simulator.print_recent_events(limit=15)

    # Simulate a full day
    print("\n" + "="*60)
    print("SIMULATING FULL DAY...")
    print("="*60)

    simulator.simulate_day(minutes_per_step=60)

    # Print state after day
    print("\n" + "-"*60)
    print("STATE AFTER ONE DAY")
    print("-"*60)
    simulator.print_summary()
    simulator.print_npc_status(limit=5)
    simulator.print_location_status(limit=5)
    simulator.print_recent_events(limit=20)

    # Spawn a new NPC
    print("\n" + "="*60)
    print("SPAWNING NEW NPC...")
    print("="*60)

    first_location = list(world.locations.keys())[0]
    new_npc = world.spawn_npc(first_location, professions=["merchant"])
    print(f"\nSpawned: {new_npc.get_name()} ({new_npc.get_profession()})")
    print(f"Location: {world.get_location(first_location).get_name()}")

    # Simulate a bit more
    simulator.simulate_hours(2, minutes_per_step=30)

    print("\n" + "-"*60)
    print("FINAL STATE")
    print("-"*60)
    simulator.print_summary()

    # Save world
    print("\n" + "="*60)
    print("SAVING WORLD...")
    print("="*60)

    save_path = world.save("fantasy_realm", format="json", compressed=True)
    print(f"World saved to: {save_path}")

    print("\n" + "="*60)
    print("SIMULATION COMPLETE!")
    print("="*60)
    print("\nKey Differences from Static Generation:")
    print("  - NPCs have energy, hunger, mood that changes over time")
    print("  - NPCs work, eat, sleep based on time of day")
    print("  - Markets open and close based on time")
    print("  - Weather updates periodically")
    print("  - Events are tracked and logged")
    print("  - NPCs can craft items while working")
    print("  - World state can be saved and loaded")
    print("="*60)


if __name__ == "__main__":
    main()
