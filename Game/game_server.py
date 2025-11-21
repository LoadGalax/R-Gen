#!/usr/bin/env python3
"""
R-Gen Game Server - Flask + WebSocket server for the web game
Provides REST API and real-time simulation updates via WebSocket
"""

from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import sys
import threading
import time
import secrets
from pathlib import Path
from datetime import datetime
from functools import wraps

# Add engines to path
project_root = Path(__file__).parent.parent  # Go up one level from Game/ to R-Gen/
sys.path.insert(0, str(project_root))

from GenerationEngine import ContentGenerator
from game_database import GameDatabase

# Client folder is at the root level, not in Game/
client_folder = project_root / "Client"
app = Flask(__name__, static_folder=str(client_folder), static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
# Point to the GenerationEngine data directory
data_dir = project_root / "GenerationEngine" / "data"
generator = ContentGenerator(data_dir=str(data_dir))
db = None
world = None

def get_db():
    """Get or create game database instance."""
    global db
    if db is None:
        db = GameDatabase()
    return db

def get_or_create_world():
    """Get or create world instance."""
    global world
    if world is None:
        print("Creating new world...")
        # Import World here to avoid requiring SimulationEngine at module level
        from SimulationEngine import World
        world = World.create_new(num_locations=10, seed=42, name="Fantasy Realm")
        print(f"World created with {len(world.locations)} locations and {len(world.npcs)} NPCs")
    return world

def login_required(f):
    """Decorator to require player login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'player_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# Static File Serving
# ============================================================================

@app.route('/')
def serve_game():
    """Serve the main game page."""
    response = send_from_directory(client_folder, 'index.html')
    # Prevent caching during development
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files."""
    response = send_from_directory(client_folder, path)
    # Prevent caching for JS files during development
    if path.endswith('.js'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# ============================================================================
# REST API Endpoints
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'world_active': world is not None
    })

@app.route('/api/world/info', methods=['GET'])
def get_world_info():
    """Get current world information."""
    w = get_or_create_world()

    return jsonify({
        'name': w.name,
        'current_time': {
            'day': w.time_manager.current_day,
            'season': w.time_manager.current_season,
            'time': w.time_manager.get_time_string(),
            'is_day': w.time_manager.is_daytime
        },
        'stats': {
            'total_locations': len(w.locations),
            'total_npcs': len(w.npcs),
            'total_events': len(w.event_system.event_history)
        }
    })

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Get all locations."""
    w = get_or_create_world()

    locations = []
    for loc_id, location in w.locations.items():
        loc_data = location.to_dict()
        # Add commonly needed fields
        loc_data['name'] = location.get_name()
        loc_data['template'] = location.data.get('template', 'unknown') if location.data else 'unknown'
        # Add NPCs at this location
        npcs_here = [npc_id for npc_id, npc in w.npcs.items()
                     if npc.current_location_id == loc_id]
        loc_data['npcs'] = npcs_here
        loc_data['npc_count'] = len(npcs_here)
        locations.append(loc_data)

    return jsonify({'locations': locations})

@app.route('/api/location/<location_id>', methods=['GET'])
def get_location_details(location_id):
    """Get detailed information about a specific location."""
    w = get_or_create_world()

    if location_id not in w.locations:
        return jsonify({'error': 'Location not found'}), 404

    location = w.locations[location_id]
    loc_data = location.to_dict()

    # Add commonly needed fields from nested data
    loc_data['name'] = location.get_name()
    loc_data['description'] = location.data.get('description', '') if location.data else ''
    loc_data['template'] = location.data.get('template', 'unknown') if location.data else 'unknown'

    # Add NPCs at this location with full details
    npcs_here = []
    for npc_id, npc in w.npcs.items():
        if npc.current_location_id == location_id:
            npc_data = npc.to_dict()
            npc_data['id'] = npc_id
            npc_data['name'] = npc.get_name()
            npc_data['profession'] = npc.get_profession()
            npc_data['level'] = npc.data.get('level', 1) if npc.data else 1
            npc_data['current_activity'] = npc.current_activity
            npcs_here.append(npc_data)

    loc_data['npcs'] = npcs_here
    loc_data['weather'] = location.current_weather or 'Clear'

    # Add connected locations
    connections = []
    for conn_id in location.get_connections():
        if conn_id in w.locations:
            conn_loc = w.locations[conn_id]
            connections.append({
                'id': conn_id,
                'name': conn_loc.get_name(),
                'template': conn_loc.data.get('template', 'unknown') if conn_loc.data else 'unknown'
            })
    loc_data['connections'] = connections

    return jsonify(loc_data)

@app.route('/api/npcs', methods=['GET'])
def get_npcs():
    """Get all NPCs."""
    w = get_or_create_world()

    npcs = []
    for npc_id, npc in w.npcs.items():
        npc_data = npc.to_dict()
        npc_data['id'] = npc_id
        npc_data['location_id'] = npc.current_location_id
        if npc.current_location_id in w.locations:
            npc_data['location_name'] = w.locations[npc.current_location_id].get_name()
        npcs.append(npc_data)

    return jsonify({'npcs': npcs})

@app.route('/api/npc/<npc_id>', methods=['GET'])
def get_npc_details(npc_id):
    """Get detailed information about a specific NPC."""
    w = get_or_create_world()

    if npc_id not in w.npcs:
        return jsonify({'error': 'NPC not found'}), 404

    npc = w.npcs[npc_id]
    npc_data = npc.to_dict()
    npc_data['id'] = npc_id
    npc_data['name'] = npc.get_name()
    npc_data['profession'] = npc.get_profession()
    npc_data['location_id'] = npc.current_location_id

    if npc.current_location_id in w.locations:
        npc_data['location_name'] = w.locations[npc.current_location_id].get_name()

    return jsonify(npc_data)

@app.route('/api/npc/<npc_id>/dialogue', methods=['GET'])
def get_npc_dialogue(npc_id):
    """Get dialogue options for an NPC."""
    w = get_or_create_world()

    if npc_id not in w.npcs:
        return jsonify({'error': 'NPC not found'}), 404

    npc = w.npcs[npc_id]

    # Generate dialogue based on NPC profession and mood
    profession = npc.get_profession()
    mood_value = npc.mood
    # Convert mood value to text
    if mood_value > 70:
        mood = "happy"
    elif mood_value > 40:
        mood = "content"
    else:
        mood = "troubled"

    dialogues = {
        'greeting': f"Greetings, traveler! I am {npc.get_name()}, a {profession}.",
        'mood': f"I'm feeling {mood} today.",
        'profession': get_profession_dialogue(profession, npc),
        'farewell': "Safe travels, friend!"
    }

    return jsonify({
        'npc_id': npc_id,
        'npc_name': npc.get_name(),
        'profession': profession,
        'mood': mood,
        'dialogues': dialogues
    })

def get_profession_dialogue(profession, npc):
    """Generate profession-specific dialogue."""
    dialogues = {
        'blacksmith': f"I craft the finest weapons and armor. My current project is a masterwork blade.",
        'merchant': f"I have many wares to sell. Perhaps you need supplies for your journey?",
        'innkeeper': f"Welcome to my establishment! A warm bed and hot meal await you.",
        'wizard': f"I study the arcane arts. The magical energies are particularly strong today.",
        'guard': f"I keep watch over this place. All seems quiet for now.",
        'farmer': f"The harvest has been good this season. Hard work pays off.",
        'bard': f"Would you like to hear a tale? I know many stories from distant lands."
    }
    return dialogues.get(profession.lower(), f"As a {profession}, I have many tasks to attend to.")

def format_event(event, world):
    """Format an Event object into a human-readable string."""
    try:
        event_type = event.event_type
        data = event.data

        # Get entity names
        source_name = ""
        if event.source_id and event.source_id in world.npcs:
            source_name = world.npcs[event.source_id].get_name()

        location_name = ""
        if event.location_id and event.location_id in world.locations:
            location_name = world.locations[event.location_id].get_name()

        # Format based on event type
        if event_type == "npc_moved":
            return f"{source_name} traveled to {location_name}"
        elif event_type == "npc_spawned":
            npc_name = data.get("npc_name", "Someone")
            profession = data.get("profession", "wanderer")
            return f"{npc_name} the {profession} arrived at {location_name}"
        elif event_type == "location_created":
            return f"World '{data.get('world_name')}' created with {data.get('num_locations')} locations"
        elif event_type == "hour_passed":
            hour = data.get("hour", 0)
            return f"Hour {hour} has arrived"
        elif event_type == "day_passed":
            day = data.get("day", 0)
            return f"A new day begins (Day {day})"
        else:
            # Generic format
            if source_name and location_name:
                return f"{source_name} {event_type.replace('_', ' ')} at {location_name}"
            elif source_name:
                return f"{source_name} {event_type.replace('_', ' ')}"
            else:
                return event_type.replace('_', ' ').capitalize()
    except Exception as e:
        print(f"Error formatting event: {e}")
        return None

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get recent events."""
    w = get_or_create_world()

    limit = request.args.get('limit', 50, type=int)
    recent_events = w.event_system.get_recent_events(limit)

    # Convert Event objects to readable strings
    event_strings = []
    for event in recent_events:
        event_str = format_event(event, w)
        if event_str:
            event_strings.append(event_str)

    return jsonify({
        'events': event_strings,
        'total_events': len(w.event_system.event_history)
    })

@app.route('/api/player/travel', methods=['POST'])
@login_required
def player_travel():
    """Move player to a new location."""
    data = request.get_json()
    target_location = data.get('location_id')

    w = get_or_create_world()
    database = get_db()

    if target_location not in w.locations:
        return jsonify({'error': 'Location not found'}), 404

    # Update player location in database
    player_id = session['player_id']
    database.update_player(player_id, {'current_location_id': target_location})

    location = w.locations[target_location]
    player = database.get_player_by_id(player_id)

    # Broadcast to all clients that player moved
    socketio.emit('player_moved', {
        'player_name': player['character_name'],
        'location_id': target_location,
        'location_name': location.get_name(),
        'timestamp': datetime.now().isoformat()
    })

    return jsonify({
        'success': True,
        'location_id': target_location,
        'message': f'Traveled to {location.get_name()}'
    })

# ============================================================================
# Player Management Endpoints
# ============================================================================

@app.route('/api/player/register', methods=['POST'])
def register_player():
    """Register a new player account."""
    data = request.get_json()

    required_fields = ['username', 'password', 'character_name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    username = data['username']
    password = data['password']
    character_name = data['character_name']
    email = data.get('email')
    race = data.get('race', 'Human')
    character_class = data.get('class', 'Adventurer')

    database = get_db()
    w = get_or_create_world()

    # Check if username already exists
    existing_player = database.get_player_by_username(username)
    if existing_player:
        return jsonify({'error': 'Username already exists'}), 400

    # Hash password
    password_hash = generate_password_hash(password)

    # Get starting location (first location in the world)
    starting_location = list(w.locations.keys())[0] if w.locations else None

    try:
        # Create player in database
        player_id = database.create_player(
            username=username,
            password_hash=password_hash,
            character_name=character_name,
            email=email,
            race=race,
            character_class=character_class,
            starting_location=starting_location
        )

        # Log the player in automatically
        session['player_id'] = player_id
        session['username'] = username

        # Get player data to return
        player = database.get_player_by_id(player_id)
        stats = database.get_player_stats(player_id)

        return jsonify({
            'success': True,
            'message': 'Player registered successfully',
            'player': {
                'id': player['id'],
                'username': player['username'],
                'character_name': player['character_name'],
                'race': player['race'],
                'class': player['class'],
                'level': player['level'],
                'gold': player['gold'],
                'current_location_id': player['current_location_id'],
                'stats': stats
            }
        }), 201

    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/player/login', methods=['POST'])
def login_player():
    """Login a player."""
    data = request.get_json()

    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400

    username = data['username']
    password = data['password']

    database = get_db()

    # Get player from database
    player = database.get_player_by_username(username)
    if not player:
        return jsonify({'error': 'Invalid username or password'}), 401

    # Check password
    if not check_password_hash(player['password_hash'], password):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Update last login time
    database.update_player(player['id'], {'last_login': datetime.now()})

    # Set session
    session['player_id'] = player['id']
    session['username'] = player['username']

    # Get player stats
    stats = database.get_player_stats(player['id'])

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'player': {
            'id': player['id'],
            'username': player['username'],
            'character_name': player['character_name'],
            'race': player['race'],
            'class': player['class'],
            'level': player['level'],
            'experience': player['experience'],
            'gold': player['gold'],
            'current_location_id': player['current_location_id'],
            'stats': stats
        }
    })

@app.route('/api/player/logout', methods=['POST'])
@login_required
def logout_player():
    """Logout the current player."""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/player/me', methods=['GET'])
@login_required
def get_current_player():
    """Get current player data."""
    database = get_db()
    player_id = session['player_id']

    player = database.get_player_by_id(player_id)
    if not player:
        return jsonify({'error': 'Player not found'}), 404

    stats = database.get_player_stats(player_id)
    inventory = database.get_player_inventory(player_id)

    return jsonify({
        'player': {
            'id': player['id'],
            'username': player['username'],
            'character_name': player['character_name'],
            'race': player['race'],
            'class': player['class'],
            'level': player['level'],
            'experience': player['experience'],
            'gold': player['gold'],
            'current_location_id': player['current_location_id'],
            'stats': stats,
            'inventory': inventory
        }
    })

@app.route('/api/player/stats', methods=['GET'])
@login_required
def get_player_stats():
    """Get player stats."""
    database = get_db()
    player_id = session['player_id']

    stats = database.get_player_stats(player_id)
    if not stats:
        return jsonify({'error': 'Stats not found'}), 404

    return jsonify({'stats': stats})

@app.route('/api/player/stats', methods=['PATCH'])
@login_required
def update_player_stats():
    """Update player stats."""
    data = request.get_json()
    database = get_db()
    player_id = session['player_id']

    success = database.update_player_stats(player_id, data)
    if not success:
        return jsonify({'error': 'Failed to update stats'}), 500

    stats = database.get_player_stats(player_id)
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/player/inventory', methods=['GET'])
@login_required
def get_player_inventory():
    """Get player inventory."""
    database = get_db()
    player_id = session['player_id']

    inventory = database.get_player_inventory(player_id)

    # Parse JSON data field for each item
    for item in inventory:
        if 'data' in item and isinstance(item['data'], str):
            try:
                item['item_data'] = json.loads(item['data'])
                del item['data']  # Remove the raw JSON string
            except json.JSONDecodeError:
                item['item_data'] = {}

    return jsonify({'inventory': inventory})

@app.route('/api/player/inventory', methods=['POST'])
@login_required
def add_to_player_inventory():
    """Add an item to player inventory."""
    data = request.get_json()
    database = get_db()
    player_id = session['player_id']

    required_fields = ['item_name', 'item_type', 'item_data']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        inventory_id = database.add_to_inventory(
            player_id=player_id,
            item_name=data['item_name'],
            item_type=data['item_type'],
            item_data=data['item_data'],
            quantity=data.get('quantity', 1)
        )

        return jsonify({
            'success': True,
            'message': 'Item added to inventory',
            'inventory_id': inventory_id
        }), 201

    except Exception as e:
        return jsonify({'error': f'Failed to add item: {str(e)}'}), 500

@app.route('/api/player/inventory/<int:inventory_id>', methods=['DELETE'])
@login_required
def remove_from_player_inventory(inventory_id):
    """Remove an item from player inventory."""
    database = get_db()
    player_id = session['player_id']

    data = request.get_json() or {}
    quantity = data.get('quantity')

    success = database.remove_from_inventory(player_id, inventory_id, quantity)
    if not success:
        return jsonify({'error': 'Failed to remove item'}), 500

    return jsonify({'success': True, 'message': 'Item removed from inventory'})

@app.route('/api/player/inventory/<int:inventory_id>', methods=['PATCH'])
@login_required
def update_player_inventory_item(inventory_id):
    """Update an inventory item (e.g., equip/unequip)."""
    data = request.get_json()
    database = get_db()
    player_id = session['player_id']

    success = database.update_inventory_item(inventory_id, player_id, data)
    if not success:
        return jsonify({'error': 'Failed to update item'}), 500

    return jsonify({'success': True, 'message': 'Item updated'})

# ========================================================================
# Profession Endpoints
# ========================================================================

# Icon mapping for professions
PROFESSION_ICONS = {
    'blacksmith': '⚒️', 'alchemist': '🧪', 'enchanter': '✨', 'leatherworker': '🦌',
    'tailor': '🧵', 'jeweler': '💎', 'cook': '🍳', 'carpenter': '🪓',
    'engineer': '⚙️', 'scribe': '📜', 'miner': '⛏️', 'herbalist': '🌿',
    'skinner': '🔪', 'fisherman': '🎣', 'fisher': '🎣', 'archaeologist': '🏺',
    'armorer': '🛡️', 'weaponsmith': '⚔️', 'brewer': '🍺', 'baker': '🍞',
    'potter': '🏺', 'glassblower': '🫧', 'mason': '🧱', 'chandler': '🕯️',
    'tanner': '🦌', 'bowyer': '🏹', 'fletcher': '🎯', 'saddler': '🐴',
    'cobbler': '👞', 'cartographer': '🗺️', 'astrologer': '⭐', 'apothecary': '💊',
    'sage': '📚', 'bard': '🎵', 'painter': '🎨', 'sculptor': '🗿', 'architect': '🏛️',
    'guard': '🛡️', 'merchant': '💰', 'mage': '🔮', 'innkeeper': '🍺',
    'hermit': '🧙', 'cleric': '⛪', 'druid': '🌳', 'thief': '🗡️',
    'assassin': '⚔️', 'farmer': '🌾', 'hunter': '🏹', 'scholar': '📚',
    'healer': '💊', 'knight': '⚔️', 'soldier': '⚔️', 'archer': '🏹',
    'smuggler': '💼', 'necromancer': '💀', 'ranger': '🌲', 'paladin': '⚔️',
    'warlock': '🔥', 'monk': '🥋', 'barbarian': '⚡', 'spy': '🕵️',
    'navigator': '🧭', 'diplomat': '🤝', 'gladiator': '⚔️', 'fortune_teller': '🔮',
    'sailor': '⚓', 'pirate': '☠️'
}

@app.route('/api/professions', methods=['GET'])
def get_all_professions():
    """Get all available professions from GenerationEngine."""
    professions_data = generator.professions

    # Convert to list format expected by frontend
    professions = []
    for prof_name, prof_data in professions_data.items():
        profession = {
            'id': prof_name.lower(),
            'name': prof_name.title(),
            'icon': PROFESSION_ICONS.get(prof_name.lower(), '🔨'),
            'description': prof_data.get('description_templates', [f"A skilled {prof_name}."])[0] if prof_data.get('description_templates') else f"A skilled {prof_name}.",
            'skills': prof_data.get('skills', []),
            'base_stats': prof_data.get('base_stats', {}),
            'typical_inventory': prof_data.get('typical_inventory', []),
            'typical_locations': prof_data.get('typical_locations', []),
            'possible_races': prof_data.get('possible_races', []),
            'dialogue_hooks': prof_data.get('dialogue_hooks', [])
        }
        professions.append(profession)

    return jsonify({'professions': professions})

@app.route('/api/player/professions', methods=['GET'])
@login_required
def get_player_professions():
    """Get player's professions with levels and XP."""
    database = get_db()
    player_id = session['player_id']

    # Get player data
    player = database.get_player_by_id(player_id)
    if not player:
        return jsonify({'error': 'Player not found'}), 404

    # Get player professions from game database
    player_professions_data = database.get_player_professions(player_id)

    # Enrich with profession info from GenerationEngine
    professions = []
    for prof_record in player_professions_data:
        prof_id = prof_record['profession_id']
        if prof_id in generator.professions:
            prof_data = generator.professions[prof_id]
            professions.append({
                'id': prof_record['id'],
                'profession_id': prof_id,
                'name': prof_id.title(),
                'icon': PROFESSION_ICONS.get(prof_id.lower(), '🔨'),
                'level': prof_record['level'],
                'experience': prof_record['experience'],
                'description': prof_data.get('description_templates', [f"A skilled {prof_id}."])[0] if prof_data.get('description_templates') else f"A skilled {prof_id}.",
                'skills': prof_data.get('skills', []),
                'created_at': prof_record['created_at'],
                'updated_at': prof_record['updated_at']
            })

    return jsonify({'professions': professions})

@app.route('/api/player/professions', methods=['POST'])
@login_required
def add_player_profession():
    """Add a profession to player."""
    data = request.get_json()
    database = get_db()
    player_id = session['player_id']

    profession_id = data.get('profession_id')
    if not profession_id:
        return jsonify({'error': 'profession_id required'}), 400

    # Verify profession exists in GenerationEngine
    if profession_id not in generator.professions:
        return jsonify({'error': 'Invalid profession'}), 400

    level = data.get('level', 1)
    experience = data.get('experience', 0)

    try:
        # Add profession to player in game database
        player_prof_id = database.add_player_profession(player_id, profession_id, level, experience)
        return jsonify({'success': True, 'id': player_prof_id, 'profession_id': profession_id})
    except Exception as e:
        return jsonify({'error': f'Failed to add profession: {str(e)}'}), 500

@app.route('/api/player/professions/<profession_id>', methods=['PATCH'])
@login_required
def update_player_profession(profession_id):
    """Update player's profession level or XP."""
    data = request.get_json()
    database = get_db()
    player_id = session['player_id']

    # Verify profession exists in GenerationEngine
    if profession_id not in generator.professions:
        return jsonify({'error': 'Invalid profession'}), 400

    # Update profession in game database
    level = data.get('level')
    experience = data.get('experience')

    success = database.update_player_profession(player_id, profession_id, level, experience)
    if not success:
        return jsonify({'error': 'Failed to update profession'}), 500

    return jsonify({'success': True, 'message': 'Profession updated'})

# ========================================================================
# Recipe Endpoints
# ========================================================================

@app.route('/api/recipes', methods=['GET'])
def get_all_recipes():
    """Get all recipes (placeholder - to be generated from GenerationEngine)."""
    # TODO: Generate recipes dynamically from GenerationEngine
    return jsonify({'recipes': []})

@app.route('/api/player/recipes', methods=['GET'])
@login_required
def get_player_recipes():
    """Get player's known recipes (placeholder)."""
    # TODO: Generate recipes based on player professions
    return jsonify({'recipes': []})

@app.route('/api/player/recipes', methods=['POST'])
@login_required
def add_player_recipe():
    """Add a recipe to player's known recipes (placeholder)."""
    # TODO: Implement recipe learning
    return jsonify({'success': True, 'message': 'Recipe system coming soon'})

@app.route('/api/craft', methods=['POST'])
@login_required
def craft_item():
    """Craft an item from a recipe (placeholder)."""
    # TODO: Implement crafting with GenerationEngine
    return jsonify({'success': False, 'message': 'Crafting system coming soon'})

@app.route('/api/player/update', methods=['PATCH'])
@login_required
def update_player_data():
    """Update player data (level, experience, gold, etc.)."""
    data = request.get_json()
    database = get_db()
    player_id = session['player_id']

    success = database.update_player(player_id, data)
    if not success:
        return jsonify({'error': 'Failed to update player'}), 500

    player = database.get_player_by_id(player_id)
    return jsonify({'success': True, 'player': player})

# ============================================================================
# Master Admin Panel Endpoints
# ============================================================================

@app.route('/master')
def serve_master_panel():
    """Serve the master admin panel page."""
    response = send_from_directory(client_folder, 'master.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/master/world', methods=['GET'])
def get_master_world_data():
    """Get complete world data for master panel."""
    w = get_or_create_world()

    return jsonify({
        'name': w.name,
        'seed': w.seed,
        'description': w.description,
        'stats': {
            'total_locations': len(w.locations),
            'total_npcs': len(w.npcs),
            'total_events': len(w.event_system.event_history)
        }
    })

@app.route('/api/master/world', methods=['PATCH'])
def update_master_world_data():
    """Update world settings."""
    w = get_or_create_world()
    data = request.get_json()

    if 'name' in data:
        w.name = data['name']
    if 'description' in data:
        w.description = data['description']

    return jsonify({'success': True, 'message': 'World updated'})

@app.route('/api/master/npcs', methods=['GET'])
def get_master_npcs():
    """Get all NPCs with full details for editing."""
    w = get_or_create_world()

    npcs_list = []
    for npc_id, npc in w.npcs.items():
        npc_dict = {
            'id': npc_id,
            'name': npc.get_name(),
            'profession': npc.get_profession(),
            'current_location_id': npc.current_location_id,
            'current_activity': npc.current_activity,
            'energy': npc.energy,
            'hunger': npc.hunger,
            'mood': npc.mood,
            'gold': npc.gold,
            'active': npc.active,
            'work_start_hour': npc.work_start_hour,
            'work_end_hour': npc.work_end_hour,
            'work_location_id': npc.work_location_id,
            'data': npc.data
        }
        npcs_list.append(npc_dict)

    return jsonify({'npcs': npcs_list})

@app.route('/api/master/npc/<npc_id>', methods=['PATCH'])
def update_master_npc(npc_id):
    """Update NPC properties."""
    w = get_or_create_world()

    if npc_id not in w.npcs:
        return jsonify({'error': 'NPC not found'}), 404

    npc = w.npcs[npc_id]
    data = request.get_json()

    # Update mutable properties
    if 'energy' in data:
        npc.energy = float(data['energy'])
    if 'hunger' in data:
        npc.hunger = float(data['hunger'])
    if 'mood' in data:
        npc.mood = float(data['mood'])
    if 'gold' in data:
        npc.gold = int(data['gold'])
    if 'current_location_id' in data:
        old_location = npc.current_location_id
        npc.current_location_id = data['current_location_id']
        # Update location tracking
        if old_location and old_location in w.locations:
            w.locations[old_location].npc_ids.discard(npc_id)
        if npc.current_location_id in w.locations:
            w.locations[npc.current_location_id].npc_ids.add(npc_id)
    if 'current_activity' in data:
        npc.current_activity = data['current_activity']
    if 'active' in data:
        npc.active = bool(data['active'])
    if 'work_start_hour' in data:
        npc.work_start_hour = int(data['work_start_hour'])
    if 'work_end_hour' in data:
        npc.work_end_hour = int(data['work_end_hour'])
    if 'work_location_id' in data:
        npc.work_location_id = data['work_location_id']

    # Update nested data properties
    if 'data' in data:
        for key, value in data['data'].items():
            npc.data[key] = value

    return jsonify({'success': True, 'message': f'NPC {npc_id} updated'})

@app.route('/api/master/npc/<npc_id>', methods=['DELETE'])
def delete_master_npc(npc_id):
    """Delete an NPC from the world."""
    w = get_or_create_world()

    if npc_id not in w.npcs:
        return jsonify({'error': 'NPC not found'}), 404

    npc = w.npcs[npc_id]

    # Remove from location tracking
    if npc.current_location_id and npc.current_location_id in w.locations:
        w.locations[npc.current_location_id].npc_ids.discard(npc_id)

    # Remove from world
    del w.npcs[npc_id]

    return jsonify({'success': True, 'message': f'NPC {npc_id} deleted'})

@app.route('/api/master/locations', methods=['GET'])
def get_master_locations():
    """Get all locations with full details for editing."""
    w = get_or_create_world()

    locations_list = []
    for loc_id, location in w.locations.items():
        loc_dict = {
            'id': loc_id,
            'name': location.get_name(),
            'description': location.data.get('description', '') if location.data else '',
            'template': location.data.get('template', 'unknown') if location.data else 'unknown',
            'current_weather': location.current_weather,
            'market_open': location.market_open,
            'active': location.active,
            'npc_count': len(location.npc_ids),
            'connections': list(location.get_connections()),
            'data': location.data
        }
        locations_list.append(loc_dict)

    return jsonify({'locations': locations_list})

@app.route('/api/master/location/<location_id>', methods=['PATCH'])
def update_master_location(location_id):
    """Update location properties."""
    w = get_or_create_world()

    if location_id not in w.locations:
        return jsonify({'error': 'Location not found'}), 404

    location = w.locations[location_id]
    data = request.get_json()

    # Update mutable properties
    if 'current_weather' in data:
        location.current_weather = data['current_weather']
    if 'market_open' in data:
        location.market_open = bool(data['market_open'])
    if 'active' in data:
        location.active = bool(data['active'])

    # Update nested data properties
    if 'data' in data:
        for key, value in data['data'].items():
            location.data[key] = value

    # Update connections
    if 'connections' in data:
        location.data['connections'] = data['connections']

    return jsonify({'success': True, 'message': f'Location {location_id} updated'})

@app.route('/api/master/location/<location_id>', methods=['DELETE'])
def delete_master_location(location_id):
    """Delete a location from the world."""
    w = get_or_create_world()

    if location_id not in w.locations:
        return jsonify({'error': 'Location not found'}), 404

    # Move NPCs at this location to the first available location
    if len(w.locations) > 1:
        alternative_location = next(loc_id for loc_id in w.locations.keys() if loc_id != location_id)
        for npc in w.npcs.values():
            if npc.current_location_id == location_id:
                npc.current_location_id = alternative_location
                w.locations[alternative_location].npc_ids.add(npc.id)

    # Remove connections from other locations
    for loc in w.locations.values():
        if 'connections' in loc.data and location_id in loc.data['connections']:
            loc.data['connections'].remove(location_id)

    # Remove from world
    del w.locations[location_id]

    return jsonify({'success': True, 'message': f'Location {location_id} deleted'})

@app.route('/api/master/players', methods=['GET'])
def get_master_players():
    """Get all players for admin viewing/editing."""
    database = get_db()

    # Get all players from database
    with database._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, character_name, race, class, level,
                   experience, gold, current_location_id, created_at, last_login
            FROM players
            ORDER BY created_at DESC
        """)

        players = [dict(row) for row in cursor.fetchall()]

        # Enrich with stats
        for player in players:
            stats = database.get_player_stats(player['id'])
            player['stats'] = stats

            # Get profession count
            professions = database.get_player_professions(player['id'])
            player['profession_count'] = len(professions)

            # Get inventory count
            inventory = database.get_player_inventory(player['id'])
            player['inventory_count'] = len(inventory)

    return jsonify({'players': players})

@app.route('/api/master/player/<int:player_id>', methods=['PATCH'])
def update_master_player(player_id):
    """Update player properties (admin)."""
    database = get_db()
    data = request.get_json()

    # Update player basic data
    player_updates = {}
    for field in ['character_name', 'race', 'class', 'level', 'experience', 'gold', 'current_location_id']:
        if field in data:
            player_updates[field] = data[field]

    if player_updates:
        database.update_player(player_id, player_updates)

    # Update stats
    if 'stats' in data:
        database.update_player_stats(player_id, data['stats'])

    return jsonify({'success': True, 'message': f'Player {player_id} updated'})

@app.route('/api/master/player/<int:player_id>', methods=['DELETE'])
def delete_master_player(player_id):
    """Delete a player (admin)."""
    database = get_db()

    with database._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Player not found'}), 404

    return jsonify({'success': True, 'message': f'Player {player_id} deleted'})

@app.route('/api/master/events/clear', methods=['POST'])
def master_clear_events():
    """Clear event history."""
    w = get_or_create_world()

    count = len(w.event_system.event_history)
    w.event_system.event_history.clear()

    return jsonify({
        'success': True,
        'message': f'Cleared {count} events'
    })

@app.route('/api/master/player/<int:player_id>/inventory', methods=['GET'])
def get_master_player_inventory(player_id):
    """Get player inventory (admin)."""
    database = get_db()
    inventory = database.get_player_inventory(player_id)

    # Parse JSON data field for each item
    for item in inventory:
        if 'data' in item and isinstance(item['data'], str):
            try:
                item['item_data'] = json.loads(item['data'])
            except json.JSONDecodeError:
                item['item_data'] = {}

    return jsonify({'success': True, 'inventory': inventory})

@app.route('/api/master/player/<int:player_id>/inventory', methods=['POST'])
def add_master_player_inventory(player_id):
    """Add item to player inventory (admin)."""
    database = get_db()
    data = request.get_json()

    required_fields = ['item_name', 'item_type', 'item_data']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        inventory_id = database.add_to_inventory(
            player_id=player_id,
            item_name=data['item_name'],
            item_type=data['item_type'],
            item_data=data['item_data'],
            quantity=data.get('quantity', 1)
        )

        # Update equipped status if specified
        if 'equipped' in data and data['equipped']:
            database.update_inventory_item(inventory_id, player_id, {'equipped': 1})

        return jsonify({
            'success': True,
            'message': 'Item added to inventory',
            'inventory_id': inventory_id
        }), 201

    except Exception as e:
        return jsonify({'error': f'Failed to add item: {str(e)}'}), 500

@app.route('/api/master/player/<int:player_id>/inventory/<int:inventory_id>', methods=['PATCH'])
def update_master_player_inventory(player_id, inventory_id):
    """Update inventory item (admin)."""
    database = get_db()
    data = request.get_json()

    success = database.update_inventory_item(inventory_id, player_id, data)
    if not success:
        return jsonify({'error': 'Failed to update item'}), 500

    return jsonify({'success': True, 'message': 'Item updated'})

@app.route('/api/master/player/<int:player_id>/inventory/<int:inventory_id>', methods=['DELETE'])
def delete_master_player_inventory(player_id, inventory_id):
    """Delete inventory item (admin)."""
    database = get_db()

    success = database.remove_from_inventory(player_id, inventory_id)
    if not success:
        return jsonify({'error': 'Failed to delete item'}), 500

    return jsonify({'success': True, 'message': 'Item deleted'})

@app.route('/api/master/items/generate', methods=['POST'])
def generate_items():
    """Generate random items using the GenerationEngine."""
    data = request.get_json()

    template = data.get('template', 'weapon_melee')
    count = int(data.get('count', 1))
    constraints = data.get('constraints', {})

    # Validate count
    if count < 1 or count > 100:
        return jsonify({'error': 'Count must be between 1 and 100'}), 400

    try:
        generated_items = []
        for _ in range(count):
            item = generator.generate_item(template, constraints)
            generated_items.append(item)

        return jsonify({
            'success': True,
            'items': generated_items,
            'count': len(generated_items)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to generate items: {str(e)}'}), 500

@app.route('/api/master/items/templates', methods=['GET'])
def get_item_templates():
    """Get available item templates."""
    try:
        # Read item templates file
        templates_file = project_root / "data" / "item_templates.json"
        with open(templates_file, 'r') as f:
            templates = json.load(f)

        # Return template names and basic info
        template_info = {}
        for name, template in templates.items():
            template_info[name] = {
                'type': template.get('type', 'unknown'),
                'subtype': template.get('subtype', ''),
                'base_names': template.get('base_names', [])
            }

        return jsonify({
            'success': True,
            'templates': template_info
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get templates: {str(e)}'}), 500

# ============================================================================
# WebSocket Events
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"Client connected: {request.sid}")

    # Send initial world state to newly connected client
    w = get_or_create_world()

    emit('connected', {
        'message': 'Connected to R-Gen game server',
        'world_name': w.name
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f"Client disconnected: {request.sid}")

@socketio.on('request_update')
def handle_request_update():
    """Handle client request for immediate world update."""
    if world is None:
        emit('error', {'message': 'World not initialized'})
        return

    # Get recent events and format them
    recent_events = world.event_system.get_recent_events(10)
    event_strings = []
    for event in recent_events:
        event_str = format_event(event, world)
        if event_str:
            event_strings.append(event_str)

    world_update = {
        'time': {
            'day': world.time_manager.current_day,
            'season': world.time_manager.current_season,
            'time_string': world.time_manager.get_time_string(),
            'is_day': world.time_manager.is_daytime
        },
        'recent_events': event_strings,
        'timestamp': datetime.now().isoformat()
    }

    emit('world_update', world_update)

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    print("="*60)
    print("R-Gen Game Server")
    print("="*60)
    print("\nStarting server...")
    print("Game will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop\n")

    # Create world on startup
    get_or_create_world()

    # Start Flask-SocketIO server
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
