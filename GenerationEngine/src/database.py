"""
Database integration layer for R-Gen content generator.

Supports SQLite and PostgreSQL for storing and retrieving generated content.
Includes history tracking for all generated items, NPCs, locations, and worlds.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from contextlib import contextmanager


class DatabaseManager:
    """
    Database manager for storing and retrieving generated content.

    Supports both SQLite and PostgreSQL backends.
    """

    def __init__(self, db_path: str = "r_gen.db", db_type: str = "sqlite"):
        """
        Initialize the database manager.

        Args:
            db_path: Path to SQLite database file or PostgreSQL connection string
            db_type: Database type ('sqlite' or 'postgresql')
        """
        self.db_path = db_path
        self.db_type = db_type

        if db_type == "sqlite":
            self._init_sqlite()
        elif db_type == "postgresql":
            self._init_postgresql()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def _init_sqlite(self):
        """Initialize SQLite database and create tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Create items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    subtype TEXT,
                    quality TEXT,
                    rarity TEXT,
                    value INTEGER,
                    material TEXT,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seed INTEGER
                )
            """)

            # Create NPCs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS npcs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    archetype TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seed INTEGER
                )
            """)

            # Create locations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seed INTEGER
                )
            """)

            # Create worlds table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS worlds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    num_locations INTEGER,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seed INTEGER
                )
            """)

            # Create animals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS animals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    species TEXT NOT NULL,
                    category TEXT NOT NULL,
                    size TEXT,
                    danger_level TEXT,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seed INTEGER
                )
            """)

            # Create flora table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flora (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    species TEXT NOT NULL,
                    category TEXT NOT NULL,
                    rarity TEXT,
                    magical INTEGER,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seed INTEGER
                )
            """)

            # Create generation history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT NOT NULL,
                    content_id INTEGER NOT NULL,
                    template_name TEXT,
                    constraints TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seed INTEGER
                )
            """)

            # Create players table
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
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create player_inventory table
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

            # Create player_stats table
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

            # Create professions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS professions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    icon TEXT,
                    description TEXT,
                    profession_type TEXT,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create player_professions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_professions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    profession_id INTEGER NOT NULL,
                    level INTEGER DEFAULT 1,
                    experience INTEGER DEFAULT 0,
                    data TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
                    FOREIGN KEY (profession_id) REFERENCES professions(id) ON DELETE CASCADE,
                    UNIQUE(player_id, profession_id)
                )
            """)

            # Create recipes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    profession_id INTEGER NOT NULL,
                    required_level INTEGER DEFAULT 1,
                    result_item_name TEXT NOT NULL,
                    result_quantity INTEGER DEFAULT 1,
                    crafting_time INTEGER DEFAULT 5,
                    difficulty TEXT DEFAULT 'medium',
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (profession_id) REFERENCES professions(id) ON DELETE CASCADE
                )
            """)

            # Create recipe_ingredients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recipe_ingredients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipe_id INTEGER NOT NULL,
                    ingredient_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
                )
            """)

            # Create player_recipes table (known recipes)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    recipe_id INTEGER NOT NULL,
                    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    times_crafted INTEGER DEFAULT 0,
                    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
                    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
                    UNIQUE(player_id, recipe_id)
                )
            """)

            # Create indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_type ON items(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_quality ON items(quality)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_rarity ON items(rarity)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_npcs_archetype ON npcs(archetype)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_animals_species ON animals(species)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_animals_category ON animals(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_flora_species ON flora(species)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_flora_category ON flora(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_type ON generation_history(content_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_created ON generation_history(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_username ON players(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_email ON players(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_inventory_player_id ON player_inventory(player_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_inventory_item_type ON player_inventory(item_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_stats_player_id ON player_stats(player_id)")

            conn.commit()

    def _init_postgresql(self):
        """Initialize PostgreSQL database and create tables."""
        try:
            import psycopg2
        except ImportError:
            raise ImportError("psycopg2 package required for PostgreSQL support. Install with: pip install psycopg2-binary")

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Create items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    subtype TEXT,
                    quality TEXT,
                    rarity TEXT,
                    value INTEGER,
                    material TEXT,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seed INTEGER
                )
            """)

            # Create NPCs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS npcs (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    archetype TEXT NOT NULL,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seed INTEGER
                )
            """)

            # Create locations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id SERIAL PRIMARY KEY,
                    location_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seed INTEGER
                )
            """)

            # Create worlds table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS worlds (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    num_locations INTEGER,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seed INTEGER
                )
            """)

            # Create generation history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generation_history (
                    id SERIAL PRIMARY KEY,
                    content_type TEXT NOT NULL,
                    content_id INTEGER NOT NULL,
                    template_name TEXT,
                    constraints JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seed INTEGER
                )
            """)

            # Create players table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
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
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create player_inventory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_inventory (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    equipped BOOLEAN DEFAULT FALSE,
                    data JSONB NOT NULL,
                    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
                )
            """)

            # Create player_stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_stats (
                    id SERIAL PRIMARY KEY,
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

            # Create indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_type ON items(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_quality ON items(quality)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_rarity ON items(rarity)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_npcs_archetype ON npcs(archetype)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_type ON generation_history(content_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_created ON generation_history(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_username ON players(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_email ON players(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_inventory_player_id ON player_inventory(player_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_inventory_item_type ON player_inventory(item_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_stats_player_id ON player_stats(player_id)")

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        if self.db_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
        elif self.db_type == "postgresql":
            import psycopg2
            import psycopg2.extras
            conn = psycopg2.connect(self.db_path)
            try:
                yield conn
            finally:
                conn.close()

    def save_item(self, item: Dict[str, Any], template_name: Optional[str] = None,
                  constraints: Optional[Dict] = None, seed: Optional[int] = None) -> int:
        """
        Save an item to the database.

        Args:
            item: Item dictionary
            template_name: Template used to generate the item
            constraints: Constraints applied during generation
            seed: Random seed used for generation

        Returns:
            Database ID of saved item
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            data_str = json.dumps(item)

            if self.db_type == "sqlite":
                cursor.execute("""
                    INSERT INTO items (name, type, subtype, quality, rarity, value, material, data, seed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item["name"],
                    item["type"],
                    item.get("subtype"),
                    item.get("quality"),
                    item.get("rarity"),
                    item.get("value"),
                    item.get("material"),
                    data_str,
                    seed
                ))
                item_id = cursor.lastrowid
            else:  # postgresql
                cursor.execute("""
                    INSERT INTO items (name, type, subtype, quality, rarity, value, material, data, seed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    item["name"],
                    item["type"],
                    item.get("subtype"),
                    item.get("quality"),
                    item.get("rarity"),
                    item.get("value"),
                    item.get("material"),
                    data_str,
                    seed
                ))
                item_id = cursor.fetchone()[0]

            # Save to history
            self._save_history(conn, "item", item_id, template_name, constraints, seed)

            conn.commit()
            return item_id

    def save_npc(self, npc: Dict[str, Any], archetype: Optional[str] = None, seed: Optional[int] = None) -> int:
        """
        Save an NPC to the database.

        Args:
            npc: NPC dictionary
            archetype: Archetype used to generate the NPC
            seed: Random seed used for generation

        Returns:
            Database ID of saved NPC
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            data_str = json.dumps(npc)

            if self.db_type == "sqlite":
                cursor.execute("""
                    INSERT INTO npcs (name, title, archetype, data, seed)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    npc["name"],
                    npc["title"],
                    archetype,
                    data_str,
                    seed
                ))
                npc_id = cursor.lastrowid
            else:  # postgresql
                cursor.execute("""
                    INSERT INTO npcs (name, title, archetype, data, seed)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    npc["name"],
                    npc["title"],
                    archetype,
                    data_str,
                    seed
                ))
                npc_id = cursor.fetchone()[0]

            # Save to history
            self._save_history(conn, "npc", npc_id, archetype, None, seed)

            conn.commit()
            return npc_id

    def save_location(self, location: Dict[str, Any], template_name: Optional[str] = None, seed: Optional[int] = None) -> int:
        """
        Save a location to the database.

        Args:
            location: Location dictionary
            template_name: Template used to generate the location
            seed: Random seed used for generation

        Returns:
            Database ID of saved location
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            data_str = json.dumps(location)

            if self.db_type == "sqlite":
                cursor.execute("""
                    INSERT INTO locations (location_id, name, type, data, seed)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    location["id"],
                    location["name"],
                    location["type"],
                    data_str,
                    seed
                ))
                loc_id = cursor.lastrowid
            else:  # postgresql
                cursor.execute("""
                    INSERT INTO locations (location_id, name, type, data, seed)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    location["id"],
                    location["name"],
                    location["type"],
                    data_str,
                    seed
                ))
                loc_id = cursor.fetchone()[0]

            # Save to history
            self._save_history(conn, "location", loc_id, template_name, None, seed)

            conn.commit()
            return loc_id

    def save_world(self, world: Dict[str, Any], name: Optional[str] = None, seed: Optional[int] = None) -> int:
        """
        Save a world to the database.

        Args:
            world: World dictionary
            name: Optional name for the world
            seed: Random seed used for generation

        Returns:
            Database ID of saved world
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            data_str = json.dumps(world)
            num_locations = len(world.get("locations", {}))

            if self.db_type == "sqlite":
                cursor.execute("""
                    INSERT INTO worlds (name, num_locations, data, seed)
                    VALUES (?, ?, ?, ?)
                """, (name, num_locations, data_str, seed))
                world_id = cursor.lastrowid
            else:  # postgresql
                cursor.execute("""
                    INSERT INTO worlds (name, num_locations, data, seed)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (name, num_locations, data_str, seed))
                world_id = cursor.fetchone()[0]

            # Save to history
            self._save_history(conn, "world", world_id, None, None, seed)

            conn.commit()
            return world_id

    def save_animal(self, animal: Dict[str, Any], seed: Optional[int] = None) -> int:
        """
        Save an animal to the database.

        Args:
            animal: Animal dictionary
            seed: Random seed used for generation

        Returns:
            Database ID of saved animal
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            data_str = json.dumps(animal)

            if self.db_type == "sqlite":
                cursor.execute("""
                    INSERT INTO animals (name, species, category, size, danger_level, data, seed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    animal["name"],
                    animal["species"],
                    animal["category"],
                    animal.get("size"),
                    animal.get("danger_level"),
                    data_str,
                    seed
                ))
                animal_id = cursor.lastrowid
            else:  # postgresql
                cursor.execute("""
                    INSERT INTO animals (name, species, category, size, danger_level, data, seed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    animal["name"],
                    animal["species"],
                    animal["category"],
                    animal.get("size"),
                    animal.get("danger_level"),
                    data_str,
                    seed
                ))
                animal_id = cursor.fetchone()[0]

            # Save to history
            self._save_history(conn, "animal", animal_id, None, None, seed)

            conn.commit()
            return animal_id

    def save_flora(self, flora: Dict[str, Any], seed: Optional[int] = None) -> int:
        """
        Save flora to the database.

        Args:
            flora: Flora dictionary
            seed: Random seed used for generation

        Returns:
            Database ID of saved flora
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            data_str = json.dumps(flora)

            if self.db_type == "sqlite":
                cursor.execute("""
                    INSERT INTO flora (name, species, category, rarity, magical, data, seed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    flora["name"],
                    flora["species"],
                    flora["category"],
                    flora.get("rarity"),
                    1 if flora.get("magical") else 0,
                    data_str,
                    seed
                ))
                flora_id = cursor.lastrowid
            else:  # postgresql
                cursor.execute("""
                    INSERT INTO flora (name, species, category, rarity, magical, data, seed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    flora["name"],
                    flora["species"],
                    flora["category"],
                    flora.get("rarity"),
                    flora.get("magical", False),
                    data_str,
                    seed
                ))
                flora_id = cursor.fetchone()[0]

            # Save to history
            self._save_history(conn, "flora", flora_id, None, None, seed)

            conn.commit()
            return flora_id

    def _save_history(self, conn, content_type: str, content_id: int, template_name: Optional[str],
                     constraints: Optional[Dict], seed: Optional[int]):
        """Save generation history record."""
        cursor = conn.cursor()

        constraints_str = json.dumps(constraints) if constraints else None

        if self.db_type == "sqlite":
            cursor.execute("""
                INSERT INTO generation_history (content_type, content_id, template_name, constraints, seed)
                VALUES (?, ?, ?, ?, ?)
            """, (content_type, content_id, template_name, constraints_str, seed))
        else:  # postgresql
            cursor.execute("""
                INSERT INTO generation_history (content_type, content_id, template_name, constraints, seed)
                VALUES (%s, %s, %s, %s, %s)
            """, (content_type, content_id, template_name, constraints_str, seed))

    def get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve an item by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if self.db_type == "sqlite":
                cursor.execute("SELECT data FROM items WHERE id = ?", (item_id,))
            else:
                cursor.execute("SELECT data FROM items WHERE id = %s", (item_id,))

            row = cursor.fetchone()
            if row:
                return json.loads(row[0] if self.db_type == "sqlite" else row["data"])
            return None

    def get_npc(self, npc_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve an NPC by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if self.db_type == "sqlite":
                cursor.execute("SELECT data FROM npcs WHERE id = ?", (npc_id,))
            else:
                cursor.execute("SELECT data FROM npcs WHERE id = %s", (npc_id,))

            row = cursor.fetchone()
            if row:
                return json.loads(row[0] if self.db_type == "sqlite" else row["data"])
            return None

    def get_location(self, location_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a location by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if self.db_type == "sqlite":
                cursor.execute("SELECT data FROM locations WHERE id = ?", (location_id,))
            else:
                cursor.execute("SELECT data FROM locations WHERE id = %s", (location_id,))

            row = cursor.fetchone()
            if row:
                return json.loads(row[0] if self.db_type == "sqlite" else row["data"])
            return None

    def get_world(self, world_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a world by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if self.db_type == "sqlite":
                cursor.execute("SELECT data FROM worlds WHERE id = ?", (world_id,))
            else:
                cursor.execute("SELECT data FROM worlds WHERE id = %s", (world_id,))

            row = cursor.fetchone()
            if row:
                return json.loads(row[0] if self.db_type == "sqlite" else row["data"])
            return None

    def search_items(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for items with optional filters.

        Args:
            filters: Dictionary of filter criteria:
                - type: Item type
                - quality: Quality level
                - rarity: Rarity level
                - min_value: Minimum value
                - max_value: Maximum value
                - material: Material type
            limit: Maximum number of results

        Returns:
            List of matching items
        """
        filters = filters or {}

        with self._get_connection() as conn:
            cursor = conn.cursor()

            where_clauses = []
            params = []

            if "type" in filters:
                where_clauses.append("type = ?" if self.db_type == "sqlite" else "type = %s")
                params.append(filters["type"])

            if "quality" in filters:
                where_clauses.append("quality = ?" if self.db_type == "sqlite" else "quality = %s")
                params.append(filters["quality"])

            if "rarity" in filters:
                where_clauses.append("rarity = ?" if self.db_type == "sqlite" else "rarity = %s")
                params.append(filters["rarity"])

            if "min_value" in filters:
                where_clauses.append("value >= ?" if self.db_type == "sqlite" else "value >= %s")
                params.append(filters["min_value"])

            if "max_value" in filters:
                where_clauses.append("value <= ?" if self.db_type == "sqlite" else "value <= %s")
                params.append(filters["max_value"])

            if "material" in filters:
                where_clauses.append("material = ?" if self.db_type == "sqlite" else "material = %s")
                params.append(filters["material"])

            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            params.append(limit)

            query = f"SELECT data FROM items WHERE {where_sql} LIMIT {'?' if self.db_type == 'sqlite' else '%s'}"
            cursor.execute(query, params)

            results = []
            for row in cursor.fetchall():
                results.append(json.loads(row[0] if self.db_type == "sqlite" else row["data"]))

            return results

    def get_history(self, content_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve generation history.

        Args:
            content_type: Optional filter by content type (item, npc, location, world)
            limit: Maximum number of results

        Returns:
            List of history records
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if content_type:
                if self.db_type == "sqlite":
                    cursor.execute("""
                        SELECT id, content_type, content_id, template_name, constraints, created_at, seed
                        FROM generation_history
                        WHERE content_type = ?
                        ORDER BY created_at DESC
                        LIMIT ?
                    """, (content_type, limit))
                else:
                    cursor.execute("""
                        SELECT id, content_type, content_id, template_name, constraints, created_at, seed
                        FROM generation_history
                        WHERE content_type = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    """, (content_type, limit))
            else:
                if self.db_type == "sqlite":
                    cursor.execute("""
                        SELECT id, content_type, content_id, template_name, constraints, created_at, seed
                        FROM generation_history
                        ORDER BY created_at DESC
                        LIMIT ?
                    """, (limit,))
                else:
                    cursor.execute("""
                        SELECT id, content_type, content_id, template_name, constraints, created_at, seed
                        FROM generation_history
                        ORDER BY created_at DESC
                        LIMIT %s
                    """, (limit,))

            results = []
            for row in cursor.fetchall():
                if self.db_type == "sqlite":
                    results.append({
                        "id": row[0],
                        "content_type": row[1],
                        "content_id": row[2],
                        "template_name": row[3],
                        "constraints": json.loads(row[4]) if row[4] else None,
                        "created_at": row[5],
                        "seed": row[6]
                    })
                else:
                    results.append({
                        "id": row["id"],
                        "content_type": row["content_type"],
                        "content_id": row["content_id"],
                        "template_name": row["template_name"],
                        "constraints": row["constraints"],
                        "created_at": row["created_at"],
                        "seed": row["seed"]
                    })

            return results

    def clear_history(self, older_than_days: Optional[int] = None):
        """
        Clear generation history.

        Args:
            older_than_days: Only clear records older than this many days. If None, clears all.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if older_than_days:
                if self.db_type == "sqlite":
                    cursor.execute("""
                        DELETE FROM generation_history
                        WHERE created_at < datetime('now', '-' || ? || ' days')
                    """, (older_than_days,))
                else:
                    cursor.execute("""
                        DELETE FROM generation_history
                        WHERE created_at < NOW() - INTERVAL '%s days'
                    """, (older_than_days,))
            else:
                cursor.execute("DELETE FROM generation_history")

            conn.commit()

    # Player Management Methods

    def create_player(self, username: str, password_hash: str, character_name: str,
                     email: Optional[str] = None, race: Optional[str] = None,
                     character_class: Optional[str] = None, starting_location: Optional[str] = None) -> int:
        """
        Create a new player account.

        Args:
            username: Unique username for login
            password_hash: Hashed password
            character_name: Character's display name
            email: Optional email address
            race: Optional character race
            character_class: Optional character class
            starting_location: Optional starting location ID

        Returns:
            Database ID of created player
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            player_data = {
                "character_name": character_name,
                "race": race,
                "class": character_class,
                "created_at": datetime.now().isoformat()
            }
            data_str = json.dumps(player_data)

            try:
                if self.db_type == "sqlite":
                    cursor.execute("""
                        INSERT INTO players (username, password_hash, email, character_name, race, class, current_location_id, data)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (username, password_hash, email, character_name, race, character_class, starting_location, data_str))
                    player_id = cursor.lastrowid
                else:  # postgresql
                    cursor.execute("""
                        INSERT INTO players (username, password_hash, email, character_name, race, class, current_location_id, data)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (username, password_hash, email, character_name, race, character_class, starting_location, data_str))
                    player_id = cursor.fetchone()[0]

                # Create default stats for the player
                if self.db_type == "sqlite":
                    cursor.execute("""
                        INSERT INTO player_stats (player_id) VALUES (?)
                    """, (player_id,))
                else:
                    cursor.execute("""
                        INSERT INTO player_stats (player_id) VALUES (%s)
                    """, (player_id,))

                conn.commit()
                return player_id
            except Exception as e:
                conn.rollback()
                raise e

    def get_player_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a player by username.

        Args:
            username: Username to search for

        Returns:
            Player dictionary or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if self.db_type == "sqlite":
                cursor.execute("""
                    SELECT id, username, password_hash, email, character_name, race, class,
                           level, experience, gold, current_location_id, data, created_at, last_login
                    FROM players WHERE username = ?
                """, (username,))
            else:
                cursor.execute("""
                    SELECT id, username, password_hash, email, character_name, race, class,
                           level, experience, gold, current_location_id, data, created_at, last_login
                    FROM players WHERE username = %s
                """, (username,))

            row = cursor.fetchone()
            if row:
                if self.db_type == "sqlite":
                    return {
                        "id": row[0],
                        "username": row[1],
                        "password_hash": row[2],
                        "email": row[3],
                        "character_name": row[4],
                        "race": row[5],
                        "class": row[6],
                        "level": row[7],
                        "experience": row[8],
                        "gold": row[9],
                        "current_location_id": row[10],
                        "data": json.loads(row[11]),
                        "created_at": row[12],
                        "last_login": row[13]
                    }
                else:
                    return {
                        "id": row["id"],
                        "username": row["username"],
                        "password_hash": row["password_hash"],
                        "email": row["email"],
                        "character_name": row["character_name"],
                        "race": row["race"],
                        "class": row["class"],
                        "level": row["level"],
                        "experience": row["experience"],
                        "gold": row["gold"],
                        "current_location_id": row["current_location_id"],
                        "data": row["data"],
                        "created_at": row["created_at"],
                        "last_login": row["last_login"]
                    }
            return None

    def get_player_by_id(self, player_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a player by ID.

        Args:
            player_id: Player ID to search for

        Returns:
            Player dictionary or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if self.db_type == "sqlite":
                cursor.execute("""
                    SELECT id, username, password_hash, email, character_name, race, class,
                           level, experience, gold, current_location_id, data, created_at, last_login
                    FROM players WHERE id = ?
                """, (player_id,))
            else:
                cursor.execute("""
                    SELECT id, username, password_hash, email, character_name, race, class,
                           level, experience, gold, current_location_id, data, created_at, last_login
                    FROM players WHERE id = %s
                """, (player_id,))

            row = cursor.fetchone()
            if row:
                if self.db_type == "sqlite":
                    return {
                        "id": row[0],
                        "username": row[1],
                        "password_hash": row[2],
                        "email": row[3],
                        "character_name": row[4],
                        "race": row[5],
                        "class": row[6],
                        "level": row[7],
                        "experience": row[8],
                        "gold": row[9],
                        "current_location_id": row[10],
                        "data": json.loads(row[11]),
                        "created_at": row[12],
                        "last_login": row[13]
                    }
                else:
                    return {
                        "id": row["id"],
                        "username": row["username"],
                        "password_hash": row["password_hash"],
                        "email": row["email"],
                        "character_name": row["character_name"],
                        "race": row["race"],
                        "class": row["class"],
                        "level": row["level"],
                        "experience": row["experience"],
                        "gold": row["gold"],
                        "current_location_id": row["current_location_id"],
                        "data": row["data"],
                        "created_at": row["created_at"],
                        "last_login": row["last_login"]
                    }
            return None

    def update_player(self, player_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update player data.

        Args:
            player_id: Player ID
            updates: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            allowed_fields = ['character_name', 'race', 'class', 'level', 'experience',
                            'gold', 'current_location_id', 'email', 'last_login']

            set_clauses = []
            params = []

            for field, value in updates.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = {'?' if self.db_type == 'sqlite' else '%s'}")
                    params.append(value)

            if not set_clauses:
                return False

            params.append(player_id)
            query = f"UPDATE players SET {', '.join(set_clauses)} WHERE id = {'?' if self.db_type == 'sqlite' else '%s'}"

            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0

    def add_to_inventory(self, player_id: int, item_name: str, item_type: str,
                        item_data: Dict[str, Any], quantity: int = 1) -> int:
        """
        Add an item to player's inventory.

        Args:
            player_id: Player ID
            item_name: Name of the item
            item_type: Type of the item
            item_data: Full item data dictionary
            quantity: Quantity to add

        Returns:
            Database ID of inventory entry
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            data_str = json.dumps(item_data)

            if self.db_type == "sqlite":
                cursor.execute("""
                    INSERT INTO player_inventory (player_id, item_name, item_type, quantity, data)
                    VALUES (?, ?, ?, ?, ?)
                """, (player_id, item_name, item_type, quantity, data_str))
                inventory_id = cursor.lastrowid
            else:
                cursor.execute("""
                    INSERT INTO player_inventory (player_id, item_name, item_type, quantity, data)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (player_id, item_name, item_type, quantity, data_str))
                inventory_id = cursor.fetchone()[0]

            conn.commit()
            return inventory_id

    def remove_from_inventory(self, player_id: int, inventory_id: int, quantity: Optional[int] = None) -> bool:
        """
        Remove an item from player's inventory.

        Args:
            player_id: Player ID
            inventory_id: Inventory entry ID
            quantity: If specified, reduce quantity by this amount. If None, remove entirely.

        Returns:
            True if successful, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if quantity is not None:
                # Reduce quantity
                if self.db_type == "sqlite":
                    cursor.execute("""
                        UPDATE player_inventory
                        SET quantity = quantity - ?
                        WHERE id = ? AND player_id = ? AND quantity >= ?
                    """, (quantity, inventory_id, player_id, quantity))
                else:
                    cursor.execute("""
                        UPDATE player_inventory
                        SET quantity = quantity - %s
                        WHERE id = %s AND player_id = %s AND quantity >= %s
                    """, (quantity, inventory_id, player_id, quantity))

                rows_updated = cursor.rowcount

                # Delete if quantity reaches 0
                if self.db_type == "sqlite":
                    cursor.execute("""
                        DELETE FROM player_inventory
                        WHERE id = ? AND player_id = ? AND quantity <= 0
                    """, (inventory_id, player_id))
                else:
                    cursor.execute("""
                        DELETE FROM player_inventory
                        WHERE id = %s AND player_id = %s AND quantity <= 0
                    """, (inventory_id, player_id))

                conn.commit()
                return rows_updated > 0
            else:
                # Remove entirely
                if self.db_type == "sqlite":
                    cursor.execute("""
                        DELETE FROM player_inventory
                        WHERE id = ? AND player_id = ?
                    """, (inventory_id, player_id))
                else:
                    cursor.execute("""
                        DELETE FROM player_inventory
                        WHERE id = %s AND player_id = %s
                    """, (inventory_id, player_id))

                conn.commit()
                return cursor.rowcount > 0

    def get_player_inventory(self, player_id: int) -> List[Dict[str, Any]]:
        """
        Get all items in player's inventory.

        Args:
            player_id: Player ID

        Returns:
            List of inventory items
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if self.db_type == "sqlite":
                cursor.execute("""
                    SELECT id, item_name, item_type, quantity, equipped, data, acquired_at
                    FROM player_inventory
                    WHERE player_id = ?
                    ORDER BY acquired_at DESC
                """, (player_id,))
            else:
                cursor.execute("""
                    SELECT id, item_name, item_type, quantity, equipped, data, acquired_at
                    FROM player_inventory
                    WHERE player_id = %s
                    ORDER BY acquired_at DESC
                """, (player_id,))

            results = []
            for row in cursor.fetchall():
                if self.db_type == "sqlite":
                    results.append({
                        "id": row[0],
                        "item_name": row[1],
                        "item_type": row[2],
                        "quantity": row[3],
                        "equipped": bool(row[4]),
                        "data": json.loads(row[5]),
                        "acquired_at": row[6]
                    })
                else:
                    results.append({
                        "id": row["id"],
                        "item_name": row["item_name"],
                        "item_type": row["item_type"],
                        "quantity": row["quantity"],
                        "equipped": row["equipped"],
                        "data": row["data"],
                        "acquired_at": row["acquired_at"]
                    })

            return results

    def update_inventory_item(self, inventory_id: int, player_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update an inventory item.

        Args:
            inventory_id: Inventory entry ID
            player_id: Player ID
            updates: Dictionary of fields to update (quantity, equipped)

        Returns:
            True if successful, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            allowed_fields = ['quantity', 'equipped']
            set_clauses = []
            params = []

            for field, value in updates.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = {'?' if self.db_type == 'sqlite' else '%s'}")
                    params.append(value)

            if not set_clauses:
                return False

            params.extend([inventory_id, player_id])
            query = f"UPDATE player_inventory SET {', '.join(set_clauses)} WHERE id = {'?' if self.db_type == 'sqlite' else '%s'} AND player_id = {'?' if self.db_type == 'sqlite' else '%s'}"

            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0

    def get_player_stats(self, player_id: int) -> Optional[Dict[str, Any]]:
        """
        Get player's stats.

        Args:
            player_id: Player ID

        Returns:
            Stats dictionary or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if self.db_type == "sqlite":
                cursor.execute("""
                    SELECT health, max_health, mana, max_mana, energy, max_energy,
                           strength, dexterity, intelligence, constitution, wisdom, charisma, updated_at
                    FROM player_stats
                    WHERE player_id = ?
                """, (player_id,))
            else:
                cursor.execute("""
                    SELECT health, max_health, mana, max_mana, energy, max_energy,
                           strength, dexterity, intelligence, constitution, wisdom, charisma, updated_at
                    FROM player_stats
                    WHERE player_id = %s
                """, (player_id,))

            row = cursor.fetchone()
            if row:
                if self.db_type == "sqlite":
                    return {
                        "health": row[0],
                        "max_health": row[1],
                        "mana": row[2],
                        "max_mana": row[3],
                        "energy": row[4],
                        "max_energy": row[5],
                        "strength": row[6],
                        "dexterity": row[7],
                        "intelligence": row[8],
                        "constitution": row[9],
                        "wisdom": row[10],
                        "charisma": row[11],
                        "updated_at": row[12]
                    }
                else:
                    return {
                        "health": row["health"],
                        "max_health": row["max_health"],
                        "mana": row["mana"],
                        "max_mana": row["max_mana"],
                        "energy": row["energy"],
                        "max_energy": row["max_energy"],
                        "strength": row["strength"],
                        "dexterity": row["dexterity"],
                        "intelligence": row["intelligence"],
                        "constitution": row["constitution"],
                        "wisdom": row["wisdom"],
                        "charisma": row["charisma"],
                        "updated_at": row["updated_at"]
                    }
            return None

    def update_player_stats(self, player_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update player's stats.

        Args:
            player_id: Player ID
            updates: Dictionary of stats to update

        Returns:
            True if successful, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            allowed_fields = ['health', 'max_health', 'mana', 'max_mana', 'energy', 'max_energy',
                            'strength', 'dexterity', 'intelligence', 'constitution', 'wisdom', 'charisma']

            set_clauses = []
            params = []

            for field, value in updates.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = {'?' if self.db_type == 'sqlite' else '%s'}")
                    params.append(value)

            if not set_clauses:
                return False

            set_clauses.append(f"updated_at = {'?' if self.db_type == 'sqlite' else '%s'}")
            params.append(datetime.now())
            params.append(player_id)

            query = f"UPDATE player_stats SET {', '.join(set_clauses)} WHERE player_id = {'?' if self.db_type == 'sqlite' else '%s'}"

            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0

    # ===================================================================
    # Profession Management
    # ===================================================================

    def create_profession(self, name: str, icon: str, description: str,
                          profession_type: str, data: Dict[str, Any]) -> int:
        """
        Create a new profession in the database.

        Args:
            name: Profession name
            icon: Icon emoji/character
            description: Profession description
            profession_type: Type (crafting, gathering, etc.)
            data: Additional profession data (benefits, base stats, etc.)

        Returns:
            Profession ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if self.db_type == "sqlite":
                cursor.execute("""
                    INSERT INTO professions (name, icon, description, profession_type, data)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, icon, description, profession_type, json.dumps(data)))
            else:
                cursor.execute("""
                    INSERT INTO professions (name, icon, description, profession_type, data)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (name, icon, description, profession_type, json.dumps(data)))

            conn.commit()
            return cursor.lastrowid if self.db_type == "sqlite" else cursor.fetchone()[0]

    def get_all_professions(self) -> List[Dict[str, Any]]:
        """
        Get all professions.

        Returns:
            List of profession dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, icon, description, profession_type, data
                FROM professions
                ORDER BY name
            """)

            professions = []
            for row in cursor.fetchall():
                if self.db_type == "sqlite":
                    profession = {
                        'id': row[0],
                        'name': row[1],
                        'icon': row[2],
                        'description': row[3],
                        'profession_type': row[4]
                    }
                    profession.update(json.loads(row[5]))
                else:
                    profession = {
                        'id': row['id'],
                        'name': row['name'],
                        'icon': row['icon'],
                        'description': row['description'],
                        'profession_type': row['profession_type']
                    }
                    profession.update(json.loads(row['data']))

                professions.append(profession)

            return professions

    def get_player_professions(self, player_id: int) -> List[Dict[str, Any]]:
        """
        Get player's professions with their levels and experience.

        Args:
            player_id: Player ID

        Returns:
            List of player profession data
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT pp.id, pp.level, pp.experience, pp.data,
                       p.id as profession_id, p.name, p.icon, p.description,
                       p.profession_type, p.data as profession_data
                FROM player_professions pp
                JOIN professions p ON pp.profession_id = p.id
                WHERE pp.player_id = {}
                ORDER BY pp.level DESC, p.name
            """.format('?' if self.db_type == 'sqlite' else '%s'), (player_id,))

            professions = []
            for row in cursor.fetchall():
                if self.db_type == "sqlite":
                    prof_data = json.loads(row[9]) if row[9] else {}
                    player_data = json.loads(row[3]) if row[3] else {}

                    profession = {
                        'player_profession_id': row[0],
                        'level': row[1],
                        'experience': row[2],
                        'profession_id': row[4],
                        'name': row[5],
                        'icon': row[6],
                        'description': row[7],
                        'profession_type': row[8]
                    }
                    profession.update(prof_data)
                    profession.update(player_data)
                else:
                    prof_data = json.loads(row['profession_data']) if row['profession_data'] else {}
                    player_data = json.loads(row['data']) if row['data'] else {}

                    profession = {
                        'player_profession_id': row['id'],
                        'level': row['level'],
                        'experience': row['experience'],
                        'profession_id': row['profession_id'],
                        'name': row['name'],
                        'icon': row['icon'],
                        'description': row['description'],
                        'profession_type': row['profession_type']
                    }
                    profession.update(prof_data)
                    profession.update(player_data)

                professions.append(profession)

            return professions

    def add_player_profession(self, player_id: int, profession_id: int,
                             level: int = 1, experience: int = 0) -> int:
        """
        Add a profession to a player.

        Args:
            player_id: Player ID
            profession_id: Profession ID
            level: Starting level
            experience: Starting experience

        Returns:
            Player profession ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if self.db_type == "sqlite":
                cursor.execute("""
                    INSERT INTO player_professions (player_id, profession_id, level, experience)
                    VALUES (?, ?, ?, ?)
                """, (player_id, profession_id, level, experience))
            else:
                cursor.execute("""
                    INSERT INTO player_professions (player_id, profession_id, level, experience)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (player_id, profession_id, level, experience))

            conn.commit()
            return cursor.lastrowid if self.db_type == "sqlite" else cursor.fetchone()[0]

    def update_player_profession(self, player_id: int, profession_id: int,
                                 level: Optional[int] = None,
                                 experience: Optional[int] = None) -> bool:
        """
        Update player's profession level or experience.

        Args:
            player_id: Player ID
            profession_id: Profession ID
            level: New level (optional)
            experience: New experience (optional)

        Returns:
            True if successful
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            set_clauses = []
            params = []

            if level is not None:
                set_clauses.append(f"level = {'?' if self.db_type == 'sqlite' else '%s'}")
                params.append(level)

            if experience is not None:
                set_clauses.append(f"experience = {'?' if self.db_type == 'sqlite' else '%s'}")
                params.append(experience)

            if not set_clauses:
                return False

            set_clauses.append(f"updated_at = {'?' if self.db_type == 'sqlite' else '%s'}")
            params.append(datetime.now())
            params.extend([player_id, profession_id])

            query = f"""
                UPDATE player_professions
                SET {', '.join(set_clauses)}
                WHERE player_id = {'?' if self.db_type == 'sqlite' else '%s'}
                  AND profession_id = {'?' if self.db_type == 'sqlite' else '%s'}
            """

            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0

    # ===================================================================
    # Recipe Management
    # ===================================================================

    def create_recipe(self, name: str, profession_id: int, required_level: int,
                     result_item_name: str, result_quantity: int,
                     ingredients: List[Dict[str, Any]], crafting_time: int = 5,
                     difficulty: str = 'medium', data: Optional[Dict[str, Any]] = None) -> int:
        """
        Create a new recipe.

        Args:
            name: Recipe name
            profession_id: Required profession ID
            required_level: Required profession level
            result_item_name: Item produced
            result_quantity: Quantity produced
            ingredients: List of {ingredient_name, quantity}
            crafting_time: Time in seconds
            difficulty: Difficulty level
            data: Additional recipe data

        Returns:
            Recipe ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            recipe_data = data or {}

            if self.db_type == "sqlite":
                cursor.execute("""
                    INSERT INTO recipes
                    (name, profession_id, required_level, result_item_name, result_quantity,
                     crafting_time, difficulty, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, profession_id, required_level, result_item_name, result_quantity,
                      crafting_time, difficulty, json.dumps(recipe_data)))
                recipe_id = cursor.lastrowid
            else:
                cursor.execute("""
                    INSERT INTO recipes
                    (name, profession_id, required_level, result_item_name, result_quantity,
                     crafting_time, difficulty, data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (name, profession_id, required_level, result_item_name, result_quantity,
                      crafting_time, difficulty, json.dumps(recipe_data)))
                recipe_id = cursor.fetchone()[0]

            # Add ingredients
            for ingredient in ingredients:
                if self.db_type == "sqlite":
                    cursor.execute("""
                        INSERT INTO recipe_ingredients (recipe_id, ingredient_name, quantity)
                        VALUES (?, ?, ?)
                    """, (recipe_id, ingredient['ingredient_name'], ingredient['quantity']))
                else:
                    cursor.execute("""
                        INSERT INTO recipe_ingredients (recipe_id, ingredient_name, quantity)
                        VALUES (%s, %s, %s)
                    """, (recipe_id, ingredient['ingredient_name'], ingredient['quantity']))

            conn.commit()
            return recipe_id

    def get_recipes_by_profession(self, profession_id: int) -> List[Dict[str, Any]]:
        """
        Get all recipes for a profession.

        Args:
            profession_id: Profession ID

        Returns:
            List of recipe dictionaries with ingredients
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT r.id, r.name, r.required_level, r.result_item_name, r.result_quantity,
                       r.crafting_time, r.difficulty, r.data, p.name as profession_name
                FROM recipes r
                JOIN professions p ON r.profession_id = p.id
                WHERE r.profession_id = {}
                ORDER BY r.required_level, r.name
            """.format('?' if self.db_type == 'sqlite' else '%s'), (profession_id,))

            recipes = []
            for row in cursor.fetchall():
                if self.db_type == "sqlite":
                    recipe_id = row[0]
                    recipe = {
                        'id': row[0],
                        'name': row[1],
                        'required_level': row[2],
                        'result_item_name': row[3],
                        'result_quantity': row[4],
                        'crafting_time': row[5],
                        'difficulty': row[6],
                        'profession_name': row[8]
                    }
                    recipe.update(json.loads(row[7]) if row[7] else {})
                else:
                    recipe_id = row['id']
                    recipe = {
                        'id': row['id'],
                        'name': row['name'],
                        'required_level': row['required_level'],
                        'result_item_name': row['result_item_name'],
                        'result_quantity': row['result_quantity'],
                        'crafting_time': row['crafting_time'],
                        'difficulty': row['difficulty'],
                        'profession_name': row['profession_name']
                    }
                    recipe.update(json.loads(row['data']) if row['data'] else {})

                # Get ingredients
                ingredients_cursor = conn.cursor()
                ingredients_cursor.execute("""
                    SELECT ingredient_name, quantity
                    FROM recipe_ingredients
                    WHERE recipe_id = {}
                """.format('?' if self.db_type == 'sqlite' else '%s'), (recipe_id,))

                recipe['ingredients'] = []
                for ing_row in ingredients_cursor.fetchall():
                    recipe['ingredients'].append({
                        'ingredient_name': ing_row[0] if self.db_type == 'sqlite' else ing_row['ingredient_name'],
                        'quantity': ing_row[1] if self.db_type == 'sqlite' else ing_row['quantity']
                    })

                recipes.append(recipe)

            return recipes

    def get_player_recipes(self, player_id: int) -> List[Dict[str, Any]]:
        """
        Get all recipes known by a player.

        Args:
            player_id: Player ID

        Returns:
            List of known recipe dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT r.id, r.name, r.profession_id, r.required_level, r.result_item_name,
                       r.result_quantity, r.crafting_time, r.difficulty, r.data,
                       p.name as profession_name, p.icon as profession_icon,
                       pr.times_crafted, pr.learned_at
                FROM player_recipes pr
                JOIN recipes r ON pr.recipe_id = r.id
                JOIN professions p ON r.profession_id = p.id
                WHERE pr.player_id = {}
                ORDER BY p.name, r.required_level, r.name
            """.format('?' if self.db_type == 'sqlite' else '%s'), (player_id,))

            recipes = []
            for row in cursor.fetchall():
                if self.db_type == "sqlite":
                    recipe_id = row[0]
                    recipe = {
                        'id': row[0],
                        'name': row[1],
                        'profession_id': row[2],
                        'required_level': row[3],
                        'result_item_name': row[4],
                        'result_quantity': row[5],
                        'crafting_time': row[6],
                        'difficulty': row[7],
                        'profession_name': row[9],
                        'profession_icon': row[10],
                        'times_crafted': row[11],
                        'learned_at': row[12]
                    }
                    recipe.update(json.loads(row[8]) if row[8] else {})
                else:
                    recipe_id = row['id']
                    recipe = {
                        'id': row['id'],
                        'name': row['name'],
                        'profession_id': row['profession_id'],
                        'required_level': row['required_level'],
                        'result_item_name': row['result_item_name'],
                        'result_quantity': row['result_quantity'],
                        'crafting_time': row['crafting_time'],
                        'difficulty': row['difficulty'],
                        'profession_name': row['profession_name'],
                        'profession_icon': row['profession_icon'],
                        'times_crafted': row['times_crafted'],
                        'learned_at': row['learned_at']
                    }
                    recipe.update(json.loads(row['data']) if row['data'] else {})

                # Get ingredients
                ingredients_cursor = conn.cursor()
                ingredients_cursor.execute("""
                    SELECT ingredient_name, quantity
                    FROM recipe_ingredients
                    WHERE recipe_id = {}
                """.format('?' if self.db_type == 'sqlite' else '%s'), (recipe_id,))

                recipe['ingredients'] = []
                for ing_row in ingredients_cursor.fetchall():
                    recipe['ingredients'].append({
                        'ingredient_name': ing_row[0] if self.db_type == 'sqlite' else ing_row['ingredient_name'],
                        'quantity': ing_row[1] if self.db_type == 'sqlite' else ing_row['quantity']
                    })

                recipes.append(recipe)

            return recipes

    def add_player_recipe(self, player_id: int, recipe_id: int) -> int:
        """
        Add a recipe to player's known recipes.

        Args:
            player_id: Player ID
            recipe_id: Recipe ID

        Returns:
            Player recipe ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if self.db_type == "sqlite":
                cursor.execute("""
                    INSERT INTO player_recipes (player_id, recipe_id)
                    VALUES (?, ?)
                """, (player_id, recipe_id))
            else:
                cursor.execute("""
                    INSERT INTO player_recipes (player_id, recipe_id)
                    VALUES (%s, %s)
                    RETURNING id
                """, (player_id, recipe_id))

            conn.commit()
            return cursor.lastrowid if self.db_type == "sqlite" else cursor.fetchone()[0]
