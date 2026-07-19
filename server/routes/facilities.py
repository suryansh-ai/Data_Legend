"""
Facilities API — List, detail, map data endpoints.
"""

import math
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from server.data_loader import get_facilities_df, get_facility_by_id, _STATE_COL, _CITY_COL

router = APIRouter(tags=["facilities"])


def _sc():
    return _STATE_COL or "state"

def _cc():
    return _CITY_COL or "city"


@router.get("/facilities/autocomplete")
def autocomplete_facilities(q: str = Query("", min_length=1)):
    df = get_facilities_df()
    if df.empty or not q:
        return []
    
    q_lower = q.lower()
    cc = _cc()
    sc = _sc()
    
    # Filter by prefix first (starts with)
    starts_mask = df["name"].str.lower().str.startswith(q_lower, na=False)
    starts_with = df[starts_mask]
    
    # Filter by containment (contains) excluding starts_with
    contains_mask = df["name"].str.lower().str.contains(q_lower, na=False) & ~starts_mask
    contains = df[contains_mask]
    
    # Concatenate starts_with first, then contains
    matched = pd.concat([starts_with, contains]).head(10)
    
    results = []
    for _, row in matched.iterrows():
        results.append({
            "unique_id": row.get("unique_id"),
            "name": row.get("name"),
            "city": row.get(cc) if cc in row else row.get("address_city"),
            "state": row.get(sc) if sc in row else row.get("address_stateOrRegion"),
        })
    return results


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

    cols_to_select = ["unique_id", "name", cc, sc, "latitude", "longitude", "_trust_score", "_trust_signal", "capability", "capacity"]
    cols_present = [c for c in cols_to_select if c in filtered.columns]
    
    subset = filtered[cols_present].copy()
    subset["latitude"] = subset["latitude"].fillna(0.0)
    subset["longitude"] = subset["longitude"].fillna(0.0)
    if "_trust_score" in subset.columns:
        subset["_trust_score"] = subset["_trust_score"].fillna(0.0)
        
    items = subset.to_dict('records')
    for item in items:
        if cc in item:
            item["city"] = item[cc]
        else:
            item["city"] = item.get("address_city")
            
        if sc in item:
            item["state"] = item[sc]
        else:
            item["state"] = item.get("address_stateOrRegion")
            
    return items


@router.get("/facilities/{facility_id}")
def get_facility(facility_id: str):
    facility = get_facility_by_id(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility
