# NPC & Enemy Inventory Generation Update

## Summary

This update improves NPC and enemy generation by implementing profession-specific inventory sets and adding dedicated enemy types with appropriate loot.

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

### 3. New Enemy Professions

Added 7 new enemy types with full profession definitions:

#### Goblin
- **Stats**: High DEX (8), Low STR (4)
- **Skills**: Stealth, Ambush, Backstab, Scavenging
- **Inventory**: Crude weapons and potions
- **Typical Locations**: Cave, Forest, Ruins

#### Skeleton
- **Stats**: Balanced STR/CON (6/8), Very Low INT/WIS/CHA (2/2/1)
- **Skills**: Combat, Endurance, Relentless, Undead
- **Inventory**: Rusty weapons and armor
- **Typical Locations**: Crypt, Tomb, Graveyard

#### Orc
- **Stats**: High STR/CON (8/8), Low INT (3)
- **Skills**: Combat, Intimidation, Endurance, Rage
- **Inventory**: Brutal weapons and armor
- **Typical Locations**: Mountain, Battlefield, Stronghold

#### Bandit
- **Stats**: Balanced (6/7/6)
- **Skills**: Combat, Stealth, Intimidation, Robbery
- **Inventory**: Weapons, potions, and stolen jewelry
- **Typical Locations**: Forest, Road, Hideout

#### Cultist
- **Stats**: High INT/CHA (7/7), Low STR (4)
- **Skills**: Dark Magic, Rituals, Persuasion, Curses
- **Inventory**: Dark scrolls, weapons, potions
- **Typical Locations**: Ruins, Temple, Underground

#### Zombie
- **Stats**: High CON (9), Very Low INT/WIS/CHA (1/1/1)
- **Skills**: Endurance, Grapple, Relentless, Undead
- **Inventory**: Minimal (weapons/armor from their past life)
- **Typical Locations**: Graveyard, Crypt, Ruins

#### Wolf
- **Stats**: Balanced DEX/CON (7/6), Low INT/CHA (2/2)
- **Skills**: Tracking, Bite, Pack Tactics, Stealth
- **Inventory**: Minimal beast loot
- **Typical Locations**: Forest, Wilderness, Mountain

### 4. New Enemy Generation API Endpoint

**File**: `Game/game_server.py`

Added a new dedicated endpoint for easier enemy creation:

**Endpoint**: `POST /api/master/enemy`

**Request Body**:
```json
{
  "enemy_type": "goblin",      // goblin, skeleton, orc, bandit, cultist, zombie, wolf
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
  "message": "Standard Goblin created",
  "enemy_id": "npc_abc123",
  "enemy_data": {
    "name": "Snik Raider",
    "max_health": 50,
    "attack_power": 14,
    "defense": 5,
    "experience_reward": 75,
    "inventory": [...]
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

### Create a Standard Goblin Enemy
```bash
curl -X POST http://localhost:5000/api/master/enemy \
  -H "Content-Type: application/json" \
  -d '{
    "enemy_type": "goblin",
    "difficulty": "standard"
  }'
```

### Create a Boss Orc
```bash
curl -X POST http://localhost:5000/api/master/enemy \
  -H "Content-Type: application/json" \
  -d '{
    "enemy_type": "orc",
    "difficulty": "boss",
    "name": "Grok the Destroyer",
    "location_id": "mountain_pass_1"
  }'
```

### Create a Minion Skeleton (for groups)
```bash
curl -X POST http://localhost:5000/api/master/enemy \
  -H "Content-Type: application/json" \
  -d '{
    "enemy_type": "skeleton",
    "difficulty": "minion"
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
   - Merchants have jewelry and potions
   - Guards have weapons and armor
   - Farmers have basic consumables
   - Alchemists have potions and scrolls

2. **Enemy Variety**: 7 different enemy types with unique stats and loot
   - Weak but sneaky goblins
   - Tough orcs with heavy weapons
   - Undead with rusted gear
   - Smart cultists with magic items

3. **Flexible Difficulty**: Single enemy type can be scaled from minion to boss
   - Spawn groups of weak minions
   - Create challenging boss encounters
   - Balance encounters easily

4. **Better Loot Tables**: Enemies drop appropriate items
   - Warriors drop weapons/armor
   - Casters drop scrolls/potions
   - Bandits drop stolen goods
   - Beasts drop minimal loot

## Backward Compatibility

All existing functionality remains unchanged:
- Old NPC generation still works
- Existing NPCs are unaffected
- Original `/api/master/npc` endpoint still available
- New enemy endpoint is additive, not replacing anything
