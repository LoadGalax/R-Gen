#!/usr/bin/env python3
"""
Dark Web JSON Editor for GenerationEngine
A Flask-based web application for editing JSON files in the GenerationEngine directory.
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from pathlib import Path

app = Flask(__name__)

# Configuration
GENERATION_ENGINE_DIR = Path(__file__).parent / "GenerationEngine" / "data"


def get_json_files():
    """Get all JSON files in the GenerationEngine directory."""
    if not GENERATION_ENGINE_DIR.exists():
        return []

    json_files = sorted([f.name for f in GENERATION_ENGINE_DIR.glob("*.json")])
    return json_files


def read_json_file(filename):
    """Read and parse a JSON file."""
    filepath = GENERATION_ENGINE_DIR / filename
    if not filepath.exists():
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


def write_json_file(filename, content):
    """Write content to a JSON file."""
    filepath = GENERATION_ENGINE_DIR / filename

    try:
        # Validate JSON
        if isinstance(content, str):
            parsed = json.loads(content)
        else:
            parsed = content

        # Write with pretty formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)

        return {"success": True, "message": f"Successfully saved {filename}"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Invalid JSON: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.route('/')
def index():
    """Render the main editor page."""
    return render_template('editor.html')


@app.route('/api/files')
def list_files():
    """API endpoint to list all JSON files."""
    files = get_json_files()
    return jsonify(files)


@app.route('/api/file/<filename>')
def get_file(filename):
    """API endpoint to get the content of a specific JSON file."""
    # Security check - ensure filename is just a name, not a path
    if '/' in filename or '\\' in filename or '..' in filename:
        return jsonify({"error": "Invalid filename"}), 400

    content = read_json_file(filename)
    if content is None:
        return jsonify({"error": "File not found"}), 404

    return jsonify(content)


@app.route('/api/file/<filename>', methods=['POST'])
def save_file(filename):
    """API endpoint to save content to a JSON file."""
    # Security check
    if '/' in filename or '\\' in filename or '..' in filename:
        return jsonify({"error": "Invalid filename"}), 400

    try:
        content = request.get_json()
        result = write_json_file(filename, content)

        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/api/validate', methods=['POST'])
def validate_json():
    """API endpoint to validate JSON without saving."""
    try:
        content = request.get_data(as_text=True)
        json.loads(content)
        return jsonify({"valid": True, "message": "Valid JSON"})
    except json.JSONDecodeError as e:
        return jsonify({"valid": False, "error": str(e), "position": e.pos})


if __name__ == '__main__':
    print("=" * 60)
    print("Dark Web JSON Editor for GenerationEngine")
    print("=" * 60)
    print(f"GenerationEngine Directory: {GENERATION_ENGINE_DIR.absolute()}")
    print(f"JSON Files Found: {len(get_json_files())}")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("Press CTRL+C to stop the server")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
