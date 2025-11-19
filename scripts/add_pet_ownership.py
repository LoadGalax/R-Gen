#!/usr/bin/env python3
"""Add pet ownership data to professions.json"""

import json
import os

# Define pet ownership rules for different professions
PET_OWNERSHIP_RULES = {
    "farmer": {
        "pet_chance": 0.7,
        "preferred_pets": [
            {"species": "Dog", "weight": 15},
            {"species": "Cat", "weight": 8},
            {"species": "Pig", "weight": 5},
            {"species": "Horse", "weight": 3}
        ]
    },
    "hunter": {
        "pet_chance": 0.8,
        "preferred_pets": [
            {"species": "Dog", "weight": 20},
            {"species": "Hawk", "weight": 8}
        ]
    },
    "shepherd": {
        "pet_chance": 0.9,
        "preferred_pets": [
            {"species": "Dog", "weight": 25}
        ]
    },
    "guard": {
        "pet_chance": 0.5,
        "preferred_pets": [
            {"species": "Dog", "weight": 15}
        ]
    },
    "noble": {
        "pet_chance": 0.6,
        "preferred_pets": [
            {"species": "Dog", "weight": 10},
            {"species": "Hawk", "weight": 10},
            {"species": "Horse", "weight": 12},
            {"species": "Cat", "weight": 5}
        ]
    },
    "merchant": {
        "pet_chance": 0.4,
        "preferred_pets": [
            {"species": "Cat", "weight": 10},
            {"species": "Dog", "weight": 5},
            {"species": "Horse", "weight": 8}
        ]
    },
    "innkeeper": {
        "pet_chance": 0.5,
        "preferred_pets": [
            {"species": "Cat", "weight": 15},
            {"species": "Dog", "weight": 8}
        ]
    },
    "mage": {
        "pet_chance": 0.4,
        "preferred_pets": [
            {"species": "Raven", "weight": 12},
            {"species": "Cat", "weight": 10}
        ]
    },
    "wizard": {
        "pet_chance": 0.5,
        "preferred_pets": [
            {"species": "Raven", "weight": 15},
            {"species": "Cat", "weight": 8}
        ]
    },
    "witch": {
        "pet_chance": 0.6,
        "preferred_pets": [
            {"species": "Raven", "weight": 15},
            {"species": "Cat", "weight": 12}
        ]
    },
    "hermit": {
        "pet_chance": 0.3,
        "preferred_pets": [
            {"species": "Cat", "weight": 10},
            {"species": "Raven", "weight": 5}
        ]
    },
    "alchemist": {
        "pet_chance": 0.4,
        "preferred_pets": [
            {"species": "Cat", "weight": 10},
            {"species": "Raven", "weight": 5}
        ]
    },
    "knight": {
        "pet_chance": 0.7,
        "preferred_pets": [
            {"species": "Horse", "weight": 20},
            {"species": "Dog", "weight": 8}
        ]
    },
    "soldier": {
        "pet_chance": 0.3,
        "preferred_pets": [
            {"species": "Dog", "weight": 8},
            {"species": "Horse", "weight": 5}
        ]
    },
    "messenger": {
        "pet_chance": 0.6,
        "preferred_pets": [
            {"species": "Horse", "weight": 15}
        ]
    },
    "scribe": {
        "pet_chance": 0.3,
        "preferred_pets": [
            {"species": "Cat", "weight": 10}
        ]
    },
    "ranger": {
        "pet_chance": 0.7,
        "preferred_pets": [
            {"species": "Dog", "weight": 12},
            {"species": "Hawk", "weight": 10}
        ]
    },
    "falconer": {
        "pet_chance": 0.95,
        "preferred_pets": [
            {"species": "Hawk", "weight": 25}
        ]
    },
    "butcher": {
        "pet_chance": 0.3,
        "preferred_pets": [
            {"species": "Pig", "weight": 8},
            {"species": "Dog", "weight": 5}
        ]
    },
    "peasant": {
        "pet_chance": 0.4,
        "preferred_pets": [
            {"species": "Dog", "weight": 8},
            {"species": "Cat", "weight": 5},
            {"species": "Pig", "weight": 3}
        ]
    },
    "necromancer": {
        "pet_chance": 0.4,
        "preferred_pets": [
            {"species": "Raven", "weight": 15}
        ]
    },
    # Default for professions not explicitly listed
    "default": {
        "pet_chance": 0.1,
        "preferred_pets": [
            {"species": "Cat", "weight": 5},
            {"species": "Dog", "weight": 5}
        ]
    }
}

def main():
    # Load professions.json
    professions_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'professions.json')

    with open(professions_path, 'r') as f:
        professions = json.load(f)

    # Add pet ownership to each profession
    for profession_key in professions:
        # Get the pet ownership rule for this profession, or use default
        pet_rule = PET_OWNERSHIP_RULES.get(profession_key, PET_OWNERSHIP_RULES["default"])

        # Add pet ownership field
        professions[profession_key]["pet_ownership"] = pet_rule

    # Save updated professions.json
    with open(professions_path, 'w') as f:
        json.dump(professions, f, indent=2)

    print(f"✓ Added pet ownership data to {len(professions)} professions")

if __name__ == "__main__":
    main()
