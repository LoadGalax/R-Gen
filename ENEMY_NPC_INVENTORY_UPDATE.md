# NPC & Enemy Inventory Generation Update

## Summary

This update improves NPC and enemy generation by implementing profession-specific inventory sets and using a race-based enemy system where enemies are generated from **race (what they ARE) + profession (what they DO)** instead of hardcoded enemy types.

## Changes Made

### 1. Profession-Specific Inventory Sets

**File**: `GenerationEngine/data/item_sets.json`

Added specific inventory sets for each profession:

- `guard_inventory` - Guards carry weapons and armor
- `alchemist_inventory` - Alchemists carry potions and scrolls
- `innkeeper_inventory` - Innkeepers carry potions
- `farmer_inventory` - Farmers carry potions
- `hunter_inventory` - Hunters carry ranged weapons, melee weapons, and potions
- `thief_inventory` - Thieves carry weapons, potions, and jewelry
- `cleric_inventory` - Clerics carry scrolls, potions, and jewelry
- `carpenter_inventory` - Carpenters carry melee weapons (tools)
- `miner_inventory` - Miners carry melee weapons and armor

**Enemy-Specific Inventory Sets:**

- `goblin_inventory` - Goblins carry crude weapons and potions
- `skeleton_inventory` - Skeletons carry weapons and armor
- `orc_inventory` - Orcs carry weapons and armor
- `bandit_inventory` - Bandits carry weapons, potions, and stolen jewelry
- `cultist_inventory` - Cultists carry scrolls, weapons, and potions
- `undead_inventory` - Undead carry weapons and armor
- `beast_inventory` - Beasts carry minimal loot (potions)
- `dragon_inventory` - Dragons hoard jewelry, weapons, and armor

### 2. Updated Profession Configurations

**File**: `GenerationEngine/data/professions.json`

Updated existing professions to use their specific inventory sets instead of generic ones:

- Guard: `warrior_inventory` → `guard_inventory`
- Alchemist: `mage_inventory` → `alchemist_inventory`
- Cleric: `mage_inventory` → `cleric_inventory`
- Innkeeper: `merchant_inventory` → `innkeeper_inventory`
- Farmer: `merchant_inventory` → `farmer_inventory`
- Hunter: `warrior_inventory` → `hunter_inventory`
- Thief: `merchant_inventory` → `thief_inventory`
- Carpenter: `blacksmith_inventory` → `carpenter_inventory`
- Miner: `blacksmith_inventory` → `miner_inventory`

### 3. New Enemy Races

Added 4 new enemy races to the race system (`GenerationEngine/data/races.json`):

#### Goblin (Race)
- **Base Stats**: High DEX (7), Low STR (3), Low CHA (2)
- **Size**: Small
- **Traits**: Cunning, Cowardly, Nimble
- **Special Abilities**: Nimble Escape, Fury of the Small
- **Languages**: Goblin, Common
- **Preferred Biomes**: Cave, Forest, Ruins, Swamp
- **Appearance**: Green skin, yellow eyes, pointed ears, sharp teeth

#### Skeleton (Race)
- **Base Stats**: Balanced STR/DEX/CON (5/5/6), Very Low mental (1/1/1)
- **Size**: Medium
- **Traits**: Undead, Mindless, Tireless
- **Special Abilities**: Undead Fortitude, Mindless
- **Languages**: None (mindless)
- **Preferred Biomes**: Crypt, Tomb, Graveyard, Ruins, Underground
- **Appearance**: Animated bones, empty sockets, skeletal, clicking

#### Zombie (Race)
- **Base Stats**: High CON (8), Low DEX (2), Very Low mental (1/1/1)
- **Size**: Medium
- **Traits**: Undead, Relentless, Mindless
- **Special Abilities**: Undead Fortitude, Relentless
- **Languages**: None (mindless)
- **Preferred Biomes**: Graveyard, Crypt, Ruins, Swamp
- **Appearance**: Rotting flesh, sunken eyes, shambling, moaning

#### Wolf (Race)
- **Base Stats**: Balanced DEX/CON (6/5), Very Low INT (1)
- **Size**: Medium
- **Traits**: Predatory, Pack-Minded, Wild
- **Special Abilities**: Pack Tactics, Keen Senses
- **Languages**: None (beast)
- **Preferred Biomes**: Forest, Wilderness, Mountain, Plains, Tundra
- **Appearance**: Fur, fangs, four-legged, wild eyes, predatory

### 4. Profession Updates

**Added**:
- **Warrior**: Generic combat profession for enemies (uses warrior_inventory)
- Kept **Bandit** and **Cultist** as actual professions (what they DO, not what they ARE)

### 5. New Enemy Generation API Endpoint

**File**: `Game/game_server.py`

Added a new race-based enemy generation endpoint:

**Endpoint**: `POST /api/master/enemy`

**Request Body**:
```json
{
  "race": "goblin",             // goblin, skeleton, orc, zombie, wolf, human, etc.
  "profession": "warrior",      // warrior, bandit, cultist, thief, or null for beasts
  "difficulty": "standard",     // minion (0.5x), standard (1x), elite (1.5x), boss (2.5x)
  "location_id": "forest_1",    // Optional
  "name": "Custom Name"         // Optional custom name
}
```

**Difficulty Multipliers**:
- `minion`: 0.5x stats (weaker enemies for groups)
- `standard`: 1.0x stats (normal enemies)
- `elite`: 1.5x stats (stronger enemies)
- `boss`: 2.5x stats (boss encounters)

**Response**:
```json
{
  "success": true,
  "message": "Standard Goblin Warrior created",
  "enemy_id": "npc_abc123",
  "enemy_data": {
    "name": "Zik Creeper",
    "race": "goblin",
    "professions": ["warrior"],
    "max_health": 50,
    "attack_power": 14,
    "defense": 5,
    "experience_reward": 75,
    "inventory": [
      {"name": "Standard Leather Shield", "type": "armor"},
      {"name": "Excellent Bronze Mace", "type": "weapon"}
    ]
  }
}
```

**Auto-Calculated Stats**:
- `max_health` = Constitution × 10 × difficulty_multiplier
- `attack_power` = (Strength + 5) × difficulty_multiplier
- `defense` = Constitution × difficulty_multiplier
- `experience_reward` = 50 × difficulty_multiplier × (1 + challenge_rating)

**Manual Overrides**:
You can still override any stat by including it in the request:
```json
{
  "enemy_type": "goblin",
  "difficulty": "boss",
  "max_health": 200,
  "attack_power": 30
}
```

## Testing Results

Successfully tested NPC and enemy generation:

### NPC Tests
- **Merchant**: Generated with jewelry (amulet, crown) ✓
- **Blacksmith**: Generated with armor (chestplates, shields) ✓
- **Alchemist**: Generated with potions and scrolls ✓

### Enemy Tests
- **Goblin**: Low-stat enemy with potion ✓
- **Orc**: High-strength warrior with weapons/armor ✓
- **Skeleton**: Undead warrior with rusty weapons ✓

## Usage Examples

### Create a Standard Goblin Warrior
```bash
curl -X POST http://localhost:5000/api/master/enemy \
  -H "Content-Type: application/json" \
  -d '{
    "race": "goblin",
    "profession": "warrior",
    "difficulty": "standard"
  }'
```

### Create a Boss Orc Warrior
```bash
curl -X POST http://localhost:5000/api/master/enemy \
  -H "Content-Type: application/json" \
  -d '{
    "race": "orc",
    "profession": "warrior",
    "difficulty": "boss",
    "name": "Grok the Destroyer",
    "location_id": "mountain_pass_1"
  }'
```

### Create an Elite Skeleton (no profession)
```bash
curl -X POST http://localhost:5000/api/master/enemy \
  -H "Content-Type: application/json" \
  -d '{
    "race": "skeleton",
    "difficulty": "elite"
  }'
```

### Create a Human Bandit
```bash
curl -X POST http://localhost:5000/api/master/enemy \
  -H "Content-Type: application/json" \
  -d '{
    "race": "human",
    "profession": "bandit",
    "difficulty": "standard"
  }'
```

### Create a Wolf Pack (minions)
```bash
curl -X POST http://localhost:5000/api/master/enemy \
  -H "Content-Type: application/json" \
  -d '{
    "race": "wolf",
    "difficulty": "minion"
  }'
```

### Create an Orc Bandit (cross combinations!)
```bash
curl -X POST http://localhost:5000/api/master/enemy \
  -H "Content-Type: application/json" \
  -d '{
    "race": "orc",
    "profession": "bandit",
    "difficulty": "standard"
  }'
```

### Create a Merchant NPC with Appropriate Inventory
```bash
curl -X POST http://localhost:5000/api/master/npc \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gundren Rockseeker",
    "professions": ["merchant"],
    "location_id": "phandalin_1"
  }'
```

## Benefits

1. **More Realistic Inventories**: NPCs now carry items appropriate to their profession
   - Merchants have jewelry and potions (not weapons)
   - Guards have weapons and armor (not scrolls)
   - Farmers have basic consumables
   - Alchemists have potions and scrolls

2. **Race-Based Enemy System**: Enemies use race + profession combinations
   - **Races** (what they ARE): goblin, orc, skeleton, zombie, wolf, human, etc.
   - **Professions** (what they DO): warrior, bandit, cultist, thief, etc.
   - Any race can have any profession: goblin bandit, orc cultist, human warrior

3. **Flexible Combinations**: Unlimited enemy variety
   - Goblin Warrior - sneaky fighter
   - Orc Bandit - brutal outlaw
   - Human Cultist - dark mage
   - Skeleton - mindless undead (no profession)
   - Wolf - wild beast (no profession)

4. **Flexible Difficulty**: Single enemy type can be scaled from minion to boss
   - Spawn groups of weak minions (0.5x stats)
   - Create challenging boss encounters (2.5x stats)
   - Balance encounters easily

5. **Better Loot Tables**: Enemies drop items based on their profession
   - Warriors drop weapons/armor
   - Bandits drop weapons/stolen goods
   - Cultists drop scrolls/dark items
   - Beasts drop minimal loot

6. **Proper Architecture**: Follows D&D-style conventions
   - Races define physical/mental attributes
   - Professions define skills and inventory
   - No duplicate/redundant definitions

## Backward Compatibility

All existing functionality remains unchanged:
- Old NPC generation still works
- Existing NPCs are unaffected
- Original `/api/master/npc` endpoint still available
- New enemy endpoint is additive, not replacing anything
- Orc race was already in races.json, no breaking changes
