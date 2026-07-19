"""
Search API — Natural language search across facilities.
"""

import math
from fastapi import APIRouter, Query
from server.data_loader import get_facilities_df, _STATE_COL, _CITY_COL

router = APIRouter(tags=["search"])


@router.get("/search")
def search_facilities(
    q: str = Query(..., min_length=1),
    state: str = Query(None),
    trust_signal: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    df = get_facilities_df()
    if df.empty:
        return {"items": [], "total": 0, "page": 1, "limit": limit, "pages": 0}

    sc = _STATE_COL or "state"
    cc = _CITY_COL or "city"
    q_lower = q.lower()

    # Multi-field search with relevance scoring
    scores = []
    for idx, row in df.iterrows():
        score = 0
        name = str(row.get("name", "")).lower()
        desc = str(row.get("description", "")).lower()
        city = str(row.get(cc, "")).lower() if cc in row.index else ""
        state_name = str(row.get(sc, "")).lower() if sc in row.index else ""
        capability = str(row.get("capability", "")).lower()
        specialties = str(row.get("specialties", "")).lower()

        # Exact name match = highest score
        if q_lower == name:
            score += 100
        elif q_lower in name:
            score += 50

        # Description match
        if q_lower in desc:
            score += 20

        # City/state match
        if q_lower in city:
            score += 30
        if q_lower in state_name:
            score += 25

        # Capability/specialty match
        if q_lower in capability:
            score += 15
        if q_lower in specialties:
            score += 15

        # Word-level matching
        words = q_lower.split()
        for word in words:
            if word in name:
                score += 10
            if word in desc:
                score += 5

        if score > 0:
            scores.append((idx, score))

    # Sort by relevance
    scores.sort(key=lambda x: x[1], reverse=True)
    matched_indices = [s[0] for s in scores]

    filtered = df.loc[matched_indices]

    if state and sc in filtered.columns:
        filtered = filtered[filtered[sc] == state]
    if trust_signal:
        filtered = filtered[filtered["_trust_signal"] == trust_signal]

    total = len(filtered)
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
