"""
Hospital Recommendation Engine — Composite scoring for facility matching.

Combines trust scores, distance, capability matching, and district health data
to recommend the best facilities for patient needs.
"""

import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class RecommendationCriteria:
    """Criteria for hospital recommendation."""
    specialties: List[str]
    urgency_level: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_distance_km: float = 100.0
    min_trust_score: float = 0.0
    require_emergency: bool = False
    require_icu: bool = False
    require_maternity: bool = False


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in kilometers."""
    R = 6371.0  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def calculate_capability_match(facility_capabilities: List[str], required_specialties: List[str]) -> float:
    """Calculate how well facility capabilities match required specialties."""
    if not required_specialties:
        return 0.5  # Neutral if no specific requirements
    
    # Map specialties to capabilities
    from server.triage_engine import get_specialty_capabilities
    specialty_caps = get_specialty_capabilities()
    
    required_capabilities = set()
    for specialty in required_specialties:
        if specialty in specialty_caps:
            required_capabilities.update(specialty_caps[specialty])
    
    if not required_capabilities:
        return 0.5
    
    # Parse facility capabilities
    facility_caps = set()
    for cap in facility_capabilities:
        if isinstance(cap, str):
            facility_caps.add(cap.lower())
        elif isinstance(cap, list):
            facility_caps.update([c.lower() for c in cap])
    
    # Calculate match score
    matched = required_capabilities.intersection(facility_caps)
    if not required_capabilities:
        return 0.5
    
    return len(matched) / len(required_capabilities)


def calculate_urgency_bonus(urgency_level: str, facility_has_emergency: bool, facility_has_icu: bool) -> float:
    """Calculate bonus score based on urgency and facility capabilities."""
    urgency_scores = {
        "EMERGENT": 1.0,
        "URGENT": 0.8,
        "SEMI_URGENT": 0.6,
        "NON_URGENT": 0.4,
        "ROUTINE": 0.2,
    }
    
    base_bonus = urgency_scores.get(urgency_level, 0.3)
    
    # Additional bonus for emergency facilities when needed
    if urgency_level in ["EMERGENT", "URGENT"]:
        if facility_has_emergency:
            base_bonus += 0.2
        if facility_has_icu:
            base_bonus += 0.1
    
    return min(1.0, base_bonus)


def calculate_capacity_score(capacity, number_doctors) -> float:
    """Calculate capacity score based on facility size."""
    if capacity is None and number_doctors is None:
        return 0.5
    
    # Convert to numbers safely
    try:
        cap_num = float(capacity) if capacity else 0
    except (ValueError, TypeError):
        cap_num = 0
    
    try:
        doc_num = float(number_doctors) if number_doctors else 0
    except (ValueError, TypeError):
        doc_num = 0
    
    # Normalize capacity (assuming max 500 beds)
    capacity_score = min(1.0, cap_num / 500) if cap_num > 0 else 0
    
    # Normalize doctors (assuming max 100 doctors)
    doctor_score = min(1.0, doc_num / 100) if doc_num > 0 else 0
    
    # Weighted average
    return 0.6 * capacity_score + 0.4 * doctor_score


def calculate_trust_score(trust_score: float) -> float:
    """Normalize trust score to 0-1 range."""
    return min(1.0, max(0.0, trust_score / 100))


def calculate_distance_score(distance_km: float, max_distance: float) -> float:
    """Calculate distance score (closer is better)."""
    if distance_km > max_distance:
        return 0.0
    
    # Exponential decay: closer facilities get higher scores
    return math.exp(-distance_km / (max_distance / 2))


def calculate_district_health_bonus(district_data: Dict) -> float:
    """Calculate bonus based on district health indicators."""
    if not district_data:
        return 0.0
    
    # Higher institutional births percentage indicates better healthcare
    institutional_births = district_data.get("institutional_births_pct", 50) or 50
    
    # Higher ANC visits indicate better prenatal care
    anc_visits = district_data.get("anc_4plus_visits_pct", 50) or 50
    
    # Higher electricity percentage indicates better infrastructure
    electricity = district_data.get("electricity_pct", 50) or 50
    
    # Calculate bonus (0-0.2 range)
    bonus = 0.0
    if institutional_births > 70:
        bonus += 0.1
    if anc_visits > 60:
        bonus += 0.05
    if electricity > 80:
        bonus += 0.05
    
    return min(0.2, bonus)


def recommend_hospitals(
    facilities: List[Dict],
    criteria: RecommendationCriteria,
    district_health_data: Dict[str, Dict] = None,
    top_n: int = 10
) -> List[Dict]:
    """
    Recommend hospitals based on composite scoring.
    
    Args:
        facilities: List of facility dictionaries
        criteria: Recommendation criteria
        district_health_data: District health indicators
        top_n: Number of recommendations to return
    
    Returns:
        List of recommended facilities with scores
    """
    recommendations = []
    
    for facility in facilities:
        # Skip facilities without coordinates if location is required
        if criteria.latitude and criteria.longitude:
            fac_lat = facility.get("latitude")
            fac_lng = facility.get("longitude")
            if fac_lat is None or fac_lng is None:
                continue
            
            # Calculate distance
            distance = haversine_distance(
                criteria.latitude, criteria.longitude,
                fac_lat, fac_lng
            )
            
            # Skip if too far
            if distance > criteria.max_distance_km:
                continue
        else:
            distance = None
        
        # Get facility data
        trust_score = facility.get("_trust_score", 0) or 0
        capabilities = facility.get("capability", [])
        if isinstance(capabilities, str):
            try:
                import json
                capabilities = json.loads(capabilities)
            except:
                capabilities = [capabilities]
        
        has_emergency = any("emergency" in str(cap).lower() for cap in capabilities)
        has_icu = any("icu" in str(cap).lower() for cap in capabilities)
        has_maternity = any("maternity" in str(cap).lower() for cap in capabilities)
        
        # Check minimum trust score
        if trust_score < criteria.min_trust_score:
            continue
        
        # Check emergency/ICU/maternity requirements
        if criteria.require_emergency and not has_emergency:
            continue
        if criteria.require_icu and not has_icu:
            continue
        if criteria.require_maternity and not has_maternity:
            continue
        
        # Calculate composite score
        trust_norm = calculate_trust_score(trust_score)
        capability_match = calculate_capability_match(capabilities, criteria.specialties)
        urgency_bonus = calculate_urgency_bonus(criteria.urgency_level, has_emergency, has_icu)
        capacity_score = calculate_capacity_score(
            facility.get("capacity"),
            facility.get("numberDoctors")
        )
        
        # Distance score
        if distance is not None:
            distance_score = calculate_distance_score(distance, criteria.max_distance_km)
        else:
            distance_score = 0.5  # Neutral if no location
        
        # District health bonus
        district_name = facility.get("district") or facility.get("city", "")
        district_bonus = 0.0
        if district_health_data and district_name in district_health_data:
            district_bonus = calculate_district_health_bonus(district_health_data[district_name])
        
        # Composite score with weights
        composite_score = (
            0.35 * trust_norm +           # Trust is most important
            0.25 * capability_match +     # Capability match
            0.15 * urgency_bonus +        # Urgency consideration
            0.10 * distance_score +       # Proximity
            0.10 * capacity_score +       # Capacity
            0.05 * district_bonus         # District health
        )
        
        # Build recommendation
        recommendation = {
            "facility_id": facility.get("unique_id"),
            "name": facility.get("name"),
            "city": facility.get("city") or facility.get("address_city"),
            "state": facility.get("state") or facility.get("address_stateOrRegion"),
            "latitude": facility.get("latitude"),
            "longitude": facility.get("longitude"),
            "trust_score": trust_score,
            "trust_signal": facility.get("_trust_signal"),
            "capabilities": capabilities,
            "distance_km": round(distance, 1) if distance else None,
            "composite_score": round(composite_score * 100, 1),
            "score_breakdown": {
                "trust": round(trust_norm * 100, 1),
                "capability_match": round(capability_match * 100, 1),
                "urgency": round(urgency_bonus * 100, 1),
                "proximity": round(distance_score * 100, 1),
                "capacity": round(capacity_score * 100, 1),
                "district_health": round(district_bonus * 100, 1),
            },
            "specialties_matched": [
                spec for spec in criteria.specialties
                if any(spec in str(cap).lower() for cap in capabilities)
            ],
            "has_emergency": has_emergency,
            "has_icu": has_icu,
            "has_maternity": has_maternity,
            "number_doctors": facility.get("numberDoctors"),
            "capacity": facility.get("capacity"),
            "description": facility.get("description"),
        }
        
        recommendations.append(recommendation)
    
    # Sort by composite score
    recommendations.sort(key=lambda x: x["composite_score"], reverse=True)
    
    # Return top N
    return recommendations[:top_n]


def get_recommendation_explanation(recommendation: Dict) -> str:
    """Generate human-readable explanation for a recommendation."""
    parts = []
    
    # Trust explanation
    trust = recommendation["trust_score"]
    signal = recommendation["trust_signal"]
    if trust >= 70:
        parts.append(f"High trust score ({trust}/100, {signal})")
    elif trust >= 40:
        parts.append(f"Moderate trust score ({trust}/100, {signal})")
    else:
        parts.append(f"Low trust score ({trust}/100, {signal})")
    
    # Capability match
    matched = recommendation["specialties_matched"]
    if matched:
        parts.append(f"Matches required specialties: {', '.join(matched)}")
    
    # Distance
    dist = recommendation["distance_km"]
    if dist is not None:
        if dist < 5:
            parts.append(f"Very close ({dist} km)")
        elif dist < 20:
            parts.append(f"Nearby ({dist} km)")
        else:
            parts.append(f"Within distance ({dist} km)")
    
    # Special capabilities
    caps = []
    if recommendation["has_emergency"]:
        caps.append("emergency")
    if recommendation["has_icu"]:
        caps.append("ICU")
    if recommendation["has_maternity"]:
        caps.append("maternity")
    if caps:
        parts.append(f"Has {', '.join(caps)} services")
    
    return ". ".join(parts) + "."