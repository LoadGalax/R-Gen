#!/usr/bin/env python3
"""
R-Gen CLI - Command-line interface for the Random Game Content Generator

Usage:
    python cli.py generate-item [--template TEMPLATE] [--count N] [--seed SEED] [--save] [constraints...]
    python cli.py generate-npc [--profession PROFESSION] [--count N] [--seed SEED] [--save]
    python cli.py generate-location [--template TEMPLATE] [--connections] [--seed SEED] [--save]
    python cli.py generate-world --size N [--seed SEED] [--save]
    python cli.py search-items [filters...]
    python cli.py history [--type TYPE] [--limit N]
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

    # Support both old 'archetype' (single) and new 'professions' (list)
    if npc.get('professions') is not None:
        if len(npc['professions']) == 0:
            lines.append(f"{prefix}   Professions: None")
        elif len(npc['professions']) == 1:
            lines.append(f"{prefix}   Profession: {npc['professions'][0]}")
        else:
            lines.append(f"{prefix}   Professions: {', '.join(npc['professions'])}")
    elif npc.get('archetype'):
        # Backward compatibility
        lines.append(f"{prefix}   Profession: {npc['archetype']}")

    if npc.get('race'):
        lines.append(f"{prefix}   Race: {npc['race']}")

    if npc.get('faction'):
        lines.append(f"{prefix}   Faction: {npc['faction']}")

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

    if location.get('biome'):
        lines.append(f"{prefix}   Biome: {location['biome']}")

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
                # Check for NPC (either old 'archetype' or new 'professions')
                if 'archetype' in data[0] or 'professions' in data[0]:
                    output = "\n\n".join([format_npc(npc) for npc in data])
                elif 'environment_tags' in data[0] or 'id' in data[0] and data[0].get('id', '').startswith(('tavern_', 'forge_', 'cave_', 'market_')):
                    output = "\n\n".join([format_location(loc) for loc in data])
                else:
                    output = "\n\n".join([format_item(item) for item in data])
            else:
                output = "No items generated"
        elif isinstance(data, dict):
            # Check for NPC (either old 'archetype' or new 'professions')
            if 'archetype' in data or 'professions' in data:
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


def cmd_generate_item(args, generator, db=None):
    """Generate item(s)"""
    count = args.count if args.count else 1

    # Build constraints
    constraints = {}
    if args.min_quality:
        constraints['min_quality'] = args.min_quality
    if args.max_quality:
        constraints['max_quality'] = args.max_quality
    if args.min_rarity:
        constraints['min_rarity'] = args.min_rarity
    if args.max_rarity:
        constraints['max_rarity'] = args.max_rarity
    if args.min_value:
        constraints['min_value'] = args.min_value
    if args.max_value:
        constraints['max_value'] = args.max_value
    if args.exclude_materials:
        constraints['exclude_materials'] = args.exclude_materials.split(',')
    if args.required_stats:
        constraints['required_stats'] = args.required_stats.split(',')

    if count == 1:
        item = generator.generate_item(args.template, constraints if constraints else None)

        # Save to database if requested
        if args.save and db:
            item_id = db.save_item(item, args.template, constraints if constraints else None, args.seed)
            print(f"💾 Saved to database with ID: {item_id}")

        output_data(item, args.format, args.output)
    else:
        items = []
        for _ in range(count):
            item = generator.generate_item(args.template, constraints if constraints else None)
            items.append(item)

            # Save to database if requested
            if args.save and db:
                db.save_item(item, args.template, constraints if constraints else None, args.seed)

        if args.save and db:
            print(f"💾 Saved {len(items)} items to database")

        output_data(items, args.format, args.output)


def cmd_generate_npc(args, generator, db=None):
    """Generate NPC(s)"""
    count = args.count if args.count else 1

    # Handle professions argument (can be None, empty list, or list of professions)
    profession_names = args.professions if hasattr(args, 'professions') else None

    if count == 1:
        npc = generator.generate_npc(
            profession_names=profession_names,
            race=args.race,
            faction=args.faction
        )

        # Save to database if requested
        if args.save and db:
            # Store professions as comma-separated string for archetype field
            archetype_str = ','.join(npc.get('professions', [])) if npc.get('professions') else None
            npc_id = db.save_npc(npc, archetype_str, args.seed)
            print(f"💾 Saved to database with ID: {npc_id}")

        output_data(npc, args.format, args.output)
    else:
        npcs = []
        for _ in range(count):
            npc = generator.generate_npc(
                profession_names=profession_names,
                race=args.race,
                faction=args.faction
            )
            npcs.append(npc)

            # Save to database if requested
            if args.save and db:
                archetype_str = ','.join(npc.get('professions', [])) if npc.get('professions') else None
                db.save_npc(npc, archetype_str, args.seed)

        if args.save and db:
            print(f"💾 Saved {len(npcs)} NPCs to database")

        output_data(npcs, args.format, args.output)


def cmd_generate_location(args, generator, db=None):
    """Generate location"""
    location = generator.generate_location(
        template_name=args.template,
        generate_connections=args.connections,
        biome=args.biome
    )

    # Save to database if requested
    if args.save and db:
        location_id = db.save_location(location, args.template, args.seed)
        print(f"💾 Saved to database with ID: {location_id}")

    output_data(location, args.format, args.output)


def cmd_generate_world(args, generator, db=None):
    """Generate world"""
    world = generator.generate_world(args.size)

    # Save to database if requested
    if args.save and db:
        world_id = db.save_world(world, args.name, args.seed)
        print(f"💾 Saved to database with ID: {world_id}")

    output_data(world, args.format, args.output)


def cmd_search_items(args, db):
    """Search items in database"""
    filters = {}
    if args.type:
        filters['type'] = args.type
    if args.quality:
        filters['quality'] = args.quality
    if args.rarity:
        filters['rarity'] = args.rarity
    if args.min_value:
        filters['min_value'] = args.min_value
    if args.max_value:
        filters['max_value'] = args.max_value
    if args.material:
        filters['material'] = args.material

    items = db.search_items(filters, args.limit)

    if items:
        print(f"🔍 Found {len(items)} items:\n")
        output_data(items, args.format, None)
    else:
        print("No items found matching the criteria")


def cmd_history(args, db):
    """View generation history"""
    history = db.get_history(args.type, args.limit)

    if history:
        print(f"📜 Generation History ({len(history)} records):\n")
        for record in history:
            print(f"ID: {record['id']} | Type: {record['content_type']} | Content ID: {record['content_id']}")
            if record.get('template_name'):
                print(f"  Template: {record['template_name']}")
            if record.get('seed'):
                print(f"  Seed: {record['seed']}")
            print(f"  Created: {record['created_at']}")
            if record.get('constraints'):
                print(f"  Constraints: {json.dumps(record['constraints'])}")
            print()
    else:
        print("No history records found")


def cmd_get_item(args, db):
    """Get item by ID"""
    item = db.get_item(args.id)
    if item:
        output_data(item, args.format, None)
    else:
        print(f"Item with ID {args.id} not found")


def cmd_get_npc(args, db):
    """Get NPC by ID"""
    npc = db.get_npc(args.id)
    if npc:
        output_data(npc, args.format, None)
    else:
        print(f"NPC with ID {args.id} not found")


def cmd_get_location(args, db):
    """Get location by ID"""
    location = db.get_location(args.id)
    if location:
        output_data(location, args.format, None)
    else:
        print(f"Location with ID {args.id} not found")


def cmd_get_world(args, db):
    """Get world by ID"""
    world = db.get_world(args.id)
    if world:
        output_data(world, args.format, None)
    else:
        print(f"World with ID {args.id} not found")


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

    print("\nNPC Professions:")
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


def cmd_list_races(args, generator):
    """List available races"""
    print("🧬 Available Races\n")
    for race_id, race_data in generator.races_config['races'].items():
        print(f"  • {race_data['name']} ({race_id})")
        print(f"    Size: {race_data['size']}, Lifespan: {race_data['lifespan']['min']}-{race_data['lifespan']['max']} years")
        print(f"    Traits: {', '.join(race_data['traits'])}")
        print()


def cmd_list_factions(args, generator):
    """List available factions"""
    print("⚔️  Available Factions\n")
    for faction_id, faction_data in generator.factions_config['factions'].items():
        print(f"  • {faction_data['name']} ({faction_id})")
        print(f"    Type: {faction_data['type']}, Alignment: {faction_data['alignment']}")
        print(f"    {faction_data['description']}")
        print()


def cmd_list_biomes(args, generator):
    """List available biomes"""
    print("🌍 Available Biomes\n")
    for biome_id, biome_data in generator.biomes_config['biomes'].items():
        print(f"  • {biome_data['name']} ({biome_id})")
        print(f"    Climate: {biome_data['climate']}, Terrain: {biome_data['terrain']}")
        print(f"    Danger Level: {biome_data['danger_level']}")
        print(f"    {biome_data['description']}")
        print()


def cmd_list_professions(args, generator):
    """List available professions (archetypes)"""
    print("👨‍💼 Available Professions\n")

    # Show profession levels first
    if 'profession_levels' in generator.npcs_config:
        print("📊 Profession Levels:")
        for level_id, level_data in generator.npcs_config['profession_levels'].items():
            print(f"  • {level_data['title']} (Rank {level_data['rank']})")
            print(f"    Stat Multiplier: {level_data['stat_multiplier']}x, Skill Bonus: +{level_data['skill_bonus']}")
            print(f"    {level_data['description']}")
            print()
        print("\n" + "="*60 + "\n")

    # Show all professions
    print("🎭 All Professions:\n")
    for archetype_id, archetype_data in generator.npcs_config['archetypes'].items():
        print(f"  • {archetype_data['title']} ({archetype_id})")
        print(f"    Skills: {', '.join(archetype_data['skills'])}")
        print(f"    Races: {', '.join(archetype_data.get('possible_races', ['any']))}")
        print(f"    Factions: {', '.join(archetype_data.get('possible_factions', ['any']))}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='R-Gen - Random Game Content Generator CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic generation
  %(prog)s generate-item --template weapon_melee
  %(prog)s generate-npc --profession blacksmith

  # With seed for reproducibility
  %(prog)s generate-item --template weapon_melee --seed 42

  # With constraints
  %(prog)s generate-item --template weapon_melee --min-quality Excellent --min-rarity Rare --min-value 500

  # Save to database
  %(prog)s generate-item --template weapon_melee --save

  # Multiple items
  %(prog)s generate-item --count 10 --save

  # Search database
  %(prog)s search-items --rarity Legendary --min-value 1000

  # View history
  %(prog)s history --type item --limit 50

  # Retrieve by ID
  %(prog)s get-item 1
        """
    )

    parser.add_argument('--data-dir', default='data',
                        help='Path to data directory (default: data)')
    parser.add_argument('--db', default='r_gen.db',
                        help='Database file path (default: r_gen.db)')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Generate item command
    item_parser = subparsers.add_parser('generate-item', help='Generate random item(s)')
    item_parser.add_argument('--template', help='Item template name (e.g., weapon_melee, armor, potion)')
    item_parser.add_argument('--count', type=int, help='Number of items to generate')
    item_parser.add_argument('--seed', type=int, help='Random seed for reproducible generation')
    item_parser.add_argument('--save', action='store_true', help='Save to database')

    # Constraint options
    item_parser.add_argument('--min-quality', help='Minimum quality (e.g., Poor, Standard, Fine, Excellent, Masterwork, Legendary)')
    item_parser.add_argument('--max-quality', help='Maximum quality')
    item_parser.add_argument('--min-rarity', help='Minimum rarity (e.g., Common, Uncommon, Rare, Epic, Legendary, Mythic)')
    item_parser.add_argument('--max-rarity', help='Maximum rarity')
    item_parser.add_argument('--min-value', type=int, help='Minimum gold value')
    item_parser.add_argument('--max-value', type=int, help='Maximum gold value')
    item_parser.add_argument('--exclude-materials', help='Comma-separated list of materials to exclude')
    item_parser.add_argument('--required-stats', help='Comma-separated list of required stats')

    item_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                             help='Output format (default: text)')
    item_parser.add_argument('--output', help='Output file path')

    # Generate NPC command
    npc_parser = subparsers.add_parser('generate-npc', help='Generate random NPC(s)')
    npc_parser.add_argument('--profession', '--professions', '--archetype', dest='professions',
                            nargs='*',
                            help='NPC profession(s) (e.g., blacksmith, merchant). Can specify multiple. Use empty list for no professions.')
    npc_parser.add_argument('--race', help='Specific race (e.g., human, dwarf, elf)')
    npc_parser.add_argument('--faction', help='Specific faction (e.g., kingdom_of_valor, merchants_guild)')
    npc_parser.add_argument('--count', type=int, help='Number of NPCs to generate')
    npc_parser.add_argument('--seed', type=int, help='Random seed for reproducible generation')
    npc_parser.add_argument('--save', action='store_true', help='Save to database')
    npc_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                            help='Output format (default: text)')
    npc_parser.add_argument('--output', help='Output file path')

    # Generate location command
    location_parser = subparsers.add_parser('generate-location', help='Generate random location')
    location_parser.add_argument('--template', help='Location template (e.g., tavern, forge, cave)')
    location_parser.add_argument('--biome', help='Specific biome (e.g., urban, temperate_forest, mountains)')
    location_parser.add_argument('--connections', action='store_true',
                                 help='Generate connected locations')
    location_parser.add_argument('--seed', type=int, help='Random seed for reproducible generation')
    location_parser.add_argument('--save', action='store_true', help='Save to database')
    location_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                                 help='Output format (default: text)')
    location_parser.add_argument('--output', help='Output file path')

    # Generate world command
    world_parser = subparsers.add_parser('generate-world', help='Generate complete world')
    world_parser.add_argument('--size', type=int, required=True,
                              help='Number of locations in the world')
    world_parser.add_argument('--name', help='Name for the world')
    world_parser.add_argument('--seed', type=int, help='Random seed for reproducible generation')
    world_parser.add_argument('--save', action='store_true', help='Save to database')
    world_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                              help='Output format (default: text)')
    world_parser.add_argument('--output', help='Output file path')

    # Search items command
    search_parser = subparsers.add_parser('search-items', help='Search items in database')
    search_parser.add_argument('--type', help='Item type filter')
    search_parser.add_argument('--quality', help='Quality filter')
    search_parser.add_argument('--rarity', help='Rarity filter')
    search_parser.add_argument('--min-value', type=int, help='Minimum value filter')
    search_parser.add_argument('--max-value', type=int, help='Maximum value filter')
    search_parser.add_argument('--material', help='Material filter')
    search_parser.add_argument('--limit', type=int, default=100, help='Maximum results (default: 100)')
    search_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                               help='Output format (default: text)')

    # History command
    history_parser = subparsers.add_parser('history', help='View generation history')
    history_parser.add_argument('--type', help='Filter by content type (item, npc, location, world)')
    history_parser.add_argument('--limit', type=int, default=100, help='Maximum records (default: 100)')

    # Get item command
    get_item_parser = subparsers.add_parser('get-item', help='Get item by ID')
    get_item_parser.add_argument('id', type=int, help='Item ID')
    get_item_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                                 help='Output format (default: text)')

    # Get NPC command
    get_npc_parser = subparsers.add_parser('get-npc', help='Get NPC by ID')
    get_npc_parser.add_argument('id', type=int, help='NPC ID')
    get_npc_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                                help='Output format (default: text)')

    # Get location command
    get_location_parser = subparsers.add_parser('get-location', help='Get location by ID')
    get_location_parser.add_argument('id', type=int, help='Location ID')
    get_location_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                                     help='Output format (default: text)')

    # Get world command
    get_world_parser = subparsers.add_parser('get-world', help='Get world by ID')
    get_world_parser.add_argument('id', type=int, help='World ID')
    get_world_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                                  help='Output format (default: text)')

    # List templates command
    list_parser = subparsers.add_parser('list-templates', help='List all available templates')

    # List races command
    races_parser = subparsers.add_parser('list-races', help='List all available races')

    # List factions command
    factions_parser = subparsers.add_parser('list-factions', help='List all available factions')

    # List biomes command
    biomes_parser = subparsers.add_parser('list-biomes', help='List all available biomes')

    # List professions command
    professions_parser = subparsers.add_parser('list-professions', help='List all available professions and profession levels')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        # Initialize database if needed
        db = None
        if args.command in ['generate-item', 'generate-npc', 'generate-location', 'generate-world'] and hasattr(args, 'save') and args.save:
            from src.database import DatabaseManager
            db = DatabaseManager(args.db)
            print(f"💾 Database: {args.db}")
        elif args.command in ['search-items', 'history', 'get-item', 'get-npc', 'get-location', 'get-world']:
            from src.database import DatabaseManager
            db = DatabaseManager(args.db)

        # Initialize generator with seed if provided
        seed = getattr(args, 'seed', None)
        if seed:
            print(f"🌱 Using seed: {seed}")
        generator = ContentGenerator(data_dir=args.data_dir, seed=seed)

        # Execute command
        if args.command == 'generate-item':
            cmd_generate_item(args, generator, db)
        elif args.command == 'generate-npc':
            cmd_generate_npc(args, generator, db)
        elif args.command == 'generate-location':
            cmd_generate_location(args, generator, db)
        elif args.command == 'generate-world':
            cmd_generate_world(args, generator, db)
        elif args.command == 'search-items':
            cmd_search_items(args, db)
        elif args.command == 'history':
            cmd_history(args, db)
        elif args.command == 'get-item':
            cmd_get_item(args, db)
        elif args.command == 'get-npc':
            cmd_get_npc(args, db)
        elif args.command == 'get-location':
            cmd_get_location(args, db)
        elif args.command == 'get-world':
            cmd_get_world(args, db)
        elif args.command == 'list-templates':
            cmd_list_templates(args, generator)
        elif args.command == 'list-races':
            cmd_list_races(args, generator)
        elif args.command == 'list-factions':
            cmd_list_factions(args, generator)
        elif args.command == 'list-biomes':
            cmd_list_biomes(args, generator)
        elif args.command == 'list-professions':
            cmd_list_professions(args, generator)

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
