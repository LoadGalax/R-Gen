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

    if npc.get('equipment'):
        # Count how many equipment slots are filled
        equipped_count = sum(1 for item in npc['equipment'].values() if item is not None)
        lines.append(f"{prefix}   Equipment ({equipped_count}/11 slots):")

        # Display equipment in a logical order
        slot_order = ['helmet', 'collar', 'chest', 'gloves', 'belt', 'legs', 'boots', 'ring1', 'ring2', 'earring1', 'earring2']
        slot_labels = {
            'helmet': 'Helmet',
            'collar': 'Collar',
            'chest': 'Chest',
            'gloves': 'Gloves',
            'belt': 'Belt',
            'legs': 'Legs',
            'boots': 'Boots',
            'ring1': 'Ring 1',
            'ring2': 'Ring 2',
            'earring1': 'Earring 1',
            'earring2': 'Earring 2'
        }

        for slot in slot_order:
            if slot in npc['equipment']:
                item = npc['equipment'][slot]
                if item is not None:
                    # Format equipped item with slot name
                    lines.append(f"{prefix}     [{slot_labels[slot]}]")
                    item_lines = format_item(item, indent + 3)
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


def format_animal(animal, indent=0):
    """Format an animal for human-readable output"""
    prefix = "  " * indent
    lines = []

    # Icon based on category
    icon = "🦁" if animal.get('category') == 'wild_fauna' else "🐾"
    lines.append(f"{prefix}{icon} {animal['name']}")
    lines.append(f"{prefix}   Species: {animal['species']}")
    lines.append(f"{prefix}   Category: {animal['category'].replace('_', ' ').title()}")
    lines.append(f"{prefix}   Size: {animal.get('size', 'medium').title()}")

    if animal.get('danger_level'):
        lines.append(f"{prefix}   Danger Level: {animal['danger_level'].replace('_', ' ').title()}")

    if animal.get('stats'):
        stat_str = ', '.join([f"{k}: {v}" for k, v in animal['stats'].items()])
        lines.append(f"{prefix}   Stats: {stat_str}")

    if animal.get('loyalty') is not None:
        lines.append(f"{prefix}   Loyalty: {animal['loyalty']}")

    if animal.get('owner'):
        owner_info = f"{animal['owner'].get('name', 'Unknown')}"
        if animal['owner'].get('profession'):
            owner_info += f" ({animal['owner']['profession']})"
        lines.append(f"{prefix}   Owner: {owner_info}")

    if animal.get('habitat'):
        if isinstance(animal['habitat'], list):
            lines.append(f"{prefix}   Habitat: {', '.join(animal['habitat'])}")
        else:
            lines.append(f"{prefix}   Habitat: {animal['habitat']}")

    if animal.get('description'):
        lines.append(f"{prefix}   Description: {animal['description']}")

    return "\n".join(lines)


def format_flora(flora, indent=0):
    """Format flora for human-readable output"""
    prefix = "  " * indent
    lines = []

    # Icon based on category
    icon_map = {
        'trees': '🌳',
        'plants': '🌿',
        'mushrooms': '🍄',
        'crops': '🌾',
        'vines': '🌱'
    }
    icon = icon_map.get(flora.get('category'), '🌿')

    lines.append(f"{prefix}{icon} {flora['name']}")
    lines.append(f"{prefix}   Category: {flora.get('category', 'unknown').title()}")
    lines.append(f"{prefix}   Size: {flora.get('size', 'medium').title()}")
    lines.append(f"{prefix}   Rarity: {flora.get('rarity', 'common').title()}")

    if flora.get('magical'):
        lines.append(f"{prefix}   Magical: Yes ✨")

    if flora.get('uses'):
        lines.append(f"{prefix}   Uses: {', '.join(flora['uses'])}")

    if flora.get('habitat'):
        if isinstance(flora['habitat'], list):
            lines.append(f"{prefix}   Habitat: {', '.join(flora['habitat'])}")
        else:
            lines.append(f"{prefix}   Habitat: {flora['habitat']}")

    if flora.get('description'):
        lines.append(f"{prefix}   Description: {flora['description']}")

    return "\n".join(lines)


def format_market(market, indent=0):
    """Format a market for human-readable output"""
    prefix = "  " * indent
    lines = []
    lines.append(f"{prefix}🏪 Market at {market['location']}")
    lines.append(f"{prefix}   Wealth Level: {market['wealth_level'].title()}")
    lines.append(f"{prefix}   Market Conditions: {market['market_conditions'].title()}")
    lines.append(f"{prefix}   Merchant Count: {market['merchant_count']}")

    if market.get('taxes'):
        lines.append(f"{prefix}   Taxes: Sales Tax {market['taxes']['sales_tax']*100:.1f}%, Tariff {market['taxes']['tariff']*100:.1f}%")

    if market.get('merchants'):
        lines.append(f"{prefix}   Merchants ({len(market['merchants'])}):")
        for idx, merchant in enumerate(market['merchants'][:5]):  # Show first 5
            lines.append(f"{prefix}      {idx+1}. {merchant.get('name', 'Unknown')}")
        if len(market['merchants']) > 5:
            lines.append(f"{prefix}      ... and {len(market['merchants']) - 5} more")

    if market.get('available_goods'):
        lines.append(f"{prefix}   Available Goods ({len(market['available_goods'])}):")
        for idx, good in enumerate(market['available_goods'][:10]):  # Show first 10
            item = good.get('item', {})
            pricing = good.get('pricing', {})
            price = pricing.get('final_price', pricing.get('base_price', item.get('value', 0)))
            lines.append(f"{prefix}      {idx+1}. {item.get('name', 'Unknown')} - {price} gold")
        if len(market['available_goods']) > 10:
            lines.append(f"{prefix}      ... and {len(market['available_goods']) - 10} more")

    if market.get('available_services'):
        lines.append(f"{prefix}   Available Services ({len(market['available_services'])}):")
        for idx, service in enumerate(market['available_services'][:10]):  # Show first 10
            lines.append(f"{prefix}      {idx+1}. {service.get('name', 'Unknown')} ({service.get('type', 'unknown').title()}) - {service.get('base_price', 0)} gold")
        if len(market['available_services']) > 10:
            lines.append(f"{prefix}      ... and {len(market['available_services']) - 10} more")

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
                # Check for Animal
                if 'species' in data[0] and ('danger_level' in data[0] or 'loyalty' in data[0]):
                    output = "\n\n".join([format_animal(animal) for animal in data])
                # Check for Flora
                elif 'species' in data[0] and 'uses' in data[0]:
                    output = "\n\n".join([format_flora(flora) for flora in data])
                # Check for NPC (either old 'archetype' or new 'professions')
                elif 'archetype' in data[0] or 'professions' in data[0]:
                    output = "\n\n".join([format_npc(npc) for npc in data])
                elif 'environment_tags' in data[0] or 'id' in data[0] and data[0].get('id', '').startswith(('tavern_', 'forge_', 'cave_', 'market_')):
                    output = "\n\n".join([format_location(loc) for loc in data])
                else:
                    output = "\n\n".join([format_item(item) for item in data])
            else:
                output = "No items generated"
        elif isinstance(data, dict):
            # Check for Animal
            if 'species' in data and ('danger_level' in data or 'loyalty' in data):
                output = format_animal(data)
            # Check for Flora
            elif 'species' in data and 'uses' in data:
                output = format_flora(data)
            # Check for NPC (either old 'archetype' or new 'professions')
            elif 'archetype' in data or 'professions' in data:
                output = format_npc(data)
            elif 'environment_tags' in data or ('id' in data and isinstance(data.get('id'), str) and '_' in data.get('id', '')):
                output = format_location(data)
            elif 'locations' in data:
                output = format_world(data)
            elif 'merchants' in data and 'available_goods' in data and 'wealth_level' in data:
                output = format_market(data)
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


def cmd_generate_animal(args, generator, db=None):
    """Generate animal(s)"""
    count = args.count if args.count else 1

    if count == 1:
        animal = generator.generate_animal(
            category=args.category,
            species=args.species,
            habitat=args.habitat
        )

        # Save to database if requested
        if args.save and db:
            animal_id = db.save_animal(animal, args.seed)
            print(f"💾 Saved to database with ID: {animal_id}")

        output_data(animal, args.format, args.output)
    else:
        animals = []
        for _ in range(count):
            animal = generator.generate_animal(
                category=args.category,
                species=args.species,
                habitat=args.habitat
            )
            animals.append(animal)

            # Save to database if requested
            if args.save and db:
                db.save_animal(animal, args.seed)

        if args.save and db:
            print(f"💾 Saved {len(animals)} animals to database")

        output_data(animals, args.format, args.output)


def cmd_generate_flora(args, generator, db=None):
    """Generate flora"""
    count = args.count if args.count else 1

    if count == 1:
        flora = generator.generate_flora(
            category=args.category,
            species=args.species,
            habitat=args.habitat
        )

        # Save to database if requested
        if args.save and db:
            flora_id = db.save_flora(flora, args.seed)
            print(f"💾 Saved to database with ID: {flora_id}")

        output_data(flora, args.format, args.output)
    else:
        flora_list = []
        for _ in range(count):
            flora = generator.generate_flora(
                category=args.category,
                species=args.species,
                habitat=args.habitat
            )
            flora_list.append(flora)

            # Save to database if requested
            if args.save and db:
                db.save_flora(flora, args.seed)

        if args.save and db:
            print(f"💾 Saved {len(flora_list)} flora to database")

        output_data(flora_list, args.format, args.output)


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


def cmd_generate_loot(args, generator):
    """Generate loot table"""
    loot = generator.generate_loot_table(
        enemy_type=args.enemy_type,
        difficulty=args.difficulty,
        quantity_range=(args.min_items, args.max_items),
        biome=args.biome
    )
    output_data(loot, args.format, args.output)


def cmd_generate_quest(args, generator):
    """Generate quest"""
    quest = generator.generate_quest(
        quest_type=args.quest_type,
        difficulty=args.difficulty,
        faction=args.faction,
        location_id=args.location
    )
    output_data(quest, args.format, args.output)


def cmd_generate_recipe(args, generator):
    """Generate crafting recipe"""
    output_item = None
    if args.for_item_template:
        output_item = generator.generate_item(args.for_item_template)

    recipe = generator.generate_crafting_recipe(
        output_item=output_item,
        difficulty=args.difficulty
    )
    output_data(recipe, args.format, args.output)


def cmd_generate_encounter(args, generator):
    """Generate encounter"""
    encounter = generator.generate_encounter(
        party_level=args.party_level,
        biome=args.biome,
        faction=args.faction,
        encounter_type=args.encounter_type
    )
    output_data(encounter, args.format, args.output)


def cmd_generate_item_with_modifiers(args, generator):
    """Generate item with modifiers"""
    item = generator.generate_item_with_modifiers(
        template_name=args.template,
        num_modifiers=args.num_modifiers
    )
    output_data(item, args.format, args.output)


def cmd_generate_item_set(args, generator):
    """Generate item set collection"""
    item_set = generator.generate_item_set_collection(
        set_name=args.set_name,
        set_size=args.set_size
    )
    output_data(item_set, args.format, args.output)


def cmd_generate_batch(args, generator):
    """Generate batch content with distribution"""
    distribution = None
    if args.distribution:
        # Parse distribution like "Common:0.5,Rare:0.3,Epic:0.2"
        distribution = {}
        for pair in args.distribution.split(','):
            key, val = pair.split(':')
            distribution[key.strip()] = float(val.strip())

    batch = generator.generate_batch_with_distribution(
        content_type=args.content_type,
        count=args.count,
        distribution=distribution
    )
    output_data(batch, args.format, args.output)


def cmd_generate_weather(args, generator):
    """Generate weather and time"""
    weather = generator.generate_weather_and_time(biome=args.biome)
    output_data(weather, args.format, args.output)


def cmd_generate_trap(args, generator):
    """Generate trap or puzzle"""
    trap = generator.generate_trap_or_puzzle(
        difficulty=args.difficulty,
        trap_type=args.trap_type
    )
    output_data(trap, args.format, args.output)


def cmd_generate_procedural_name(args, generator):
    """Generate procedural name"""
    name = generator.generate_procedural_name(
        race=args.race,
        gender=args.gender
    )
    print(f"Generated name: {name}")


def cmd_validate_thematic(args, generator):
    """Validate thematic consistency"""
    # Load item from JSON if provided
    if args.item_json:
        with open(args.item_json, 'r') as f:
            item = json.load(f)
    else:
        # Generate a random item
        item = generator.generate_item()

    validation = generator.validate_thematic_consistency(item, biome=args.biome)
    output_data(validation, args.format, args.output)


def cmd_export(args, generator):
    """Export data to various formats"""
    # Load data from input file
    with open(args.input, 'r') as f:
        data = json.load(f)

    # Export to requested format
    if args.export_format == 'xml':
        generator.export_to_xml(data, args.output)
    elif args.export_format == 'csv':
        generator.export_to_csv(data, args.output)
    elif args.export_format == 'sql':
        generator.export_to_sql(data, args.output, table_name=args.table_name or "game_content")
    elif args.export_format == 'markdown':
        generator.export_to_markdown(data, args.output, title=args.title or "Generated Content")
    else:  # json
        generator.export_to_json(data, args.output)


def cmd_generate_spell(args, generator):
    """Generate spell"""
    spell = generator.generate_spell(
        spell_level=args.spell_level,
        school=args.school,
        spell_template=args.spell_template
    )
    output_data(spell, args.format, args.output)


def cmd_generate_spellbook(args, generator):
    """Generate spellbook"""
    spellbook = generator.generate_spellbook(
        caster_level=args.caster_level,
        school_preference=args.school_preference
    )
    output_data(spellbook, args.format, args.output)


def cmd_generate_organization(args, generator):
    """Generate organization"""
    organization = generator.generate_organization(
        org_type=args.org_type,
        faction=args.faction,
        size=args.size
    )
    output_data(organization, args.format, args.output)


def cmd_generate_weather_detailed(args, generator):
    """Generate detailed weather"""
    weather = generator.generate_weather_detailed(
        biome=args.biome,
        season=args.season,
        time_of_day=args.time_of_day
    )
    output_data(weather, args.format, args.output)


def cmd_generate_market(args, generator):
    """Generate market"""
    location = None
    if args.location_id:
        # Try to load location from database if ID provided
        # For now, just pass None
        pass

    market = generator.generate_market(
        location=location,
        wealth_level=args.wealth_level
    )
    output_data(market, args.format, args.output)


def cmd_generate_quest_advanced(args, generator):
    """Generate advanced quest with branching"""
    quest = generator.generate_quest_advanced(
        quest_type=args.quest_type,
        difficulty=args.difficulty,
        faction=args.faction,
        create_chain=args.create_chain
    )
    output_data(quest, args.format, args.output)


def cmd_generate_npc_network(args, generator):
    """Generate NPC social network"""
    central_npc = generator.generate_npc(faction=args.faction)
    network = generator.generate_npc_network(
        central_npc=central_npc,
        network_size=args.network_size
    )
    output_data(network, args.format, args.output)


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

    # Generate animal command
    animal_parser = subparsers.add_parser('generate-animal', help='Generate random animal(s)')
    animal_parser.add_argument('--category', choices=['wild_fauna', 'pet'],
                               help='Animal category (wild_fauna or pet)')
    animal_parser.add_argument('--species', help='Specific species (e.g., Wolf, Dog, Cat, Horse)')
    animal_parser.add_argument('--habitat', help='Preferred habitat/biome')
    animal_parser.add_argument('--count', type=int, help='Number of animals to generate')
    animal_parser.add_argument('--seed', type=int, help='Random seed for reproducible generation')
    animal_parser.add_argument('--save', action='store_true', help='Save to database')
    animal_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                               help='Output format (default: text)')
    animal_parser.add_argument('--output', help='Output file path')

    # Generate flora command
    flora_parser = subparsers.add_parser('generate-flora', help='Generate random flora')
    flora_parser.add_argument('--category', choices=['trees', 'plants', 'mushrooms', 'crops', 'vines'],
                             help='Flora category')
    flora_parser.add_argument('--species', help='Specific species (e.g., Oak, Pine, Moonflower)')
    flora_parser.add_argument('--habitat', help='Preferred habitat/biome')
    flora_parser.add_argument('--count', type=int, help='Number of flora to generate')
    flora_parser.add_argument('--seed', type=int, help='Random seed for reproducible generation')
    flora_parser.add_argument('--save', action='store_true', help='Save to database')
    flora_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                             help='Output format (default: text)')
    flora_parser.add_argument('--output', help='Output file path')

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

    # Generate loot command
    loot_parser = subparsers.add_parser('generate-loot', help='Generate a loot table')
    loot_parser.add_argument('--enemy-type', choices=['minion', 'standard', 'elite', 'boss'], default='standard',
                            help='Enemy type (default: standard)')
    loot_parser.add_argument('--difficulty', type=int, default=1, help='Difficulty level 1-10 (default: 1)')
    loot_parser.add_argument('--min-items', type=int, default=1, help='Minimum items (default: 1)')
    loot_parser.add_argument('--max-items', type=int, default=3, help='Maximum items (default: 3)')
    loot_parser.add_argument('--biome', help='Biome type for material filtering')
    loot_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                            help='Output format (default: text)')
    loot_parser.add_argument('--output', help='Output file (default: stdout)')
    loot_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate quest command
    quest_parser = subparsers.add_parser('generate-quest', help='Generate a quest')
    quest_parser.add_argument('--quest-type', choices=['fetch', 'kill', 'escort', 'explore', 'craft', 'deliver'],
                             help='Quest type (default: random)')
    quest_parser.add_argument('--difficulty', type=int, default=1, help='Quest difficulty 1-10 (default: 1)')
    quest_parser.add_argument('--faction', help='Faction offering the quest')
    quest_parser.add_argument('--location', help='Starting location ID')
    quest_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                             help='Output format (default: text)')
    quest_parser.add_argument('--output', help='Output file (default: stdout)')
    quest_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate recipe command
    recipe_parser = subparsers.add_parser('generate-recipe', help='Generate a crafting recipe')
    recipe_parser.add_argument('--for-item-template', help='Generate recipe for specific item template')
    recipe_parser.add_argument('--difficulty', type=int, default=1, help='Recipe difficulty 1-10 (default: 1)')
    recipe_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                              help='Output format (default: text)')
    recipe_parser.add_argument('--output', help='Output file (default: stdout)')
    recipe_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate encounter command
    encounter_parser = subparsers.add_parser('generate-encounter', help='Generate an encounter')
    encounter_parser.add_argument('--party-level', type=int, default=1, help='Party level 1-20 (default: 1)')
    encounter_parser.add_argument('--biome', help='Biome where encounter occurs')
    encounter_parser.add_argument('--faction', help='Faction involved')
    encounter_parser.add_argument('--encounter-type', choices=['combat', 'social', 'puzzle', 'trap'], default='combat',
                                  help='Encounter type (default: combat)')
    encounter_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                                  help='Output format (default: text)')
    encounter_parser.add_argument('--output', help='Output file (default: stdout)')
    encounter_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate item with modifiers command
    item_mod_parser = subparsers.add_parser('generate-item-modifiers', help='Generate item with prefix/suffix modifiers')
    item_mod_parser.add_argument('--template', help='Item template to use')
    item_mod_parser.add_argument('--num-modifiers', type=int, default=1, help='Number of modifiers 0-2 (default: 1)')
    item_mod_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                                help='Output format (default: text)')
    item_mod_parser.add_argument('--output', help='Output file (default: stdout)')
    item_mod_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate item set command
    itemset_parser = subparsers.add_parser('generate-item-set', help='Generate a themed item set')
    itemset_parser.add_argument('--set-name', help='Name of the item set')
    itemset_parser.add_argument('--set-size', type=int, default=5, help='Number of items in set (default: 5)')
    itemset_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                               help='Output format (default: text)')
    itemset_parser.add_argument('--output', help='Output file (default: stdout)')
    itemset_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate batch command
    batch_parser = subparsers.add_parser('generate-batch', help='Generate batch content with distribution')
    batch_parser.add_argument('--content-type', choices=['item', 'npc', 'location'], default='item',
                             help='Content type (default: item)')
    batch_parser.add_argument('--count', type=int, default=100, help='Number to generate (default: 100)')
    batch_parser.add_argument('--distribution', help='Rarity distribution (e.g., "Common:0.5,Rare:0.3,Epic:0.2")')
    batch_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='json',
                             help='Output format (default: json)')
    batch_parser.add_argument('--output', help='Output file (default: stdout)')
    batch_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate weather command
    weather_parser = subparsers.add_parser('generate-weather', help='Generate weather and time conditions')
    weather_parser.add_argument('--biome', help='Biome type')
    weather_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                               help='Output format (default: text)')
    weather_parser.add_argument('--output', help='Output file (default: stdout)')
    weather_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate trap command
    trap_parser = subparsers.add_parser('generate-trap', help='Generate a trap or puzzle')
    trap_parser.add_argument('--difficulty', type=int, default=1, help='Difficulty level 1-10 (default: 1)')
    trap_parser.add_argument('--trap-type', choices=['mechanical', 'magical', 'puzzle', 'environmental'],
                            help='Trap type (default: random)')
    trap_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                            help='Output format (default: text)')
    trap_parser.add_argument('--output', help='Output file (default: stdout)')
    trap_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate procedural name command
    procname_parser = subparsers.add_parser('generate-name', help='Generate a procedural name')
    procname_parser.add_argument('--race', default='human', help='Race type (default: human)')
    procname_parser.add_argument('--gender', choices=['male', 'female'], default='male',
                                help='Gender (default: male)')
    procname_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Validate thematic consistency command
    validate_parser = subparsers.add_parser('validate-thematic', help='Validate item thematic consistency')
    validate_parser.add_argument('--item-json', help='Path to item JSON file (default: generates random item)')
    validate_parser.add_argument('--biome', required=True, help='Biome to validate against')
    validate_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                                help='Output format (default: text)')
    validate_parser.add_argument('--output', help='Output file (default: stdout)')
    validate_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate spell command
    spell_parser = subparsers.add_parser('generate-spell', help='Generate a spell')
    spell_parser.add_argument('--spell-level', type=int, help='Spell level 0-9 (0 is cantrip)')
    spell_parser.add_argument('--school', help='Magic school (Evocation, Necromancy, Illusion, etc.)')
    spell_parser.add_argument('--spell-template', help='Spell template (damage_single, damage_area, healing, buff, debuff, summon, utility)')
    spell_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                             help='Output format (default: text)')
    spell_parser.add_argument('--output', help='Output file (default: stdout)')
    spell_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate spellbook command
    spellbook_parser = subparsers.add_parser('generate-spellbook', help='Generate a spellbook')
    spellbook_parser.add_argument('--caster-level', type=int, default=1, help='Caster level 1-20 (default: 1)')
    spellbook_parser.add_argument('--school-preference', help='Preferred magic school')
    spellbook_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                                  help='Output format (default: text)')
    spellbook_parser.add_argument('--output', help='Output file (default: stdout)')
    spellbook_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate organization command
    org_parser = subparsers.add_parser('generate-organization', help='Generate an organization or guild')
    org_parser.add_argument('--org-type', help='Organization type (guild, thieves_guild, mages_circle, religious_order, etc.)')
    org_parser.add_argument('--faction', help='Associated faction')
    org_parser.add_argument('--size', choices=['small', 'medium', 'large'], help='Organization size')
    org_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                           help='Output format (default: text)')
    org_parser.add_argument('--output', help='Output file (default: stdout)')
    org_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate detailed weather command
    weather_detail_parser = subparsers.add_parser('generate-weather-detailed', help='Generate detailed weather with seasons and disasters')
    weather_detail_parser.add_argument('--biome', help='Biome type')
    weather_detail_parser.add_argument('--season', choices=['spring', 'summer', 'autumn', 'winter'], help='Season')
    weather_detail_parser.add_argument('--time-of-day', choices=['dawn', 'morning', 'noon', 'afternoon', 'dusk', 'night'], help='Time of day')
    weather_detail_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                                       help='Output format (default: text)')
    weather_detail_parser.add_argument('--output', help='Output file (default: stdout)')
    weather_detail_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate market command
    market_parser = subparsers.add_parser('generate-market', help='Generate a market with goods and services')
    market_parser.add_argument('--location-id', help='Location ID for the market')
    market_parser.add_argument('--wealth-level', choices=['destitute', 'poor', 'modest', 'comfortable', 'wealthy', 'aristocratic'],
                              default='modest', help='Wealth level (default: modest)')
    market_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                              help='Output format (default: text)')
    market_parser.add_argument('--output', help='Output file (default: stdout)')
    market_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate advanced quest command
    quest_adv_parser = subparsers.add_parser('generate-quest-advanced', help='Generate advanced quest with branching objectives')
    quest_adv_parser.add_argument('--quest-type', help='Quest type (fetch, kill, escort, rescue, investigate, diplomacy, craft, exploration, defense, heist)')
    quest_adv_parser.add_argument('--difficulty', type=int, default=1, help='Quest difficulty 1-10 (default: 1)')
    quest_adv_parser.add_argument('--faction', help='Faction offering the quest')
    quest_adv_parser.add_argument('--create-chain', action='store_true', help='Create a quest chain')
    quest_adv_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                                  help='Output format (default: text)')
    quest_adv_parser.add_argument('--output', help='Output file (default: stdout)')
    quest_adv_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Generate NPC network command
    npc_network_parser = subparsers.add_parser('generate-npc-network', help='Generate NPC social network')
    npc_network_parser.add_argument('--network-size', type=int, default=5, help='Number of connected NPCs (default: 5)')
    npc_network_parser.add_argument('--faction', help='Faction for NPCs')
    npc_network_parser.add_argument('--format', choices=['json', 'pretty', 'text'], default='text',
                                    help='Output format (default: text)')
    npc_network_parser.add_argument('--output', help='Output file (default: stdout)')
    npc_network_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to various formats')
    export_parser.add_argument('--input', required=True, help='Input JSON file')
    export_parser.add_argument('--output', required=True, help='Output file')
    export_parser.add_argument('--export-format', choices=['json', 'xml', 'csv', 'sql', 'markdown'], required=True,
                              help='Export format')
    export_parser.add_argument('--table-name', help='SQL table name (for SQL export)')
    export_parser.add_argument('--title', help='Document title (for Markdown export)')

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
        elif args.command == 'generate-animal':
            cmd_generate_animal(args, generator, db)
        elif args.command == 'generate-flora':
            cmd_generate_flora(args, generator, db)
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
        elif args.command == 'generate-loot':
            cmd_generate_loot(args, generator)
        elif args.command == 'generate-quest':
            cmd_generate_quest(args, generator)
        elif args.command == 'generate-recipe':
            cmd_generate_recipe(args, generator)
        elif args.command == 'generate-encounter':
            cmd_generate_encounter(args, generator)
        elif args.command == 'generate-item-modifiers':
            cmd_generate_item_with_modifiers(args, generator)
        elif args.command == 'generate-item-set':
            cmd_generate_item_set(args, generator)
        elif args.command == 'generate-batch':
            cmd_generate_batch(args, generator)
        elif args.command == 'generate-weather':
            cmd_generate_weather(args, generator)
        elif args.command == 'generate-trap':
            cmd_generate_trap(args, generator)
        elif args.command == 'generate-name':
            cmd_generate_procedural_name(args, generator)
        elif args.command == 'validate-thematic':
            cmd_validate_thematic(args, generator)
        elif args.command == 'export':
            cmd_export(args, generator)
        elif args.command == 'generate-spell':
            cmd_generate_spell(args, generator)
        elif args.command == 'generate-spellbook':
            cmd_generate_spellbook(args, generator)
        elif args.command == 'generate-organization':
            cmd_generate_organization(args, generator)
        elif args.command == 'generate-weather-detailed':
            cmd_generate_weather_detailed(args, generator)
        elif args.command == 'generate-market':
            cmd_generate_market(args, generator)
        elif args.command == 'generate-quest-advanced':
            cmd_generate_quest_advanced(args, generator)
        elif args.command == 'generate-npc-network':
            cmd_generate_npc_network(args, generator)

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
