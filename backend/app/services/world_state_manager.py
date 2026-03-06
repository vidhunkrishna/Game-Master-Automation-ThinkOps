"""World State Manager - Manages persistent world state with SQLite."""
from typing import Dict, Any, Optional
from datetime import datetime
import sqlite3
import json
from pathlib import Path


class WorldStateManager:
    """
    Manages persistent world state using SQLite.
    Stores player state, NPC states, world events, and analytics.
    """

    def __init__(self, db_path: str = "world_state.db"):
        """
        Initialize world state manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_initialized()

    def _ensure_db_initialized(self) -> None:
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Player state table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_state (
                    player_id TEXT PRIMARY KEY,
                    health INTEGER DEFAULT 100,
                    position_x REAL DEFAULT 0.0,
                    position_y REAL DEFAULT 0.0,
                    inventory TEXT DEFAULT '{}',
                    behavior_class TEXT DEFAULT 'neutral',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # NPC state table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS npc_state (
                    npc_id TEXT PRIMARY KEY,
                    name TEXT,
                    health INTEGER DEFAULT 100,
                    mood TEXT DEFAULT 'neutral',
                    position_x REAL DEFAULT 0.0,
                    position_y REAL DEFAULT 0.0,
                    goal TEXT,
                    last_action TEXT DEFAULT 'idle',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # World events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS world_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT,
                    description TEXT,
                    severity TEXT DEFAULT 'low',
                    timestamp INTEGER,
                    affected_npcs TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # World analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS world_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tick INTEGER,
                    danger_level REAL,
                    risk_level TEXT DEFAULT 'medium',
                    weather TEXT DEFAULT 'sunny',
                    avg_npc_health REAL,
                    event_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def initialize_world(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize world state in database.

        Args:
            world_state: Initial world state dictionary

        Returns:
            dict: Initialization result
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Insert or update NPCs
                npcs = world_state.get("npcs", {})
                for npc_id, npc_data in npcs.items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO npc_state
                        (npc_id, name, health, mood, position_x, position_y, goal, last_action)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        npc_data.get("id"),
                        npc_data.get("name"),
                        int(npc_data.get("health", 100)),
                        npc_data.get("mood", "neutral"),
                        float(npc_data.get("position_x", 0.0)),
                        float(npc_data.get("position_y", 0.0)),
                        npc_data.get("goal", "idle"),
                        npc_data.get("last_action", "idle"),
                    ))

                conn.commit()
                return {
                    "success": True,
                    "message": "World initialized",
                    "npcs_initialized": len(npcs),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_world_state(self) -> Dict[str, Any]:
        """
        Retrieve current world state from database.

        Returns:
            dict: Complete world state
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get NPCs
                cursor.execute("SELECT * FROM npc_state")
                npcs = {}
                for row in cursor.fetchall():
                    npcs[row["npc_id"]] = {
                        "id": row["npc_id"],
                        "name": row["name"],
                        "health": row["health"],
                        "mood": row["mood"],
                        "position_x": row["position_x"],
                        "position_y": row["position_y"],
                        "goal": row["goal"],
                        "last_action": row["last_action"],
                    }

                # Get latest analytics
                cursor.execute("""
                    SELECT danger_level, risk_level, weather, avg_npc_health, event_count
                    FROM world_analytics
                    ORDER BY id DESC LIMIT 1
                """)
                analytics = cursor.fetchone()

                if analytics:
                    danger_level = analytics["danger_level"]
                    risk_level = analytics["risk_level"]
                    weather = analytics["weather"]
                else:
                    danger_level = 20.0
                    risk_level = "low"
                    weather = "sunny"

                return {
                    "npcs": npcs,
                    "danger_level": danger_level,
                    "risk_level": risk_level,
                    "weather": weather,
                    "success": True,
                }
        except Exception as e:
            return {"success": False, "error": str(e), "npcs": {}}

    def update_player_state(
        self, player_id: str, player_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update player state in database.

        Args:
            player_id: Player identifier
            player_data: Player state dictionary

        Returns:
            dict: Update result
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT OR REPLACE INTO player_state
                    (player_id, health, position_x, position_y, inventory, behavior_class)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    player_id,
                    int(player_data.get("health", 100)),
                    float(player_data.get("position_x", 0.0)),
                    float(player_data.get("position_y", 0.0)),
                    json.dumps(player_data.get("inventory", {})),
                    player_data.get("behavior_class", "neutral"),
                ))

                conn.commit()
                return {
                    "success": True,
                    "message": f"Player {player_id} updated",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_npc_state(self, npc_id: str, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update NPC state in database.

        Args:
            npc_id: NPC identifier
            npc_data: NPC state dictionary

        Returns:
            dict: Update result
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT OR REPLACE INTO npc_state
                    (npc_id, name, health, mood, position_x, position_y, goal, last_action)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    npc_id,
                    npc_data.get("name", "Unknown"),
                    int(npc_data.get("health", 100)),
                    npc_data.get("mood", "neutral"),
                    float(npc_data.get("position_x", 0.0)),
                    float(npc_data.get("position_y", 0.0)),
                    npc_data.get("goal", "idle"),
                    npc_data.get("last_action", "idle"),
                ))

                conn.commit()
                return {
                    "success": True,
                    "message": f"NPC {npc_id} updated",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def log_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log a world event.

        Args:
            event: Event dictionary

        Returns:
            dict: Logging result
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO world_events
                    (event_id, event_type, description, severity, timestamp, affected_npcs)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    event.get("event_id", ""),
                    event.get("event_type", "unknown"),
                    event.get("description", ""),
                    event.get("severity", "low"),
                    event.get("timestamp", 0),
                    json.dumps(event.get("affected_npcs", [])),
                ))

                conn.commit()
                return {
                    "success": True,
                    "message": "Event logged",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_risk_level(
        self, tick: int, danger_level: float, risk_level: str,
        weather: str = "sunny", avg_npc_health: float = 75.0,
        event_count: int = 0
    ) -> Dict[str, Any]:
        """
        Record world analytics and risk assessment.

        Args:
            tick: Simulation tick
            danger_level: World danger level (0-100)
            risk_level: Risk classification (low, medium, high)
            weather: Current weather
            avg_npc_health: Average NPC health
            event_count: Number of recent events

        Returns:
            dict: Update result
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO world_analytics
                    (tick, danger_level, risk_level, weather, avg_npc_health, event_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    int(tick),
                    float(danger_level),
                    risk_level,
                    weather,
                    float(avg_npc_health),
                    int(event_count),
                ))

                conn.commit()
                return {
                    "success": True,
                    "message": "Risk level updated",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_event_history(self, limit: int = 20) -> Dict[str, Any]:
        """
        Get recent event history.

        Args:
            limit: Maximum number of events to retrieve

        Returns:
            dict: Event history
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT * FROM world_events
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))

                events = []
                for row in cursor.fetchall():
                    events.append({
                        "event_id": row["event_id"],
                        "event_type": row["event_type"],
                        "description": row["description"],
                        "severity": row["severity"],
                        "timestamp": row["timestamp"],
                        "affected_npcs": json.loads(row["affected_npcs"] or "[]"),
                    })

                return {
                    "success": True,
                    "events": events,
                    "count": len(events),
                }
        except Exception as e:
            return {"success": False, "error": str(e), "events": []}

    def clear_world(self) -> Dict[str, Any]:
        """
        Clear all world data (useful for testing/reset).

        Returns:
            dict: Clear result
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM player_state")
                cursor.execute("DELETE FROM npc_state")
                cursor.execute("DELETE FROM world_events")
                cursor.execute("DELETE FROM world_analytics")
                conn.commit()

                return {
                    "success": True,
                    "message": "World data cleared",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
