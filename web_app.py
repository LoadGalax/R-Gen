#!/usr/bin/env python3
"""
R-Gen Web Interface - Flask web application for content generation

Provides a user-friendly web interface for generating and managing game content.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from pathlib import Path

from src.content_generator import ContentGenerator
from src.database import DatabaseManager

app = Flask(__name__)
CORS(app)

# Initialize generator and database
generator = ContentGenerator()
db = None  # Will be initialized when needed

def get_db():
    """Get or create database instance."""
    global db
    if db is None:
        db = DatabaseManager()
    return db


@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')


@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all available templates."""
    return jsonify({
        'items': list(generator.items_config['templates'].keys()),
        'npcs': list(generator.npcs_config['archetypes'].keys()),
        'locations': list(generator.locations_config['templates'].keys()),
        'item_sets': list(generator.items_config['item_sets'].keys())
    })


@app.route('/api/attributes', methods=['GET'])
def get_attributes():
    """Get available attributes for filtering."""
    return jsonify({
        'quality': list(generator.attributes['quality'].keys()),
        'rarity': list(generator.attributes['rarity'].keys()),
        'materials': generator.attributes['materials'],
        'stats': list(generator.attributes['stats'].keys()),
        'damage_types': generator.attributes['damage_types'],
        'environment_tags': generator.attributes['environment_tags']
    })


@app.route('/api/generate/item', methods=['POST'])
def generate_item():
    """Generate an item with optional constraints."""
    data = request.json or {}

    template = data.get('template')
    seed = data.get('seed')
    save_to_db = data.get('save', False)

    # Build constraints
    constraints = {}
    if data.get('min_quality'):
        constraints['min_quality'] = data['min_quality']
    if data.get('max_quality'):
        constraints['max_quality'] = data['max_quality']
    if data.get('min_rarity'):
        constraints['min_rarity'] = data['min_rarity']
    if data.get('max_rarity'):
        constraints['max_rarity'] = data['max_rarity']
    if data.get('min_value'):
        constraints['min_value'] = int(data['min_value'])
    if data.get('max_value'):
        constraints['max_value'] = int(data['max_value'])
    if data.get('exclude_materials'):
        constraints['exclude_materials'] = data['exclude_materials']
    if data.get('required_stats'):
        constraints['required_stats'] = data['required_stats']

    # Set seed if provided
    if seed is not None:
        generator.reset_seed(int(seed))

    try:
        item = generator.generate_item(template, constraints if constraints else None)

        # Save to database if requested
        item_id = None
        if save_to_db:
            item_id = get_db().save_item(item, template, constraints, seed)

        return jsonify({
            'success': True,
            'item': item,
            'db_id': item_id,
            'seed': seed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/generate/npc', methods=['POST'])
def generate_npc():
    """Generate an NPC."""
    data = request.json or {}

    archetype = data.get('archetype')
    seed = data.get('seed')
    save_to_db = data.get('save', False)

    # Set seed if provided
    if seed is not None:
        generator.reset_seed(int(seed))

    try:
        npc = generator.generate_npc(archetype)

        # Save to database if requested
        npc_id = None
        if save_to_db:
            npc_id = get_db().save_npc(npc, archetype, seed)

        return jsonify({
            'success': True,
            'npc': npc,
            'db_id': npc_id,
            'seed': seed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/generate/location', methods=['POST'])
def generate_location():
    """Generate a location."""
    data = request.json or {}

    template = data.get('template')
    generate_connections = data.get('connections', True)
    seed = data.get('seed')
    save_to_db = data.get('save', False)

    # Set seed if provided
    if seed is not None:
        generator.reset_seed(int(seed))

    try:
        location = generator.generate_location(template, generate_connections)

        # Save to database if requested
        location_id = None
        if save_to_db:
            location_id = get_db().save_location(location, template, seed)

        return jsonify({
            'success': True,
            'location': location,
            'db_id': location_id,
            'seed': seed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/generate/world', methods=['POST'])
def generate_world():
    """Generate a world."""
    data = request.json or {}

    size = data.get('size', 5)
    seed = data.get('seed')
    save_to_db = data.get('save', False)
    name = data.get('name')

    # Set seed if provided
    if seed is not None:
        generator.reset_seed(int(seed))

    try:
        world = generator.generate_world(int(size))

        # Save to database if requested
        world_id = None
        if save_to_db:
            world_id = get_db().save_world(world, name, seed)

        return jsonify({
            'success': True,
            'world': world,
            'db_id': world_id,
            'seed': seed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/generate/bulk', methods=['POST'])
def generate_bulk():
    """Generate multiple items in bulk."""
    data = request.json or {}

    content_type = data.get('type', 'item')
    count = data.get('count', 10)
    template = data.get('template')
    seed = data.get('seed')
    save_to_db = data.get('save', False)

    # Set seed if provided
    if seed is not None:
        generator.reset_seed(int(seed))

    try:
        results = []
        db_ids = []

        for i in range(int(count)):
            if content_type == 'item':
                content = generator.generate_item(template)
                if save_to_db:
                    db_id = get_db().save_item(content, template, None, seed)
                    db_ids.append(db_id)
            elif content_type == 'npc':
                content = generator.generate_npc(template)
                if save_to_db:
                    db_id = get_db().save_npc(content, template, seed)
                    db_ids.append(db_id)
            elif content_type == 'location':
                content = generator.generate_location(template, False)
                if save_to_db:
                    db_id = get_db().save_location(content, template, seed)
                    db_ids.append(db_id)
            else:
                return jsonify({'success': False, 'error': 'Invalid content type'}), 400

            results.append(content)

        return jsonify({
            'success': True,
            'results': results,
            'count': len(results),
            'db_ids': db_ids if save_to_db else None,
            'seed': seed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get generation history."""
    content_type = request.args.get('type')
    limit = request.args.get('limit', 100)

    try:
        history = get_db().get_history(content_type, int(limit))
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/search/items', methods=['GET'])
def search_items():
    """Search for items in database."""
    filters = {}

    if request.args.get('type'):
        filters['type'] = request.args.get('type')
    if request.args.get('quality'):
        filters['quality'] = request.args.get('quality')
    if request.args.get('rarity'):
        filters['rarity'] = request.args.get('rarity')
    if request.args.get('min_value'):
        filters['min_value'] = int(request.args.get('min_value'))
    if request.args.get('max_value'):
        filters['max_value'] = int(request.args.get('max_value'))
    if request.args.get('material'):
        filters['material'] = request.args.get('material')

    limit = request.args.get('limit', 100)

    try:
        items = get_db().search_items(filters, int(limit))
        return jsonify({
            'success': True,
            'items': items,
            'count': len(items)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/item/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get a specific item by ID."""
    try:
        item = get_db().get_item(item_id)
        if item:
            return jsonify({
                'success': True,
                'item': item
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Item not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/npc/<int:npc_id>', methods=['GET'])
def get_npc(npc_id):
    """Get a specific NPC by ID."""
    try:
        npc = get_db().get_npc(npc_id)
        if npc:
            return jsonify({
                'success': True,
                'npc': npc
            })
        else:
            return jsonify({
                'success': False,
                'error': 'NPC not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/location/<int:location_id>', methods=['GET'])
def get_location(location_id):
    """Get a specific location by ID."""
    try:
        location = get_db().get_location(location_id)
        if location:
            return jsonify({
                'success': True,
                'location': location
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Location not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/world/<int:world_id>', methods=['GET'])
def get_world(world_id):
    """Get a specific world by ID."""
    try:
        world = get_db().get_world(world_id)
        if world:
            return jsonify({
                'success': True,
                'world': world
            })
        else:
            return jsonify({
                'success': False,
                'error': 'World not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about generated content."""
    # This would require additional DB queries
    # For now, return a placeholder
    return jsonify({
        'success': True,
        'stats': {
            'total_items': 0,
            'total_npcs': 0,
            'total_locations': 0,
            'total_worlds': 0
        }
    })


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)

    # Run the app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'

    print(f"""
╔══════════════════════════════════════════════════════════╗
║           R-Gen Web Interface Starting...                ║
║                                                          ║
║   Open your browser to: http://localhost:{port}      ║
║                                                          ║
║   API Documentation:                                     ║
║   - GET  /api/templates       - List all templates       ║
║   - GET  /api/attributes      - Get filter attributes    ║
║   - POST /api/generate/item   - Generate item            ║
║   - POST /api/generate/npc    - Generate NPC             ║
║   - POST /api/generate/location - Generate location      ║
║   - POST /api/generate/world  - Generate world           ║
║   - GET  /api/history         - Get generation history   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)

    app.run(host='0.0.0.0', port=port, debug=debug)
