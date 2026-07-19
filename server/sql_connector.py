"""
SQL Warehouse Connector — Query Databricks SQL Warehouse for analytics.

On Databricks Apps:
  - DATABRICKS_CLIENT_ID + DATABRICKS_CLIENT_SECRET are auto-injected
  - DATABRICKS_WAREHOUSE_ID must be set via app.yaml (valueFrom: sql-warehouse)

Local dev:
  - Returns None when warehouse is not available
"""

import os
from typing import Optional

WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "")
_connection = None
_available = False


def init_warehouse() -> bool:
    """Initialize SQL Warehouse connection. Returns True if successful."""
    global _connection, _available

    if not WAREHOUSE_ID:
        _available = False
        return False

    try:
        from databricks import sql
        from databricks.sdk.core import Config

        cfg = Config()
        _connection = sql.connect(
            server_hostname=cfg.host,
            http_path=f"/sql/1.0/warehouses/{WAREHOUSE_ID}",
            credentials_provider=lambda: cfg.authenticate,
        )
        _available = True
        return True
    except Exception:
        _connection = None
        _available = False
        return False


def is_available() -> bool:
    return _available


def warehouse_query(query: str, params: list | None = None) -> list[dict]:
    """Execute a SQL query against the warehouse. Returns list of row dicts."""
    if not _available or not _connection:
        return []

    try:
        cursor = _connection.cursor()
        cursor.execute(query, params or [])
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            return [dict(zip(columns, row)) for row in rows]
        cursor.close()
        return []
    except Exception:
        return []


def warehouse_query_df(query: str, params: list | None = None):
    """Execute a SQL query and return a pandas DataFrame."""
    if not _available or not _connection:
        return None

    try:
        import pandas as pd
        cursor = _connection.cursor()
        cursor.execute(query, params or [])
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            return pd.DataFrame(rows, columns=columns)
        cursor.close()
        return None
    except Exception:
        return None


# --- Pre-built analytics queries ---

def get_state_coverage_from_warehouse() -> list[dict]:
    """Get state-level coverage analysis from SQL Warehouse."""
    return warehouse_query("""
        SELECT
            address_stateOrRegion AS state,
            COUNT(*) AS total,
            ROUND(AVG(_trust_score), 1) AS avg_trust,
            SUM(CASE WHEN _trust_score < 30 THEN 1 ELSE 0 END) AS low_trust_count
        FROM facilities
        WHERE address_stateOrRegion IS NOT NULL
        GROUP BY address_stateOrRegion
        ORDER BY total DESC
    """)


def get_trust_distribution_from_warehouse() -> dict:
    """Get trust signal distribution from SQL Warehouse."""
    rows = warehouse_query("""
        SELECT _trust_signal, COUNT(*) AS count
        FROM facilities
        WHERE _trust_signal IS NOT NULL
        GROUP BY _trust_signal
    """)
    return {r["_trust_signal"]: r["count"] for r in rows} if rows else {}


def get_facility_search_from_warehouse(q: str, state: str = None, limit: int = 20) -> list[dict]:
    """Search facilities via SQL Warehouse."""
    query = """
        SELECT unique_id, name, description, address_city, address_stateOrRegion,
               latitude, longitude, _trust_score, _trust_signal,
               numberDoctors, capacity
        FROM facilities
        WHERE LOWER(name) LIKE %s OR LOWER(description) LIKE %s
              OR LOWER(address_city) LIKE %s
    """
    params = [f"%{q.lower()}%", f"%{q.lower()}%", f"%{q.lower()}%"]

    if state:
        query += " AND address_stateOrRegion = %s"
        params.append(state)

    query += f" ORDER BY _trust_score DESC LIMIT {limit}"
    return warehouse_query(query, params)
