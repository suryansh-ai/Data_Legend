from .data_loader import (
    load_facilities,
    get_facility_by_id,
    get_facilities_by_state,
    get_unique_states,
    get_unique_cities,
    get_dataset_stats,
)

try:
    from .lakebase import LakebaseClient
except Exception:
    LakebaseClient = None

__all__ = [
    "load_facilities",
    "get_facility_by_id",
    "get_facilities_by_state",
    "get_unique_states",
    "get_unique_cities",
    "get_dataset_stats",
    "LakebaseClient",
]
