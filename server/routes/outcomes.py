"""
Outcome Routes — Patient outcome recording and analytics endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/outcomes", tags=["outcomes"])


class OutcomeCreate(BaseModel):
    facility_id: str
    facility_name: str
    patient_id: str
    outcome_type: str = "treatment"
    specialty: str
    treatment_date: str
    diagnosis: Optional[str] = None
    treatment_provided: Optional[str] = None
    outcome_status: str = "stable"
    satisfaction_score: int = 3
    follow_up_required: bool = False
    follow_up_date: Optional[str] = None
    notes: Optional[str] = None
    appointment_id: Optional[str] = None
    would_recommend: bool = True
    recovery_days: Optional[int] = None
    cost_incurred: Optional[float] = None
    insurance_claim: bool = False


@router.post("/record")
async def record_outcome(request: OutcomeCreate):
    """Record a patient outcome."""
    from server.outcome_tracker import outcome_tracker
    
    # Validate satisfaction score
    if not 1 <= request.satisfaction_score <= 5:
        raise HTTPException(status_code=400, detail="Satisfaction score must be between 1 and 5")
    
    # Validate outcome status
    valid_statuses = ["improved", "stable", "worsened", "complications"]
    if request.outcome_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid outcome status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Record outcome
    outcome = outcome_tracker.record_outcome(
        facility_id=request.facility_id,
        facility_name=request.facility_name,
        patient_id=request.patient_id,
        outcome_type=request.outcome_type,
        specialty=request.specialty,
        treatment_date=request.treatment_date,
        diagnosis=request.diagnosis,
        treatment_provided=request.treatment_provided,
        outcome_status=request.outcome_status,
        satisfaction_score=request.satisfaction_score,
        follow_up_required=request.follow_up_required,
        follow_up_date=request.follow_up_date,
        notes=request.notes,
        appointment_id=request.appointment_id,
        would_recommend=request.would_recommend,
        recovery_days=request.recovery_days,
        cost_incurred=request.cost_incurred,
        insurance_claim=request.insurance_claim
    )
    
    return {
        "status": "success",
        "data": {
            "outcome_id": outcome.id,
            "message": "Outcome recorded successfully"
        }
    }


@router.get("/facility/{facility_id}")
async def get_facility_outcomes(facility_id: str):
    """Get all outcomes for a facility."""
    from server.outcome_tracker import outcome_tracker
    
    outcomes = outcome_tracker.get_outcomes_by_facility(facility_id)
    
    return {
        "status": "success",
        "count": len(outcomes),
        "data": [
            {
                "id": out.id,
                "patient_id": out.patient_id,
                "specialty": out.specialty,
                "treatment_date": out.treatment_date,
                "outcome_status": out.outcome_status,
                "satisfaction_score": out.satisfaction_score,
                "would_recommend": out.would_recommend,
                "created_at": out.created_at,
            }
            for out in outcomes
        ]
    }


@router.get("/patient/{patient_id}")
async def get_patient_outcomes(patient_id: str):
    """Get all outcomes for a patient."""
    from server.outcome_tracker import outcome_tracker
    
    outcomes = outcome_tracker.get_outcomes_by_patient(patient_id)
    
    return {
        "status": "success",
        "count": len(outcomes),
        "data": [
            {
                "id": out.id,
                "facility_name": out.facility_name,
                "specialty": out.specialty,
                "treatment_date": out.treatment_date,
                "outcome_status": out.outcome_status,
                "satisfaction_score": out.satisfaction_score,
                "diagnosis": out.diagnosis,
                "treatment_provided": out.treatment_provided,
            }
            for out in outcomes
        ]
    }


@router.get("/facility/{facility_id}/summary")
async def get_facility_outcome_summary(facility_id: str):
    """Get outcome summary for a facility."""
    from server.outcome_tracker import outcome_tracker
    
    summary = outcome_tracker.get_facility_outcome_summary(facility_id)
    
    return {
        "status": "success",
        "data": summary
    }


@router.get("/facility/{facility_id}/trust-impact")
async def get_trust_impact(facility_id: str):
    """Calculate how outcomes should impact trust scores."""
    from server.outcome_tracker import outcome_tracker
    
    impact = outcome_tracker.calculate_trust_impact(facility_id)
    
    return {
        "status": "success",
        "data": impact
    }


@router.get("/insights")
async def get_learning_insights():
    """Get insights from all outcomes for learning."""
    from server.outcome_tracker import outcome_tracker
    
    insights = outcome_tracker.get_learning_insights()
    
    return {
        "status": "success",
        "data": insights
    }


@router.get("/stats")
async def get_outcome_stats():
    """Get overall outcome statistics."""
    from server.outcome_tracker import outcome_tracker
    
    all_outcomes = list(outcome_tracker.outcomes.values())
    
    if not all_outcomes:
        return {
            "status": "success",
            "data": {
                "total_outcomes": 0,
                "average_satisfaction": 0,
                "recommendation_rate": 0,
                "outcome_distribution": {},
            }
        }
    
    total = len(all_outcomes)
    avg_satisfaction = sum(out.satisfaction_score for out in all_outcomes) / total
    recommend_rate = sum(1 for out in all_outcomes if out.would_recommend) / total
    
    # Outcome distribution
    outcome_dist = {}
    for out in all_outcomes:
        outcome_dist[out.outcome_status] = outcome_dist.get(out.outcome_status, 0) + 1
    
    return {
        "status": "success",
        "data": {
            "total_outcomes": total,
            "average_satisfaction": round(avg_satisfaction, 2),
            "recommendation_rate": round(recommend_rate * 100, 1),
            "outcome_distribution": outcome_dist,
        }
    }