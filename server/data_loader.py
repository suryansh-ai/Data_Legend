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
_district_df: Optional[pd.DataFrame] = None
_lower_cache: dict[str, pd.Series] = {}

# Detect if we're on Databricks
_ON_DATABRICKS = bool(os.getenv("DATABRICKS_WAREHOUSE_ID"))

# Column name aliases for backward compatibility with old column names
# The new master dataset uses: city, state
# Old datasets used: address_city, address_stateOrRegion
_STATE_COL = None
_CITY_COL = None

# Lazy data directory - only search filesystem on first access
_DATA_DIR = None

def _get_data_dir() -> str:
    global _DATA_DIR
    if _DATA_DIR is not None:
        return _DATA_DIR
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"),
        os.path.join(os.getcwd(), "data"),
        "/tmp/databricks/apps/data",
        os.path.join(os.getenv("HOME", ""), "data"),
    ]
    for path in candidates:
        if os.path.isdir(path):
            _DATA_DIR = path
            return _DATA_DIR
    _DATA_DIR = os.path.join(os.getcwd(), "data")
    return _DATA_DIR


def _data_path(filename: str) -> str:
    return os.path.join(_get_data_dir(), filename)


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


def _lowered_series(column: str) -> pd.Series:
    global _lower_cache
    if column in _lower_cache:
        return _lower_cache[column]

    df = get_facilities_df()
    if df.empty or column not in df.columns:
        series = pd.Series([""] * len(df), index=df.index)
    else:
        series = df[column].fillna("").astype(str).str.lower()

    _lower_cache[column] = series
    return series


def _load_from_parquet() -> Optional[pd.DataFrame]:
    """Try loading from local parquet files. Prefers facilities_master.parquet."""
    global _STATE_COL, _CITY_COL

    # Priority order: master > scored > generic
    # Essential columns for faster startup - only load what's available
    _ESSENTIAL_COLS = [
        "unique_id", "name", "description", "capability", "procedure",
        "equipment", "specialties", "numberDoctors", "capacity",
        "address_stateOrRegion", "address_city", "latitude", "longitude",
        "_trust_score", "_trust_signal", "_total_claims", "_corroborated",
        "city", "state", "state_type", "country",
        "officialPhone", "phone_numbers", "email",
        "officialWebsite", "websites",
        "yearEstablished", "acceptsVolunteers",
        "_facility_type", "_operator_type",
        "address_line1", "address_line2", "pincode",
    ]
    for fname in ["facilities_master.parquet", "facilities_scored.parquet", "facilities.parquet"]:
        fpath = _data_path(fname)
        if os.path.exists(fpath):
            try:
                # Read schema first (metadata only, no data) to get available columns
                import pyarrow.parquet as pq
                available_cols = pq.read_schema(fpath).names
                cols_to_read = [c for c in _ESSENTIAL_COLS if c in available_cols]
                df = pd.read_parquet(fpath, columns=cols_to_read or None)
                if len(df) > 0:
                    # Detect column names
                    if "state" in df.columns:
                        _STATE_COL = "state"
                        _CITY_COL = "city"
                    elif "address_stateOrRegion" in df.columns:
                        _STATE_COL = "address_stateOrRegion"
                        _CITY_COL = "address_city"
                    else:
                        _STATE_COL = "address_stateOrRegion"
                        _CITY_COL = "address_city"
                    print(f"[data] Loaded {len(df)} facilities from {fname} (state_col={_STATE_COL})")
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
            _lower_cache.clear()
            return _df

        print("[data] SQL Warehouse failed, falling back to parquet...")
        df = _load_from_parquet()
        if df is not None and not df.empty:
            _df = df
            _lower_cache.clear()
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
            _lower_cache.clear()
            return _df

    print("[data] WARNING: No data loaded from any source!")
    _df = pd.DataFrame()
    return _df


def get_facilities_df() -> pd.DataFrame:
    if _df is None or _df.empty:
        return load_facilities()
    return _df


def get_district_health_df() -> pd.DataFrame:
    """Load district health data from NFHS-5."""
    global _district_df
    if _district_df is not None and not _district_df.empty:
        return _district_df
    fpath = _data_path("district_health.parquet")
    if os.path.exists(fpath):
        try:
            _district_df = pd.read_parquet(fpath)
            print(f"[data] Loaded {len(_district_df)} districts from NFHS-5")
            return _district_df
        except Exception as e:
            print(f"[data] Error loading district health: {e}")
    return pd.DataFrame()


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


_dataset_stats_cache = None

def get_dataset_stats() -> dict:
    global _dataset_stats_cache
    if _dataset_stats_cache is not None:
        return _dataset_stats_cache
    df = get_facilities_df()
    if df.empty:
        return {
            "total": 0, "states": 0, "cities": 0,
            "with_description": 0, "with_capability": 0, "with_procedure": 0,
            "with_equipment": 0, "with_specialties": 0, "with_doctors": 0, "with_capacity": 0,
        }
    sc = _STATE_COL or "state"
    cc = _CITY_COL or "city"
    _dataset_stats_cache = {
        "total": len(df),
        "states": int(df[sc].nunique()) if sc in df.columns else 0,
        "cities": int(df[cc].nunique()) if cc in df.columns else 0,
        "with_description": int(df["_has_description"].sum()) if "_has_description" in df.columns else int(df["description"].notna().sum()),
        "with_capability": int(df["_has_capability"].sum()) if "_has_capability" in df.columns else int(df["capability"].notna().sum()) if "capability" in df.columns else 0,
        "with_procedure": int(df["_has_procedure"].sum()) if "_has_procedure" in df.columns else int(df["procedure"].notna().sum()) if "procedure" in df.columns else 0,
        "with_equipment": int(df["_has_equipment"].sum()) if "_has_equipment" in df.columns else int(df["equipment"].notna().sum()) if "equipment" in df.columns else 0,
        "with_specialties": int(df["_has_specialties"].sum()) if "_has_specialties" in df.columns else int(df["specialties"].notna().sum()) if "specialties" in df.columns else 0,
        "with_doctors": int(df["_has_doctors"].sum()) if "_has_doctors" in df.columns else int(df["numberDoctors"].notna().sum()) if "numberDoctors" in df.columns else 0,
        "with_capacity": int(df["_has_capacity"].sum()) if "_has_capacity" in df.columns else int(df["capacity"].notna().sum()) if "capacity" in df.columns else 0,
    }
    return _dataset_stats_cache


_column_completeness_cache = None

def get_column_completeness() -> dict:
    global _column_completeness_cache
    if _column_completeness_cache is not None:
        return _column_completeness_cache
    df = get_facilities_df()
    if df.empty:
        return {}
    sc = _STATE_COL or "state"
    cc = _CITY_COL or "city"
    key_cols = [
        "name", "description", "capability", "procedure", "equipment",
        "specialties", "numberDoctors", "capacity",
        sc, cc, "latitude", "longitude",
    ]
    _column_completeness_cache = {col: int(df[col].notna().sum()) for col in key_cols if col in df.columns}
    return _column_completeness_cache


_state_stats_cache = None

def get_state_stats() -> list[dict]:
    global _state_stats_cache
    if _state_stats_cache is not None:
        return _state_stats_cache
    df = get_facilities_df()
    if df.empty:
        return []
    sc = _STATE_COL or "state"
    grouped = df.groupby(sc).agg(
        total=("unique_id", "count"),
        avg_trust=("_trust_score", "mean"),
        low_trust_count=("_trust_score", lambda x: (x < 30).sum()),
    ).reset_index()
    grouped = grouped.rename(columns={sc: "state"})
    grouped["avg_trust"] = grouped["avg_trust"].fillna(0).round(1)
    grouped["low_trust_count"] = grouped["low_trust_count"].fillna(0).astype(int)
    _state_stats_cache = grouped.sort_values("total", ascending=False).to_dict("records")
    return _state_stats_cache


_trust_distribution_cache = None

def get_trust_distribution() -> dict:
    global _trust_distribution_cache
    if _trust_distribution_cache is not None:
        return _trust_distribution_cache
    df = get_facilities_df()
    if df.empty:
        return {}
    counts = df["_trust_signal"].value_counts()
    _trust_distribution_cache = {str(k): int(v) for k, v in counts.items()}
    return _trust_distribution_cache


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


_facilities_list = None
_district_health_dict = None


def get_facilities_list() -> list:
    global _facilities_list
    if _facilities_list is not None:
        return _facilities_list
    df = get_facilities_df()
    if df.empty:
        return []
    
    # Pre-clean NaN values so it is JSON serializable
    df_clean = df.copy()
    for col in df_clean.columns:
        if df_clean[col].dtype == object or df_clean[col].dtype == 'O':
            df_clean[col] = df_clean[col].fillna('')
        else:
            df_clean[col] = df_clean[col].fillna(0)
    _facilities_list = df_clean.to_dict('records')
    return _facilities_list


def get_district_health_dict() -> dict:
    global _district_health_dict
    if _district_health_dict is not None:
        return _district_health_dict
    df = get_district_health_df()
    if df.empty:
        return {}
    _district_health_dict = {}
    for _, row in df.iterrows():
        r_dict = row.to_dict()
        for k, v in r_dict.items():
            if pd.isna(v):
                r_dict[k] = None
        _district_health_dict[row.get("district", "")] = r_dict
    return _district_health_dict

