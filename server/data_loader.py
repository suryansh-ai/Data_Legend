"""
Data Loader — Multi-source data loading with smart fallback.

On Databricks: SQL Warehouse FIRST (full 10K dataset), then parquet.
Local dev: Parquet FIRST (fast), then SQL Warehouse (if available).
"""

import os
import glob as globmod
import pandas as pd
from typing import Optional

_df: Optional[pd.DataFrame] = None

# Detect if we're on Databricks
_ON_DATABRICKS = bool(os.getenv("DATABRICKS_WAREHOUSE_ID"))


def _find_data_dir() -> str:
    """Find the data directory regardless of where the app is run from."""
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"),
        os.path.join(os.getcwd(), "data"),
        "/tmp/databricks/apps/data",
        os.path.join(os.getenv("HOME", ""), "data"),
    ]
    for path in candidates:
        if os.path.isdir(path):
            return path
    return os.path.join(os.getcwd(), "data")


_DATA_DIR = _find_data_dir()


def _data_path(filename: str) -> str:
    return os.path.join(_DATA_DIR, filename)


def _ensure_trust_columns(df: pd.DataFrame) -> pd.DataFrame:
    """If trust columns are missing (raw Marketplace data), compute them."""
    if "_trust_score" in df.columns and "_trust_signal" in df.columns:
        return df

    print("[data] Trust columns missing — computing from raw data...")
    try:
        from server.trust_engine import score_facility
        scores = []
        for _, row in df.iterrows():
            result = score_facility(row.to_dict())
            scores.append(result)
        df["_trust_score"] = [s.get("overall_trust", 0) for s in scores]
        df["_trust_signal"] = [s.get("overall_signal", "UNKNOWN") for s in scores]
        df["_total_claims"] = [s.get("metadata", {}).get("total_claims", 0) for s in scores]
        df["_corroborated"] = [s.get("metadata", {}).get("corroborated_claims", 0) for s in scores]
        print(f"[data] Computed trust scores for {len(df)} facilities")
    except Exception as e:
        print(f"[data] Could not compute trust scores: {e}")
        df["_trust_score"] = 0
        df["_trust_signal"] = "unknown"

    return df


def _load_from_parquet() -> Optional[pd.DataFrame]:
    """Try loading from local parquet files."""
    for fname in ["facilities_scored.parquet", "facilities.parquet"]:
        fpath = _data_path(fname)
        if os.path.exists(fpath):
            try:
                df = pd.read_parquet(fpath)
                if len(df) > 0:
                    print(f"[data] Loaded {len(df)} facilities from parquet: {fpath}")
                    return df
            except Exception as e:
                print(f"[data] Error loading {fpath}: {e}")

    # Fallback: search for any parquet file in the repo
    try:
        repo_root = os.path.dirname(_DATA_DIR)
        parquet_files = globmod.glob(os.path.join(repo_root, "**", "*.parquet"), recursive=True)
        for fpath in parquet_files:
            try:
                df = pd.read_parquet(fpath)
                if len(df) > 100:
                    print(f"[data] Loaded {len(df)} facilities from fallback parquet: {fpath}")
                    return df
            except Exception:
                continue
    except Exception:
        pass

    return None


def _load_from_warehouse() -> Optional[pd.DataFrame]:
    """Try loading from Databricks SQL Warehouse."""
    try:
        from server.sql_connector import init_warehouse, warehouse_query_df, get_facilities_table, is_available

        if not is_available():
            init_warehouse()

        if not is_available():
            print("[data] SQL Warehouse not available")
            return None

        table = get_facilities_table()
        print(f"[data] Querying SQL Warehouse: {table}")

        # First check if trust columns exist
        df_check = warehouse_query_df(f"SELECT * FROM {table} LIMIT 1")
        if df_check is not None and len(df_check) > 0:
            cols = list(df_check.columns)
            has_trust = "_trust_score" in cols and "_trust_signal" in cols

            if has_trust:
                df = warehouse_query_df(f"SELECT * FROM {table}")
            else:
                # Load in chunks to avoid memory issues with 10K rows
                df = warehouse_query_df(f"SELECT * FROM {table}")
                if df is not None:
                    df = _ensure_trust_columns(df)

            if df is not None and len(df) > 0:
                print(f"[data] Loaded {len(df)} facilities from SQL Warehouse ({table})")
                return df
    except Exception as e:
        print(f"[data] SQL Warehouse error: {e}")

    return None


def load_facilities() -> pd.DataFrame:
    """Load facilities — SQL Warehouse first on Databricks, parquet first locally."""
    global _df
    if _df is not None and not _df.empty:
        return _df

    if _ON_DATABRICKS:
        # On Databricks: SQL Warehouse FIRST (full 10K), parquet as fallback
        df = _load_from_warehouse()
        if df is not None and not df.empty:
            _df = df
            return _df

        print("[data] SQL Warehouse failed, falling back to parquet...")
        df = _load_from_parquet()
        if df is not None and not df.empty:
            _df = df
            return _df
    else:
        # Local dev: parquet FIRST (fast), SQL Warehouse as fallback
        df = _load_from_parquet()
        if df is not None and not df.empty:
            _df = df
            return _df

        print("[data] Parquet not found, trying SQL Warehouse...")
        df = _load_from_warehouse()
        if df is not None and not df.empty:
            _df = df
            return _df

    print("[data] WARNING: No data loaded from any source!")
    _df = pd.DataFrame()
    return _df


def get_facilities_df() -> pd.DataFrame:
    if _df is None or _df.empty:
        return load_facilities()
    return _df


def get_facility_by_id(facility_id: str) -> Optional[dict]:
    df = get_facilities_df()
    if df.empty:
        return None
    match = df[df["unique_id"] == facility_id]
    if match.empty:
        return None
    row = match.iloc[0].to_dict()
    for k, v in row.items():
        if pd.isna(v):
            row[k] = None
    return row


def get_dataset_stats() -> dict:
    df = get_facilities_df()
    if df.empty:
        return {
            "total": 0, "states": 0, "cities": 0,
            "with_description": 0, "with_capability": 0, "with_procedure": 0,
            "with_equipment": 0, "with_specialties": 0, "with_doctors": 0, "with_capacity": 0,
        }
    return {
        "total": len(df),
        "states": int(df["address_stateOrRegion"].nunique()),
        "cities": int(df["address_city"].nunique()),
        "with_description": int(df["description"].notna().sum()),
        "with_capability": int(df["capability"].notna().sum()) if "capability" in df.columns else 0,
        "with_procedure": int(df["procedure"].notna().sum()) if "procedure" in df.columns else 0,
        "with_equipment": int(df["equipment"].notna().sum()) if "equipment" in df.columns else 0,
        "with_specialties": int(df["specialties"].notna().sum()) if "specialties" in df.columns else 0,
        "with_doctors": int(df["numberDoctors"].notna().sum()) if "numberDoctors" in df.columns else 0,
        "with_capacity": int(df["capacity"].notna().sum()) if "capacity" in df.columns else 0,
    }


def get_column_completeness() -> dict:
    df = get_facilities_df()
    if df.empty:
        return {}
    total = len(df)
    key_cols = [
        "name", "description", "capability", "procedure", "equipment",
        "specialties", "numberDoctors", "capacity",
        "address_stateOrRegion", "address_city", "latitude", "longitude",
    ]
    return {col: int(df[col].notna().sum()) for col in key_cols if col in df.columns}


def get_state_stats() -> list[dict]:
    df = get_facilities_df()
    if df.empty:
        return []
    grouped = df.groupby("address_stateOrRegion").agg(
        total=("unique_id", "count"),
        avg_trust=("_trust_score", "mean"),
        low_trust_count=("_trust_score", lambda x: (x < 30).sum()),
    ).reset_index()
    grouped = grouped.rename(columns={"address_stateOrRegion": "state"})
    grouped["avg_trust"] = grouped["avg_trust"].fillna(0).round(1)
    grouped["low_trust_count"] = grouped["low_trust_count"].fillna(0).astype(int)
    return grouped.sort_values("total", ascending=False).to_dict("records")


def get_trust_distribution() -> dict:
    df = get_facilities_df()
    if df.empty:
        return {}
    counts = df["_trust_signal"].value_counts()
    return {str(k): int(v) for k, v in counts.items()}


def get_data_source_info() -> dict:
    """Report which data source is active."""
    df = get_facilities_df()
    source = "none"
    if not df.empty:
        source = "sql_warehouse" if _ON_DATABRICKS and _df is not None else "parquet"
    try:
        from server.sql_connector import is_available as wh_available
        warehouse = wh_available()
    except Exception:
        warehouse = False
    try:
        from server.lakebase import db
        persistence = db.get_backend()
    except Exception:
        persistence = "memory"
    return {
        "data_source": source,
        "facility_count": len(df) if not df.empty else 0,
        "data_dir": _DATA_DIR,
        "on_databricks": _ON_DATABRICKS,
        "warehouse_available": warehouse,
        "persistence_backend": persistence,
    }
