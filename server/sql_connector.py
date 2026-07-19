"""
SQL Warehouse Connector — Query Databricks SQL Warehouse for analytics.

On Databricks Apps:
  - DATABRICKS_CLIENT_ID + DATABRICKS_CLIENT_SECRET are auto-injected
  - DATABRICKS_WAREHOUSE_ID must be set via app.yaml (valueFrom: sql-warehouse)
  - DATASET_CATALOG can be set to override auto-discovery

Local dev:
  - Returns None when warehouse is not available
"""

import os
from typing import Optional

WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "")
DATASET_CATALOG = os.getenv("DATASET_CATALOG", "")
_connection = None
_available = False
_resolved_table: Optional[str] = None


def _get_config():
    from databricks.sdk.core import Config
    return Config()


def init_warehouse() -> bool:
    """Initialize SQL Warehouse connection. Returns True if successful."""
    global _connection, _available

    if not WAREHOUSE_ID:
        _available = False
        return False

    try:
        from databricks import sql as dbsql
        cfg = _get_config()

        _connection = dbsql.connect(
            server_hostname=cfg.host,
            http_path=f"/sql/1.0/warehouses/{WAREHOUSE_ID}",
            credentials_provider=lambda: cfg.authenticate(),
        )
        _available = True
        print(f"[sql] Connected to SQL Warehouse {WAREHOUSE_ID}")
        _discover_table()
        return True
    except Exception as e:
        print(f"[sql] Failed to connect: {e}")
        _connection = None
        _available = False
        return False


def _discover_table():
    """Auto-discover the facilities table in Unity Catalog."""
    global _resolved_table

    if _resolved_table:
        return

    if not _available or not _connection:
        return

    cursor = _connection.cursor()

    # If catalog is specified via env var, use it directly
    if DATASET_CATALOG:
        candidates = [
            f"{DATASET_CATALOG}.default.facilities",
            f"{DATASET_CATALOG}.main.facilities",
            f"{DATASET_CATALOG}.virtue_foundation.facilities",
        ]
        for table in candidates:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                if count > 0:
                    _resolved_table = table
                    print(f"[sql] Found facilities table: {_resolved_table} ({count} rows)")
                    cursor.close()
                    return
            except Exception:
                continue

    # Auto-discover: search all catalogs for a facilities table
    try:
        cursor.execute("SHOW CATALOGS")
        catalogs = [row[0] for row in cursor.fetchall()]
        print(f"[sql] Available catalogs: {catalogs}")

        for cat in catalogs:
            if cat.startswith("hive_metastore") or cat == "system":
                continue
            try:
                cursor.execute(f"SHOW SCHEMAS IN {cat}")
                schemas = [row[0] for row in cursor.fetchall()]

                for schema in schemas:
                    try:
                        cursor.execute(f"SHOW TABLES IN {cat}.{schema}")
                        tables = [row[1] for row in cursor.fetchall()]
                        if "facilities" in tables:
                            full = f"{cat}.{schema}.facilities"
                            cursor.execute(f"SELECT COUNT(*) FROM {full}")
                            count = cursor.fetchone()[0]
                            if count > 100:
                                _resolved_table = full
                                print(f"[sql] Auto-discovered: {_resolved_table} ({count} rows)")
                                cursor.close()
                                return
                    except Exception:
                        continue
            except Exception:
                continue
    except Exception as e:
        print(f"[sql] Discovery error: {e}")

    cursor.close()
    print("[sql] WARNING: Could not find facilities table in any catalog")


def get_facilities_table() -> str:
    """Return the resolved fully-qualified table name."""
    if not _resolved_table:
        _discover_table()
    return _resolved_table or "facilities"


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
    except Exception as e:
        print(f"[sql] Query error: {e}")
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
    except Exception as e:
        print(f"[sql] DataFrame query error: {e}")
        return None


# --- Pre-built analytics queries ---

def get_state_coverage_from_warehouse() -> list[dict]:
    """Get state-level coverage analysis from SQL Warehouse."""
    table = get_facilities_table()
    return warehouse_query(f"""
        SELECT
            address_stateOrRegion AS state,
            COUNT(*) AS total,
            COALESCE(ROUND(AVG(_trust_score), 1), 0) AS avg_trust,
            SUM(CASE WHEN _trust_score < 30 THEN 1 ELSE 0 END) AS low_trust_count
        FROM {table}
        WHERE address_stateOrRegion IS NOT NULL
        GROUP BY address_stateOrRegion
        ORDER BY total DESC
    """)


def get_trust_distribution_from_warehouse() -> dict:
    """Get trust signal distribution from SQL Warehouse."""
    table = get_facilities_table()
    rows = warehouse_query(f"""
        SELECT _trust_signal, COUNT(*) AS count
        FROM {table}
        WHERE _trust_signal IS NOT NULL
        GROUP BY _trust_signal
    """)
    return {r["_trust_signal"]: r["count"] for r in rows} if rows else {}


def get_facility_search_from_warehouse(q: str, state: str = None, limit: int = 20) -> list[dict]:
    """Search facilities via SQL Warehouse."""
    table = get_facilities_table()
    query = f"""
        SELECT unique_id, name, description, address_city, address_stateOrRegion,
               latitude, longitude, _trust_score, _trust_signal,
               numberDoctors, capacity
        FROM {table}
        WHERE LOWER(name) LIKE %s OR LOWER(description) LIKE %s
              OR LOWER(address_city) LIKE %s
    """
    params = [f"%{q.lower()}%", f"%{q.lower()}%", f"%{q.lower()}%"]

    if state:
        query += " AND address_stateOrRegion = %s"
        params.append(state)

    query += " ORDER BY _trust_score DESC LIMIT %s"
    params.append(limit)
    return warehouse_query(query, params)
