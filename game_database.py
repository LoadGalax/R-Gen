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
                    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
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

            conn.commit()

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
                       updated_at
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
                            'strength', 'dexterity', 'intelligence', 'constitution', 'wisdom', 'charisma']

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
                SELECT id, item_name, item_type, quantity, equipped, data, acquired_at
                FROM player_inventory WHERE player_id = ?
                ORDER BY acquired_at DESC
            """, (player_id,))

            return [dict(row) for row in cursor.fetchall()]

    def add_to_inventory(self, player_id: int, item_name: str, item_type: str,
                        item_data: Dict[str, Any], quantity: int = 1) -> int:
        """Add item to inventory."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO player_inventory (player_id, item_name, item_type, quantity, data)
                VALUES (?, ?, ?, ?, ?)
            """, (player_id, item_name, item_type, quantity, json.dumps(item_data)))

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

            allowed_fields = ['equipped', 'quantity']
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
