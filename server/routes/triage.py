"""
Triage Routes — Symptom assessment and hospital recommendation endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/triage", tags=["triage"])


class TriageRequest(BaseModel):
    symptoms: str
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None


class RecommendationRequest(BaseModel):
    specialties: List[str]
    urgency_level: str = "NON_URGENT"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_distance_km: float = 100.0
    min_trust_score: float = 0.0
    require_emergency: bool = False
    require_icu: bool = False
    require_maternity: bool = False


@router.post("/assess")
async def assess_symptoms(request: TriageRequest):
    """
    Assess patient symptoms and provide triage classification.
    
    Returns:
    - Classified specialties with confidence scores
    - Urgency level assessment
    - Recommendations for care
    - Red flags if any
    """
    from server.triage_engine import triage
    
    result = triage(
        text=request.symptoms,
        patient_age=request.patient_age,
        patient_gender=request.patient_gender
    )
    
    return {
        "status": "success",
        "data": result
    }


@router.post("/recommend")
async def recommend_hospitals(request: RecommendationRequest):
    """
    Recommend hospitals based on specialty requirements and location.
    
    Returns ranked list of facilities with composite scores.
    """
    from server.recommendation_engine import recommend_hospitals, RecommendationCriteria
    from server.data_loader import get_facilities_df, get_district_health_df
    
    # Load facilities from fast cache
    from server.data_loader import get_facilities_list, get_district_health_dict
    facilities = get_facilities_list()
    if not facilities:
        raise HTTPException(status_code=404, detail="No facilities data available")
    
    # Load district health data from fast cache
    district_health_data = get_district_health_dict()
    
    # Create criteria
    criteria = RecommendationCriteria(
        specialties=request.specialties,
        urgency_level=request.urgency_level,
        latitude=request.latitude,
        longitude=request.longitude,
        max_distance_km=request.max_distance_km,
        min_trust_score=request.min_trust_score,
        require_emergency=request.require_emergency,
        require_icu=request.require_icu,
        require_maternity=request.require_maternity
    )
    
    # Get recommendations
    recommendations = recommend_hospitals(
        facilities=facilities,
        criteria=criteria,
        district_health_data=district_health_data,
        top_n=10
    )
    
    return {
        "status": "success",
        "count": len(recommendations),
        "data": recommendations
    }


@router.get("/specialties")
async def get_specialties():
    """Get list of supported medical specialties."""
    from server.triage_engine import SYMPTOM_SPECIALTY_MAP, get_specialty_capabilities
    
    # Get unique specialties
    all_specialties = set()
    for specialties in SYMPTOM_SPECIALTY_MAP.values():
        all_specialties.update(specialties.keys())
    
    capabilities = get_specialty_capabilities()
    
    return {
        "status": "success",
        "data": {
            "specialties": sorted(list(all_specialties)),
            "capability_mapping": capabilities
        }
    }


@router.get("/urgency-levels")
async def get_urgency_levels():
    """Get available urgency levels and their criteria."""
    from server.triage_engine import URGENCY_LEVELS
    
    return {
        "status": "success",
        "data": URGENCY_LEVELS
    }