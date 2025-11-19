#!/usr/bin/env python3
"""
R-Gen Game Server - Flask + WebSocket server for the web game
Provides REST API and real-time simulation updates via WebSocket
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import os
import sys
import threading
import time
from pathlib import Path
from datetime import datetime

# Add engines to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from GenerationEngine import ContentGenerator, DatabaseManager
from SimulationEngine import World, WorldSimulator

app = Flask(__name__, static_folder='Client', static_url_path='')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
generator = ContentGenerator()
db = None
world = None
simulator = None
simulation_thread = None
simulation_running = False

def get_db():
    """Get or create database instance."""
    global db
    if db is None:
        db = DatabaseManager()
    return db

def get_or_create_world():
    """Get or create world instance."""
    global world, simulator
    if world is None:
        print("Creating new world...")
        world = World.create_new(num_locations=10, seed=42, name="Fantasy Realm")
        simulator = WorldSimulator(world)
        print(f"World created with {len(world.locations)} locations and {len(world.npcs)} NPCs")
    return world, simulator

# ============================================================================
# Static File Serving
# ============================================================================

@app.route('/')
def serve_game():
    """Serve the main game page."""
    return send_from_directory('Client', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('Client', path)

# ============================================================================
# REST API Endpoints
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'world_active': world is not None,
        'simulation_running': simulation_running
    })

@app.route('/api/world/info', methods=['GET'])
def get_world_info():
    """Get current world information."""
    w, sim = get_or_create_world()

    return jsonify({
        'name': w.name,
        'current_time': {
            'day': w.time_manager.get_current_day(),
            'season': w.time_manager.get_current_season(),
            'time': w.time_manager.get_time_string(),
            'is_day': w.time_manager.is_day()
        },
        'stats': {
            'total_locations': len(w.locations),
            'total_npcs': len(w.npcs),
            'total_events': len(w.event_history)
        }
    })

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Get all locations."""
    w, sim = get_or_create_world()

    locations = []
    for loc_id, location in w.locations.items():
        loc_data = location.to_dict()
        # Add NPCs at this location
        npcs_here = [npc_id for npc_id, npc in w.npcs.items()
                     if npc.get_current_location() == loc_id]
        loc_data['npcs'] = npcs_here
        loc_data['npc_count'] = len(npcs_here)
        locations.append(loc_data)

    return jsonify({'locations': locations})

@app.route('/api/location/<location_id>', methods=['GET'])
def get_location_details(location_id):
    """Get detailed information about a specific location."""
    w, sim = get_or_create_world()

    if location_id not in w.locations:
        return jsonify({'error': 'Location not found'}), 404

    location = w.locations[location_id]
    loc_data = location.to_dict()

    # Add NPCs at this location with full details
    npcs_here = []
    for npc_id, npc in w.npcs.items():
        if npc.get_current_location() == location_id:
            npc_data = npc.to_dict()
            npc_data['id'] = npc_id
            npcs_here.append(npc_data)

    loc_data['npcs'] = npcs_here
    loc_data['weather'] = location.get_weather()

    # Add connected locations
    connections = []
    for conn_id in location.get_connections():
        if conn_id in w.locations:
            conn_loc = w.locations[conn_id]
            connections.append({
                'id': conn_id,
                'name': conn_loc.get_name(),
                'template': conn_loc.template
            })
    loc_data['connections'] = connections

    return jsonify(loc_data)

@app.route('/api/npcs', methods=['GET'])
def get_npcs():
    """Get all NPCs."""
    w, sim = get_or_create_world()

    npcs = []
    for npc_id, npc in w.npcs.items():
        npc_data = npc.to_dict()
        npc_data['id'] = npc_id
        npc_data['location_id'] = npc.get_current_location()
        if npc.get_current_location() in w.locations:
            npc_data['location_name'] = w.locations[npc.get_current_location()].get_name()
        npcs.append(npc_data)

    return jsonify({'npcs': npcs})

@app.route('/api/npc/<npc_id>', methods=['GET'])
def get_npc_details(npc_id):
    """Get detailed information about a specific NPC."""
    w, sim = get_or_create_world()

    if npc_id not in w.npcs:
        return jsonify({'error': 'NPC not found'}), 404

    npc = w.npcs[npc_id]
    npc_data = npc.to_dict()
    npc_data['id'] = npc_id
    npc_data['location_id'] = npc.get_current_location()

    if npc.get_current_location() in w.locations:
        npc_data['location_name'] = w.locations[npc.get_current_location()].get_name()

    return jsonify(npc_data)

@app.route('/api/npc/<npc_id>/dialogue', methods=['GET'])
def get_npc_dialogue(npc_id):
    """Get dialogue options for an NPC."""
    w, sim = get_or_create_world()

    if npc_id not in w.npcs:
        return jsonify({'error': 'NPC not found'}), 404

    npc = w.npcs[npc_id]

    # Generate dialogue based on NPC profession and mood
    profession = npc.get_profession()
    mood = npc.get_mood()

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

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get recent events."""
    w, sim = get_or_create_world()

    limit = request.args.get('limit', 50, type=int)
    events = w.event_history[-limit:] if len(w.event_history) > limit else w.event_history

    return jsonify({
        'events': events,
        'total_events': len(w.event_history)
    })

@app.route('/api/player/travel', methods=['POST'])
def player_travel():
    """Move player to a new location."""
    data = request.get_json()
    target_location = data.get('location_id')

    w, sim = get_or_create_world()

    if target_location not in w.locations:
        return jsonify({'error': 'Location not found'}), 404

    # In a real game, you'd track player position
    # For now, just return the new location details
    location = w.locations[target_location]

    # Broadcast to all clients that player moved
    socketio.emit('player_moved', {
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
# Simulation Control
# ============================================================================

@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    """Start the world simulation."""
    global simulation_running, simulation_thread

    if simulation_running:
        return jsonify({'error': 'Simulation already running'}), 400

    get_or_create_world()
    simulation_running = True

    simulation_thread = threading.Thread(target=run_simulation_loop, daemon=True)
    simulation_thread.start()

    return jsonify({'success': True, 'message': 'Simulation started'})

@app.route('/api/simulation/stop', methods=['POST'])
def stop_simulation():
    """Stop the world simulation."""
    global simulation_running

    if not simulation_running:
        return jsonify({'error': 'Simulation not running'}), 400

    simulation_running = False

    return jsonify({'success': True, 'message': 'Simulation stopped'})

@app.route('/api/simulation/status', methods=['GET'])
def simulation_status():
    """Get simulation status."""
    return jsonify({
        'running': simulation_running,
        'world_exists': world is not None
    })

def run_simulation_loop():
    """Main simulation loop that runs in background."""
    global simulation_running, world, simulator

    print("Simulation loop started")

    while simulation_running:
        try:
            # Advance simulation by 30 minutes
            simulator.simulate_minutes(30)

            # Get recent events (last 10)
            recent_events = world.event_history[-10:] if len(world.event_history) > 0 else []

            # Broadcast world update to all connected clients
            world_update = {
                'time': {
                    'day': world.time_manager.get_current_day(),
                    'season': world.time_manager.get_current_season(),
                    'time_string': world.time_manager.get_time_string(),
                    'is_day': world.time_manager.is_day()
                },
                'recent_events': recent_events[-5:],  # Last 5 events
                'timestamp': datetime.now().isoformat()
            }

            socketio.emit('world_update', world_update)

            # Sleep for 5 seconds (real time) before next simulation step
            time.sleep(5)

        except Exception as e:
            print(f"Error in simulation loop: {e}")
            import traceback
            traceback.print_exc()
            simulation_running = False

    print("Simulation loop stopped")

# ============================================================================
# WebSocket Events
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"Client connected: {request.sid}")

    # Send initial world state to newly connected client
    w, sim = get_or_create_world()

    emit('connected', {
        'message': 'Connected to R-Gen game server',
        'world_name': w.name,
        'simulation_running': simulation_running
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

    world_update = {
        'time': {
            'day': world.time_manager.get_current_day(),
            'season': world.time_manager.get_current_season(),
            'time_string': world.time_manager.get_time_string(),
            'is_day': world.time_manager.is_day()
        },
        'recent_events': world.event_history[-10:],
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
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
