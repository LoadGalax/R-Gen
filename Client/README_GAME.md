# R-Gen Web Game - Play Guide

Welcome to the R-Gen Web Game! This is a fully functional dark fantasy RPG with real-time simulation.

## Features

### 🎮 Core Gameplay
- **Explore Living World** - Visit dynamically simulated locations with NPCs going about their daily lives
- **NPC Interactions** - Talk to NPCs, learn about their professions and moods
- **Travel System** - Move between connected locations across the world
- **Real-Time Simulation** - Watch as time progresses, NPCs work, rest, and interact
- **Event Chronicle** - Track everything happening in the world

### 📖 Grimoire Interface
The game uses a unique **open grimoire** interface with bookmark navigation:
- **🗺️ World** - Current location, NPCs present, weather, and actions
- **👤 Hero** - Character stats (health, mana, energy, experience)
- **🎒 Items** - Inventory management (coming soon)
- **🧭 Map** - Visual map of all discovered locations
- **📜 Quests** - Quest tracking (coming soon)
- **📖 Log** - Scrollable event history

### 🔄 Real-Time Features
- **WebSocket Connection** - Live updates from the simulation
- **Time Progression** - Day/night cycle, seasons
- **NPC Activities** - NPCs work, eat, sleep, craft, and socialize
- **Weather Changes** - Dynamic weather affects locations
- **Event Stream** - New events appear as they happen

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r Game/requirements_game.txt
```

### 2. Start the Game Server

```bash
# From the R-Gen root directory
python Game/game_server.py
```

You should see:
```
R-Gen Game Server
============================================================

Starting server...
Game will be available at: http://localhost:5000
Press Ctrl+C to stop
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

The game will automatically:
- Create a fantasy world with 10 locations
- Spawn NPCs in various professions
- Start the real-time simulation
- Connect via WebSocket for live updates

## How to Play

### 🗺️ Exploring the World

1. **View Current Location**
   - The main page shows your current location
   - See description, weather, time, and NPCs present

2. **Talk to NPCs**
   - Click any NPC to open a dialogue
   - Learn about their profession and mood
   - Ask them questions

3. **Travel**
   - Click "Journey" button
   - Select a connected destination
   - Instantly travel to the new location

4. **Rest**
   - Click "Rest" to restore energy (feature coming soon)

### 🧭 Using the Map

1. Click the **Map** bookmark (🧭)
2. See all discovered locations in a grid
3. Current location is highlighted in gold
4. Click any location to travel there instantly

### 📖 Tracking Events

1. Click the **Log** bookmark (📖)
2. Scroll through recent world events
3. Events update in real-time
4. See what NPCs are doing across the world

### 👤 Character Page

1. Click the **Hero** bookmark (👤)
2. View your character stats:
   - Health, Mana, Experience, Energy
   - Current mood and hunger
   - Attack, Defense, Magic Power

## Technical Details

### Architecture

**Backend** (`Game/game_server.py`):
- Flask REST API for game data
- Flask-SocketIO for real-time communication
- SimulationEngine runs in background thread
- World state is maintained server-side

**Frontend** (`index.html` + `game.js`):
- Dark grimoire styled UI
- Socket.IO client for live updates
- REST API calls for actions
- Modal dialogs for interactions

### API Endpoints

```
GET  /api/world/info          - World information and time
GET  /api/locations           - All locations
GET  /api/location/<id>       - Specific location details
GET  /api/npcs                - All NPCs
GET  /api/npc/<id>            - Specific NPC details
GET  /api/npc/<id>/dialogue   - NPC conversation options
GET  /api/events              - Recent events
POST /api/player/travel       - Travel to location
POST /api/simulation/start    - Start simulation
POST /api/simulation/stop     - Stop simulation
```

### WebSocket Events

**Received from Server**:
- `connected` - Initial connection confirmation
- `world_update` - Periodic world state updates
- `player_moved` - When player travels

**Sent to Server**:
- `request_update` - Request immediate update

## Development

### File Structure

```
R-Gen/
├── Game/
│   ├── game_server.py         # Flask+WebSocket game server
│   ├── game_database.py       # Game database management
│   └── requirements_game.txt  # Python dependencies
└── Client/
    ├── index.html             # Main game interface
    ├── game.js                # Game client logic
    └── README_GAME.md         # This file
```

### Extending the Game

**Adding New Features**:

1. **New API Endpoints** - Add to `Game/game_server.py`
2. **New UI Pages** - Add page content to `index.html`
3. **New Actions** - Add functions to `game.js`
4. **New Bookmarks** - Add bookmark HTML and page content

**Simulation Control**:

The simulation runs automatically with:
- 30-minute steps (in-game time)
- 5-second intervals (real time)
- Background thread

To customize: Edit `run_simulation_loop()` in `Game/game_server.py`

## Troubleshooting

### Server Won't Start

```bash
# Check if port 5000 is already in use
lsof -i :5000

# Kill the process if needed
kill -9 <PID>
```

### WebSocket Not Connecting

- Check browser console for errors
- Ensure `flask-socketio` is installed
- Try refreshing the page

### No NPCs or Locations

- The world is created on first server start
- Check server console for errors
- Restart the server

### Events Not Updating

- Check WebSocket connection (browser console)
- Verify simulation is running: `/api/simulation/status`
- Restart server if needed

## Coming Soon

- 🎒 **Inventory System** - Manage items, equipment, and loot
- 📜 **Quest System** - Accept and complete quests
- ⚔️ **Combat System** - Battle monsters and NPCs
- 🏪 **Market Trading** - Buy and sell items
- 🎲 **Character Creation** - Customize your hero
- 💾 **Save/Load** - Persist your game progress
- 🌐 **Multiplayer** - Play with friends

## Credits

Built with:
- **Backend**: Flask, Flask-SocketIO, R-Gen Simulation Engine
- **Frontend**: Vanilla JavaScript, Socket.IO Client
- **Design**: Dark Fantasy Grimoire aesthetic

Enjoy your adventures in the R-Gen fantasy world! ⚔️📖
