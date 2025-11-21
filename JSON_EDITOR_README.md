# Dark Web JSON Editor for GenerationEngine

A beautiful dark-themed web application for editing all JSON files in the GenerationEngine directory.

## Features

### 🎨 Dark Theme
- Beautiful dark interface optimized for extended editing sessions
- Easy on the eyes with carefully selected color palette
- Professional GitHub-inspired design

### 📝 File Management
- View all 24 JSON files from GenerationEngine
- Quick file search and filtering
- File count display
- Easy file switching

### ✨ Editor Features
- **Syntax Highlighting**: Monospace font with clear formatting
- **Auto-validation**: Real-time JSON validation
- **Format Button**: Automatically format/prettify JSON
- **Save/Revert**: Save changes or revert to original
- **Modified Indicator**: Visual indicator when file has unsaved changes
- **Line/Character Count**: Status bar with file statistics

### 🎯 Quality of Life
- **Keyboard Shortcuts**:
  - `Ctrl+S` / `Cmd+S` - Save file
  - `Ctrl+F` / `Cmd+F` - Format JSON
  - `Ctrl+Z` / `Cmd+Z` - Undo (native)
- **Unsaved Changes Warning**: Prevents accidental data loss
- **Toast Notifications**: Visual feedback for all actions
- **Status Bar**: Real-time status and file information
- **Responsive Design**: Works on different screen sizes

## Installation

1. Install Flask:
```bash
pip install -r requirements_json_editor.txt
```

Or install Flask directly:
```bash
pip install Flask
```

## Usage

1. Start the web server:
```bash
python json_editor.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. You should see:
```
============================================================
Dark Web JSON Editor for GenerationEngine
============================================================
GenerationEngine Directory: /path/to/R-Gen/GenerationEngine
JSON Files Found: 24
============================================================
Starting server on http://localhost:5000
Press CTRL+C to stop the server
============================================================
```

## How to Use

### Editing Files

1. **Select a File**: Click on any file in the left sidebar
2. **Edit Content**: Modify the JSON in the text editor
3. **Validate**: Click "✓ Validate" to check JSON syntax
4. **Format**: Click "📐 Format" to auto-format the JSON
5. **Save**: Click "💾 Save" to save your changes
6. **Revert**: Click "↶ Revert" to discard changes

### Searching Files

- Use the search box at the top of the sidebar
- Type any part of the filename to filter
- Search is case-insensitive

### Status Indicators

- 🟢 **Green dot**: File loaded successfully / Valid JSON
- 🟡 **Yellow dot**: File has unsaved changes
- 🔴 **Red dot**: Error (invalid JSON or save failed)

## JSON Files Available (24 Total)

The editor provides access to all GenerationEngine JSON files:

1. **adjectives.json** - Descriptive words (tactile, visual)
2. **animal_species.json** - Creatures and pets
3. **biomes.json** - Environment biomes (12 types)
4. **damage_types.json** - Combat damage types (10 types)
5. **description_styles.json** - Text generation styles (13 styles)
6. **economy.json** - Economic system
7. **environment_tags.json** - Location atmosphere tags
8. **factions.json** - Political factions (7 major factions)
9. **flora_species.json** - Plants and flora
10. **item_sets.json** - Inventory presets
11. **item_templates.json** - Item generation (11 types)
12. **locations.json** - Location templates (15+ types)
13. **materials.json** - Crafting materials (10 types)
14. **npc_traits.json** - NPC personality traits
15. **organizations.json** - Faction & organization system
16. **profession_levels.json** - Profession ranks (6 levels)
17. **professions.json** - NPC professions (40+ types)
18. **quality.json** - Item quality tiers (6 levels)
19. **quests.json** - Quest system (10 quest types)
20. **races.json** - Playable races (12 races)
21. **rarity.json** - Item rarity system (6 levels)
22. **spells.json** - Magic system (8 schools)
23. **stats.json** - Character statistics (6 core stats)
24. **weather.json** - Environmental & seasonal data

## Security Features

- Path traversal protection (prevents accessing files outside GenerationEngine)
- JSON validation before saving
- Automatic backups (original content preserved until save)
- Warning prompts for unsaved changes

## Technical Details

- **Backend**: Python Flask
- **Frontend**: Vanilla JavaScript (no dependencies)
- **Port**: 5000 (configurable in json_editor.py)
- **Host**: 0.0.0.0 (accessible from network)

## API Endpoints

The application provides a RESTful API:

- `GET /` - Main editor interface
- `GET /api/files` - List all JSON files
- `GET /api/file/<filename>` - Get file content
- `POST /api/file/<filename>` - Save file content
- `POST /api/validate` - Validate JSON without saving

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, edit `json_editor.py` and change:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```
To a different port number, e.g., `port=5001`

### Files Not Loading
- Ensure the `GenerationEngine` directory exists
- Check that JSON files are in the correct location
- Verify file permissions (read/write access)

### Save Failed
- Check JSON syntax using the Validate button
- Ensure you have write permissions to the GenerationEngine directory
- Check console for detailed error messages

## Tips

1. **Always validate before saving** - Use the Validate button to catch errors
2. **Use Format button** - Keep your JSON clean and readable
3. **Search efficiently** - Use the search box to quickly find files
4. **Watch the status bar** - It shows real-time information
5. **Save regularly** - The editor shows unsaved changes indicator

## Development

To run in debug mode (auto-reload on changes):
```bash
python json_editor.py
```

Debug mode is enabled by default. To disable, edit `json_editor.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## License

Part of the R-Gen project.
