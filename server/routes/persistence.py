"""
Persistence API — Notes, overrides, shortlists via Lakebase.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from server.lakebase import db

router = APIRouter(tags=["persistence"])


class NoteRequest(BaseModel):
    facility_id: str
    note: str


class OverrideRequest(BaseModel):
    facility_id: str
    original_score: float
    new_score: float
    reason: str = ""


class ShortlistRequest(BaseModel):
    facility_id: str


@router.get("/persistence/notes/{facility_id}")
def get_notes(facility_id: str):
    return db.get_notes(facility_id)


@router.post("/persistence/notes")
def add_note(req: NoteRequest):
    ok = db.add_note(req.facility_id, req.note)
    return {"ok": ok}


@router.get("/persistence/overrides/{facility_id}")
def get_override(facility_id: str):
    result = db.get_override(facility_id)
    return result or {"detail": "No override found"}


@router.post("/persistence/overrides")
def set_override(req: OverrideRequest):
    ok = db.add_override(req.facility_id, req.original_score, req.new_score, req.reason)
    return {"ok": ok}


@router.get("/persistence/shortlist")
def get_shortlist():
    return db.get_shortlist()


@router.post("/persistence/shortlist")
def add_to_shortlist(req: ShortlistRequest):
    ok = db.add_to_shortlist(req.facility_id)
    return {"ok": ok}


@router.delete("/persistence/shortlist")
def remove_from_shortlist(req: ShortlistRequest):
    ok = db.remove_from_shortlist(req.facility_id)
    return {"ok": ok}
