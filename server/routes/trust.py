"""
Trust API — Score facilities and get trust breakdowns.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.data_loader import get_facility_by_id
from server.trust_engine import score_facility

router = APIRouter(tags=["trust"])


class BatchScoreRequest(BaseModel):
    facility_ids: list[str]


@router.post("/trust/score/{facility_id}")
def score_single(facility_id: str):
    facility = get_facility_by_id(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return score_facility(facility)


@router.post("/trust/batch")
def batch_score(req: BatchScoreRequest):
    results = []
    for fid in req.facility_ids[:50]:  # Cap at 50
        facility = get_facility_by_id(fid)
        if facility:
            results.append(score_facility(facility))
    return results
