"""
NGO Dashboard Routes — District health gap analysis and resource mapping.
"""

import json
import re
from typing import List, Optional, Dict, Iterable

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/ngo", tags=["ngo"])


def _parse_specialty_values(value) -> List[str]:
    """Normalize specialty values from JSON arrays, Python lists, or comma-separated strings."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []

    if isinstance(value, str):
        raw_value = value.strip()
        if not raw_value:
            return []
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError:
            parsed = raw_value

        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
        if isinstance(parsed, str):
            if "," in parsed:
                return [part.strip() for part in parsed.split(",") if part.strip()]
            return [parsed.strip()]
        return [str(parsed).strip()]

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    return [str(value).strip()]


def _build_specialty_counts(specialty_values: Iterable[object]) -> Dict[str, int]:
    """Count each specialty once per facility to avoid double counting duplicates."""
    counts: Dict[str, int] = {}
    for value in specialty_values:
        facility_specs = set(_parse_specialty_values(value))
        for specialty in facility_specs:
            specialty_name = specialty.strip()
            if specialty_name:
                counts[specialty_name] = counts.get(specialty_name, 0) + 1
    return counts


def _format_specialty_name(name: str) -> str:
    """Format specialty identifiers into readable labels for the UI."""
    mappings = {
        "gynecologyAndObstetrics": "Gynecology & Obstetrics",
        "reproductiveEndocrinologyAndInfertility": "Reproductive Endocrinology & Infertility",
        "endocrinologyAndDiabetesAndMetabolism": "Endocrinology & Diabetes",
        "oralAndMaxillofacialSurgery": "Oral & Maxillofacial Surgery",
        "icu": "ICU",
        "emergencyMedicine": "Emergency Medicine",
        "criticalCareMedicine": "Critical Care Medicine",
        "maternalFetalMedicineOrPerinatology": "Maternal-Fetal Medicine",
    }
    if name in mappings:
        return mappings[name]

    cleaned = str(name).strip()
    if not cleaned:
        return ""

    res = re.sub(r'(?<!^)(?=[A-Z])', ' ', cleaned)
    return res.title().replace('And', '&')


def _check_facility_has_capability(row, cap: str) -> bool:
    """Check whether a facility row appears to have a capability via specialties, capability field, or description."""
    cap_lower = cap.lower()

    spec_keywords = {
        "emergency": ["emergency", "criticalcare", "trauma"],
        "maternity": ["obstetrics", "gynecology", "maternity", "reproductive", "maternal"],
        "surgery": ["surgery"],
        "icu": ["criticalcare", "icu"],
        "pharmacy": ["pharmacy"],
        "laboratory": ["pathology", "laboratory"],
        "radiology": ["radiology", "imaging"],
        "pediatrics": ["pediatrics"],
    }

    # 1. Check specialties first using normalized keyword matching.
    specs = row.get("specialties")
    if pd.notna(specs):
        parsed_specs = _parse_specialty_values(specs)
        keywords = spec_keywords.get(cap_lower, [cap_lower])
        if any(any(kw in specialty.lower() for kw in keywords) for specialty in parsed_specs):
            return True

    # 2. Check capability field using normalized substring matching.
    caps = row.get("capability")
    if pd.notna(caps):
        parsed_caps = _parse_specialty_values(caps)
        if any(cap_lower in str(c).lower() for c in parsed_caps):
            return True

    # 3. Check description fallback with keyword-aware matching.
    desc = row.get("description")
    if pd.notna(desc) and isinstance(desc, str):
        desc_lower = desc.lower()
        if any(keyword in desc_lower for keyword in spec_keywords.get(cap_lower, [cap_lower])):
            return True
        if cap_lower in desc_lower:
            return True

    return False


class GapAnalysisRequest(BaseModel):
    state: Optional[str] = None
    district: Optional[str] = None
    capability: Optional[str] = None
    min_facilities: int = 0
    max_distance_km: float = 50.0


_ngo_dashboard_cache = None
_resource_gaps_cache = {}
_intervention_plan_cache = {}

@router.get("/dashboard")
async def get_ngo_dashboard():
    """Get NGO dashboard overview with key metrics."""
    global _ngo_dashboard_cache
    if _ngo_dashboard_cache is not None:
        return _ngo_dashboard_cache
        
    from server.data_loader import get_facilities_df, get_district_health_df
    
    facilities_df = get_facilities_df()
    district_df = get_district_health_df()
    
    if facilities_df.empty:
        raise HTTPException(status_code=404, detail="No facilities data available")
    
    # Calculate key metrics
    total_facilities = len(facilities_df)
    total_districts = len(district_df) if not district_df.empty else 0
    
    # State coverage analysis
    state_col = "state" if "state" in facilities_df.columns else "address_stateOrRegion"
    if state_col in facilities_df.columns:
        state_stats = facilities_df.groupby(state_col).agg(
            total=("unique_id", "count"),
            avg_trust=("_trust_score", "mean"),
            low_trust=("_trust_score", lambda x: (x < 30).sum()),
        ).to_dict('index')
    else:
        state_stats = {}
    
    # District health summary
    district_summary = {}
    if not district_df.empty:
        district_summary = {
            "total_districts": len(district_df),
            "avg_institutional_births": round(district_df["institutional_births_pct"].mean(), 1) if "institutional_births_pct" in district_df.columns else 0,
            "avg_anc_visits": round(district_df["anc_4plus_visits_pct"].mean(), 1) if "anc_4plus_visits_pct" in district_df.columns else 0,
            "avg_health_insurance": round(district_df["health_insurance_pct"].mean(), 1) if "health_insurance_pct" in district_df.columns else 0,
            "avg_electricity": round(district_df["electricity_pct"].mean(), 1) if "electricity_pct" in district_df.columns else 0,
        }
    
    # Capability gaps (analyzing specialties)
    capability_gaps = {}
    if "specialties" in facilities_df.columns:
        spec_counts = _build_specialty_counts(facilities_df["specialties"].dropna())

        # Group by formatted name to avoid collisions (e.g. ophthalmology and Ophthalmology)
        formatted_counts = {}
        for spec, count in spec_counts.items():
            pretty_name = _format_specialty_name(spec)
            formatted_counts[pretty_name] = formatted_counts.get(pretty_name, 0) + count

        # Gaps are specialties with lower coverage (< 30%)
        for pretty_name, count in formatted_counts.items():
            coverage_pct = (count / total_facilities * 100) if total_facilities > 0 else 0
            if coverage_pct < 30:
                capability_gaps[pretty_name] = {
                    "count": count,
                    "coverage_pct": round(coverage_pct, 1),
                    "status": "critical" if coverage_pct < 18 else "low"
                }
    
    _ngo_dashboard_cache = {
        "status": "success",
        "data": {
            "overview": {
                "total_facilities": total_facilities,
                "total_districts": total_districts,
                "states_covered": len(state_stats),
            },
            "state_stats": state_stats,
            "district_summary": district_summary,
            "capability_gaps": capability_gaps,
        }
    }
    return _ngo_dashboard_cache


@router.post("/gap-analysis")
async def analyze_gaps(request: GapAnalysisRequest):
    """Analyze healthcare gaps in a specific region."""
    from server.data_loader import get_facilities_df, get_district_health_df
    import json
    
    facilities_df = get_facilities_df()
    district_df = get_district_health_df()
    
    if facilities_df.empty:
        raise HTTPException(status_code=404, detail="No facilities data available")
    
    # Filter by state if provided
    state_col = "state" if "state" in facilities_df.columns else "address_stateOrRegion"
    if request.state and state_col in facilities_df.columns:
        facilities_df = facilities_df[facilities_df[state_col] == request.state]
    
    # Filter by district if provided
    city_col = "city" if "city" in facilities_df.columns else "address_city"
    if request.district and city_col in facilities_df.columns:
        facilities_df = facilities_df[facilities_df[city_col] == request.district]
    
    # Analyze specialties
    capability_analysis = {}
    if "specialties" in facilities_df.columns:
        spec_counts = _build_specialty_counts(facilities_df["specialties"].dropna())

        total_facilities = len(facilities_df)
        for spec, count in spec_counts.items():
            coverage_pct = (count / total_facilities * 100) if total_facilities > 0 else 0
            pretty_name = _format_specialty_name(spec)
            capability_analysis[pretty_name] = {
                "count": count,
                "coverage_pct": round(coverage_pct, 1),
                "facilities_with_cap": count,
            }
    
    # District health data for region
    district_health = {}
    if not district_df.empty:
        if request.district:
            district_data = district_df[district_df["district"] == request.district]
            if not district_data.empty:
                district_health = district_data.iloc[0].to_dict()
        elif request.state:
            state_data = district_df[district_df["state"] == request.state]
            if not state_data.empty:
                district_health = {
                    "districts_in_state": len(state_data),
                    "avg_institutional_births": round(state_data["institutional_births_pct"].mean(), 1) if "institutional_births_pct" in state_data.columns else 0,
                    "avg_anc_visits": round(state_data["anc_4plus_visits_pct"].mean(), 1) if "anc_4plus_visits_pct" in state_data.columns else 0,
                }
    
    # Trust analysis
    trust_analysis = {}
    if "_trust_score" in facilities_df.columns:
        trust_scores = facilities_df["_trust_score"].dropna()
        if not trust_scores.empty:
            trust_analysis = {
                "avg_trust": round(trust_scores.mean(), 1),
                "min_trust": round(trust_scores.min(), 1),
                "max_trust": round(trust_scores.max(), 1),
                "low_trust_count": int((trust_scores < 30).sum()),
                "high_trust_count": int((trust_scores >= 70).sum()),
            }
    
    return {
        "status": "success",
        "data": {
            "region": {
                "state": request.state,
                "district": request.district,
                "total_facilities": len(facilities_df),
            },
            "capability_analysis": capability_analysis,
            "district_health": district_health,
            "trust_analysis": trust_analysis,
        }
    }


@router.get("/resource-gaps")
async def get_resource_gaps(state: Optional[str] = None):
    """Get resource gaps analysis for a state or nationwide."""
    global _resource_gaps_cache
    cache_key = state or "nationwide"
    if cache_key in _resource_gaps_cache:
        return _resource_gaps_cache[cache_key]

    from server.data_loader import get_facilities_df, get_district_health_df
    import json
    
    facilities_df = get_facilities_df()
    district_df = get_district_health_df()
    
    if facilities_df.empty:
        raise HTTPException(status_code=404, detail="No facilities data available")
    
    # Filter by state if provided
    state_col = "state" if "state" in facilities_df.columns else "address_stateOrRegion"
    if state and state_col in facilities_df.columns:
        facilities_df = facilities_df[facilities_df[state_col] == state]
    
    # Essential capabilities that should be available
    essential_capabilities = [
        "emergency", "maternity", "surgery", "icu", "pharmacy",
        "laboratory", "radiology", "pediatrics"
    ]
    
    # Analyze each capability
    resource_gaps = {}
    total_facilities = len(facilities_df)
    
    import pandas as pd
    for cap in essential_capabilities:
        # Count facilities with this capability
        facilities_with_cap = 0
        for _, row in facilities_df.iterrows():
            if _check_facility_has_capability(row, cap):
                facilities_with_cap += 1
        
        coverage_pct = (facilities_with_cap / total_facilities * 100) if total_facilities > 0 else 0
        
        # Determine gap severity
        if coverage_pct < 15:
            severity = "critical"
        elif coverage_pct < 30:
            severity = "high"
        elif coverage_pct < 50:
            severity = "medium"
        else:
            severity = "low"
        
        resource_gaps[cap] = {
            "capability": cap,
            "facilities_with": facilities_with_cap,
            "total_facilities": total_facilities,
            "coverage_pct": round(coverage_pct, 1),
            "severity": severity,
            "recommendation": f"Need {max(0, int(total_facilities * 0.3) - facilities_with_cap)} more facilities" if severity in ["critical", "high"] else "Adequate coverage",
        }
    
    # District health gaps
    district_gaps = {}
    if not district_df.empty:
        if state:
            state_districts = district_df[district_df["state"] == state]
        else:
            state_districts = district_df
        
        # Identify districts with poor health indicators
        if "institutional_births_pct" in state_districts.columns:
            low_birth_care = state_districts[state_districts["institutional_births_pct"] < 50]
            district_gaps["low_institutional_births"] = {
                "count": len(low_birth_care),
                "districts": low_birth_care["district"].tolist() if "district" in low_birth_care.columns else [],
            }
        
        if "health_insurance_pct" in state_districts.columns:
            low_insurance = state_districts[state_districts["health_insurance_pct"] < 30]
            district_gaps["low_health_insurance"] = {
                "count": len(low_insurance),
                "districts": low_insurance["district"].tolist() if "district" in low_insurance.columns else [],
            }
    
    res = {
        "status": "success",
        "data": {
            "state": state or "nationwide",
            "total_facilities": total_facilities,
            "resource_gaps": resource_gaps,
            "district_gaps": district_gaps,
        }
    }
    _resource_gaps_cache[cache_key] = res
    return res


@router.get("/intervention-plan")
async def get_intervention_plan(state: Optional[str] = None, capability: Optional[str] = None):
    """Get recommended intervention plan for improving healthcare access."""
    global _intervention_plan_cache
    cache_key = (state or "nationwide", capability or "all")
    if cache_key in _intervention_plan_cache:
        return _intervention_plan_cache[cache_key]

    from server.data_loader import get_facilities_df
    import json
    
    facilities_df = get_facilities_df()
    
    if facilities_df.empty:
        raise HTTPException(status_code=404, detail="No facilities data available")
    
    # Filter by state if provided
    state_col = "state" if "state" in facilities_df.columns else "address_stateOrRegion"
    if state and state_col in facilities_df.columns:
        facilities_df = facilities_df[facilities_df[state_col] == state]
    
    # Analyze current state
    total_facilities = len(facilities_df)
    
    # Get capability distribution
    capability_dist = {}
    if "capability" in facilities_df.columns:
        for cap_str in facilities_df["capability"].dropna():
            try:
                if isinstance(cap_str, str):
                    parsed = json.loads(cap_str)
                    if isinstance(parsed, list):
                        for cap in parsed:
                            cap_lower = cap.lower().strip()
                            capability_dist[cap_lower] = capability_dist.get(cap_lower, 0) + 1
            except:
                if isinstance(cap_str, str):
                    for cap in cap_str.split(","):
                        cap_lower = cap.lower().strip()
                        capability_dist[cap_lower] = capability_dist.get(cap_lower, 0) + 1
    
    # Generate intervention recommendations
    interventions = []
    
    # Check for critical gaps
    critical_capabilities = ["emergency", "maternity", "surgery", "icu"]
    for cap in critical_capabilities:
        count = capability_dist.get(cap, 0)
        coverage = (count / total_facilities * 100) if total_facilities > 0 else 0
        
        if coverage < 20:
            interventions.append({
                "priority": "high",
                "capability": cap,
                "current_coverage": round(coverage, 1),
                "target_coverage": 50,
                "facilities_needed": max(0, int(total_facilities * 0.5) - count),
                "recommendation": f"Establish {cap} services in at least 50% of facilities",
                "impact": "high",
            })
    
    # Trust improvement recommendations
    if "_trust_score" in facilities_df.columns:
        low_trust = facilities_df[facilities_df["_trust_score"] < 30]
        low_trust_count = len(low_trust)
        
        if low_trust_count > total_facilities * 0.2:
            interventions.append({
                "priority": "high",
                "capability": "trust_improvement",
                "current_coverage": round((1 - low_trust_count / total_facilities) * 100, 1),
                "target_coverage": 80,
                "facilities_needed": low_trust_count,
                "recommendation": "Improve data quality and verification for low-trust facilities",
                "impact": "high",
            })
    
    # Sort by priority
    interventions.sort(key=lambda x: 0 if x["priority"] == "high" else 1)
    
    res = {
        "status": "success",
        "data": {
            "state": state or "nationwide",
            "total_facilities": total_facilities,
            "current_capability_distribution": capability_dist,
            "interventions": interventions,
            "summary": {
                "critical_gaps": len([i for i in interventions if i["priority"] == "high"]),
                "total_facilities_needing_improvement": sum(i["facilities_needed"] for i in interventions),
            }
        }
    }
    _intervention_plan_cache[cache_key] = res
    return res