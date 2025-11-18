#!/usr/bin/env python3
"""
Example script demonstrating the ContentGenerator engine.

This script shows how to:
1. Generate individual items with random properties
2. Generate NPCs with inventories and descriptions
3. Generate locations with connected areas
4. Create a full world with multiple interconnected locations
5. Export generated content to JSON files
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from content_generator import ContentGenerator


def print_separator(title: str = ""):
    """Print a formatted separator line."""
    if title:
        print(f"\n{'=' * 80}")
        print(f"  {title}")
        print('=' * 80)
    else:
        print('-' * 80)


def print_item(item: dict):
    """Pretty print an item."""
    print(f"\n📦 {item['name']}")
    print(f"   Type: {item['type']} ({item['subtype']})")
    print(f"   Quality: {item['quality']} | Rarity: {item['rarity']}")
    print(f"   Value: {item['value']} gold")

    if item.get('material'):
        print(f"   Material: {item['material']}")

    if item.get('damage_types'):
        print(f"   Damage Types: {', '.join(item['damage_types'])}")

    if item['stats']:
        stats_str = ', '.join([f"{k}: {v:+d}" for k, v in item['stats'].items()])
        print(f"   Stats: {stats_str}")

    if item['properties']:
        props_str = ', '.join([k for k, v in item['properties'].items() if v])
        print(f"   Properties: {props_str}")

    print(f"   Description: {item['description']}")


def print_npc(npc: dict, show_inventory: bool = True):
    """Pretty print an NPC."""
    print(f"\n👤 {npc['name']} - {npc['title']}")
    print(f"   Archetype: {npc['archetype']}")

    stats_str = ', '.join([f"{k}: {v}" for k, v in npc['stats'].items()])
    print(f"   Stats: {stats_str}")

    print(f"   Skills: {', '.join(npc['skills'])}")
    print(f"   Dialogue: \"{npc['dialogue']}\"")
    print(f"   Description: {npc['description']}")

    if npc.get('location'):
        print(f"   Location: {npc['location']}")

    if show_inventory and npc.get('inventory'):
        print(f"   Inventory ({len(npc['inventory'])} items):")
        for item in npc['inventory'][:3]:  # Show first 3 items
            print(f"      • {item['name']} ({item['value']} gold)")
        if len(npc['inventory']) > 3:
            print(f"      ... and {len(npc['inventory']) - 3} more items")


def print_location(location: dict, show_details: bool = True):
    """Pretty print a location."""
    print(f"\n🗺️  {location['name']} (ID: {location['id']})")
    print(f"   Type: {location['type']}")
    print(f"   Environment: {', '.join(location['environment_tags'])}")
    print(f"   Description: {location['description']}")

    if location['connections']:
        print(f"   Connections: {len(location['connections'])} areas")
        for conn_type, conn_id in location['connections'].items():
            print(f"      → {conn_type} (ID: {conn_id})")

    print(f"   NPCs: {len(location['npcs'])} | Items: {len(location['items'])}")

    if show_details:
        if location['npcs']:
            print("\n   NPCs in this location:")
            for npc in location['npcs']:
                print(f"      • {npc['name']} ({npc['title']})")

        if location['items']:
            print("\n   Items in this location:")
            for item in location['items'][:5]:  # Show first 5 items
                print(f"      • {item['name']} ({item['value']} gold)")
            if len(location['items']) > 5:
                print(f"      ... and {len(location['items']) - 5} more items")


def example_1_generate_items():
    """Example 1: Generate various types of items."""
    print_separator("Example 1: Generating Items")

    generator = ContentGenerator()

    print("\n🎲 Generating random items...")

    # Generate specific item types
    weapon = generator.generate_item("weapon_melee")
    print_item(weapon)

    armor = generator.generate_item("armor")
    print_item(armor)

    potion = generator.generate_item("potion")
    print_item(potion)

    jewelry = generator.generate_item("jewelry")
    print_item(jewelry)

    # Generate a random item
    print("\n🎲 Generating completely random item...")
    random_item = generator.generate_item()
    print_item(random_item)


def example_2_generate_npcs():
    """Example 2: Generate NPCs with inventories."""
    print_separator("Example 2: Generating NPCs")

    generator = ContentGenerator()

    print("\n🎲 Generating NPCs from different archetypes...")

    # Generate specific archetypes
    blacksmith = generator.generate_npc("blacksmith")
    print_npc(blacksmith)

    merchant = generator.generate_npc("merchant")
    print_npc(merchant)

    mage = generator.generate_npc("mage")
    print_npc(mage)

    # Generate a random NPC
    print("\n🎲 Generating completely random NPC...")
    random_npc = generator.generate_npc()
    print_npc(random_npc)


def example_3_generate_locations():
    """Example 3: Generate locations with NPCs and items."""
    print_separator("Example 3: Generating Locations")

    generator = ContentGenerator()

    print("\n🎲 Generating different types of locations...")

    # Generate specific locations
    tavern = generator.generate_location("tavern", generate_connections=False)
    print_location(tavern)

    forge = generator.generate_location("forge", generate_connections=False)
    print_location(forge)

    cave = generator.generate_location("cave", generate_connections=False)
    print_location(cave)


def example_4_generate_world():
    """Example 4: Generate a connected world."""
    print_separator("Example 4: Generating a Connected World")

    generator = ContentGenerator()

    print("\n🎲 Generating a world with 5 interconnected locations...")

    world = generator.generate_world(num_locations=5)

    print(f"\n🌍 World generated with {len(world['locations'])} total locations!")

    print("\n📊 World Map Summary:")
    for loc_id, summary in world['world_map'].items():
        print(f"\n   {summary['name']} ({summary['type']})")
        print(f"      ID: {loc_id}")
        print(f"      NPCs: {summary['npc_count']} | Items: {summary['item_count']}")
        print(f"      Connections: {len(summary['connections'])}")

    # Show details of one location
    print("\n🔍 Detailed view of first location:")
    first_location = list(world['locations'].values())[0]
    print_location(first_location, show_details=True)

    return world


def example_5_cross_referencing():
    """Example 5: Demonstrate cross-referencing between content."""
    print_separator("Example 5: Cross-Referencing Between Content Types")

    generator = ContentGenerator()

    print("\n🎲 Generating a location with NPCs that have item inventories...")

    # Generate a market location
    market = generator.generate_location("market", generate_connections=False)

    print_location(market, show_details=False)

    # Show NPC details with their inventories
    print("\n👥 NPCs in this location (with inventories):")
    for npc in market['npcs']:
        print_npc(npc, show_inventory=True)


def example_6_export():
    """Example 6: Export generated content to JSON."""
    print_separator("Example 6: Exporting Content to JSON")

    generator = ContentGenerator()

    print("\n🎲 Generating content and exporting to JSON files...")

    # Generate various content
    items = [generator.generate_item() for _ in range(5)]
    npcs = [generator.generate_npc() for _ in range(3)]
    world = generator.generate_world(num_locations=3)

    # Export to files
    generator.export_to_json(items, "output_items.json")
    generator.export_to_json(npcs, "output_npcs.json")
    generator.export_to_json(world, "output_world.json")

    print("\n✅ Content exported successfully!")
    print("   - output_items.json (5 items)")
    print("   - output_npcs.json (3 NPCs)")
    print("   - output_world.json (complete world)")


def main():
    """Run all examples."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                        ContentGenerator Demo                                ║
║                   Dynamic Game Content Generation Engine                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

    try:
        # Run all examples
        example_1_generate_items()
        example_2_generate_npcs()
        example_3_generate_locations()
        example_4_generate_world()
        example_5_cross_referencing()
        example_6_export()

        print_separator("Demo Complete")
        print("\n✨ All examples completed successfully!")
        print("\nCheck the output_*.json files for exported content.")
        print("\nTry modifying the JSON config files in the data/ directory")
        print("to customize the content generation!\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
