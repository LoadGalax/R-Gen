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

# Set up paths
project_root = Path(__file__).parent.parent  # Go up one level from Game/ to R-Gen/

# Import all game logic from local src module (fully self-contained)
from src import ContentGenerator, World, LivingNPC as NPC, LivingLocation as Location
from game_database import GameDatabase

# Client folder is in the Game directory
client_folder = Path(__file__).parent / "Client"
app = Flask(__name__, static_folder=str(client_folder), static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
# Use the Game's own data directory (detached from GenerationEngine)
# These JSONs are copied from GenerationEngine and can be customized per game
data_dir = project_root / "Game" / "data"
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
        # World is imported from local src module
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

@app.route('/api/master/settings', methods=['GET'])
def get_settings():
    """Get all system settings."""
    database = get_db()
    settings = database.get_all_settings()
    return jsonify(settings)

@app.route('/api/master/settings', methods=['PATCH'])
def update_settings():
    """Update system settings."""
    database = get_db()
    data = request.get_json()

    for key, value in data.items():
        database.set_setting(key, str(value))

    return jsonify({'success': True, 'message': 'Settings updated'})

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
            'entity_type': npc.entity_type,
            'max_health': npc.max_health,
            'current_health': npc.current_health,
            'attack_power': npc.attack_power,
            'defense': npc.defense,
            'experience_reward': npc.experience_reward,
            'loot_table_id': npc.loot_table_id,
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
    if 'entity_type' in data:
        npc.entity_type = data['entity_type']
    if 'max_health' in data:
        npc.max_health = int(data['max_health'])
    if 'current_health' in data:
        npc.current_health = int(data['current_health'])
    if 'attack_power' in data:
        npc.attack_power = int(data['attack_power'])
    if 'defense' in data:
        npc.defense = int(data['defense'])
    if 'experience_reward' in data:
        npc.experience_reward = int(data['experience_reward'])
    if 'loot_table_id' in data:
        npc.loot_table_id = data['loot_table_id']

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

@app.route('/api/master/npc', methods=['POST'])
def create_master_npc():
    """Create a new NPC or Enemy."""
    w = get_or_create_world()
    data = request.get_json()

    name = data.get('name', 'Unknown NPC')
    professions = data.get('professions', None)
    location_id = data.get('location_id')
    entity_type = data.get('entity_type', 'npc')

    # Generate NPC data
    if w.generator_adapter:
        npc_data = w.generator_adapter.spawn_npc(
            professions=professions,
            location_id=location_id
        )
        # Override name if provided
        npc_data['name'] = name
        npc_data['entity_type'] = entity_type

        # Set enemy-specific properties if creating an enemy
        if entity_type == 'enemy':
            npc_data['max_health'] = data.get('max_health', 100)
            npc_data['current_health'] = npc_data['max_health']
            npc_data['attack_power'] = data.get('attack_power', 15)
            npc_data['defense'] = data.get('defense', 8)
            npc_data['experience_reward'] = data.get('experience_reward', 100)
            npc_data['loot_table_id'] = data.get('loot_table_id')

        # Create NPC entity
        npc = w.spawn_npc(npc_data)

        return jsonify({
            'success': True,
            'message': f'{entity_type.title()} {name} created',
            'npc_id': npc.id
        })
    else:
        return jsonify({'error': 'Generator not available'}), 500

@app.route('/api/master/enemy', methods=['POST'])
def create_master_enemy():
    """
    Create a new Enemy using race + profession system.

    Enemies are generated using race (what they are) and profession (what they do):
    - Races: goblin, orc, skeleton, zombie, wolf, human, etc.
    - Professions: warrior, bandit, cultist, thief, or none for beasts

    Examples:
    - goblin + warrior = goblin warrior
    - skeleton + (no profession) = skeleton
    - human + bandit = human bandit
    - wolf + (no profession) = wolf (beasts don't need professions)
    """
    w = get_or_create_world()
    data = request.get_json()

    # Race determines what the enemy IS
    race = data.get('race', 'goblin')  # goblin, skeleton, orc, zombie, wolf, human, etc.

    # Profession determines what the enemy DOES (optional for beasts)
    profession = data.get('profession', None)  # warrior, bandit, cultist, thief, or None

    # If profession is provided as a string, convert to list
    if profession and isinstance(profession, str):
        professions = [profession] if profession else []
    elif profession:
        professions = profession
    else:
        professions = []

    # Auto-assign default professions for certain races if not specified
    if not professions:
        default_professions = {
            'goblin': ['warrior'],
            'orc': ['warrior'],
            'skeleton': [],  # No profession for undead
            'zombie': [],    # No profession for undead
            'wolf': [],      # No profession for beasts
        }
        professions = default_professions.get(race, ['warrior'])

    location_id = data.get('location_id')
    custom_name = data.get('name')  # Optional custom name

    # Enemy difficulty level affects stats
    difficulty = data.get('difficulty', 'standard')  # minion, standard, elite, boss

    # Difficulty multipliers for stats
    difficulty_multipliers = {
        'minion': 0.5,
        'standard': 1.0,
        'elite': 1.5,
        'boss': 2.5
    }
    multiplier = difficulty_multipliers.get(difficulty, 1.0)

    # Generate enemy data using race + profession
    if w.generator_adapter:
        enemy_data = w.generator_adapter.spawn_npc(
            professions=professions,
            race=race,
            location_id=location_id
        )

        # Override name if custom name provided
        if custom_name:
            enemy_data['name'] = custom_name

        # Set entity type to enemy
        enemy_data['entity_type'] = 'enemy'
        enemy_data['enemy_type'] = difficulty

        # Calculate enemy stats based on base stats and difficulty
        base_health = enemy_data.get('stats', {}).get('Constitution', 5) * 10
        base_attack = enemy_data.get('stats', {}).get('Strength', 5) + 5
        base_defense = enemy_data.get('stats', {}).get('Constitution', 5)

        enemy_data['max_health'] = int(base_health * multiplier)
        enemy_data['current_health'] = enemy_data['max_health']
        enemy_data['attack_power'] = int(base_attack * multiplier)
        enemy_data['defense'] = int(base_defense * multiplier)
        enemy_data['experience_reward'] = int(50 * multiplier * (1 + enemy_data.get('challenge_rating', 1)))

        # Allow manual overrides
        if 'max_health' in data:
            enemy_data['max_health'] = data['max_health']
            enemy_data['current_health'] = enemy_data['max_health']
        if 'attack_power' in data:
            enemy_data['attack_power'] = data['attack_power']
        if 'defense' in data:
            enemy_data['defense'] = data['defense']
        if 'experience_reward' in data:
            enemy_data['experience_reward'] = data['experience_reward']

        # Create enemy entity
        enemy = w.spawn_npc(enemy_data)

        profession_text = f" {professions[0].title()}" if professions else ""
        return jsonify({
            'success': True,
            'message': f'{difficulty.title()} {race.title()}{profession_text} created',
            'enemy_id': enemy.id,
            'enemy_data': {
                'name': enemy_data['name'],
                'race': enemy_data.get('race'),
                'professions': enemy_data.get('professions', []),
                'max_health': enemy_data['max_health'],
                'attack_power': enemy_data['attack_power'],
                'defense': enemy_data['defense'],
                'experience_reward': enemy_data['experience_reward'],
                'inventory': enemy_data.get('inventory', [])
            }
        })
    else:
        return jsonify({'error': 'Generator not available'}), 500

@app.route('/api/master/npc/<npc_id>/inventory', methods=['GET'])
def get_npc_inventory(npc_id):
    """Get NPC inventory."""
    w = get_or_create_world()

    if npc_id not in w.npcs:
        return jsonify({'error': 'NPC not found'}), 404

    npc = w.npcs[npc_id]
    inventory = npc.data.get('inventory', [])

    return jsonify({'inventory': inventory})

@app.route('/api/master/npc/<npc_id>/inventory', methods=['POST'])
def add_npc_inventory_item(npc_id):
    """Add item to NPC inventory."""
    w = get_or_create_world()

    if npc_id not in w.npcs:
        return jsonify({'error': 'NPC not found'}), 404

    npc = w.npcs[npc_id]
    data = request.get_json()

    item = {
        'name': data.get('name', 'Unknown Item'),
        'type': data.get('type', 'misc'),
        'subtype': data.get('subtype'),
        'quality': data.get('quality', 'common'),
        'quantity': data.get('quantity', 1),
        'value': data.get('value', 0),
    }

    # Add optional fields if present
    if 'material' in data:
        item['material'] = data['material']
    if 'rarity' in data:
        item['rarity'] = data['rarity']

    if 'inventory' not in npc.data:
        npc.data['inventory'] = []

    npc.data['inventory'].append(item)

    return jsonify({'success': True, 'message': 'Item added to NPC inventory'})

@app.route('/api/master/npc/<npc_id>/inventory/<int:item_index>', methods=['DELETE'])
def delete_npc_inventory_item(npc_id, item_index):
    """Remove item from NPC inventory."""
    w = get_or_create_world()

    if npc_id not in w.npcs:
        return jsonify({'error': 'NPC not found'}), 404

    npc = w.npcs[npc_id]
    inventory = npc.data.get('inventory', [])

    if item_index < 0 or item_index >= len(inventory):
        return jsonify({'error': 'Invalid item index'}), 400

    removed_item = inventory.pop(item_index)

    return jsonify({
        'success': True,
        'message': f'Removed {removed_item.get("name", "item")} from inventory'
    })

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

@app.route('/api/master/location', methods=['POST'])
def create_master_location():
    """Create a new location."""
    w = get_or_create_world()
    data = request.get_json()

    name = data.get('name', 'Unknown Location')
    template = data.get('template', 'settlement')
    description = data.get('description', '')
    connections = data.get('connections', [])
    npc_ids = data.get('npc_ids', [])

    # Generate location data
    if w.generator_adapter:
        location_data = w.generator_adapter.spawn_location(
            template=template
        )
        # Override properties if provided
        location_data['name'] = name
        location_data['description'] = description
        location_data['connections'] = connections

        # Create location entity
        location = w.spawn_location(location_data)

        # Assign NPCs to this location
        for npc_id in npc_ids:
            if npc_id in w.npcs:
                npc = w.npcs[npc_id]
                old_location = npc.current_location_id
                npc.current_location_id = location.id

                # Update location tracking
                if old_location and old_location in w.locations:
                    w.locations[old_location].npc_ids.discard(npc_id)
                location.npc_ids.add(npc_id)

        return jsonify({
            'success': True,
            'message': f'Location {name} created',
            'location_id': location.id
        })
    else:
        return jsonify({'error': 'Generator not available'}), 500

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

@app.route('/api/master/items/save', methods=['POST'])
def save_generated_items():
    """Save generated items to the database."""
    data = request.get_json()
    items = data.get('items', [])

    if not items:
        return jsonify({'error': 'No items provided'}), 400

    try:
        database = get_db()
        saved_count = 0
        saved_ids = []

        for item in items:
            # Save to game database
            item_name = item.get('name', 'Unknown Item')
            item_type = item.get('type', 'misc')
            item_data = item  # Store the entire item object as data

            item_id = database.save_generated_item(item_name, item_type, item_data)
            saved_ids.append(item_id)
            saved_count += 1

        return jsonify({
            'success': True,
            'message': f'Saved {saved_count} items',
            'count': saved_count,
            'ids': saved_ids
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to save items: {str(e)}'}), 500

@app.route('/api/master/items/templates', methods=['GET'])
def get_item_templates():
    """Get available item templates."""
    try:
        # Read item templates file from Game's data directory
        templates_file = project_root / "Game" / "data" / "item_templates.json"
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

@app.route('/api/master/items', methods=['GET'])
def get_all_items():
    """Get all items from all player inventories."""
    database = get_db()

    try:
        items = database.get_all_items()

        # Parse JSON data field for each item
        for item in items:
            if item.get('data'):
                try:
                    item['data'] = json.loads(item['data'])
                except:
                    item['data'] = {}

        return jsonify({
            'success': True,
            'items': items,
            'count': len(items)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get items: {str(e)}'}), 500

@app.route('/api/master/items/saved', methods=['GET'])
def get_saved_items():
    """Get all saved/generated items from the game database."""
    try:
        database = get_db()

        # Get all generated items
        items = database.get_all_generated_items()

        return jsonify({
            'success': True,
            'items': items,
            'count': len(items)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get saved items: {str(e)}'}), 500

@app.route('/api/master/items/generated', methods=['GET'])
def get_generated_items():
    """Get all generated items (for loot table selection, etc)."""
    try:
        database = get_db()
        items = database.get_all_generated_items()

        return jsonify({
            'success': True,
            'items': items,
            'count': len(items)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get generated items: {str(e)}'}), 500

@app.route('/api/master/loot_tables', methods=['GET'])
def get_loot_tables():
    """Get all loot tables."""
    w = get_or_create_world()

    # Initialize loot_tables if not exists
    if not hasattr(w, 'loot_tables'):
        w.loot_tables = {}

    return jsonify({
        'success': True,
        'loot_tables': w.loot_tables
    })

@app.route('/api/master/loot_table', methods=['POST'])
def create_loot_table():
    """Create a new loot table."""
    w = get_or_create_world()
    data = request.get_json()

    # Initialize loot_tables if not exists
    if not hasattr(w, 'loot_tables'):
        w.loot_tables = {}

    loot_table_id = data.get('id') or f"loot_table_{len(w.loot_tables) + 1}"

    loot_table = {
        'id': loot_table_id,
        'name': data.get('name', 'Unnamed Loot Table'),
        'description': data.get('description', ''),
        'items': data.get('items', [])  # List of {item_name, drop_chance, quantity_min, quantity_max}
    }

    w.loot_tables[loot_table_id] = loot_table

    return jsonify({
        'success': True,
        'message': f'Loot table {loot_table["name"]} created',
        'loot_table_id': loot_table_id
    })

@app.route('/api/master/loot_table/<loot_table_id>', methods=['PATCH'])
def update_loot_table(loot_table_id):
    """Update an existing loot table."""
    w = get_or_create_world()
    data = request.get_json()

    if not hasattr(w, 'loot_tables'):
        w.loot_tables = {}

    if loot_table_id not in w.loot_tables:
        return jsonify({'error': 'Loot table not found'}), 404

    loot_table = w.loot_tables[loot_table_id]

    if 'name' in data:
        loot_table['name'] = data['name']
    if 'description' in data:
        loot_table['description'] = data['description']
    if 'items' in data:
        loot_table['items'] = data['items']

    return jsonify({
        'success': True,
        'message': f'Loot table {loot_table_id} updated'
    })

@app.route('/api/master/loot_table/<loot_table_id>', methods=['DELETE'])
def delete_loot_table(loot_table_id):
    """Delete a loot table."""
    w = get_or_create_world()

    if not hasattr(w, 'loot_tables'):
        w.loot_tables = {}

    if loot_table_id not in w.loot_tables:
        return jsonify({'error': 'Loot table not found'}), 404

    del w.loot_tables[loot_table_id]

    return jsonify({
        'success': True,
        'message': f'Loot table {loot_table_id} deleted'
    })

@app.route('/api/master/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete an item from inventory (admin)."""
    database = get_db()

    try:
        # Get item to find player_id
        with database._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT player_id FROM player_inventory WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Item not found'}), 404
            player_id = row['player_id']

        # Delete the item
        success = database.remove_from_inventory(player_id, item_id)
        if not success:
            return jsonify({'error': 'Failed to delete item'}), 500

        return jsonify({'success': True, 'message': 'Item deleted'}), 200

    except Exception as e:
        return jsonify({'error': f'Failed to delete item: {str(e)}'}), 500

@app.route('/api/master/database/export', methods=['GET'])
def export_database():
    """Export the entire database as JSON."""
    database = get_db()
    w = get_or_create_world()

    try:
        export_data = {
            'export_date': datetime.now().isoformat(),
            'world': {
                'name': w.name,
                'description': getattr(w, 'description', ''),
                'seed': w.seed,
                'time_of_day': w.time_of_day,
                'current_day': w.current_day,
                'npcs': [],
                'locations': [],
                'events': []
            },
            'players': [],
            'generated_items': []
        }

        # Export NPCs
        for npc_id, npc in w.npcs.items():
            npc_data = {
                'id': npc.id,
                'name': npc.name,
                'entity_type': getattr(npc, 'entity_type', 'npc'),
                'profession': npc.profession,
                'professions': npc.professions if hasattr(npc, 'professions') else [npc.profession],
                'current_location_id': npc.current_location_id,
                'energy': npc.energy,
                'hunger': npc.hunger,
                'mood': npc.mood,
                'gold': npc.gold,
                'current_activity': npc.current_activity,
                'work_start_hour': npc.work_start_hour,
                'work_end_hour': npc.work_end_hour,
                'active': npc.active,
                'inventory': npc.inventory,
                'relationships': getattr(npc, 'relationships', {})
            }
            # Add enemy-specific fields if applicable
            if hasattr(npc, 'max_health'):
                npc_data['max_health'] = npc.max_health
                npc_data['health'] = getattr(npc, 'health', npc.max_health)
                npc_data['attack_power'] = getattr(npc, 'attack_power', 0)
                npc_data['defense'] = getattr(npc, 'defense', 0)
                npc_data['experience_reward'] = getattr(npc, 'experience_reward', 0)
                npc_data['loot_table_id'] = getattr(npc, 'loot_table_id', None)
            export_data['world']['npcs'].append(npc_data)

        # Export locations
        for loc_id, loc in w.locations.items():
            loc_data = {
                'id': loc.id,
                'name': loc.name,
                'template': loc.template,
                'description': getattr(loc, 'description', ''),
                'current_weather': loc.current_weather,
                'market_open': loc.market_open,
                'active': loc.active,
                'npc_ids': [npc_id for npc_id, npc in w.npcs.items() if npc.current_location_id == loc.id]
            }
            export_data['world']['locations'].append(loc_data)

        # Export events
        if hasattr(w, 'events'):
            for event in w.events:
                event_data = {
                    'timestamp': event.timestamp.isoformat() if hasattr(event.timestamp, 'isoformat') else str(event.timestamp),
                    'event_type': event.event_type,
                    'description': event.description,
                    'entities': event.entities,
                    'location_id': getattr(event, 'location_id', None)
                }
                export_data['world']['events'].append(event_data)

        # Export loot tables
        if hasattr(w, 'loot_tables'):
            export_data['world']['loot_tables'] = w.loot_tables

        # Export players from database
        with database._get_connection() as conn:
            cursor = conn.cursor()

            # Get all players with stats
            cursor.execute("""
                SELECT p.*, ps.*
                FROM players p
                LEFT JOIN player_stats ps ON p.id = ps.player_id
            """)
            players = cursor.fetchall()

            for player in players:
                player_id = player['id']
                player_data = {
                    'id': player_id,
                    'username': player['username'],
                    'email': player['email'],
                    'character_name': player['character_name'],
                    'race': player['race'],
                    'class': player['class'],
                    'level': player['level'],
                    'experience': player['experience'],
                    'gold': player['gold'],
                    'current_location_id': player['current_location_id'],
                    'stats': {
                        'health': player['health'],
                        'max_health': player['max_health'],
                        'mana': player['mana'],
                        'max_mana': player['max_mana'],
                        'energy': player['energy'],
                        'max_energy': player['max_energy'],
                        'strength': player['strength'],
                        'dexterity': player['dexterity'],
                        'intelligence': player['intelligence'],
                        'constitution': player['constitution'],
                        'wisdom': player['wisdom'],
                        'charisma': player['charisma']
                    } if player.get('health') is not None else {},
                    'inventory': [],
                    'professions': []
                }

                # Get player inventory
                cursor.execute("SELECT * FROM player_inventory WHERE player_id = ?", (player_id,))
                for item in cursor.fetchall():
                    item_data = json.loads(item['data']) if item['data'] else {}
                    player_data['inventory'].append({
                        'item_name': item['item_name'],
                        'item_type': item['item_type'],
                        'quantity': item['quantity'],
                        'equipped': item['equipped'],
                        'data': item_data
                    })

                # Get player professions
                cursor.execute("SELECT * FROM player_professions WHERE player_id = ?", (player_id,))
                for prof in cursor.fetchall():
                    player_data['professions'].append({
                        'profession_id': prof['profession_id'],
                        'level': prof['level'],
                        'experience': prof['experience']
                    })

                export_data['players'].append(player_data)

            # Export generated items
            cursor.execute("SELECT * FROM generated_items")
            for item in cursor.fetchall():
                export_data['generated_items'].append({
                    'id': item['id'],
                    'item_name': item['item_name'],
                    'item_type': item['item_type'],
                    'data': json.loads(item['data']) if item['data'] else {}
                })

        return jsonify({'success': True, 'data': export_data}), 200

    except Exception as e:
        return jsonify({'error': f'Failed to export database: {str(e)}'}), 500

@app.route('/api/master/database/import', methods=['POST'])
def import_database():
    """Import database from JSON."""
    database = get_db()
    w = get_or_create_world()

    try:
        import_data = request.json.get('data', {})

        if not import_data:
            return jsonify({'error': 'No data provided'}), 400

        imported_counts = {
            'npcs': 0,
            'locations': 0,
            'players': 0,
            'items': 0
        }

        # Import world data
        if 'world' in import_data:
            world_data = import_data['world']

            # Update world properties
            if 'name' in world_data:
                w.name = world_data['name']
            if 'description' in world_data:
                w.description = world_data['description']

            # Import NPCs (merge with existing)
            if 'npcs' in world_data:
                for npc_data in world_data['npcs']:
                    npc_id = npc_data['id']
                    if npc_id not in w.npcs:
                        # Create new NPC (imported from local src module)
                        npc = NPC(
                            id=npc_id,
                            name=npc_data['name'],
                            professions=npc_data.get('professions', [npc_data.get('profession', 'wanderer')]),
                            current_location_id=npc_data.get('current_location_id')
                        )
                        npc.energy = npc_data.get('energy', 100)
                        npc.hunger = npc_data.get('hunger', 50)
                        npc.mood = npc_data.get('mood', 70)
                        npc.gold = npc_data.get('gold', 0)
                        npc.current_activity = npc_data.get('current_activity', 'idle')
                        npc.work_start_hour = npc_data.get('work_start_hour', 8)
                        npc.work_end_hour = npc_data.get('work_end_hour', 18)
                        npc.active = npc_data.get('active', True)
                        npc.inventory = npc_data.get('inventory', [])
                        npc.entity_type = npc_data.get('entity_type', 'npc')

                        # Add enemy-specific fields
                        if 'max_health' in npc_data:
                            npc.max_health = npc_data['max_health']
                            npc.health = npc_data.get('health', npc_data['max_health'])
                            npc.attack_power = npc_data.get('attack_power', 0)
                            npc.defense = npc_data.get('defense', 0)
                            npc.experience_reward = npc_data.get('experience_reward', 0)
                            npc.loot_table_id = npc_data.get('loot_table_id')

                        w.npcs[npc_id] = npc
                        imported_counts['npcs'] += 1

            # Import locations (merge with existing)
            if 'locations' in world_data:
                for loc_data in world_data['locations']:
                    loc_id = loc_data['id']
                    if loc_id not in w.locations:
                        # Location imported from local src module
                        loc = Location(
                            id=loc_id,
                            name=loc_data['name'],
                            template=loc_data.get('template', 'settlement')
                        )
                        loc.description = loc_data.get('description', '')
                        loc.current_weather = loc_data.get('current_weather', 'Clear')
                        loc.market_open = loc_data.get('market_open', False)
                        loc.active = loc_data.get('active', True)
                        w.locations[loc_id] = loc
                        imported_counts['locations'] += 1

            # Import loot tables
            if 'loot_tables' in world_data:
                if not hasattr(w, 'loot_tables'):
                    w.loot_tables = {}
                w.loot_tables.update(world_data['loot_tables'])

        # Import players
        if 'players' in import_data:
            with database._get_connection() as conn:
                cursor = conn.cursor()

                for player_data in import_data['players']:
                    username = player_data['username']

                    # Check if player exists
                    cursor.execute("SELECT id FROM players WHERE username = ?", (username,))
                    existing = cursor.fetchone()

                    if not existing:
                        # Create new player (note: password will need to be reset)
                        from werkzeug.security import generate_password_hash
                        cursor.execute("""
                            INSERT INTO players (username, password_hash, email, character_name, race, class, level, experience, gold, current_location_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            username,
                            generate_password_hash('changeme'),  # Default password
                            player_data.get('email', f'{username}@imported.com'),
                            player_data['character_name'],
                            player_data.get('race', 'Human'),
                            player_data.get('class', 'Adventurer'),
                            player_data.get('level', 1),
                            player_data.get('experience', 0),
                            player_data.get('gold', 100),
                            player_data.get('current_location_id')
                        ))

                        player_id = cursor.lastrowid

                        # Insert player stats
                        if 'stats' in player_data and player_data['stats']:
                            stats = player_data['stats']
                            cursor.execute("""
                                INSERT INTO player_stats (player_id, health, max_health, mana, max_mana, energy, max_energy,
                                    strength, dexterity, intelligence, constitution, wisdom, charisma)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                player_id,
                                stats.get('health', 100),
                                stats.get('max_health', 100),
                                stats.get('mana', 100),
                                stats.get('max_mana', 100),
                                stats.get('energy', 100),
                                stats.get('max_energy', 100),
                                stats.get('strength', 10),
                                stats.get('dexterity', 10),
                                stats.get('intelligence', 10),
                                stats.get('constitution', 10),
                                stats.get('wisdom', 10),
                                stats.get('charisma', 10)
                            ))

                        # Import inventory
                        for item in player_data.get('inventory', []):
                            cursor.execute("""
                                INSERT INTO player_inventory (player_id, item_name, item_type, quantity, equipped, data)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                                player_id,
                                item['item_name'],
                                item['item_type'],
                                item.get('quantity', 1),
                                item.get('equipped', 0),
                                json.dumps(item.get('data', {}))
                            ))

                        # Import professions
                        for prof in player_data.get('professions', []):
                            cursor.execute("""
                                INSERT INTO player_professions (player_id, profession_id, level, experience)
                                VALUES (?, ?, ?, ?)
                            """, (
                                player_id,
                                prof['profession_id'],
                                prof.get('level', 1),
                                prof.get('experience', 0)
                            ))

                        imported_counts['players'] += 1

                conn.commit()

        # Import generated items
        if 'generated_items' in import_data:
            with database._get_connection() as conn:
                cursor = conn.cursor()

                for item in import_data['generated_items']:
                    cursor.execute("""
                        INSERT INTO generated_items (item_name, item_type, data)
                        VALUES (?, ?, ?)
                    """, (
                        item['item_name'],
                        item['item_type'],
                        json.dumps(item.get('data', {}))
                    ))
                    imported_counts['items'] += 1

                conn.commit()

        return jsonify({
            'success': True,
            'message': f'Database imported successfully',
            'imported': imported_counts
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to import database: {str(e)}'}), 500

@app.route('/api/master/database/clear', methods=['POST'])
def clear_database():
    """Clear all data from the database and world."""
    database = get_db()
    w = get_or_create_world()

    try:
        # Clear world data
        w.npcs.clear()
        w.locations.clear()
        if hasattr(w, 'events'):
            w.events.clear()
        if hasattr(w, 'loot_tables'):
            w.loot_tables.clear()

        # Clear database tables
        with database._get_connection() as conn:
            cursor = conn.cursor()

            # Clear all tables (CASCADE will handle related records)
            cursor.execute("DELETE FROM players")
            cursor.execute("DELETE FROM player_stats")
            cursor.execute("DELETE FROM player_inventory")
            cursor.execute("DELETE FROM player_professions")
            cursor.execute("DELETE FROM generated_items")

            conn.commit()

        return jsonify({
            'success': True,
            'message': 'All data has been cleared from the database'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to clear database: {str(e)}'}), 500

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
