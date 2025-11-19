#!/usr/bin/env python3
"""Quick integration test for client-server connection"""

import sys
sys.path.insert(0, '/home/user/R-Gen')

from game_server import app, get_or_create_world

def test_integration():
    """Test that the server can be initialized and endpoints work"""
    print("Testing server integration...")

    # Test 1: Create world
    print("\n1. Testing world creation...")
    world, simulator = get_or_create_world()
    print(f"   ✓ World created: {world.name}")
    print(f"   ✓ Locations: {len(world.locations)}")
    print(f"   ✓ NPCs: {len(world.npcs)}")

    # Test 2: Test event system access
    print("\n2. Testing event system...")
    event_count = len(world.event_system.event_history)
    print(f"   ✓ Event history accessible: {event_count} events")

    # Test 3: Test Flask app
    print("\n3. Testing Flask app endpoints...")
    with app.test_client() as client:
        # Test health endpoint
        response = client.get('/api/health')
        assert response.status_code == 200
        print(f"   ✓ /api/health: {response.json['status']}")

        # Test world info endpoint
        response = client.get('/api/world/info')
        assert response.status_code == 200
        data = response.json
        assert 'current_time' in data
        assert 'name' in data
        print(f"   ✓ /api/world/info: {data['name']}")

        # Test locations endpoint
        response = client.get('/api/locations')
        assert response.status_code == 200
        assert 'locations' in response.json
        print(f"   ✓ /api/locations: {len(response.json['locations'])} locations")

        # Test NPCs endpoint
        response = client.get('/api/npcs')
        assert response.status_code == 200
        assert 'npcs' in response.json
        print(f"   ✓ /api/npcs: {len(response.json['npcs'])} NPCs")

        # Test events endpoint
        response = client.get('/api/events?limit=10')
        assert response.status_code == 200
        assert 'events' in response.json
        print(f"   ✓ /api/events: {len(response.json['events'])} events")

        # Test location details
        if len(world.locations) > 0:
            loc_id = list(world.locations.keys())[0]
            response = client.get(f'/api/location/{loc_id}')
            assert response.status_code == 200
            assert 'name' in response.json
            assert 'npcs' in response.json
            assert 'connections' in response.json
            print(f"   ✓ /api/location/{{id}}: {response.json['name']}")

        # Test NPC details
        if len(world.npcs) > 0:
            npc_id = list(world.npcs.keys())[0]
            response = client.get(f'/api/npc/{npc_id}')
            assert response.status_code == 200
            assert 'name' in response.json
            print(f"   ✓ /api/npc/{{id}}: {response.json['name']}")

            # Test dialogue
            response = client.get(f'/api/npc/{npc_id}/dialogue')
            assert response.status_code == 200
            assert 'dialogues' in response.json
            print(f"   ✓ /api/npc/{{id}}/dialogue: OK")

    print("\n" + "="*50)
    print("✅ All integration tests passed!")
    print("="*50)
    print("\nThe client and game_server are now fully integrated!")
    print("To start the server, run:")
    print("  python3 game_server.py")
    print("\nThen open http://localhost:5000 in your browser")

if __name__ == '__main__':
    try:
        test_integration()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
