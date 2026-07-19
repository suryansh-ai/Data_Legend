"""
Lakebase Client — Persistence layer for notes, overrides, shortlists.
Falls back to in-memory storage when Lakebase is unavailable.
"""

import os
from datetime import datetime
from typing import Optional


class LakebaseClient:
    def __init__(self):
        self.connection = None
        self._connect()

    def _connect(self):
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
        self.notes: dict[str, list] = {}
        self.overrides: dict[str, dict] = {}
        self.shortlists: dict[str, list[str]] = {}

    def _init_schema(self):
        if not self.connection:
            return
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                facility_id VARCHAR(255) NOT NULL,
                note TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS overrides (
                id SERIAL PRIMARY KEY,
                facility_id VARCHAR(255) NOT NULL UNIQUE,
                original_score FLOAT,
                new_score FLOAT NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shortlists (
                id SERIAL PRIMARY KEY,
                facility_id VARCHAR(255) NOT NULL,
                list_name VARCHAR(255) DEFAULT 'default',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(facility_id, list_name)
            )
        """)
        self.connection.commit()
        cursor.close()

    def add_note(self, facility_id: str, note: str) -> bool:
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("INSERT INTO notes (facility_id, note) VALUES (%s, %s)", (facility_id, note))
                self.connection.commit()
                cursor.close()
                return True
            except Exception:
                self.connection.rollback()
        if facility_id not in self.notes:
            self.notes[facility_id] = []
        self.notes[facility_id].append({"note": note, "created_at": datetime.now().isoformat()})
        return True

    def get_notes(self, facility_id: str) -> list[dict]:
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT note, created_at FROM notes WHERE facility_id = %s ORDER BY created_at DESC", (facility_id,))
                results = [{"note": r[0], "created_at": str(r[1])} for r in cursor.fetchall()]
                cursor.close()
                return results
            except Exception:
                return []
        return self.notes.get(facility_id, [])

    def add_override(self, facility_id: str, original_score: float, new_score: float, reason: str = "") -> bool:
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    """INSERT INTO overrides (facility_id, original_score, new_score, reason)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (facility_id) DO UPDATE
                       SET new_score = EXCLUDED.new_score, reason = EXCLUDED.reason""",
                    (facility_id, original_score, new_score, reason),
                )
                self.connection.commit()
                cursor.close()
                return True
            except Exception:
                self.connection.rollback()
        self.overrides[facility_id] = {
            "original_score": original_score, "new_score": new_score,
            "reason": reason, "created_at": datetime.now().isoformat(),
        }
        return True

    def get_override(self, facility_id: str) -> Optional[dict]:
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT original_score, new_score, reason, created_at FROM overrides WHERE facility_id = %s", (facility_id,))
                row = cursor.fetchone()
                cursor.close()
                if row:
                    return {"original_score": row[0], "new_score": row[1], "reason": row[2], "created_at": str(row[3])}
                return None
            except Exception:
                return None
        return self.overrides.get(facility_id)

    def add_to_shortlist(self, facility_id: str, list_name: str = "default") -> bool:
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("INSERT INTO shortlists (facility_id, list_name) VALUES (%s, %s) ON CONFLICT DO NOTHING", (facility_id, list_name))
                self.connection.commit()
                cursor.close()
                return True
            except Exception:
                self.connection.rollback()
        if list_name not in self.shortlists:
            self.shortlists[list_name] = []
        if facility_id not in self.shortlists[list_name]:
            self.shortlists[list_name].append(facility_id)
        return True

    def get_shortlist(self, list_name: str = "default") -> list[str]:
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT facility_id FROM shortlists WHERE list_name = %s ORDER BY added_at", (list_name,))
                results = [r[0] for r in cursor.fetchall()]
                cursor.close()
                return results
            except Exception:
                return []
        return self.shortlists.get(list_name, [])

    def remove_from_shortlist(self, facility_id: str, list_name: str = "default") -> bool:
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM shortlists WHERE facility_id = %s AND list_name = %s", (facility_id, list_name))
                self.connection.commit()
                cursor.close()
                return True
            except Exception:
                self.connection.rollback()
        if list_name in self.shortlists and facility_id in self.shortlists[list_name]:
            self.shortlists[list_name].remove(facility_id)
        return True


db = LakebaseClient()
