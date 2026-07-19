"""
AI Routes — LLM-powered features endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/ai", tags=["ai"])


class ChatRequest(BaseModel):
    messages: List[dict]
    model: str = "llama-3.3-70b"
    temperature: float = 0.7
    max_tokens: int = 1024


class TriageAIRequest(BaseModel):
    symptoms: str
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None


class ExplainRequest(BaseModel):
    facility_name: str
    trust_score: float
    capabilities: List[str]
    patient_needs: str


class AnalyzeFacilityRequest(BaseModel):
    facility_data: dict


class HealthInsightsRequest(BaseModel):
    region_data: dict
    facility_data: List[dict]


@router.post("/chat")
async def chat_completion(request: ChatRequest):
    """Get chat completion from Databricks Foundation Model."""
    from server.ai_service import ai_service, AIMessage
    
    if not ai_service.available:
        raise HTTPException(
            status_code=503,
            detail="AI service not available. Databricks credentials not configured."
        )
    
    messages = [AIMessage(role=msg["role"], content=msg["content"]) for msg in request.messages]
    
    response = ai_service.chat_completion(
        messages=messages,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    
    if response is None:
        raise HTTPException(status_code=500, detail="Failed to get AI response")
    
    return {
        "status": "success",
        "data": {
            "response": response,
            "model": request.model,
        }
    }


@router.post("/triage")
async def ai_triage(request: TriageAIRequest):
    """AI-powered triage assessment."""
    from server.ai_service import ai_service
    
    if not ai_service.available:
        # Fall back to rule-based triage
        from server.triage_engine import triage
        result = triage(
            text=request.symptoms,
            patient_age=request.patient_age,
            patient_gender=request.patient_gender
        )
        return {
            "status": "success",
            "data": result,
            "source": "rule_based"
        }
    
    result = ai_service.triage_assessment(
        symptoms=request.symptoms,
        patient_age=request.patient_age,
        patient_gender=request.patient_gender
    )
    
    if result is None:
        # Fall back to rule-based triage
        from server.triage_engine import triage
        result = triage(
            text=request.symptoms,
            patient_age=request.patient_age,
            patient_gender=request.patient_gender
        )
        return {
            "status": "success",
            "data": result,
            "source": "rule_based"
        }
    
    return {
        "status": "success",
        "data": result,
        "source": "llm"
    }


@router.post("/explain")
async def explain_recommendation(request: ExplainRequest):
    """Generate AI explanation for hospital recommendation."""
    from server.ai_service import ai_service
    
    if not ai_service.available:
        raise HTTPException(
            status_code=503,
            detail="AI service not available. Databricks credentials not configured."
        )
    
    explanation = ai_service.explain_recommendation(
        facility_name=request.facility_name,
        trust_score=request.trust_score,
        capabilities=request.capabilities,
        patient_needs=request.patient_needs
    )
    
    if explanation is None:
        raise HTTPException(status_code=500, detail="Failed to generate explanation")
    
    return {
        "status": "success",
        "data": {
            "explanation": explanation,
        }
    }


@router.post("/analyze-facility")
async def analyze_facility(request: AnalyzeFacilityRequest):
    """AI-powered facility quality analysis."""
    from server.ai_service import ai_service
    
    if not ai_service.available:
        raise HTTPException(
            status_code=503,
            detail="AI service not available. Databricks credentials not configured."
        )
    
    analysis = ai_service.analyze_facility_quality(request.facility_data)
    
    if analysis is None:
        raise HTTPException(status_code=500, detail="Failed to analyze facility")
    
    return {
        "status": "success",
        "data": analysis
    }


@router.post("/health-insights")
async def health_insights(request: HealthInsightsRequest):
    """Generate AI health insights for a region."""
    from server.ai_service import ai_service
    
    if not ai_service.available:
        raise HTTPException(
            status_code=503,
            detail="AI service not available. Databricks credentials not configured."
        )
    
    insights = ai_service.generate_health_insights(
        region_data=request.region_data,
        facility_data=request.facility_data
    )
    
    if insights is None:
        raise HTTPException(status_code=500, detail="Failed to generate insights")
    
    return {
        "status": "success",
        "data": insights
    }


@router.get("/models")
async def get_available_models():
    """Get list of available AI models."""
    from server.ai_service import AVAILABLE_MODELS, ai_service
    
    return {
        "status": "success",
        "data": {
            "available": ai_service.available,
            "models": AVAILABLE_MODELS,
        }
    }