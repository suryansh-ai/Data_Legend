"""
Data Loader — Ultra-fast parquet-based data loading.
"""

import os
import pandas as pd
import streamlit as st
from typing import Optional

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _data_path(filename: str) -> str:
    return os.path.join(_PROJECT_ROOT, "data", filename)


@st.cache_data(show_spinner=False)
def load_facilities() -> pd.DataFrame:
    """Load facilities from parquet — instant."""
    for fname in ["facilities_scored.parquet", "facilities.parquet"]:
        try:
            return pd.read_parquet(_data_path(fname))
        except Exception:
            pass
    try:
        return pd.read_csv(_data_path("facilities.csv"), on_bad_lines="skip", engine="python")
    except Exception:
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def get_dataset_stats(facilities: pd.DataFrame) -> dict:
    if facilities.empty:
        return {"total": 0, "states": 0, "cities": 0, "with_description": 0,
                "with_capability": 0, "with_procedure": 0, "with_equipment": 0,
                "with_specialties": 0, "with_doctors": 0, "with_capacity": 0}
    return {
        "total": len(facilities),
        "states": int(facilities["address_stateOrRegion"].nunique()),
        "cities": int(facilities["address_city"].nunique()),
        "with_description": int(facilities["description"].notna().sum()),
        "with_capability": int(facilities["capability"].notna().sum()),
        "with_procedure": int(facilities["procedure"].notna().sum()),
        "with_equipment": int(facilities["equipment"].notna().sum()),
        "with_specialties": int(facilities["specialties"].notna().sum()),
        "with_doctors": int(facilities["numberDoctors"].notna().sum()),
        "with_capacity": int(facilities["capacity"].notna().sum()),
    }


def get_facility_by_id(facilities: pd.DataFrame, facility_id: str) -> Optional[dict]:
    if facilities.empty: return None
    match = facilities[facilities["unique_id"] == facility_id]
    if match.empty: return None
    return match.iloc[0].to_dict()


def get_facilities_by_state(facilities: pd.DataFrame, state: str) -> pd.DataFrame:
    if facilities.empty: return pd.DataFrame()
    return facilities[facilities["address_stateOrRegion"] == state]


def get_unique_states(facilities: pd.DataFrame) -> list:
    if facilities.empty: return []
    return sorted(facilities["address_stateOrRegion"].dropna().unique().tolist())


def get_unique_cities(facilities: pd.DataFrame, state: Optional[str] = None) -> list:
    if facilities.empty: return []
    if state and state != "All States":
        return sorted(facilities[facilities["address_stateOrRegion"] == state]["address_city"].dropna().unique().tolist())
    return sorted(facilities["address_city"].dropna().unique().tolist())
