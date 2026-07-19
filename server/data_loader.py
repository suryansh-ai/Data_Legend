"""
Data Loader — Multi-source data loading with fallback chain.

Priority:
  1. Parquet files (fastest, 0ms cold start)
  2. SQL Warehouse (Databricks, for complex analytics)
  3. Empty DataFrame (graceful degradation)
"""

import os
import pandas as pd
from typing import Optional

_PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
_df: Optional[pd.DataFrame] = None


def _data_path(filename: str) -> str:
    return os.path.join(_PROJECT_ROOT, "data", filename)


def load_facilities() -> pd.DataFrame:
    """Load facilities from parquet — instant."""
    global _df
    if _df is not None and not _df.empty:
        return _df

    for fname in ["facilities_scored.parquet", "facilities.parquet"]:
        try:
            _df = pd.read_parquet(_data_path(fname))
            return _df
        except Exception:
            pass

    # Fallback: try SQL Warehouse
    try:
        from server.sql_connector import warehouse_query_df, is_available
        if is_available():
            df = warehouse_query_df("SELECT * FROM facilities")
            if df is not None and not df.empty:
                _df = df
                return _df
    except Exception:
        pass

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
        "with_capability": int(df["capability"].notna().sum()),
        "with_procedure": int(df["procedure"].notna().sum()),
        "with_equipment": int(df["equipment"].notna().sum()),
        "with_specialties": int(df["specialties"].notna().sum()),
        "with_doctors": int(df["numberDoctors"].notna().sum()),
        "with_capacity": int(df["capacity"].notna().sum()),
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
        if _df is not None and os.path.exists(_data_path("facilities_scored.parquet")):
            source = "parquet"
        else:
            source = "sql_warehouse"
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
        "warehouse_available": warehouse,
        "persistence_backend": persistence,
    }
