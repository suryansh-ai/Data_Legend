"""
Trust Engine — Claim-level trust scoring for healthcare facility capabilities.
"""

import json
from typing import Any

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except Exception:
    MLFLOW_AVAILABLE = False

CAPABILITY_KEYWORDS = {
    "icu": ["icu", "intensive care", "critical care", "ccu"],
    "nicu": ["nicu", "neonatal intensive care", "newborn care"],
    "maternity": ["maternity", "obstetric", "labor delivery", "natal"],
    "emergency": ["emergency", "24/7", "trauma", "accident"],
    "oncology": ["oncology", "cancer", "chemotherapy", "radiation therapy"],
    "trauma": ["trauma", "surgery", "surgical", "operation"],
    "dialysis": ["dialysis", "renal", "kidney"],
    "surgery": ["surgery", "surgical", "operation theatre"],
    "pharmacy": ["pharmacy", "drugstore", "medicines"],
    "laboratory": ["laboratory", "lab", "diagnostic"],
    "radiology": ["radiology", "x-ray", "mri", "ct scan", "imaging"],
    "cardiology": ["cardiology", "cardiac", "heart"],
    "ophthalmology": ["ophthalmology", "eye", "cataract"],
    "orthopedics": ["orthopedics", "orthopaedic", "bone", "joint"],
    "pediatrics": ["pediatrics", "paediatric", "child"],
    "dental": ["dental", "dentistry", "tooth"],
}

NEGATION_PATTERNS = [
    "not available", "not equipped", "not provided", "proposed",
    "planned", "under construction", "coming soon", "discontinued",
]

ASPIRATIONAL_PATTERNS = [
    "aims to", "intends to", "plans to", "will provide",
    "future", "upcoming", "expected",
]

SOURCE_WEIGHTS = {
    "description": 1.0, "capability": 0.8, "procedure": 0.8,
    "equipment": 0.7, "specialties": 0.6,
}


def _parse_json_field(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip().lower() for v in value if v]
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(v).strip().lower() for v in parsed if v]
        except (json.JSONDecodeError, TypeError):
            pass
        return [v.strip().lower() for v in value.split(",") if v.strip()]
    return []


def _extract_snippet(text: str, keyword: str, ctx: int = 80) -> str:
    text_lower = text.lower()
    idx = text_lower.find(keyword)
    if idx == -1:
        return ""
    start = max(0, idx - ctx)
    end = min(len(text), idx + len(keyword) + ctx)
    snippet = text[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet += "..."
    return snippet


def score_facility(facility: dict) -> dict:
    description = str(facility.get("description", "") or "")
    cap_items = _parse_json_field(facility.get("capability"))
    proc_items = _parse_json_field(facility.get("procedure"))
    equip_items = _parse_json_field(facility.get("equipment"))
    spec_items = _parse_json_field(facility.get("specialties"))

    field_texts = {
        "description": description,
        "capability": " ".join(cap_items),
        "procedure": " ".join(proc_items),
        "equipment": " ".join(equip_items),
        "specialties": " ".join(spec_items),
    }

    capabilities = {}
    total_claims = 0
    corroborated_claims = 0

    for cap_name, cap_keywords in CAPABILITY_KEYWORDS.items():
        evidence = []
        matched_fields = set()
        negated = False
        aspirational = False

        for field_name, field_text in field_texts.items():
            if not field_text:
                continue
            for kw in cap_keywords:
                if kw in field_text.lower():
                    for pat in NEGATION_PATTERNS:
                        if pat in field_text.lower() and kw in field_text.lower():
                            negated = True
                    for pat in ASPIRATIONAL_PATTERNS:
                        if pat in field_text.lower() and kw in field_text.lower():
                            aspirational = True
                    snippet = _extract_snippet(field_text, kw)
                    evidence.append({
                        "field": field_name,
                        "text": snippet or kw,
                        "weight": SOURCE_WEIGHTS.get(field_name, 0.5),
                    })
                    matched_fields.add(field_name)
                    break

        if not evidence:
            signal, score = "UNKNOWN", 0.0
        elif negated:
            signal, score = "WEAK", 0.1
        elif aspirational:
            signal, score = "WEAK", 0.3
        elif len(matched_fields) >= 2:
            signal = "CORROBORATED"
            score = min(1.0, 0.7 + len(matched_fields) * 0.1)
            corroborated_claims += 1
        else:
            signal, score = "CLAIMED_ONLY", 0.5

        total_claims += 1
        capabilities[cap_name] = {
            "signal": signal,
            "score": round(score, 2),
            "evidence": evidence,
            "gaps": [
                f"Not found in {f}" for f in
                ["description", "capability", "procedure", "equipment", "specialties"]
                if f not in matched_fields
            ],
        }

    if not capabilities:
        overall_score, overall_signal = 0.0, "UNKNOWN"
    else:
        scores = [c["score"] for c in capabilities.values()]
        overall_score = sum(scores) / len(scores) * 100
        signals = [c["signal"] for c in capabilities.values()]
        if "CORROBORATED" in signals:
            overall_signal = "CORROBORATED"
        elif "CLAIMED_ONLY" in signals:
            overall_signal = "CLAIMED_ONLY"
        elif "WEAK" in signals:
            overall_signal = "WEAK"
        else:
            overall_signal = "UNKNOWN"

    fields_with_data = sum(1 for v in field_texts.values() if v)

    result = {
        "overall_trust": round(overall_score, 1),
        "overall_signal": overall_signal,
        "capabilities": capabilities,
        "metadata": {
            "fields_with_data": fields_with_data,
            "fields_empty": len(field_texts) - fields_with_data,
            "total_claims": total_claims,
            "corroborated_claims": corroborated_claims,
        },
    }

    if MLFLOW_AVAILABLE:
        try:
            facility_id = facility.get("unique_id", "unknown")
            with mlflow.start_run(run_name=f"score_{facility_id}", nested=True):
                mlflow.log_param("facility_id", facility_id)
                mlflow.log_metric("trust_score", overall_score)
                mlflow.log_metric("total_claims", total_claims)
                mlflow.log_metric("corroborated_claims", corroborated_claims)
                mlflow.set_tag("overall_signal", overall_signal)
                mlflow.log_dict(result, "trust_result.json")
        except Exception:
            pass

    return result
