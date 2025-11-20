#!/usr/bin/env python3
"""
Test script for player database and API endpoints
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from GenerationEngine.src.database import DatabaseManager
from werkzeug.security import generate_password_hash

def test_database_operations():
    """Test player database operations."""
    print("="*60)
    print("Testing Player Database Operations")
    print("="*60)

    # Clean up any existing test database
    import os
    if os.path.exists("test_players.db"):
        os.remove("test_players.db")
        print("Cleaned up old test database\n")

    # Create test database
    db = DatabaseManager(db_path="test_players.db", db_type="sqlite")

    # Test 1: Create a player
    print("\n1. Testing player creation...")
    try:
        player_id = db.create_player(
            username="test_hero",
            password_hash=generate_password_hash("password123"),
            character_name="Test Hero",
            email="test@example.com",
            race="Elf",
            character_class="Warrior"
        )
        print(f"✓ Player created with ID: {player_id}")
    except Exception as e:
        print(f"✗ Failed to create player: {e}")
        return False

    # Test 2: Retrieve player by username
    print("\n2. Testing player retrieval by username...")
    try:
        player = db.get_player_by_username("test_hero")
        if player:
            print(f"✓ Player retrieved: {player['character_name']} (Level {player['level']})")
        else:
            print("✗ Player not found")
            return False
    except Exception as e:
        print(f"✗ Failed to retrieve player: {e}")
        return False

    # Test 3: Get player stats
    print("\n3. Testing player stats retrieval...")
    try:
        stats = db.get_player_stats(player_id)
        if stats:
            print(f"✓ Stats retrieved:")
            print(f"  - Health: {stats['health']}/{stats['max_health']}")
            print(f"  - Strength: {stats['strength']}")
            print(f"  - Dexterity: {stats['dexterity']}")
            print(f"  - Intelligence: {stats['intelligence']}")
        else:
            print("✗ Stats not found")
            return False
    except Exception as e:
        print(f"✗ Failed to retrieve stats: {e}")
        return False

    # Test 4: Update player stats
    print("\n4. Testing player stats update...")
    try:
        success = db.update_player_stats(player_id, {
            'strength': 15,
            'health': 90
        })
        if success:
            stats = db.get_player_stats(player_id)
            print(f"✓ Stats updated:")
            print(f"  - Health: {stats['health']}/{stats['max_health']}")
            print(f"  - Strength: {stats['strength']}")
        else:
            print("✗ Failed to update stats")
            return False
    except Exception as e:
        print(f"✗ Failed to update stats: {e}")
        return False

    # Test 5: Add item to inventory
    print("\n5. Testing inventory - add item...")
    try:
        item_data = {
            "name": "Iron Sword",
            "damage": "1d8",
            "weight": 3.5,
            "value": 50
        }
        inventory_id = db.add_to_inventory(
            player_id=player_id,
            item_name="Iron Sword",
            item_type="weapon",
            item_data=item_data,
            quantity=1
        )
        print(f"✓ Item added to inventory with ID: {inventory_id}")
    except Exception as e:
        print(f"✗ Failed to add item: {e}")
        return False

    # Test 6: Add another item
    print("\n6. Testing inventory - add potion...")
    try:
        potion_data = {
            "name": "Health Potion",
            "healing": 50,
            "weight": 0.5,
            "value": 25
        }
        potion_id = db.add_to_inventory(
            player_id=player_id,
            item_name="Health Potion",
            item_type="consumable",
            item_data=potion_data,
            quantity=5
        )
        print(f"✓ Potion added to inventory with ID: {potion_id}")
    except Exception as e:
        print(f"✗ Failed to add potion: {e}")
        return False

    # Test 7: Get player inventory
    print("\n7. Testing inventory retrieval...")
    try:
        inventory = db.get_player_inventory(player_id)
        if inventory:
            print(f"✓ Inventory retrieved ({len(inventory)} items):")
            for item in inventory:
                print(f"  - {item['item_name']} x{item['quantity']} ({item['item_type']})")
        else:
            print("✗ Inventory is empty")
    except Exception as e:
        print(f"✗ Failed to retrieve inventory: {e}")
        return False

    # Test 8: Equip an item
    print("\n8. Testing item equip...")
    try:
        success = db.update_inventory_item(inventory_id, player_id, {'equipped': True})
        if success:
            inventory = db.get_player_inventory(player_id)
            equipped = [item for item in inventory if item['equipped']]
            print(f"✓ Item equipped: {equipped[0]['item_name']}")
        else:
            print("✗ Failed to equip item")
            return False
    except Exception as e:
        print(f"✗ Failed to equip item: {e}")
        return False

    # Test 9: Remove some potions
    print("\n9. Testing inventory - remove items...")
    try:
        success = db.remove_from_inventory(player_id, potion_id, quantity=3)
        if success:
            inventory = db.get_player_inventory(player_id)
            potions = [item for item in inventory if item['item_name'] == 'Health Potion']
            if potions:
                print(f"✓ Removed 3 potions, {potions[0]['quantity']} remaining")
            else:
                print("✓ All potions removed")
        else:
            print("✗ Failed to remove potions")
            return False
    except Exception as e:
        print(f"✗ Failed to remove items: {e}")
        return False

    # Test 10: Update player data
    print("\n10. Testing player data update...")
    try:
        success = db.update_player(player_id, {
            'level': 2,
            'experience': 150,
            'gold': 250
        })
        if success:
            player = db.get_player_by_id(player_id)
            print(f"✓ Player updated:")
            print(f"  - Level: {player['level']}")
            print(f"  - Experience: {player['experience']}")
            print(f"  - Gold: {player['gold']}")
        else:
            print("✗ Failed to update player")
            return False
    except Exception as e:
        print(f"✗ Failed to update player: {e}")
        return False

    print("\n" + "="*60)
    print("✓ All database tests passed!")
    print("="*60)

    # Clean up test database
    import os
    if os.path.exists("test_players.db"):
        os.remove("test_players.db")
        print("\nTest database cleaned up.")

    return True

def main():
    """Run all tests."""
    print("\nR-Gen Player System Test Suite\n")

    success = test_database_operations()

    if success:
        print("\n✓ All tests completed successfully!")
        print("\nNext steps:")
        print("1. Start the game server: python game_server.py")
        print("2. Test API endpoints with curl or a client")
        print("3. Register a player: POST /api/player/register")
        print("4. Login: POST /api/player/login")
        print("5. Check inventory: GET /api/player/inventory")
        return 0
    else:
        print("\n✗ Some tests failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
