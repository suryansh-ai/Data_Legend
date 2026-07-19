"""
Outcome Tracking — Patient outcome recording and learning loop.

Tracks treatment outcomes, patient satisfaction, and provides feedback
for improving facility trust scores and recommendations.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
from enum import Enum


class OutcomeType(Enum):
    TREATMENT = "treatment"
    DIAGNOSIS = "diagnosis"
    PROCEDURE = "procedure"
    EMERGENCY = "emergency"
    FOLLOW_UP = "follow_up"


class SatisfactionLevel(Enum):
    VERY_SATISFIED = 5
    SATISFIED = 4
    NEUTRAL = 3
    DISSATISFIED = 2
    VERY_DISSATISFIED = 1


@dataclass
class PatientOutcome:
    id: str
    facility_id: str
    facility_name: str
    patient_id: str  # Anonymous patient identifier
    appointment_id: Optional[str]
    outcome_type: str
    specialty: str
    treatment_date: str
    diagnosis: Optional[str]
    treatment_provided: Optional[str]
    outcome_status: str  # improved, stable, worsened, complications
    satisfaction_score: int
    follow_up_required: bool
    follow_up_date: Optional[str]
    notes: Optional[str]
    created_at: str
    updated_at: str
    would_recommend: bool = True
    recovery_days: Optional[int] = None
    cost_incurred: Optional[float] = None
    insurance_claim: bool = False


class OutcomeTracker:
    def __init__(self):
        self.outcomes: Dict[str, PatientOutcome] = {}
        self._load_persistence()
    
    def _load_persistence(self):
        """Load outcomes from persistence layer."""
        try:
            from server.lakebase import db
            # Load from database if available
            pass
        except:
            pass
    
    def _save_persistence(self, outcome: PatientOutcome):
        """Save outcome to persistence layer."""
        try:
            from server.lakebase import db
            # Save to database if available
            pass
        except:
            pass
    
    def record_outcome(
        self,
        facility_id: str,
        facility_name: str,
        patient_id: str,
        outcome_type: str,
        specialty: str,
        treatment_date: str,
        diagnosis: Optional[str] = None,
        treatment_provided: Optional[str] = None,
        outcome_status: str = "stable",
        satisfaction_score: int = 3,
        follow_up_required: bool = False,
        follow_up_date: Optional[str] = None,
        notes: Optional[str] = None,
        appointment_id: Optional[str] = None,
        would_recommend: bool = True,
        recovery_days: Optional[int] = None,
        cost_incurred: Optional[float] = None,
        insurance_claim: bool = False
    ) -> PatientOutcome:
        """Record a patient outcome."""
        outcome_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        outcome = PatientOutcome(
            id=outcome_id,
            facility_id=facility_id,
            facility_name=facility_name,
            patient_id=patient_id,
            appointment_id=appointment_id,
            outcome_type=outcome_type,
            specialty=specialty,
            treatment_date=treatment_date,
            diagnosis=diagnosis,
            treatment_provided=treatment_provided,
            outcome_status=outcome_status,
            satisfaction_score=satisfaction_score,
            follow_up_required=follow_up_required,
            follow_up_date=follow_up_date,
            notes=notes,
            created_at=now,
            updated_at=now,
            would_recommend=would_recommend,
            recovery_days=recovery_days,
            cost_incurred=cost_incurred,
            insurance_claim=insurance_claim
        )
        
        self.outcomes[outcome_id] = outcome
        self._save_persistence(outcome)
        
        return outcome
    
    def get_outcome(self, outcome_id: str) -> Optional[PatientOutcome]:
        """Get outcome by ID."""
        return self.outcomes.get(outcome_id)
    
    def get_outcomes_by_facility(self, facility_id: str) -> List[PatientOutcome]:
        """Get all outcomes for a facility."""
        return [out for out in self.outcomes.values() if out.facility_id == facility_id]
    
    def get_outcomes_by_patient(self, patient_id: str) -> List[PatientOutcome]:
        """Get all outcomes for a patient."""
        return [out for out in self.outcomes.values() if out.patient_id == patient_id]
    
    def get_facility_outcome_summary(self, facility_id: str) -> Dict:
        """Get outcome summary for a facility."""
        outcomes = self.get_outcomes_by_facility(facility_id)
        
        if not outcomes:
            return {
                "facility_id": facility_id,
                "total_outcomes": 0,
                "average_satisfaction": 0,
                "recommendation_rate": 0,
                "outcome_distribution": {},
                "specialty_breakdown": {},
            }
        
        total = len(outcomes)
        avg_satisfaction = sum(out.satisfaction_score for out in outcomes) / total
        recommend_count = sum(1 for out in outcomes if out.would_recommend)
        
        # Outcome status distribution
        outcome_dist = {}
        for out in outcomes:
            outcome_dist[out.outcome_status] = outcome_dist.get(out.outcome_status, 0) + 1
        
        # Specialty breakdown
        specialty_breakdown = {}
        for out in outcomes:
            if out.specialty not in specialty_breakdown:
                specialty_breakdown[out.specialty] = {
                    "count": 0,
                    "avg_satisfaction": 0,
                    "recommendation_rate": 0,
                }
            specialty_breakdown[out.specialty]["count"] += 1
            specialty_breakdown[out.specialty]["avg_satisfaction"] += out.satisfaction_score
            if out.would_recommend:
                specialty_breakdown[out.specialty]["recommendation_rate"] += 1
        
        # Calculate averages
        for spec in specialty_breakdown:
            count = specialty_breakdown[spec]["count"]
            specialty_breakdown[spec]["avg_satisfaction"] = round(
                specialty_breakdown[spec]["avg_satisfaction"] / count, 2
            )
            specialty_breakdown[spec]["recommendation_rate"] = round(
                specialty_breakdown[spec]["recommendation_rate"] / count * 100, 1
            )
        
        return {
            "facility_id": facility_id,
            "total_outcomes": total,
            "average_satisfaction": round(avg_satisfaction, 2),
            "recommendation_rate": round(recommend_count / total * 100, 1),
            "outcome_distribution": outcome_dist,
            "specialty_breakdown": specialty_breakdown,
            "follow_up_required": sum(1 for out in outcomes if out.follow_up_required),
            "average_recovery_days": round(
                sum(out.recovery_days for out in outcomes if out.recovery_days) / 
                max(1, sum(1 for out in outcomes if out.recovery_days)), 1
            ),
        }
    
    def calculate_trust_impact(self, facility_id: str) -> Dict:
        """Calculate how outcomes should impact trust scores."""
        outcomes = self.get_outcomes_by_facility(facility_id)
        
        if not outcomes:
            return {
                "facility_id": facility_id,
                "trust_adjustment": 0,
                "confidence": 0,
                "factors": [],
            }
        
        total = len(outcomes)
        
        # Calculate factors
        factors = []
        
        # 1. Satisfaction factor
        avg_satisfaction = sum(out.satisfaction_score for out in outcomes) / total
        satisfaction_factor = (avg_satisfaction - 3) / 2  # Normalize to -1 to 1
        factors.append({
            "name": "patient_satisfaction",
            "value": round(satisfaction_factor, 3),
            "weight": 0.3,
            "description": f"Average satisfaction: {avg_satisfaction:.1f}/5"
        })
        
        # 2. Outcome status factor
        positive_outcomes = sum(1 for out in outcomes if out.outcome_status in ["improved", "stable"])
        outcome_factor = (positive_outcomes / total) * 2 - 1  # Normalize to -1 to 1
        factors.append({
            "name": "outcome_quality",
            "value": round(outcome_factor, 3),
            "weight": 0.4,
            "description": f"{positive_outcomes}/{total} positive outcomes"
        })
        
        # 3. Recommendation factor
        recommend_rate = sum(1 for out in outcomes if out.would_recommend) / total
        recommendation_factor = recommend_rate * 2 - 1  # Normalize to -1 to 1
        factors.append({
            "name": "recommendation_rate",
            "value": round(recommendation_factor, 3),
            "weight": 0.3,
            "description": f"{recommend_rate*100:.0f}% would recommend"
        })
        
        # Calculate weighted adjustment
        trust_adjustment = sum(f["value"] * f["weight"] for f in factors)
        
        # Confidence based on sample size
        confidence = min(1.0, total / 10)  # Full confidence at 10+ outcomes
        
        return {
            "facility_id": facility_id,
            "trust_adjustment": round(trust_adjustment * 10, 1),  # Scale to -10 to +10
            "confidence": round(confidence, 2),
            "factors": factors,
            "sample_size": total,
        }
    
    def get_learning_insights(self) -> Dict:
        """Get insights from all outcomes for learning."""
        all_outcomes = list(self.outcomes.values())
        
        if not all_outcomes:
            return {
                "total_outcomes": 0,
                "insights": [],
                "trends": {},
            }
        
        # Calculate insights
        insights = []
        
        # 1. Overall satisfaction trend
        avg_satisfaction = sum(out.satisfaction_score for out in all_outcomes) / len(all_outcomes)
        insights.append({
            "type": "satisfaction",
            "value": round(avg_satisfaction, 2),
            "description": f"Overall average satisfaction: {avg_satisfaction:.1f}/5",
            "trend": "positive" if avg_satisfaction > 3.5 else "negative" if avg_satisfaction < 2.5 else "neutral"
        })
        
        # 2. Recommendation rate
        recommend_rate = sum(1 for out in all_outcomes if out.would_recommend) / len(all_outcomes)
        insights.append({
            "type": "recommendation",
            "value": round(recommend_rate * 100, 1),
            "description": f"{recommend_rate*100:.0f}% of patients would recommend",
            "trend": "positive" if recommend_rate > 0.7 else "negative" if recommend_rate < 0.5 else "neutral"
        })
        
        # 3. Outcome improvement rate
        improved = sum(1 for out in all_outcomes if out.outcome_status == "improved")
        improvement_rate = improved / len(all_outcomes)
        insights.append({
            "type": "improvement",
            "value": round(improvement_rate * 100, 1),
            "description": f"{improvement_rate*100:.0f}% of patients improved",
            "trend": "positive" if improvement_rate > 0.6 else "negative" if improvement_rate < 0.4 else "neutral"
        })
        
        # 4. Complication rate
        complications = sum(1 for out in all_outcomes if out.outcome_status == "complications")
        complication_rate = complications / len(all_outcomes)
        insights.append({
            "type": "complications",
            "value": round(complication_rate * 100, 1),
            "description": f"{complication_rate*100:.0f}% had complications",
            "trend": "negative" if complication_rate > 0.1 else "positive"
        })
        
        # Trends by specialty
        specialty_trends = {}
        for out in all_outcomes:
            if out.specialty not in specialty_trends:
                specialty_trends[out.specialty] = {
                    "count": 0,
                    "total_satisfaction": 0,
                    "improved_count": 0,
                }
            specialty_trends[out.specialty]["count"] += 1
            specialty_trends[out.specialty]["total_satisfaction"] += out.satisfaction_score
            if out.outcome_status == "improved":
                specialty_trends[out.specialty]["improved_count"] += 1
        
        # Calculate specialty trends
        for spec in specialty_trends:
            count = specialty_trends[spec]["count"]
            specialty_trends[spec]["avg_satisfaction"] = round(
                specialty_trends[spec]["total_satisfaction"] / count, 2
            )
            specialty_trends[spec]["improvement_rate"] = round(
                specialty_trends[spec]["improved_count"] / count * 100, 1
            )
            del specialty_trends[spec]["total_satisfaction"]
            del specialty_trends[spec]["improved_count"]
        
        return {
            "total_outcomes": len(all_outcomes),
            "insights": insights,
            "trends": specialty_trends,
        }


# Global outcome tracker instance
outcome_tracker = OutcomeTracker()