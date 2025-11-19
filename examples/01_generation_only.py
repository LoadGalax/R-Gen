#!/usr/bin/env python3
"""
Example 1: Using GenerationEngine Only

This example shows how to use the GenerationEngine to create static content
without running any simulation.
"""

import sys
from pathlib import Path

# Add GenerationEngine to path
sys.path.insert(0, str(Path(__file__).parent.parent / "GenerationEngine"))

from src.content_generator import ContentGenerator


def main():
    print("="*60)
    print("EXAMPLE 1: Generation Engine Only")
    print("="*60)

    # Create generator
    print("\nCreating content generator...")
    gen = ContentGenerator(seed=42)

    # Generate items
    print("\n" + "-"*60)
    print("GENERATING ITEMS")
    print("-"*60)

    weapon = gen.generate_item("weapon_melee")
    print(f"\nWeapon: {weapon['name']}")
    print(f"  Quality: {weapon['quality']}")
    print(f"  Rarity: {weapon['rarity']}")
    print(f"  Value: {weapon['value']} gold")

    potion = gen.generate_item("potion")
    print(f"\nPotion: {potion['name']}")
    print(f"  Description: {potion['description'][:80]}...")

    # Generate NPCs
    print("\n" + "-"*60)
    print("GENERATING NPCs")
    print("-"*60)

    blacksmith = gen.generate_npc("blacksmith")
    print(f"\nBlacksmith: {blacksmith['name']} ({blacksmith['race']})")
    print(f"  Title: {blacksmith['title']}")
    print(f"  Level: {blacksmith['profession_level']}")
    print(f"  Skills: {', '.join(blacksmith['skills'][:3])}...")
    print(f"  Inventory: {len(blacksmith['inventory'])} items")

    merchant = gen.generate_npc("merchant")
    print(f"\nMerchant: {merchant['name']} ({merchant['race']})")
    print(f"  Gold: {merchant.get('gold', 'N/A')}")
    print(f"  Inventory: {len(merchant['inventory'])} items")

    # Generate a world
    print("\n" + "-"*60)
    print("GENERATING WORLD")
    print("-"*60)

    world = gen.generate_world(num_locations=5)
    print(f"\nWorld created with {len(world['locations'])} locations")

    for loc_id, location in list(world['locations'].items())[:3]:
        print(f"\n  Location: {location['name']}")
        print(f"    Type: {location['type']}")
        print(f"    Biome: {location['biome']}")
        print(f"    NPCs: {len(location.get('npcs', []))}")
        print(f"    Connections: {len(location.get('connections', {}))}")

    print("\n" + "="*60)
    print("This is STATIC content - nothing is simulated!")
    print("NPCs don't move, time doesn't pass, markets don't open/close.")
    print("See example 02 for simulation!")
    print("="*60)


if __name__ == "__main__":
    main()
