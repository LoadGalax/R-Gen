# 🎮 GenerationEngine JSON Editor

A beautiful dark-themed web interface for editing all JSON files in the GenerationEngine.

## ✨ Features

- **Dark Theme** - Easy on the eyes for long editing sessions
- **File Browser** - Quick navigation with search functionality
- **Live Stats** - See line count, character count in real-time
- **Auto Backup** - Automatic backups before every save
- **JSON Validation** - Validates JSON before saving
- **Format Tool** - One-click JSON formatting
- **Keyboard Shortcuts** - Fast workflow with shortcuts
- **Unsaved Changes Protection** - Warns before switching files
- **Beautiful UI** - Modern, responsive design

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start the Server

```bash
npm run editor
```

Or simply:

```bash
npm start
```

### 3. Open in Browser

Navigate to: **http://localhost:3000/json-editor.html**

## ⌨️ Keyboard Shortcuts

- `Ctrl+S` (or `Cmd+S`) - Save current file
- `Ctrl+F` (or `Cmd+F`) - Focus search box

## 📁 Files

All JSON files in `GenerationEngine/data/` are available for editing:

- adjectives.json
- animal_species.json
- biomes.json
- damage_types.json
- description_styles.json
- economy.json
- environment_tags.json
- factions.json
- flora_species.json
- item_sets.json
- item_templates.json
- locations.json
- materials.json
- npc_traits.json
- organizations.json
- profession_levels.json
- professions.json
- quality.json
- quests.json
- races.json
- rarity.json
- spells.json
- stats.json
- weather.json

## 💾 Backups

All changes create automatic backups in the `backups/` directory with timestamps.

## 🎨 UI Elements

- **File List** (Left Sidebar) - Browse and search files
- **Toolbar** - Save, format, validate, and reload buttons
- **Editor** - Main text area for editing JSON
- **Status Bar** - Shows modification state and file stats
- **Notifications** - Success/error messages for actions

## 🛡️ Safety Features

- JSON validation before saving
- Automatic backups before every save
- Unsaved changes warning
- Directory traversal protection

## 🔧 API Endpoints

The server provides these endpoints:

- `GET /api/read/:filename` - Read a JSON file
- `POST /api/save/:filename` - Save a JSON file
- `GET /api/files` - List all JSON files
- `GET /api/info/:filename` - Get file information
- `GET /api/health` - Health check

## 📝 Notes

- The server runs on port 3000 by default
- Backups are stored in the `backups/` directory
- The editor validates JSON before allowing saves
- All files are pretty-printed with 2-space indentation

## 🎯 Tips

1. Use the search box to quickly find files
2. Format JSON before saving for consistency
3. Validate your JSON if you're unsure about syntax
4. The editor auto-saves on Ctrl+S for quick workflows
5. Check the backups folder if you need to revert changes

Enjoy editing! 🚀
