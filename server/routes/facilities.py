"""
Facilities API — List, detail, map data endpoints.
"""

import math
from fastapi import APIRouter, HTTPException, Query
from server.data_loader import get_facilities_df, get_facility_by_id, _STATE_COL, _CITY_COL

router = APIRouter(tags=["facilities"])


def _sc():
    return _STATE_COL or "state"

def _cc():
    return _CITY_COL or "city"


@router.get("/facilities")
def list_facilities(
    q: str = Query(None),
    state: str = Query(None),
    city: str = Query(None),
    trust_signal: str = Query(None),
    capability: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query(None),
    sort_order: str = Query("asc"),
):
    df = get_facilities_df()
    if df.empty:
        return {"items": [], "total": 0, "page": 1, "limit": limit, "pages": 0}

    sc, cc = _sc(), _cc()
    filtered = df.copy()

    if q:
        q_lower = q.lower()
        mask = (
            filtered["name"].str.lower().str.contains(q_lower, na=False) |
            filtered["description"].str.lower().str.contains(q_lower, na=False)
        )
        if cc in filtered.columns:
            mask = mask | filtered[cc].astype(str).str.lower().str.contains(q_lower, na=False)
        if sc in filtered.columns:
            mask = mask | filtered[sc].astype(str).str.lower().str.contains(q_lower, na=False)
        if "capability" in filtered.columns:
            mask = mask | filtered["capability"].astype(str).str.lower().str.contains(q_lower, na=False)
        if "specialties" in filtered.columns:
            mask = mask | filtered["specialties"].astype(str).str.lower().str.contains(q_lower, na=False)
        filtered = filtered[mask]

    if state and sc in filtered.columns:
        filtered = filtered[filtered[sc] == state]
    if city and cc in filtered.columns:
        filtered = filtered[filtered[cc] == city]
    if trust_signal:
        filtered = filtered[filtered["_trust_signal"] == trust_signal]
    if capability:
        cap_lower = capability.lower()
        if "capability" in filtered.columns:
            filtered = filtered[filtered["capability"].astype(str).str.lower().str.contains(cap_lower, na=False)]

    total = len(filtered)

    if sort_by and sort_by in filtered.columns:
        ascending = sort_order == "asc"
        filtered = filtered.sort_values(sort_by, ascending=ascending, na_position="last")

    start = (page - 1) * limit
    end = start + limit
    page_data = filtered.iloc[start:end]

    items = []
    for _, row in page_data.iterrows():
        item = row.to_dict()
        for k, v in item.items():
            if isinstance(v, float) and math.isnan(v):
                item[k] = None
        items.append(item)

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": math.ceil(total / limit) if limit else 0,
    }


@router.get("/facilities/map")
def map_data(state: str = Query(None), trust_signal: str = Query(None)):
    df = get_facilities_df()
    if df.empty:
        return []

    sc, cc = _sc(), _cc()
    filtered = df.copy()
    if state and sc in filtered.columns:
        filtered = filtered[filtered[sc] == state]
    if trust_signal:
        filtered = filtered[filtered["_trust_signal"] == trust_signal]

    filtered = filtered.dropna(subset=["latitude", "longitude"])

    items = []
    for _, row in filtered.iterrows():
        item = {
            "unique_id": row.get("unique_id"),
            "name": row.get("name"),
            "city": row.get(cc) if cc in row else row.get("address_city"),
            "state": row.get(sc) if sc in row else row.get("address_stateOrRegion"),
            "latitude": float(row["latitude"]) if not math.isnan(row["latitude"]) else None,
            "longitude": float(row["longitude"]) if not math.isnan(row["longitude"]) else None,
            "_trust_score": float(row["_trust_score"]) if "_trust_score" in row and not math.isnan(row.get("_trust_score", float("nan"))) else None,
            "_trust_signal": row.get("_trust_signal"),
        }
        items.append(item)

    return items


@router.get("/facilities/{facility_id}")
def get_facility(facility_id: str):
    facility = get_facility_by_id(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility
