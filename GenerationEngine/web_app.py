#!/usr/bin/env python3
"""
R-Gen REST API - Flask-based REST API for content generation

Provides a comprehensive REST API for generating and managing game content
with interactive API documentation at /doc
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from pathlib import Path
from datetime import datetime

from src.content_generator import ContentGenerator

app = Flask(__name__)
CORS(app)

# Initialize generator
generator = ContentGenerator()


# ============================================================================
# API Documentation Route
# ============================================================================

@app.route('/')
@app.route('/doc')
@app.route('/docs')
def api_docs():
    """Serve interactive API documentation."""
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>R-Gen API Documentation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .content {
            padding: 40px;
        }

        .section {
            margin-bottom: 40px;
        }

        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }

        .endpoint {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }

        .endpoint h3 {
            color: #333;
            margin-bottom: 10px;
        }

        .method {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 3px;
            font-weight: bold;
            margin-right: 10px;
            font-size: 0.9em;
        }

        .method.get {
            background: #28a745;
            color: white;
        }

        .method.post {
            background: #007bff;
            color: white;
        }

        .path {
            font-family: 'Courier New', monospace;
            background: #e9ecef;
            padding: 5px 10px;
            border-radius: 3px;
            display: inline-block;
        }

        .description {
            margin: 15px 0;
            color: #555;
        }

        .params {
            background: white;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
        }

        .params h4 {
            color: #667eea;
            margin-bottom: 10px;
        }

        .param {
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }

        .param:last-child {
            border-bottom: none;
        }

        .param-name {
            font-family: 'Courier New', monospace;
            color: #e83e8c;
            font-weight: bold;
        }

        .param-type {
            color: #6c757d;
            font-size: 0.9em;
        }

        code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #e83e8c;
        }

        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 15px 0;
        }

        .test-button {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin-top: 10px;
            transition: background 0.3s;
        }

        .test-button:hover {
            background: #764ba2;
        }

        .response {
            margin-top: 15px;
            display: none;
        }

        .response.visible {
            display: block;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }

        .stat-card h3 {
            font-size: 2em;
            margin-bottom: 5px;
        }

        .stat-card p {
            opacity: 0.9;
        }

        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 R-Gen REST API</h1>
            <p>Random Game Content Generation API</p>
        </div>

        <div class="content">
            <!-- Quick Stats -->
            <div class="section">
                <h2>📊 API Overview</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>11</h3>
                        <p>Endpoints</p>
                    </div>
                    <div class="stat-card">
                        <h3>10+</h3>
                        <p>Content Types</p>
                    </div>
                    <div class="stat-card">
                        <h3>REST</h3>
                        <p>JSON API</p>
                    </div>
                    <div class="stat-card">
                        <h3>Free</h3>
                        <p>Open Source</p>
                    </div>
                </div>
            </div>

            <!-- Configuration Endpoints -->
            <div class="section">
                <h2>⚙️ Configuration Endpoints</h2>

                <div class="endpoint">
                    <h3>
                        <span class="method get">GET</span>
                        <span class="path">/api/templates</span>
                    </h3>
                    <div class="description">
                        Get all available templates for items, NPCs, locations, spells, and organizations.
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/templates', 'GET', null, 'resp-templates')">
                        Test Endpoint
                    </button>
                    <div id="resp-templates" class="response"></div>
                </div>

                <div class="endpoint">
                    <h3>
                        <span class="method get">GET</span>
                        <span class="path">/api/attributes</span>
                    </h3>
                    <div class="description">
                        Get available attributes for filtering (quality levels, rarity tiers, materials, stats, etc.).
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/attributes', 'GET', null, 'resp-attributes')">
                        Test Endpoint
                    </button>
                    <div id="resp-attributes" class="response"></div>
                </div>

                <div class="endpoint">
                    <h3>
                        <span class="method get">GET</span>
                        <span class="path">/api/health</span>
                    </h3>
                    <div class="description">
                        Check API health status and version information.
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/health', 'GET', null, 'resp-health')">
                        Test Endpoint
                    </button>
                    <div id="resp-health" class="response"></div>
                </div>
            </div>

            <!-- Generation Endpoints -->
            <div class="section">
                <h2>🎲 Content Generation Endpoints</h2>

                <div class="endpoint">
                    <h3>
                        <span class="method post">POST</span>
                        <span class="path">/api/generate/item</span>
                    </h3>
                    <div class="description">
                        Generate a random item with optional constraints.
                    </div>
                    <div class="params">
                        <h4>Request Body (JSON):</h4>
                        <div class="param">
                            <span class="param-name">template</span>
                            <span class="param-type">(string, optional)</span> - Item template name (e.g., "weapon_melee", "potion")
                        </div>
                        <div class="param">
                            <span class="param-name">seed</span>
                            <span class="param-type">(integer, optional)</span> - Random seed for reproducibility
                        </div>
                        <div class="param">
                            <span class="param-name">min_quality</span>
                            <span class="param-type">(string, optional)</span> - Minimum quality level
                        </div>
                        <div class="param">
                            <span class="param-name">min_rarity</span>
                            <span class="param-type">(string, optional)</span> - Minimum rarity level
                        </div>
                        <div class="param">
                            <span class="param-name">min_value</span>
                            <span class="param-type">(integer, optional)</span> - Minimum gold value
                        </div>
                    </div>
                    <pre>{
  "template": "weapon_melee",
  "seed": 12345,
  "min_quality": "Excellent",
  "min_rarity": "Rare"
}</pre>
                    <button class="test-button" onclick="testEndpoint('/api/generate/item', 'POST', {template: 'weapon_melee', seed: 42}, 'resp-item')">
                        Test Endpoint
                    </button>
                    <div id="resp-item" class="response"></div>
                </div>

                <div class="endpoint">
                    <h3>
                        <span class="method post">POST</span>
                        <span class="path">/api/generate/npc</span>
                    </h3>
                    <div class="description">
                        Generate a random NPC with optional archetype and profession.
                    </div>
                    <div class="params">
                        <h4>Request Body (JSON):</h4>
                        <div class="param">
                            <span class="param-name">archetype_name</span>
                            <span class="param-type">(string, optional)</span> - NPC profession (e.g., "blacksmith", "merchant", "mage")
                        </div>
                        <div class="param">
                            <span class="param-name">seed</span>
                            <span class="param-type">(integer, optional)</span> - Random seed
                        </div>
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/generate/npc', 'POST', {archetype_name: 'merchant', seed: 42}, 'resp-npc')">
                        Test Endpoint
                    </button>
                    <div id="resp-npc" class="response"></div>
                </div>

                <div class="endpoint">
                    <h3>
                        <span class="method post">POST</span>
                        <span class="path">/api/generate/spell</span>
                    </h3>
                    <div class="description">
                        Generate a random spell with optional parameters.
                    </div>
                    <div class="params">
                        <h4>Request Body (JSON):</h4>
                        <div class="param">
                            <span class="param-name">spell_level</span>
                            <span class="param-type">(integer, optional)</span> - Spell level (0-9)
                        </div>
                        <div class="param">
                            <span class="param-name">school</span>
                            <span class="param-type">(string, optional)</span> - Magic school (e.g., "Evocation", "Necromancy")
                        </div>
                        <div class="param">
                            <span class="param-name">seed</span>
                            <span class="param-type">(integer, optional)</span> - Random seed
                        </div>
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/generate/spell', 'POST', {spell_level: 3, school: 'Evocation', seed: 42}, 'resp-spell')">
                        Test Endpoint
                    </button>
                    <div id="resp-spell" class="response"></div>
                </div>

                <div class="endpoint">
                    <h3>
                        <span class="method post">POST</span>
                        <span class="path">/api/generate/location</span>
                    </h3>
                    <div class="description">
                        Generate a random location with NPCs and items.
                    </div>
                    <div class="params">
                        <h4>Request Body (JSON):</h4>
                        <div class="param">
                            <span class="param-name">template</span>
                            <span class="param-type">(string, optional)</span> - Location template
                        </div>
                        <div class="param">
                            <span class="param-name">connections</span>
                            <span class="param-type">(boolean, optional)</span> - Generate connected locations
                        </div>
                        <div class="param">
                            <span class="param-name">seed</span>
                            <span class="param-type">(integer, optional)</span> - Random seed
                        </div>
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/generate/location', 'POST', {template: 'tavern', seed: 42}, 'resp-location')">
                        Test Endpoint
                    </button>
                    <div id="resp-location" class="response"></div>
                </div>

                <div class="endpoint">
                    <h3>
                        <span class="method post">POST</span>
                        <span class="path">/api/generate/world</span>
                    </h3>
                    <div class="description">
                        Generate a complete world with multiple interconnected locations.
                    </div>
                    <div class="params">
                        <h4>Request Body (JSON):</h4>
                        <div class="param">
                            <span class="param-name">size</span>
                            <span class="param-type">(integer, optional)</span> - Number of locations (default: 5)
                        </div>
                        <div class="param">
                            <span class="param-name">seed</span>
                            <span class="param-type">(integer, optional)</span> - Random seed
                        </div>
                        <div class="param">
                            <span class="param-name">name</span>
                            <span class="param-type">(string, optional)</span> - World name
                        </div>
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/generate/world', 'POST', {size: 3, seed: 42}, 'resp-world')">
                        Test Endpoint (Small World)
                    </button>
                    <div id="resp-world" class="response"></div>
                </div>

                <div class="endpoint">
                    <h3>
                        <span class="method post">POST</span>
                        <span class="path">/api/generate/organization</span>
                    </h3>
                    <div class="description">
                        Generate a random organization (guild, thieves guild, mages circle, etc.).
                    </div>
                    <div class="params">
                        <h4>Request Body (JSON):</h4>
                        <div class="param">
                            <span class="param-name">org_type</span>
                            <span class="param-type">(string, optional)</span> - Organization type
                        </div>
                        <div class="param">
                            <span class="param-name">size</span>
                            <span class="param-type">(string, optional)</span> - Size (small/medium/large)
                        </div>
                        <div class="param">
                            <span class="param-name">seed</span>
                            <span class="param-type">(integer, optional)</span> - Random seed
                        </div>
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/generate/organization', 'POST', {org_type: 'thieves_guild', seed: 42}, 'resp-org')">
                        Test Endpoint
                    </button>
                    <div id="resp-org" class="response"></div>
                </div>

                <div class="endpoint">
                    <h3>
                        <span class="method post">POST</span>
                        <span class="path">/api/generate/market</span>
                    </h3>
                    <div class="description">
                        Generate a market with merchants and goods.
                    </div>
                    <div class="params">
                        <h4>Request Body (JSON):</h4>
                        <div class="param">
                            <span class="param-name">wealth_level</span>
                            <span class="param-type">(string, optional)</span> - Wealth level (poor/modest/wealthy/etc.)
                        </div>
                        <div class="param">
                            <span class="param-name">seed</span>
                            <span class="param-type">(integer, optional)</span> - Random seed
                        </div>
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/generate/market', 'POST', {wealth_level: 'modest', seed: 42}, 'resp-market')">
                        Test Endpoint
                    </button>
                    <div id="resp-market" class="response"></div>
                </div>

                <div class="endpoint">
                    <h3>
                        <span class="method post">POST</span>
                        <span class="path">/api/generate/bulk</span>
                    </h3>
                    <div class="description">
                        Generate multiple items, NPCs, or locations in bulk.
                    </div>
                    <div class="params">
                        <h4>Request Body (JSON):</h4>
                        <div class="param">
                            <span class="param-name">type</span>
                            <span class="param-type">(string, required)</span> - Content type ("item", "npc", "location")
                        </div>
                        <div class="param">
                            <span class="param-name">count</span>
                            <span class="param-type">(integer, optional)</span> - Number to generate (default: 10)
                        </div>
                        <div class="param">
                            <span class="param-name">template</span>
                            <span class="param-type">(string, optional)</span> - Template name
                        </div>
                    </div>
                    <button class="test-button" onclick="testEndpoint('/api/generate/bulk', 'POST', {type: 'item', count: 5, template: 'potion', seed: 42}, 'resp-bulk')">
                        Test Endpoint (5 Potions)
                    </button>
                    <div id="resp-bulk" class="response"></div>
                </div>
            </div>

            <!-- Examples -->
            <div class="section">
                <h2>📚 Usage Examples</h2>

                <h3>Python</h3>
                <pre>import requests

# Generate a legendary weapon
response = requests.post('http://localhost:5000/api/generate/item', json={
    'template': 'weapon_melee',
    'min_quality': 'Masterwork',
    'min_rarity': 'Legendary',
    'seed': 12345
})
item = response.json()
print(f"Generated: {item['item']['name']}")

# Generate a merchant NPC
response = requests.post('http://localhost:5000/api/generate/npc', json={
    'archetype_name': 'merchant'
})
npc = response.json()
print(f"Created: {npc['npc']['name']}")</pre>

                <h3>cURL</h3>
                <pre>curl -X POST http://localhost:5000/api/generate/item \\
  -H "Content-Type: application/json" \\
  -d '{"template": "weapon_melee", "seed": 42}'

curl -X GET http://localhost:5000/api/templates</pre>

                <h3>JavaScript</h3>
                <pre>// Generate an item
fetch('http://localhost:5000/api/generate/item', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    template: 'weapon_melee',
    min_rarity: 'Epic',
    seed: 42
  })
})
.then(res => res.json())
.then(data => console.log('Generated:', data.item.name));</pre>
            </div>
        </div>

        <div class="footer">
            <p>R-Gen REST API - Random Game Content Generator</p>
            <p>Built with Flask • Open Source • MIT License</p>
        </div>
    </div>

    <script>
        async function testEndpoint(endpoint, method, body, responseId) {
            const responseDiv = document.getElementById(responseId);
            responseDiv.innerHTML = '<p>Loading...</p>';
            responseDiv.classList.add('visible');

            try {
                const options = {
                    method: method,
                    headers: {'Content-Type': 'application/json'}
                };

                if (body) {
                    options.body = JSON.stringify(body);
                }

                const response = await fetch(endpoint, options);
                const data = await response.json();

                responseDiv.innerHTML = '<h4>Response:</h4><pre>' +
                    JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                responseDiv.innerHTML = '<h4 style="color: red;">Error:</h4><pre>' +
                    error.message + '</pre>';
            }
        }
    </script>
</body>
</html>
    """
    return html


# ============================================================================
# Configuration Endpoints
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': 11,
        'features': [
            'items', 'npcs', 'locations', 'worlds',
            'spells', 'organizations', 'markets',
            'quests', 'weather', 'relationships'
        ]
    })


@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all available templates."""
    try:
        # Extract template names from locations_config
        location_templates = list(generator.locations_config.get('templates', {}).keys())

        # Extract profession names
        profession_names = list(generator.professions.keys())

        # Extract spell schools if available
        spell_schools = []
        if 'schools' in generator.spells_config:
            spell_schools = list(generator.spells_config['schools'].keys())

        # Extract organization types if available
        org_types = []
        if 'organization_types' in generator.organizations_config:
            org_types = list(generator.organizations_config['organization_types'].keys())

        return jsonify({
            'success': True,
            'templates': {
                'items': list(generator.item_templates.keys()),
                'npcs': profession_names,
                'locations': location_templates,
                'item_sets': list(generator.item_sets.keys()),
                'spell_schools': spell_schools,
                'organization_types': org_types
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/attributes', methods=['GET'])
def get_attributes():
    """Get available attributes for filtering."""
    try:
        return jsonify({
            'success': True,
            'attributes': {
                'quality': list(generator.quality.keys()),
                'rarity': list(generator.rarity.keys()),
                'materials': generator.materials,
                'stats': list(generator.stats.keys()),
                'damage_types': generator.damage_types,
                'environment_tags': generator.environment_tags,
                'npc_traits': generator.npc_traits,
                'biomes': list(generator.biomes_config.keys()) if hasattr(generator, 'biomes_config') else [],
                'factions': list(generator.factions_config.keys()) if hasattr(generator, 'factions_config') else []
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# Item Generation Endpoints
# ============================================================================

@app.route('/api/generate/item', methods=['POST'])
def generate_item():
    """Generate an item with optional constraints."""
    data = request.json or {}

    template = data.get('template')
    seed = data.get('seed')

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

        return jsonify({
            'success': True,
            'item': item,
            'seed': seed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ============================================================================
# NPC Generation Endpoints
# ============================================================================

@app.route('/api/generate/npc', methods=['POST'])
def generate_npc():
    """Generate an NPC."""
    data = request.json or {}

    archetype = data.get('archetype_name')  # Support both 'archetype' and 'archetype_name'
    if not archetype:
        archetype = data.get('archetype')

    seed = data.get('seed')

    # Set seed if provided
    if seed is not None:
        generator.reset_seed(int(seed))

    try:
        npc = generator.generate_npc(archetype)

        return jsonify({
            'success': True,
            'npc': npc,
            'seed': seed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ============================================================================
# Spell Generation Endpoints
# ============================================================================

@app.route('/api/generate/spell', methods=['POST'])
def generate_spell():
    """Generate a spell."""
    data = request.json or {}

    spell_level = data.get('spell_level')
    school = data.get('school')
    spell_template = data.get('spell_template')
    seed = data.get('seed')

    # Set seed if provided
    if seed is not None:
        generator.reset_seed(int(seed))

    try:
        # Check if generator has generate_spell method
        if not hasattr(generator, 'generate_spell'):
            return jsonify({
                'success': False,
                'error': 'Spell generation not available in this version'
            }), 400

        spell = generator.generate_spell(
            spell_level=spell_level,
            school=school,
            spell_template=spell_template
        )

        return jsonify({
            'success': True,
            'spell': spell,
            'seed': seed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ============================================================================
# Location and World Generation Endpoints
# ============================================================================

@app.route('/api/generate/location', methods=['POST'])
def generate_location():
    """Generate a location."""
    data = request.json or {}

    template = data.get('template')
    generate_connections = data.get('connections', False)  # Changed default to False for API
    seed = data.get('seed')

    # Set seed if provided
    if seed is not None:
        generator.reset_seed(int(seed))

    try:
        location = generator.generate_location(template, generate_connections)

        return jsonify({
            'success': True,
            'location': location,
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
    name = data.get('name')

    # Set seed if provided
    if seed is not None:
        generator.reset_seed(int(seed))

    try:
        world = generator.generate_world(int(size))

        return jsonify({
            'success': True,
            'world': world,
            'seed': seed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ============================================================================
# Organization Generation Endpoints
# ============================================================================

@app.route('/api/generate/organization', methods=['POST'])
def generate_organization():
    """Generate an organization."""
    data = request.json or {}

    org_type = data.get('org_type')
    size = data.get('size')
    faction = data.get('faction')
    seed = data.get('seed')

    # Set seed if provided
    if seed is not None:
        generator.reset_seed(int(seed))

    try:
        # Check if generator has generate_organization method
        if not hasattr(generator, 'generate_organization'):
            return jsonify({
                'success': False,
                'error': 'Organization generation not available in this version'
            }), 400

        organization = generator.generate_organization(
            org_type=org_type,
            size=size,
            faction=faction
        )

        return jsonify({
            'success': True,
            'organization': organization,
            'seed': seed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ============================================================================
# Market Generation Endpoints
# ============================================================================

@app.route('/api/generate/market', methods=['POST'])
def generate_market():
    """Generate a market."""
    data = request.json or {}

    wealth_level = data.get('wealth_level', 'modest')
    seed = data.get('seed')

    # Set seed if provided
    if seed is not None:
        generator.reset_seed(int(seed))

    try:
        # Check if generator has generate_market method
        if not hasattr(generator, 'generate_market'):
            return jsonify({
                'success': False,
                'error': 'Market generation not available in this version'
            }), 400

        market = generator.generate_market(wealth_level=wealth_level)

        return jsonify({
            'success': True,
            'market': market,
            'seed': seed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ============================================================================
# Bulk Generation Endpoints
# ============================================================================

@app.route('/api/generate/bulk', methods=['POST'])
def generate_bulk():
    """Generate multiple items in bulk."""
    data = request.json or {}

    content_type = data.get('type', 'item')
    count = min(int(data.get('count', 10)), 100)  # Limit to 100 for performance
    template = data.get('template')
    seed = data.get('seed')

    # Set seed if provided
    if seed is not None:
        generator.reset_seed(int(seed))

    try:
        results = []

        for i in range(count):
            if content_type == 'item':
                content = generator.generate_item(template)
            elif content_type == 'npc':
                content = generator.generate_npc(template)
            elif content_type == 'location':
                content = generator.generate_location(template, False)
            else:
                return jsonify({'success': False, 'error': 'Invalid content type'}), 400

            results.append(content)

        return jsonify({
            'success': True,
            'results': results,
            'count': len(results),
            'seed': seed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'Visit /doc for API documentation'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(error)
    }), 500


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'

    print(f"""
╔══════════════════════════════════════════════════════════╗
║              R-Gen REST API Server                       ║
║                                                          ║
║   🌐 API Server: http://localhost:{port}            ║
║   📚 Documentation: http://localhost:{port}/doc      ║
║                                                          ║
║   Status: Running                                        ║
║   Mode: {'Development' if debug else 'Production'}                                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)

    app.run(host='0.0.0.0', port=port, debug=debug)
