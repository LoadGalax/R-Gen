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

            # Create indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_type ON items(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_quality ON items(quality)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_rarity ON items(rarity)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_npcs_archetype ON npcs(archetype)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_type ON generation_history(content_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_created ON generation_history(created_at)")

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
