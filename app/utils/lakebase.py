"""
Lakebase Client — Persistence layer for user actions.

Stores notes, overrides, shortlists, and review flags in PostgreSQL.
"""

import os
from typing import Optional
from datetime import datetime


class LakebaseClient:
    """Client for Lakebase (Postgres) persistence."""

    def __init__(self):
        """Initialize connection to Lakebase."""
        self.connection = None
        self._connect()

    def _connect(self):
        """Establish database connection."""
        self._init_memory_store()
        try:
            import psycopg2

            host = os.getenv("LAKEBASE_HOST", "")
            if not host:
                return

            self.connection = psycopg2.connect(
                host=host,
                port=os.getenv("LAKEBASE_PORT", "5432"),
                database=os.getenv("LAKEBASE_DB", "data_legend"),
                user=os.getenv("LAKEBASE_USER", "postgres"),
                password=os.getenv("LAKEBASE_PASSWORD", ""),
                connect_timeout=5,
            )

            self._init_schema()

        except Exception:
            self.connection = None
            self._init_memory_store()

    def _init_memory_store(self):
        """Initialize in-memory storage as fallback."""
        self.notes = {}
        self.overrides = {}
        self.shortlists = {}
        self.review_flags = {}

    def _init_schema(self):
        """Create database schema if it doesn't exist."""
        if not self.connection:
            return

        cursor = self.connection.cursor()

        # Notes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                facility_id VARCHAR(255) NOT NULL,
                note TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Overrides table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS overrides (
                id SERIAL PRIMARY KEY,
                facility_id VARCHAR(255) NOT NULL UNIQUE,
                original_score FLOAT,
                new_score FLOAT NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Shortlists table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shortlists (
                id SERIAL PRIMARY KEY,
                facility_id VARCHAR(255) NOT NULL,
                list_name VARCHAR(255) DEFAULT 'default',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(facility_id, list_name)
            )
        """)

        # Review flags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_flags (
                id SERIAL PRIMARY KEY,
                facility_id VARCHAR(255) NOT NULL,
                flag_type VARCHAR(100) NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE
            )
        """)

        self.connection.commit()
        cursor.close()

    def add_note(self, facility_id: str, note: str) -> bool:
        """Add a note to a facility."""
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    "INSERT INTO notes (facility_id, note) VALUES (%s, %s)",
                    (facility_id, note),
                )
                self.connection.commit()
                cursor.close()
                return True
            except Exception:
                self.connection.rollback()
                return False
        else:
            # In-memory fallback
            if facility_id not in self.notes:
                self.notes[facility_id] = []
            self.notes[facility_id].append({
                "note": note,
                "created_at": datetime.now().isoformat(),
            })
            return True

    def get_notes(self, facility_id: str) -> list[dict]:
        """Get all notes for a facility."""
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    "SELECT note, created_at FROM notes WHERE facility_id = %s ORDER BY created_at DESC",
                    (facility_id,),
                )
                results = [{"note": row[0], "created_at": row[1]} for row in cursor.fetchall()]
                cursor.close()
                return results
            except Exception:
                return []
        else:
            return self.notes.get(facility_id, [])

    def add_override(self, facility_id: str, original_score: float, new_score: float, reason: str = "") -> bool:
        """Add or update a trust score override."""
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    """INSERT INTO overrides (facility_id, original_score, new_score, reason)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (facility_id) DO UPDATE
                       SET new_score = EXCLUDED.new_score, reason = EXCLUDED.reason, updated_at = CURRENT_TIMESTAMP""",
                    (facility_id, original_score, new_score, reason),
                )
                self.connection.commit()
                cursor.close()
                return True
            except Exception:
                self.connection.rollback()
                return False
        else:
            self.overrides[facility_id] = {
                "original_score": original_score,
                "new_score": new_score,
                "reason": reason,
                "created_at": datetime.now().isoformat(),
            }
            return True

    def get_override(self, facility_id: str) -> Optional[dict]:
        """Get the override for a facility."""
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    "SELECT original_score, new_score, reason, created_at FROM overrides WHERE facility_id = %s",
                    (facility_id,),
                )
                row = cursor.fetchone()
                cursor.close()
                if row:
                    return {
                        "original_score": row[0],
                        "new_score": row[1],
                        "reason": row[2],
                        "created_at": row[3],
                    }
                return None
            except Exception:
                return None
        else:
            return self.overrides.get(facility_id)

    def add_to_shortlist(self, facility_id: str, list_name: str = "default") -> bool:
        """Add a facility to a shortlist."""
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    """INSERT INTO shortlists (facility_id, list_name)
                       VALUES (%s, %s)
                       ON CONFLICT DO NOTHING""",
                    (facility_id, list_name),
                )
                self.connection.commit()
                cursor.close()
                return True
            except Exception:
                self.connection.rollback()
                return False
        else:
            if list_name not in self.shortlists:
                self.shortlists[list_name] = []
            if facility_id not in self.shortlists[list_name]:
                self.shortlists[list_name].append(facility_id)
            return True

    def get_shortlist(self, list_name: str = "default") -> list[str]:
        """Get all facility IDs in a shortlist."""
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    "SELECT facility_id FROM shortlists WHERE list_name = %s ORDER BY added_at",
                    (list_name,),
                )
                results = [row[0] for row in cursor.fetchall()]
                cursor.close()
                return results
            except Exception:
                return []
        else:
            return self.shortlists.get(list_name, [])

    def remove_from_shortlist(self, facility_id: str, list_name: str = "default") -> bool:
        """Remove a facility from a shortlist."""
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    "DELETE FROM shortlists WHERE facility_id = %s AND list_name = %s",
                    (facility_id, list_name),
                )
                self.connection.commit()
                cursor.close()
                return True
            except Exception:
                self.connection.rollback()
                return False
        else:
            if list_name in self.shortlists:
                if facility_id in self.shortlists[list_name]:
                    self.shortlists[list_name].remove(facility_id)
            return True

    def flag_for_review(self, facility_id: str, flag_type: str, reason: str = "") -> bool:
        """Flag a facility for human review."""
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    "INSERT INTO review_flags (facility_id, flag_type, reason) VALUES (%s, %s, %s)",
                    (facility_id, flag_type, reason),
                )
                self.connection.commit()
                cursor.close()
                return True
            except Exception:
                self.connection.rollback()
                return False
        else:
            if facility_id not in self.review_flags:
                self.review_flags[facility_id] = []
            self.review_flags[facility_id].append({
                "flag_type": flag_type,
                "reason": reason,
                "created_at": datetime.now().isoformat(),
            })
            return True

    def get_review_flags(self, resolved: bool = False) -> list[dict]:
        """Get all review flags."""
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    "SELECT facility_id, flag_type, reason, created_at FROM review_flags WHERE resolved = %s ORDER BY created_at DESC",
                    (resolved,),
                )
                results = [
                    {"facility_id": row[0], "flag_type": row[1], "reason": row[2], "created_at": row[3]}
                    for row in cursor.fetchall()
                ]
                cursor.close()
                return results
            except Exception:
                return []
        else:
            flags = []
            for facility_id, flag_list in self.review_flags.items():
                for flag in flag_list:
                    flags.append({**flag, "facility_id": facility_id})
            return flags

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
