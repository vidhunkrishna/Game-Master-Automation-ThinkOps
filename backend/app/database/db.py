"""Database module for SQLite persistence."""
import sqlite3
from typing import Dict, Any, List
from pathlib import Path


class DatabaseManager:
    """Manages SQLite database operations for the game master system."""

    def __init__(self, db_path: str = "world.db"):
        """Initialize database manager."""
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # World events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS world_events (
                    event_id TEXT PRIMARY KEY,
                    description TEXT,
                    severity TEXT,
                    event_type TEXT,
                    timestamp INTEGER
                )
            """)

            # NPC states table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS npc_states (
                    npc_id TEXT PRIMARY KEY,
                    health INTEGER,
                    mood TEXT,
                    mood_level INTEGER,
                    goal TEXT,
                    last_action TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # World state table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS world_state (
                    time INTEGER PRIMARY KEY,
                    danger_level INTEGER,
                    weather TEXT,
                    time_of_day TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def save_event(self, event_data: Dict[str, Any]):
        """Save a world event to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO world_events
                (event_id, description, severity, event_type, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                event_data.get("event_id"),
                event_data.get("description"),
                event_data.get("severity"),
                event_data.get("event_type"),
                event_data.get("timestamp")
            ))
            conn.commit()

    def save_world_state(self, world_state):
        """Save the current world state to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO world_state
                (time, danger_level, weather, time_of_day)
                VALUES (?, ?, ?, ?)
            """, (
                world_state.time,
                int(world_state.danger_level),
                world_state.weather,
                world_state.time_of_day
            ))
            conn.commit()

    def save_npc_states(self, npcs: Dict[str, Any]):
        """Save NPC states to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for npc_id, npc in npcs.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO npc_states
                    (npc_id, health, mood, mood_level, goal, last_action)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    npc_id,
                    int(npc.health),
                    npc.mood,
                    int(npc.mood_level),
                    npc.goal,
                    npc.last_action
                ))
            conn.commit()

    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent world events from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM world_events
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_world_state(self) -> Dict[str, Any]:
        """Get the latest world state from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM world_state
                ORDER BY time DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            return dict(row) if row else {}

    def get_npc_states(self) -> Dict[str, Any]:
        """Get NPC states from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM npc_states")
            rows = cursor.fetchall()
            return {row["npc_id"]: dict(row) for row in rows}


# Global instance
db_manager = DatabaseManager()