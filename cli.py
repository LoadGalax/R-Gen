#!/usr/bin/env python3
"""
R-Gen CLI - Command-line interface for the Random Game Content Generator

Usage:
    python cli.py generate-item [--template TEMPLATE] [--count N] [--format FORMAT] [--output FILE]
    python cli.py generate-npc [--archetype ARCHETYPE] [--count N] [--format FORMAT] [--output FILE]
    python cli.py generate-location [--template TEMPLATE] [--connections] [--format FORMAT] [--output FILE]
    python cli.py generate-world --size N [--format FORMAT] [--output FILE]
    python cli.py list-templates
"""

import argparse
import json
import sys
from pathlib import Path
from src.content_generator import ContentGenerator


def format_item(item, indent=0):
    """Format an item for human-readable output"""
    prefix = "  " * indent
    lines = []
    lines.append(f"{prefix}📦 {item['name']}")
    lines.append(f"{prefix}   Type: {item['type']}")

    # Quality and rarity are optional
    quality_rarity = []
    if item.get('quality'):
        quality_rarity.append(f"Quality: {item['quality']}")
    if item.get('rarity'):
        quality_rarity.append(f"Rarity: {item['rarity']}")
    if quality_rarity:
        lines.append(f"{prefix}   {' | '.join(quality_rarity)}")

    if item.get('material'):
        lines.append(f"{prefix}   Material: {item['material']}")

    if item.get('value') is not None:
        lines.append(f"{prefix}   Value: {item['value']} gold")

    if item.get('stats') and len(item['stats']) > 0:
        lines.append(f"{prefix}   Stats: {', '.join([f'{k}+{v}' for k, v in item['stats'].items()])}")

    if item.get('damage_types'):
        lines.append(f"{prefix}   Damage: {', '.join(item['damage_types'])}")

    if item.get('description'):
        lines.append(f"{prefix}   Description: {item['description']}")

    return "\n".join(lines)


def format_npc(npc, indent=0):
    """Format an NPC for human-readable output"""
    prefix = "  " * indent
    lines = []
    lines.append(f"{prefix}👤 {npc['name']}")

    if npc.get('title'):
        lines.append(f"{prefix}   Title: {npc['title']}")

    lines.append(f"{prefix}   Archetype: {npc['archetype']}")

    if npc.get('stats'):
        stat_str = ', '.join([f"{k}: {v}" for k, v in npc['stats'].items()])
        lines.append(f"{prefix}   Stats: {stat_str}")

    if npc.get('skills'):
        lines.append(f"{prefix}   Skills: {', '.join(npc['skills'])}")

    lines.append(f"{prefix}   Description: {npc['description']}")

    if npc.get('dialogue'):
        lines.append(f"{prefix}   Dialogue: \"{npc['dialogue']}\"")

    if npc.get('inventory'):
        lines.append(f"{prefix}   Inventory ({len(npc['inventory'])} items):")
        for item in npc['inventory']:
            item_lines = format_item(item, indent + 2)
            lines.append(item_lines)

    return "\n".join(lines)


def format_location(location, indent=0):
    """Format a location for human-readable output"""
    prefix = "  " * indent
    lines = []
    lines.append(f"{prefix}🗺️  {location['name']} (ID: {location['id']})")
    lines.append(f"{prefix}   Type: {location['type']}")

    if location.get('environment_tags'):
        lines.append(f"{prefix}   Environment: {', '.join(location['environment_tags'])}")

    lines.append(f"{prefix}   Description: {location['description']}")

    if location.get('npcs'):
        lines.append(f"{prefix}   NPCs ({len(location['npcs'])}):")
        for npc in location['npcs']:
            npc_lines = format_npc(npc, indent + 2)
            lines.append(npc_lines)

    if location.get('items'):
        lines.append(f"{prefix}   Items ({len(location['items'])}):")
        for item in location['items']:
            item_lines = format_item(item, indent + 2)
            lines.append(item_lines)

    if location.get('connections'):
        lines.append(f"{prefix}   Connections: {', '.join(location['connections'])}")

    return "\n".join(lines)


def format_world(world):
    """Format a world for human-readable output"""
    lines = []
    lines.append("🌍 Generated World")
    lines.append("=" * 60)

    # Handle both dict and list formats for locations
    locations = world['locations']
    if isinstance(locations, dict):
        locations = list(locations.values())

    lines.append(f"Total Locations: {len(locations)}")
    lines.append("")

    for location in locations:
        lines.append(format_location(location))
        lines.append("")

    return "\n".join(lines)


def output_data(data, format_type, output_file=None):
    """Output data in the specified format"""
    if format_type == 'json':
        output = json.dumps(data, indent=2)
    elif format_type == 'pretty':
        output = json.dumps(data, indent=2)
    elif format_type == 'text':
        # Human-readable format
        if isinstance(data, list):
            if len(data) > 0:
                if 'archetype' in data[0]:
                    output = "\n\n".join([format_npc(npc) for npc in data])
                elif 'environment_tags' in data[0] or 'id' in data[0] and data[0].get('id', '').startswith(('tavern_', 'forge_', 'cave_', 'market_')):
                    output = "\n\n".join([format_location(loc) for loc in data])
                else:
                    output = "\n\n".join([format_item(item) for item in data])
            else:
                output = "No items generated"
        elif isinstance(data, dict):
            if 'archetype' in data:
                output = format_npc(data)
            elif 'environment_tags' in data or ('id' in data and isinstance(data.get('id'), str) and '_' in data.get('id', '')):
                output = format_location(data)
            elif 'locations' in data:
                output = format_world(data)
            else:
                output = format_item(data)
        else:
            output = str(data)
    else:
        output = str(data)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"✅ Output saved to: {output_file}")
    else:
        print(output)


def cmd_generate_item(args, generator):
    """Generate item(s)"""
    count = args.count if args.count else 1

    if count == 1:
        item = generator.generate_item(args.template)
        output_data(item, args.format, args.output)
    else:
        items = [generator.generate_item(args.template) for _ in range(count)]
        output_data(items, args.format, args.output)


def cmd_generate_npc(args, generator):
    """Generate NPC(s)"""
    count = args.count if args.count else 1

    if count == 1:
        npc = generator.generate_npc(args.archetype)
        output_data(npc, args.format, args.output)
    else:
        npcs = [generator.generate_npc(args.archetype) for _ in range(count)]
        output_data(npcs, args.format, args.output)


def cmd_generate_location(args, generator):
    """Generate location"""
    location = generator.generate_location(args.template, args.connections)
    output_data(location, args.format, args.output)


def cmd_generate_world(args, generator):
    """Generate world"""
    world = generator.generate_world(args.size)
    output_data(world, args.format, args.output)


def cmd_list_templates(args, generator):
    """List available templates"""
    print("📋 Available Templates\n")

    print("Item Templates:")
    if 'templates' in generator.items_config:
        for template in generator.items_config['templates'].keys():
            print(f"  • {template}")
    else:
        for template in generator.items_config.keys():
            print(f"  • {template}")

    print("\nItem Sets:")
    if 'item_sets' in generator.items_config:
        for item_set in generator.items_config['item_sets'].keys():
            print(f"  • {item_set}")

    print("\nNPC Archetypes:")
    if 'archetypes' in generator.npcs_config:
        for archetype in generator.npcs_config['archetypes'].keys():
            print(f"  • {archetype}")
    else:
        for archetype in generator.npcs_config.keys():
            print(f"  • {archetype}")

    print("\nLocation Templates:")
    if 'templates' in generator.locations_config:
        for template in generator.locations_config['templates'].keys():
            print(f"  • {template}")
    else:
        for template in generator.locations_config.keys():
            print(f"  • {template}")


def main():
    parser = argparse.ArgumentParser(
        description='R-Gen - Random Game Content Generator CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate-item --template weapon_melee
  %(prog)s generate-item --count 5 --format text
  %(prog)s generate-npc --archetype blacksmith --format text
  %(prog)s generate-location --template tavern --connections
  %(prog)s generate-world --size 10 --output world.json
  %(prog)s list-templates
        """
    )

    parser.add_argument('--data-dir', default='data',
                        help='Path to data directory (default: data)')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Generate item command
    item_parser = subparsers.add_parser('generate-item', help='Generate random item(s)')
    item_parser.add_argument('--template', help='Item template name (e.g., weapon_melee, armor, potion)')
    item_parser.add_argument('--count', type=int, help='Number of items to generate')
    item_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                             help='Output format (default: text)')
    item_parser.add_argument('--output', help='Output file path')

    # Generate NPC command
    npc_parser = subparsers.add_parser('generate-npc', help='Generate random NPC(s)')
    npc_parser.add_argument('--archetype', help='NPC archetype (e.g., blacksmith, merchant, guard)')
    npc_parser.add_argument('--count', type=int, help='Number of NPCs to generate')
    npc_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                            help='Output format (default: text)')
    npc_parser.add_argument('--output', help='Output file path')

    # Generate location command
    location_parser = subparsers.add_parser('generate-location', help='Generate random location')
    location_parser.add_argument('--template', help='Location template (e.g., tavern, forge, cave)')
    location_parser.add_argument('--connections', action='store_true',
                                 help='Generate connected locations')
    location_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                                 help='Output format (default: text)')
    location_parser.add_argument('--output', help='Output file path')

    # Generate world command
    world_parser = subparsers.add_parser('generate-world', help='Generate complete world')
    world_parser.add_argument('--size', type=int, required=True,
                              help='Number of locations in the world')
    world_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                              help='Output format (default: text)')
    world_parser.add_argument('--output', help='Output file path')

    # List templates command
    list_parser = subparsers.add_parser('list-templates', help='List all available templates')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        # Initialize generator
        generator = ContentGenerator(data_dir=args.data_dir)

        # Execute command
        if args.command == 'generate-item':
            cmd_generate_item(args, generator)
        elif args.command == 'generate-npc':
            cmd_generate_npc(args, generator)
        elif args.command == 'generate-location':
            cmd_generate_location(args, generator)
        elif args.command == 'generate-world':
            cmd_generate_world(args, generator)
        elif args.command == 'list-templates':
            cmd_list_templates(args, generator)

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
