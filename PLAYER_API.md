# Player Database and API Documentation

## Overview

The R-Gen game server now includes a comprehensive player management system with:
- Player account registration and authentication
- Player stats (health, mana, energy, attributes)
- Inventory management (add, remove, update items)
- Session-based authentication
- SQLite/PostgreSQL database support

## Database Schema

### Players Table
Stores player account and character information.

```sql
CREATE TABLE players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE,
    character_name TEXT NOT NULL,
    race TEXT,
    class TEXT,
    level INTEGER DEFAULT 1,
    experience INTEGER DEFAULT 0,
    gold INTEGER DEFAULT 100,
    current_location_id TEXT,
    data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Player Stats Table
Stores player character stats and attributes.

```sql
CREATE TABLE player_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER UNIQUE NOT NULL,
    health INTEGER DEFAULT 100,
    max_health INTEGER DEFAULT 100,
    mana INTEGER DEFAULT 100,
    max_mana INTEGER DEFAULT 100,
    energy INTEGER DEFAULT 100,
    max_energy INTEGER DEFAULT 100,
    strength INTEGER DEFAULT 10,
    dexterity INTEGER DEFAULT 10,
    intelligence INTEGER DEFAULT 10,
    constitution INTEGER DEFAULT 10,
    wisdom INTEGER DEFAULT 10,
    charisma INTEGER DEFAULT 10,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
)
```

### Player Inventory Table
Stores items in player's inventory.

```sql
CREATE TABLE player_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    item_type TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    equipped INTEGER DEFAULT 0,
    data TEXT NOT NULL,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
)
```

## API Endpoints

### Authentication Endpoints

#### Register Player
Create a new player account.

**Endpoint:** `POST /api/player/register`

**Request Body:**
```json
{
  "username": "hero123",
  "password": "securepassword",
  "character_name": "Aragorn",
  "email": "hero@example.com",
  "race": "Human",
  "class": "Warrior"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Player registered successfully",
  "player": {
    "id": 1,
    "username": "hero123",
    "character_name": "Aragorn",
    "race": "Human",
    "class": "Warrior",
    "level": 1,
    "gold": 100,
    "current_location_id": "loc_001",
    "stats": {
      "health": 100,
      "max_health": 100,
      "strength": 10,
      ...
    }
  }
}
```

#### Login
Authenticate and create a session.

**Endpoint:** `POST /api/player/login`

**Request Body:**
```json
{
  "username": "hero123",
  "password": "securepassword"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Login successful",
  "player": {
    "id": 1,
    "username": "hero123",
    "character_name": "Aragorn",
    "level": 1,
    ...
  }
}
```

#### Logout
End the current session.

**Endpoint:** `POST /api/player/logout`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### Player Data Endpoints

#### Get Current Player
Retrieve full player data including stats and inventory.

**Endpoint:** `GET /api/player/me`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "player": {
    "id": 1,
    "username": "hero123",
    "character_name": "Aragorn",
    "race": "Human",
    "class": "Warrior",
    "level": 2,
    "experience": 150,
    "gold": 250,
    "current_location_id": "loc_001",
    "stats": { ... },
    "inventory": [ ... ]
  }
}
```

#### Update Player Data
Update player information (level, experience, gold, etc.).

**Endpoint:** `PATCH /api/player/update`

**Authentication:** Required

**Request Body:**
```json
{
  "level": 3,
  "experience": 300,
  "gold": 500
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "player": { ... }
}
```

### Stats Endpoints

#### Get Player Stats
Retrieve player's current stats.

**Endpoint:** `GET /api/player/stats`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "stats": {
    "health": 90,
    "max_health": 100,
    "mana": 100,
    "max_mana": 100,
    "energy": 85,
    "max_energy": 100,
    "strength": 15,
    "dexterity": 12,
    "intelligence": 10,
    "constitution": 14,
    "wisdom": 10,
    "charisma": 8,
    "updated_at": "2025-11-20T10:30:00"
  }
}
```

#### Update Player Stats
Update one or more player stats.

**Endpoint:** `PATCH /api/player/stats`

**Authentication:** Required

**Request Body:**
```json
{
  "health": 95,
  "strength": 16
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "stats": { ... }
}
```

### Inventory Endpoints

#### Get Player Inventory
Retrieve all items in player's inventory.

**Endpoint:** `GET /api/player/inventory`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "inventory": [
    {
      "id": 1,
      "item_name": "Iron Sword",
      "item_type": "weapon",
      "quantity": 1,
      "equipped": true,
      "data": {
        "damage": "1d8",
        "weight": 3.5,
        "value": 50
      },
      "acquired_at": "2025-11-20T10:00:00"
    },
    {
      "id": 2,
      "item_name": "Health Potion",
      "item_type": "consumable",
      "quantity": 5,
      "equipped": false,
      "data": {
        "healing": 50,
        "weight": 0.5,
        "value": 25
      },
      "acquired_at": "2025-11-20T10:15:00"
    }
  ]
}
```

#### Add Item to Inventory
Add a new item to player's inventory.

**Endpoint:** `POST /api/player/inventory`

**Authentication:** Required

**Request Body:**
```json
{
  "item_name": "Steel Sword",
  "item_type": "weapon",
  "quantity": 1,
  "item_data": {
    "damage": "2d6",
    "weight": 4.0,
    "value": 150
  }
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Item added to inventory",
  "inventory_id": 3
}
```

#### Remove Item from Inventory
Remove or reduce quantity of an item.

**Endpoint:** `DELETE /api/player/inventory/{inventory_id}`

**Authentication:** Required

**Request Body (Optional):**
```json
{
  "quantity": 2
}
```
*If quantity is not specified, the entire item stack is removed.*

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Item removed from inventory"
}
```

#### Update Inventory Item
Update item properties (e.g., equip/unequip).

**Endpoint:** `PATCH /api/player/inventory/{inventory_id}`

**Authentication:** Required

**Request Body:**
```json
{
  "equipped": true
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Item updated"
}
```

### Travel Endpoint

#### Travel to Location
Move player to a new location.

**Endpoint:** `POST /api/player/travel`

**Authentication:** Required

**Request Body:**
```json
{
  "location_id": "loc_005"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "location_id": "loc_005",
  "message": "Traveled to Whispering Woods"
}
```

## Error Responses

All endpoints may return error responses:

**401 Unauthorized** - Authentication required
```json
{
  "error": "Authentication required"
}
```

**404 Not Found** - Resource not found
```json
{
  "error": "Player not found"
}
```

**400 Bad Request** - Invalid request data
```json
{
  "error": "Missing required field: username"
}
```

**500 Internal Server Error** - Server error
```json
{
  "error": "Registration failed: <error details>"
}
```

## Testing

Run the test suite to verify all functionality:

```bash
python test_player_system.py
```

This will test:
- Player creation and retrieval
- Stats management
- Inventory operations (add, remove, update, equip)
- Player data updates

## Example Usage with cURL

### Register a new player
```bash
curl -X POST http://localhost:5000/api/player/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "adventurer",
    "password": "secret123",
    "character_name": "Brave Hero",
    "race": "Elf",
    "class": "Ranger"
  }' \
  -c cookies.txt
```

### Login
```bash
curl -X POST http://localhost:5000/api/player/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "adventurer",
    "password": "secret123"
  }' \
  -c cookies.txt
```

### Get player data
```bash
curl -X GET http://localhost:5000/api/player/me \
  -b cookies.txt
```

### Add item to inventory
```bash
curl -X POST http://localhost:5000/api/player/inventory \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "item_name": "Magic Sword",
    "item_type": "weapon",
    "quantity": 1,
    "item_data": {
      "damage": "3d6",
      "magical": true,
      "enchantment": "fire",
      "value": 500
    }
  }'
```

### Get inventory
```bash
curl -X GET http://localhost:5000/api/player/inventory \
  -b cookies.txt
```

### Update stats
```bash
curl -X PATCH http://localhost:5000/api/player/stats \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "health": 95,
    "strength": 12
  }'
```

## Security Notes

- Passwords are hashed using Werkzeug's `generate_password_hash` (PBKDF2 by default)
- Sessions are server-side with secure cookies
- All authenticated endpoints check for valid session
- Set `SECRET_KEY` environment variable in production
- Use HTTPS in production to protect session cookies

## Database Migration

If you have an existing R-Gen database, the new player tables will be created automatically on first run. No migration is required.

To use a fresh database:
```bash
rm r_gen.db
python game_server.py
```

## Future Enhancements

Potential additions:
- Player guilds/parties
- Quest tracking system
- Achievement system
- Player-to-player trading
- Equipment slots and stat bonuses
- Skill trees and abilities
- Player housing/storage
