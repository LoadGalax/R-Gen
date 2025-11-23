"""
Game Server Database Module
Handles all game server data storage (players, professions, etc.)
Separate from GenerationEngine - this is for game state only
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import contextmanager


class GameDatabase:
    """Database manager for game server state."""

    def __init__(self, db_path: str = "game_server.db"):
        """Initialize game database."""
        self.db_path = db_path
        self._init_database()

    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_database(self):
        """Initialize database tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Players table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Migrate existing tables - add new columns if they don't exist
            self._migrate_database(cursor)

            # Player stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_stats (
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
                    carrying_capacity REAL DEFAULT 0.0,
                    max_carrying_capacity REAL DEFAULT 100.0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
                )
            """)

            # Player inventory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    equipped INTEGER DEFAULT 0,
                    data TEXT NOT NULL,
                    weight REAL DEFAULT 1.0,
                    durability INTEGER DEFAULT 100,
                    max_durability INTEGER DEFAULT 100,
                    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
                )
            """)

            # Recipes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipe_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    profession TEXT NOT NULL,
                    category TEXT NOT NULL,
                    required_level INTEGER DEFAULT 1,
                    difficulty INTEGER DEFAULT 1,
                    ingredients TEXT NOT NULL,
                    result_item_name TEXT NOT NULL,
                    result_item_type TEXT NOT NULL,
                    result_item_data TEXT NOT NULL,
                    result_quantity INTEGER DEFAULT 1,
                    crafting_time INTEGER DEFAULT 5,
                    experience_gain INTEGER DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Player known recipes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_known_recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    recipe_id TEXT NOT NULL,
                    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    times_crafted INTEGER DEFAULT 0,
                    UNIQUE(player_id, recipe_id),
                    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
                    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE
                )
            """)

            # Player professions table (stores player's profession progress)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_professions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    profession_id TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    experience INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(player_id, profession_id),
                    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
                )
            """)

            # Standalone generated items table (items not owned by anyone yet)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generated_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    item_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Settings table for system configuration
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def _migrate_database(self, cursor):
        """Migrate existing database schema to add new columns."""
        # Check and add carrying_capacity columns to player_stats
        cursor.execute("PRAGMA table_info(player_stats)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'carrying_capacity' not in columns:
            print("Migrating database: Adding carrying_capacity to player_stats...")
            cursor.execute("ALTER TABLE player_stats ADD COLUMN carrying_capacity REAL DEFAULT 0.0")

        if 'max_carrying_capacity' not in columns:
            print("Migrating database: Adding max_carrying_capacity to player_stats...")
            cursor.execute("ALTER TABLE player_stats ADD COLUMN max_carrying_capacity REAL DEFAULT 100.0")

        # Check and add new columns to player_inventory
        cursor.execute("PRAGMA table_info(player_inventory)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'weight' not in columns:
            print("Migrating database: Adding weight to player_inventory...")
            cursor.execute("ALTER TABLE player_inventory ADD COLUMN weight REAL DEFAULT 1.0")

        if 'durability' not in columns:
            print("Migrating database: Adding durability to player_inventory...")
            cursor.execute("ALTER TABLE player_inventory ADD COLUMN durability INTEGER DEFAULT 100")

        if 'max_durability' not in columns:
            print("Migrating database: Adding max_durability to player_inventory...")
            cursor.execute("ALTER TABLE player_inventory ADD COLUMN max_durability INTEGER DEFAULT 100")

    # ===================================================================
    # Player Management
    # ===================================================================

    def create_player(self, username: str, password_hash: str, character_name: str,
                     email: Optional[str] = None, race: str = "Human",
                     character_class: str = "Adventurer",
                     starting_location: Optional[str] = None) -> int:
        """Create a new player."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO players (username, password_hash, email, character_name,
                                   race, class, current_location_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, password_hash, email, character_name, race,
                  character_class, starting_location))

            player_id = cursor.lastrowid

            # Create player stats
            cursor.execute("""
                INSERT INTO player_stats (player_id)
                VALUES (?)
            """, (player_id,))

            conn.commit()
            return player_id

    def get_player_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get player by username."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, password_hash, email, character_name, race, class,
                       level, experience, gold, current_location_id, created_at, last_login
                FROM players WHERE username = ?
            """, (username,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_player_by_id(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get player by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, password_hash, email, character_name, race, class,
                       level, experience, gold, current_location_id, created_at, last_login
                FROM players WHERE id = ?
            """, (player_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def update_player(self, player_id: int, updates: Dict[str, Any]) -> bool:
        """Update player data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            allowed_fields = ['character_name', 'race', 'class', 'level', 'experience',
                            'gold', 'current_location_id', 'email', 'last_login']

            set_clauses = []
            params = []

            for field, value in updates.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)

            if not set_clauses:
                return False

            params.append(player_id)
            query = f"UPDATE players SET {', '.join(set_clauses)} WHERE id = ?"

            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0

    # ===================================================================
    # Player Stats Management
    # ===================================================================

    def get_player_stats(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get player stats."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT health, max_health, mana, max_mana, energy, max_energy,
                       strength, dexterity, intelligence, constitution, wisdom, charisma,
                       carrying_capacity, max_carrying_capacity, updated_at
                FROM player_stats WHERE player_id = ?
            """, (player_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def update_player_stats(self, player_id: int, updates: Dict[str, Any]) -> bool:
        """Update player stats."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            allowed_fields = ['health', 'max_health', 'mana', 'max_mana', 'energy', 'max_energy',
                            'strength', 'dexterity', 'intelligence', 'constitution', 'wisdom', 'charisma',
                            'carrying_capacity', 'max_carrying_capacity']

            set_clauses = []
            params = []

            for field, value in updates.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)

            if not set_clauses:
                return False

            set_clauses.append("updated_at = ?")
            params.append(datetime.now())
            params.append(player_id)

            query = f"UPDATE player_stats SET {', '.join(set_clauses)} WHERE player_id = ?"

            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0

    # ===================================================================
    # Player Inventory Management
    # ===================================================================

    def get_player_inventory(self, player_id: int) -> List[Dict[str, Any]]:
        """Get player inventory."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, item_name, item_type, quantity, equipped, data, weight,
                       durability, max_durability, acquired_at
                FROM player_inventory WHERE player_id = ?
                ORDER BY acquired_at DESC
            """, (player_id,))

            return [dict(row) for row in cursor.fetchall()]

    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get all items from both player inventories and generated items."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    i.id,
                    i.player_id,
                    p.character_name as player_name,
                    i.item_name,
                    i.item_type,
                    i.quantity,
                    i.equipped,
                    i.data,
                    i.acquired_at as timestamp
                FROM player_inventory i
                LEFT JOIN players p ON i.player_id = p.id

                UNION ALL

                SELECT
                    g.id,
                    NULL as player_id,
                    'Generated' as player_name,
                    g.item_name,
                    g.item_type,
                    1 as quantity,
                    0 as equipped,
                    g.item_data as data,
                    g.created_at as timestamp
                FROM generated_items g

                ORDER BY timestamp DESC
            """)

            return [dict(row) for row in cursor.fetchall()]

    def add_to_inventory(self, player_id: int, item_name: str, item_type: str,
                        item_data: Dict[str, Any], quantity: int = 1, weight: float = 1.0,
                        durability: Optional[int] = None, max_durability: Optional[int] = None) -> int:
        """Add item to inventory. Auto-stacks if similar item exists."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Set default durability values
            if durability is None:
                durability = 100
            if max_durability is None:
                max_durability = 100

            # Try to find similar item to stack with
            cursor.execute("""
                SELECT id, quantity FROM player_inventory
                WHERE player_id = ? AND item_name = ? AND item_type = ? AND equipped = 0
                LIMIT 1
            """, (player_id, item_name, item_type))

            existing = cursor.fetchone()
            if existing:
                # Stack with existing item
                cursor.execute("""
                    UPDATE player_inventory
                    SET quantity = quantity + ?
                    WHERE id = ? AND player_id = ?
                """, (quantity, existing['id'], player_id))
                conn.commit()
                return existing['id']
            else:
                # Add as new item
                cursor.execute("""
                    INSERT INTO player_inventory (player_id, item_name, item_type, quantity, data, weight, durability, max_durability)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (player_id, item_name, item_type, quantity, json.dumps(item_data), weight, durability, max_durability))

                conn.commit()
                return cursor.lastrowid

    def remove_from_inventory(self, player_id: int, inventory_id: int,
                             quantity: Optional[int] = None) -> bool:
        """Remove item from inventory."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if quantity is None:
                # Remove entire stack
                cursor.execute("""
                    DELETE FROM player_inventory
                    WHERE id = ? AND player_id = ?
                """, (inventory_id, player_id))
            else:
                # Reduce quantity
                cursor.execute("""
                    UPDATE player_inventory
                    SET quantity = quantity - ?
                    WHERE id = ? AND player_id = ? AND quantity >= ?
                """, (quantity, inventory_id, player_id, quantity))

                # Remove if quantity is 0 or less
                cursor.execute("""
                    DELETE FROM player_inventory
                    WHERE id = ? AND player_id = ? AND quantity <= 0
                """, (inventory_id, player_id))

            conn.commit()
            return cursor.rowcount > 0

    def update_inventory_item(self, inventory_id: int, player_id: int,
                             updates: Dict[str, Any]) -> bool:
        """Update inventory item."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            allowed_fields = ['equipped', 'quantity', 'durability', 'max_durability']
            set_clauses = []
            params = []

            for field, value in updates.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)

            if not set_clauses:
                return False

            params.extend([inventory_id, player_id])
            query = f"UPDATE player_inventory SET {', '.join(set_clauses)} WHERE id = ? AND player_id = ?"

            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0

    def calculate_carrying_weight(self, player_id: int) -> float:
        """Calculate total carrying weight for a player."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(weight * quantity) as total_weight
                FROM player_inventory
                WHERE player_id = ?
            """, (player_id,))

            row = cursor.fetchone()
            return row['total_weight'] if row['total_weight'] else 0.0

    # ===================================================================
    # Player Professions Management
    # ===================================================================

    def get_player_professions(self, player_id: int) -> List[Dict[str, Any]]:
        """Get player's professions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, profession_id, level, experience, created_at, updated_at
                FROM player_professions
                WHERE player_id = ?
                ORDER BY level DESC, experience DESC
            """, (player_id,))

            return [dict(row) for row in cursor.fetchall()]

    def add_player_profession(self, player_id: int, profession_id: str,
                             level: int = 1, experience: int = 0) -> int:
        """Add a profession to player."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO player_professions (player_id, profession_id, level, experience)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(player_id, profession_id)
                DO UPDATE SET level = ?, experience = ?, updated_at = ?
            """, (player_id, profession_id, level, experience, level, experience, datetime.now()))

            conn.commit()
            return cursor.lastrowid

    def update_player_profession(self, player_id: int, profession_id: str,
                                level: Optional[int] = None,
                                experience: Optional[int] = None) -> bool:
        """Update player's profession."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            set_clauses = []
            params = []

            if level is not None:
                set_clauses.append("level = ?")
                params.append(level)

            if experience is not None:
                set_clauses.append("experience = ?")
                params.append(experience)

            if not set_clauses:
                return False

            set_clauses.append("updated_at = ?")
            params.append(datetime.now())
            params.extend([player_id, profession_id])

            query = f"""
                UPDATE player_professions
                SET {', '.join(set_clauses)}
                WHERE player_id = ? AND profession_id = ?
            """

            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0

    # ===================================================================
    # Generated Items Management
    # ===================================================================

    def save_generated_item(self, item_name: str, item_type: str, item_data: Dict[str, Any]) -> int:
        """Save a generated item to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO generated_items (item_name, item_type, item_data)
                VALUES (?, ?, ?)
            """, (item_name, item_type, json.dumps(item_data)))

            conn.commit()
            return cursor.lastrowid

    def get_all_generated_items(self) -> List[Dict[str, Any]]:
        """Get all generated items."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, item_name, item_type, item_data, created_at
                FROM generated_items
                ORDER BY created_at DESC
            """)

            items = []
            for row in cursor.fetchall():
                item = dict(row)
                try:
                    item['data'] = json.loads(item['item_data'])
                except:
                    item['data'] = {}
                items.append(item)

            return items

    def delete_generated_item(self, item_id: int) -> bool:
        """Delete a generated item."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM generated_items WHERE id = ?", (item_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ===================================================================
    # Settings Management
    # ===================================================================

    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value by key."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else None

    def get_all_settings(self) -> Dict[str, str]:
        """Get all settings."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            return {row['key']: row['value'] for row in cursor.fetchall()}

    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting value."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = ?
            """, (key, value, datetime.now(), value, datetime.now()))
            conn.commit()
            return True

    def delete_setting(self, key: str) -> bool:
        """Delete a setting."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM settings WHERE key = ?", (key,))
            conn.commit()
            return cursor.rowcount > 0

    # ===================================================================
    # Recipe Management
    # ===================================================================

    def add_recipe(self, recipe_id: str, name: str, profession: str, category: str,
                   required_level: int, difficulty: int, ingredients: List[Dict[str, Any]],
                   result_item_name: str, result_item_type: str, result_item_data: Dict[str, Any],
                   result_quantity: int = 1, crafting_time: int = 5, experience_gain: int = 10) -> int:
        """Add a recipe to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO recipes (recipe_id, name, profession, category, required_level, difficulty,
                                   ingredients, result_item_name, result_item_type, result_item_data,
                                   result_quantity, crafting_time, experience_gain)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (recipe_id, name, profession, category, required_level, difficulty,
                  json.dumps(ingredients), result_item_name, result_item_type,
                  json.dumps(result_item_data), result_quantity, crafting_time, experience_gain))

            conn.commit()
            return cursor.lastrowid

    def get_all_recipes(self) -> List[Dict[str, Any]]:
        """Get all recipes."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT recipe_id, name, profession, category, required_level, difficulty,
                       ingredients, result_item_name, result_item_type, result_item_data,
                       result_quantity, crafting_time, experience_gain, created_at
                FROM recipes
                ORDER BY profession, required_level
            """)

            recipes = []
            for row in cursor.fetchall():
                recipe = dict(row)
                try:
                    recipe['ingredients'] = json.loads(recipe['ingredients'])
                    recipe['result_item_data'] = json.loads(recipe['result_item_data'])
                except:
                    recipe['ingredients'] = []
                    recipe['result_item_data'] = {}
                recipes.append(recipe)

            return recipes

    def get_recipes_by_profession(self, profession: str) -> List[Dict[str, Any]]:
        """Get recipes for a specific profession."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT recipe_id, name, profession, category, required_level, difficulty,
                       ingredients, result_item_name, result_item_type, result_item_data,
                       result_quantity, crafting_time, experience_gain, created_at
                FROM recipes
                WHERE profession = ?
                ORDER BY required_level
            """, (profession,))

            recipes = []
            for row in cursor.fetchall():
                recipe = dict(row)
                try:
                    recipe['ingredients'] = json.loads(recipe['ingredients'])
                    recipe['result_item_data'] = json.loads(recipe['result_item_data'])
                except:
                    recipe['ingredients'] = []
                    recipe['result_item_data'] = {}
                recipes.append(recipe)

            return recipes

    def get_recipe_by_id(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific recipe by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT recipe_id, name, profession, category, required_level, difficulty,
                       ingredients, result_item_name, result_item_type, result_item_data,
                       result_quantity, crafting_time, experience_gain, created_at
                FROM recipes
                WHERE recipe_id = ?
            """, (recipe_id,))

            row = cursor.fetchone()
            if row:
                recipe = dict(row)
                try:
                    recipe['ingredients'] = json.loads(recipe['ingredients'])
                    recipe['result_item_data'] = json.loads(recipe['result_item_data'])
                except:
                    recipe['ingredients'] = []
                    recipe['result_item_data'] = {}
                return recipe
            return None

    # ===================================================================
    # Player Known Recipes Management
    # ===================================================================

    def add_player_recipe(self, player_id: int, recipe_id: str) -> int:
        """Add a recipe to player's known recipes."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO player_known_recipes (player_id, recipe_id)
                VALUES (?, ?)
                ON CONFLICT(player_id, recipe_id) DO NOTHING
            """, (player_id, recipe_id))

            conn.commit()
            return cursor.lastrowid

    def get_player_known_recipes(self, player_id: int) -> List[Dict[str, Any]]:
        """Get all recipes known by a player."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pkr.recipe_id, pkr.learned_at, pkr.times_crafted,
                       r.name, r.profession, r.category, r.required_level, r.difficulty,
                       r.ingredients, r.result_item_name, r.result_item_type, r.result_item_data,
                       r.result_quantity, r.crafting_time, r.experience_gain
                FROM player_known_recipes pkr
                JOIN recipes r ON pkr.recipe_id = r.recipe_id
                WHERE pkr.player_id = ?
                ORDER BY r.profession, r.required_level
            """, (player_id,))

            recipes = []
            for row in cursor.fetchall():
                recipe = dict(row)
                try:
                    recipe['ingredients'] = json.loads(recipe['ingredients'])
                    recipe['result_item_data'] = json.loads(recipe['result_item_data'])
                except:
                    recipe['ingredients'] = []
                    recipe['result_item_data'] = {}
                recipes.append(recipe)

            return recipes

    def increment_recipe_craft_count(self, player_id: int, recipe_id: str) -> bool:
        """Increment the times_crafted counter for a recipe."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE player_known_recipes
                SET times_crafted = times_crafted + 1
                WHERE player_id = ? AND recipe_id = ?
            """, (player_id, recipe_id))

            conn.commit()
            return cursor.rowcount > 0
