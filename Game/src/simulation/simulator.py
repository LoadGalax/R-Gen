"""
World Simulator

High-level interface for running simulations.
"""

from typing import Optional, Callable, List
from ..core.world import World


class WorldSimulator:
    """
    High-level simulator for running world simulations.

    Provides convenient methods for:
    - Running simulations with callbacks
    - Scheduled simulation runs
    - Statistics tracking
    - Simulation control (pause, resume, step)
    """

    def __init__(self, world: World):
        """
        Initialize simulator.

        Args:
            world: World instance to simulate
        """
        self.world = world
        self.is_running = False
        self.callbacks = []  # Called each tick
        self.statistics = {
            "ticks": 0,
            "total_minutes_simulated": 0,
            "npcs_spawned": 0,
            "events_processed": 0,
        }

    def add_callback(self, callback: Callable[[World], None]):
        """
        Add callback to be called each simulation tick.

        Args:
            callback: Function that takes World as argument
        """
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[World], None]):
        """Remove callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def step(self, minutes: int = 1):
        """
        Run simulation for specified minutes.

        Args:
            minutes: Number of simulation minutes
        """
        self.world.step(minutes)
        self.statistics["ticks"] += 1
        self.statistics["total_minutes_simulated"] += minutes

        # Call callbacks
        for callback in self.callbacks:
            try:
                callback(self.world)
            except Exception as e:
                print(f"Error in callback: {e}")

    def simulate_hours(self, hours: int, minutes_per_step: int = 60):
        """
        Simulate N hours.

        Args:
            hours: Number of hours to simulate
            minutes_per_step: Minutes to advance per step
        """
        total_minutes = hours * 60
        steps = total_minutes // minutes_per_step

        for i in range(steps):
            self.step(minutes_per_step)

            # Progress update
            if (i + 1) % 10 == 0:
                progress = ((i + 1) / steps) * 100
                print(f"Progress: {progress:.1f}% ({i+1}/{steps} steps)")

    def simulate_days(self, days: int, minutes_per_step: int = 60):
        """
        Simulate N days.

        Args:
            days: Number of days to simulate
            minutes_per_step: Minutes to advance per step
        """
        print(f"Simulating {days} day(s)...")
        self.simulate_hours(days * 24, minutes_per_step)

    def simulate_day(self, minutes_per_step: int = 60):
        """
        Simulate one full day.

        Args:
            minutes_per_step: Minutes to advance per step
        """
        print(f"Simulating day {self.world.time_manager.current_day}...")
        start_day = self.world.time_manager.current_day

        while self.world.time_manager.current_day == start_day:
            self.step(minutes_per_step)

        print(f"Day {start_day} complete. Now: {self.world.time_manager.get_full_datetime_string()}")

    def run_until(self, condition: Callable[[World], bool],
                  max_iterations: int = 10000,
                  minutes_per_step: int = 1):
        """
        Run simulation until condition is met.

        Args:
            condition: Function that returns True when simulation should stop
            max_iterations: Maximum iterations to prevent infinite loops
            minutes_per_step: Minutes per simulation step
        """
        iterations = 0

        while not condition(self.world) and iterations < max_iterations:
            self.step(minutes_per_step)
            iterations += 1

        if iterations >= max_iterations:
            print(f"Warning: Reached max iterations ({max_iterations})")

    def get_statistics(self) -> dict:
        """Get simulation statistics"""
        stats = self.statistics.copy()
        stats["world_summary"] = self.world.get_world_summary()
        return stats

    def print_summary(self):
        """Print simulation summary"""
        summary = self.world.get_world_summary()

        print("\n" + "="*60)
        print(f"WORLD SUMMARY: {summary['name']}")
        print("="*60)
        print(f"Time: {summary['time']}")
        print(f"Simulation Time: {summary['total_simulation_time']:.0f} minutes "
              f"({summary['total_simulation_time']/60:.1f} hours)")
        print(f"\nLocations: {summary['locations']}")
        print(f"NPCs: {summary['npcs']} (Active: {summary['active_npcs']})")
        print(f"Events in Queue: {summary['events_in_queue']}")
        print(f"Recent Events: {summary['recent_events']}")
        print("\nSimulation Statistics:")
        print(f"  Ticks: {self.statistics['ticks']}")
        print(f"  Total Minutes: {self.statistics['total_minutes_simulated']}")
        print("="*60 + "\n")

    def print_npc_status(self, limit: int = 10):
        """
        Print status of NPCs.

        Args:
            limit: Maximum NPCs to show
        """
        print("\n" + "-"*60)
        print(f"NPC STATUS (showing up to {limit})")
        print("-"*60)

        for i, npc in enumerate(list(self.world.npcs.values())[:limit]):
            location = self.world.get_location(npc.current_location_id)
            location_name = location.get_name() if location else "Unknown"

            print(f"\n{i+1}. {npc.get_name()} ({npc.get_profession()})")
            print(f"   Location: {location_name}")
            print(f"   Activity: {npc.current_activity}")
            print(f"   Energy: {npc.energy:.1f} | Hunger: {npc.hunger:.1f} | Mood: {npc.mood:.1f}")
            if npc.destination_location_id:
                dest = self.world.get_location(npc.destination_location_id)
                dest_name = dest.get_name() if dest else "Unknown"
                print(f"   Traveling to: {dest_name} ({npc.travel_progress*100:.0f}%)")

        print("-"*60 + "\n")

    def print_location_status(self, limit: int = 10):
        """
        Print status of locations.

        Args:
            limit: Maximum locations to show
        """
        print("\n" + "-"*60)
        print(f"LOCATION STATUS (showing up to {limit})")
        print("-"*60)

        for i, location in enumerate(list(self.world.locations.values())[:limit]):
            npcs_here = self.world.get_npcs_at_location(location.id)

            print(f"\n{i+1}. {location.get_name()} ({location.get_type()})")
            print(f"   Biome: {location.get_biome()}")
            print(f"   NPCs Present: {len(npcs_here)}")
            if npcs_here:
                npc_names = [npc.get_name() for npc in npcs_here[:3]]
                print(f"   NPCs: {', '.join(npc_names)}" +
                      (f" (+{len(npcs_here)-3} more)" if len(npcs_here) > 3 else ""))
            print(f"   Market Open: {location.market_open}")
            if location.current_weather:
                print(f"   Weather: {location.current_weather.get('condition', 'Clear')}")

        print("-"*60 + "\n")

    def print_recent_events(self, limit: int = 10):
        """
        Print recent events.

        Args:
            limit: Number of events to show
        """
        events = self.world.event_system.get_recent_events(limit)

        print("\n" + "-"*60)
        print(f"RECENT EVENTS (last {limit})")
        print("-"*60)

        for i, event in enumerate(events, 1):
            print(f"{i}. {event.event_type}")
            if event.source_id:
                print(f"   Source: {event.source_id}")
            if event.target_id:
                print(f"   Target: {event.target_id}")
            if event.location_id:
                location = self.world.get_location(event.location_id)
                location_name = location.get_name() if location else event.location_id
                print(f"   Location: {location_name}")
            if event.data:
                print(f"   Data: {event.data}")

        print("-"*60 + "\n")
