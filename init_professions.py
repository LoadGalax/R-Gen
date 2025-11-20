#!/usr/bin/env python3
"""
Initialize professions and recipes from GenerationEngine data.
This script populates the database with all 35 professions from the professions.json
and generates sample recipes for each.
"""

import sys
from pathlib import Path

# Add engines to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from GenerationEngine import ContentGenerator, DatabaseManager
import json

# Icon mapping for professions
PROFESSION_ICONS = {
    'blacksmith': '⚒️',
    'alchemist': '🧪',
    'enchanter': '✨',
    'leatherworker': '🦌',
    'tailor': '🧵',
    'jeweler': '💎',
    'cook': '🍳',
    'carpenter': '🪓',
    'engineer': '⚙️',
    'scribe': '📜',
    'miner': '⛏️',
    'herbalist': '🌿',
    'skinner': '🔪',
    'fisher': '🎣',
    'archaeologist': '🏺',
    'armorer': '🛡️',
    'weaponsmith': '⚔️',
    'brewer': '🍺',
    'potter': '🏺',
    'glassblower': '🫧',
    'mason': '🧱',
    'chandler': '🕯️',
    'tanner': '🦌',
    'bowyer': '🏹',
    'fletcher': '🎯',
    'saddler': '🐴',
    'cobbler': '👞',
    'cartographer': '🗺️',
    'astrologer': '⭐',
    'apothecary': '💊',
    'sage': '📚',
    'bard': '🎵',
    'painter': '🎨',
    'sculptor': '🗿',
    'architect': '🏛️'
}

def categorize_profession(prof_name: str, skills: list) -> str:
    """Determine profession type based on name and skills."""
    name_lower = prof_name.lower()

    # Gathering professions
    if any(word in name_lower for word in ['miner', 'herbalist', 'fisher', 'skinner', 'archaeologist']):
        return 'gathering'

    # Check skills for gathering activities
    gathering_skills = ['mining', 'herbalism', 'fishing', 'skinning', 'excavation', 'foraging']
    if any(skill.lower() in gathering_skills for skill in skills):
        return 'gathering'

    # Creative/artistic professions
    if any(word in name_lower for word in ['bard', 'painter', 'sculptor', 'cartographer']):
        return 'creative'

    # Knowledge professions
    if any(word in name_lower for word in ['sage', 'astrologer', 'scribe', 'architect']):
        return 'scholarly'

    # Everything else is crafting
    return 'crafting'

def init_professions():
    """Initialize all professions from professions.json into the database."""
    print("Initializing professions from GenerationEngine...")

    generator = ContentGenerator()
    db = DatabaseManager()

    # Load professions data
    professions_data = generator.professions

    profession_ids = {}

    for prof_name, prof_data in professions_data.items():
        # Get icon
        icon = PROFESSION_ICONS.get(prof_name.lower(), '🔨')

        # Get description from description_templates (use first one)
        descriptions = prof_data.get('description_templates', [])
        description = descriptions[0] if descriptions else f"A skilled {prof_name}."

        # Determine profession type
        skills = prof_data.get('skills', [])
        profession_type = categorize_profession(prof_name, skills)

        # Prepare additional data
        data = {
            'skills': skills,
            'base_stats': prof_data.get('base_stats', {}),
            'typical_inventory': prof_data.get('typical_inventory', []),
            'typical_locations': prof_data.get('typical_locations', []),
            'possible_races': prof_data.get('possible_races', []),
            'dialogue_hooks': prof_data.get('dialogue_hooks', [])
        }

        # Create profession
        try:
            prof_id = db.create_profession(
                name=prof_name.title(),
                icon=icon,
                description=description,
                profession_type=profession_type,
                data=data
            )
            profession_ids[prof_name] = prof_id
            print(f"  ✓ Created profession: {icon} {prof_name.title()} (ID: {prof_id}, Type: {profession_type})")
        except Exception as e:
            print(f"  ✗ Error creating {prof_name}: {e}")

    print(f"\n✓ Initialized {len(profession_ids)} professions")
    return profession_ids

def generate_sample_recipes(profession_ids):
    """Generate sample recipes for major crafting professions."""
    print("\nGenerating sample recipes...")

    generator = ContentGenerator()
    db = DatabaseManager()

    # Define key professions and sample recipes
    recipe_configs = {
        'Blacksmith': [
            ('Iron Sword', 'Iron Sword', 1, [{'ingredient_name': 'Iron Ingot', 'quantity': 3}, {'ingredient_name': 'Wood', 'quantity': 1}], 3),
            ('Steel Helmet', 'Steel Helmet', 5, [{'ingredient_name': 'Steel Ingot', 'quantity': 4}], 5),
        ],
        'Alchemist': [
            ('Health Potion', 'Health Potion', 1, [{'ingredient_name': 'Red Herb', 'quantity': 2}, {'ingredient_name': 'Crystal Vial', 'quantity': 1}], 2),
            ('Mana Potion', 'Mana Potion', 3, [{'ingredient_name': 'Blue Flower', 'quantity': 2}, {'ingredient_name': 'Crystal Vial', 'quantity': 1}], 3),
        ],
        'Cook': [
            ('Bread', 'Bread', 1, [{'ingredient_name': 'Wheat', 'quantity': 2}], 1),
            ('Grilled Meat', 'Grilled Meat', 2, [{'ingredient_name': 'Raw Meat', 'quantity': 1}], 2),
        ],
        'Enchanter': [
            ('Fire Weapon Enchant', 'Enchanted Scroll', 4, [{'ingredient_name': 'Magic Essence', 'quantity': 3}, {'ingredient_name': 'Scroll', 'quantity': 1}], 5),
        ],
        'Leatherworker': [
            ('Leather Armor', 'Leather Armor', 2, [{'ingredient_name': 'Leather', 'quantity': 5}], 3),
        ],
        'Tailor': [
            ('Cloth Robe', 'Cloth Robe', 2, [{'ingredient_name': 'Cloth', 'quantity': 4}], 3),
        ],
        'Jeweler': [
            ('Ruby Ring', 'Ruby Ring', 3, [{'ingredient_name': 'Ruby', 'quantity': 1}, {'ingredient_name': 'Gold Bar', 'quantity': 2}], 4),
        ],
        'Carpenter': [
            ('Oak Bow', 'Oak Bow', 3, [{'ingredient_name': 'Oak Wood', 'quantity': 3}, {'ingredient_name': 'String', 'quantity': 1}], 4),
        ],
    }

    total_recipes = 0
    for prof_name, recipes in recipe_configs.items():
        if prof_name not in profession_ids:
            print(f"  ⚠ Profession {prof_name} not found in database")
            continue

        prof_id = profession_ids[prof_name]

        for recipe_name, result_item, req_level, ingredients, craft_time in recipes:
            try:
                recipe_id = db.create_recipe(
                    name=recipe_name,
                    profession_id=prof_id,
                    required_level=req_level,
                    result_item_name=result_item,
                    result_quantity=1,
                    ingredients=ingredients,
                    crafting_time=craft_time,
                    difficulty='easy' if req_level <= 2 else 'medium' if req_level <= 4 else 'hard'
                )
                total_recipes += 1
                print(f"  ✓ Created recipe: {recipe_name} for {prof_name} (ID: {recipe_id})")
            except Exception as e:
                print(f"  ✗ Error creating recipe {recipe_name}: {e}")

    print(f"\n✓ Generated {total_recipes} sample recipes")

def main():
    """Main initialization function."""
    print("=" * 60)
    print("R-Gen Profession System Initialization")
    print("=" * 60)

    # Initialize professions
    profession_ids = init_professions()

    # Generate sample recipes
    generate_sample_recipes(profession_ids)

    print("\n" + "=" * 60)
    print("✓ Initialization complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
