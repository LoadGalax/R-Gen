# Client-Server Integration Guide

## Overview

The R-Gen web client is now fully integrated with the game_server, providing a beautiful Dark Grimoire-themed interface for interacting with the living world simulation.

## Quick Start

### 1. Start the Game Server

```bash
python3 game_server.py
```

The server will:
- Create a fantasy world with 10 locations and ~18 NPCs
- Start listening on http://localhost:5000
- Serve both the API and the web client

### 2. Open the Web Client

Open your browser and navigate to:
```
http://localhost:5000
```

You'll see the Dark Grimoire interface with:
- **Bookmark navigation** on the left (World, Hero, Items, Map, Quests, Log)
- **Live world information** (time, weather, NPCs)
- **Interactive elements** (talk to NPCs, travel between locations)
- **Real-time updates** via WebSocket

### 3. Test the Connection

Run the demo script to verify everything works:
```bash
python3 demo_client_connection.py
```

This will test all API endpoints and confirm the client can connect successfully.

## Architecture

### Server (game_server.py)

**Port:** 5000
**Host:** 0.0.0.0 (accepts all connections)

**REST API Endpoints:**
- `GET /api/health` - Server health check
- `GET /api/world/info` - World information (time, stats)
- `GET /api/locations` - List all locations
- `GET /api/location/<id>` - Specific location details
- `GET /api/npcs` - List all NPCs
- `GET /api/npc/<id>` - Specific NPC details
- `GET /api/npc/<id>/dialogue` - NPC conversation options
- `GET /api/events?limit=N` - Recent events
- `POST /api/player/travel` - Travel to location
- `POST /api/simulation/start` - Start simulation
- `POST /api/simulation/stop` - Stop simulation
- `GET /api/simulation/status` - Simulation status

**WebSocket Events:**
- `connected` - Initial connection confirmation
- `world_update` - Periodic world state (every 5 seconds)
- `player_moved` - When player travels
- `error` - Error messages

### Client (Client/)

**Files:**
- `index.html` - Dark Grimoire themed interface
- `game.js` - Game logic and API communication

**Features:**
- Socket.IO WebSocket connection
- Real-time world updates
- NPC dialogue system
- Location navigation
- Event log

## API Examples

### Get World Info
```bash
curl http://localhost:5000/api/world/info
```

Response:
```json
{
  "name": "Fantasy Realm",
  "current_time": {
    "day": 1,
    "season": "Spring",
    "time": "08:00",
    "is_day": true
  },
  "stats": {
    "total_locations": 10,
    "total_npcs": 18,
    "total_events": 0
  }
}
```

### Travel to Location
```bash
curl -X POST http://localhost:5000/api/player/travel \
  -H "Content-Type: application/json" \
  -d '{"location_id": "market_1234"}'
```

### Talk to NPC
```bash
curl http://localhost:5000/api/npc/npc_abc123/dialogue
```

## Integration Fixes Applied

The following issues were fixed to make the client work with the server:

1. **Event System Access**
   - Changed `world.event_history` → `world.event_system.event_history`
   - Added `format_event()` to convert Event objects to strings

2. **TimeManager Properties**
   - Changed `get_current_day()` → `current_day`
   - Changed `get_current_season()` → `current_season`
   - Changed `is_day()` → `is_daytime`

3. **NPC Properties**
   - Changed `get_current_location()` → `current_location_id`
   - Changed `get_mood()` → `mood` (with text conversion)

4. **Location Properties**
   - Changed `get_weather()` → `current_weather`
   - Added season format conversion (Spring → spring, Fall → autumn)

5. **Simulator Methods**
   - Changed `simulator.simulate_minutes()` → `simulator.step()`

6. **API Response Enhancement**
   - Added name, profession, template fields to responses
   - Ensured all required data is included for client

## Testing

### Automated Test Suite
```bash
python3 test_integration.py
```

Tests all API endpoints and verifies data format compatibility.

### Manual Testing

1. Start server: `python3 game_server.py`
2. Open browser: http://localhost:5000
3. Try these actions:
   - Click on NPCs to see dialogue
   - Click "Journey" to travel to connected locations
   - Switch between bookmarks (World, Hero, Items, Map, Quests, Log)
   - Watch the time advance in the info box
   - Check the Log page for world events

## Troubleshooting

### Port Already in Use
```bash
# Kill existing server
pkill -f game_server.py

# Or use a different port (edit game_server.py line 493)
socketio.run(app, host='0.0.0.0', port=5001)
```

### Cannot Connect
- Make sure the server is running
- Check firewall settings
- Try http://127.0.0.1:5000 instead of localhost

### No Events Showing
- Events are generated when the simulation runs
- Start simulation: `curl -X POST http://localhost:5000/api/simulation/start`
- Wait a few seconds for NPCs to perform actions

## Development

### Adding New API Endpoints

1. Add route in `game_server.py`:
```python
@app.route('/api/your-endpoint', methods=['GET'])
def your_endpoint():
    w, sim = get_or_create_world()
    # Your logic here
    return jsonify({'data': ...})
```

2. Call from client in `game.js`:
```javascript
async yourFunction() {
    const data = await this.apiGet('/your-endpoint');
    // Handle response
}
```

### Adding WebSocket Events

1. Server side (`game_server.py`):
```python
@socketio.on('your_event')
def handle_your_event(data):
    emit('response_event', {'data': ...})
```

2. Client side (`game.js`):
```javascript
this.socket.on('your_event', (data) => {
    // Handle event
});
```

## Files Modified

- ✅ `game_server.py` - Fixed API endpoints and simulation loop
- ✅ `SimulationEngine/src/entities/location.py` - Fixed season conversion
- ✅ `test_integration.py` - Comprehensive test suite
- ✅ `demo_client_connection.py` - Demo script

## Next Steps

Potential enhancements:
- Add player state management
- Implement inventory system
- Add quest system
- Create combat mechanics
- Add save/load functionality
- Improve NPC AI behaviors
- Add more dynamic events

## Support

For issues or questions:
1. Check server logs: `tail -f server.log`
2. Run integration tests: `python3 test_integration.py`
3. Run demo: `python3 demo_client_connection.py`
