"""
Trust Engine — Core scoring logic for healthcare facility capabilities.

Scores facility capability claims against evidence from multiple fields.
Returns trust signals: CORROBORATED, CLAIMED_ONLY, WEAK, UNKNOWN.
"""

import re
import json
from typing import Any

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False


# Keywords for common capabilities
CAPABILITY_KEYWORDS = {
    "icu": ["icu", "intensive care", "critical care", "ccu"],
    "nicu": ["nicu", "neonatal intensive care", "newborn care", "neonatal unit"],
    "maternity": ["maternity", "obstetric", "labor delivery", "natal", "maternity ward"],
    "emergency": ["emergency", "24/7", "trauma", "accident", "emergency department"],
    "oncology": ["oncology", "cancer", "chemotherapy", "radiation therapy"],
    "trauma": ["trauma", "surgery", "surgical", "operation", "trauma care"],
    "dialysis": ["dialysis", "renal", "kidney", "haemodialysis"],
    "surgery": ["surgery", "surgical", "operation", "theatre", "operation theatre"],
    "pharmacy": ["pharmacy", "drugstore", "medicines", "dispensary"],
    "laboratory": ["laboratory", "lab", "diagnostic", "testing"],
    "radiology": ["radiology", "x-ray", "mri", "ct scan", "imaging"],
    "cardiology": ["cardiology", "cardiac", "heart", "cardiovascular"],
    "ophthalmology": ["ophthalmology", "eye", "cataract", "glaucoma"],
    "orthopedics": ["orthopedics", "orthopaedic", "bone", "joint"],
    "pediatrics": ["pediatrics", "paediatric", "child", "children"],
    "dental": ["dental", "dentistry", "tooth", "teeth"],
}

# Negation patterns
NEGATION_PATTERNS = [
    "not available", "not equipped", "not provided", "not offered",
    "proposed", "planned", "under construction", "will have",
    "coming soon", "does not have", "no longer", "discontinued",
    "absent", "lacking", "without", "missing",
]

# Aspirational language (weakens claims)
ASPIRATIONAL_PATTERNS = [
    "aims to", "intends to", "plans to", "will provide",
    "future", "upcoming", "expected", "targeted",
]

# Source weights
SOURCE_WEIGHTS = {
    "description": 1.0,
    "capability": 0.8,
    "procedure": 0.8,
    "equipment": 0.7,
    "specialties": 0.6,
}

# Trust signal definitions
SIGNAL_CORROBORATED = "CORROBORATED"
SIGNAL_CLAIMED_ONLY = "CLAIMED_ONLY"
SIGNAL_WEAK = "WEAK"
SIGNAL_UNKNOWN = "UNKNOWN"


def _parse_json_field(value: Any) -> list[str]:
    """Parse a field that might be a JSON array or comma-separated string."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip().lower() for v in value if v]
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        # Try JSON parse
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(v).strip().lower() for v in parsed if v]
        except (json.JSONDecodeError, TypeError):
            pass
        # Comma-separated fallback
        return [v.strip().lower() for v in value.split(",") if v.strip()]
    return []


def _text_matches_keyword(text: str, keywords: list[str]) -> bool:
    """Check if any keyword appears in the text (case-insensitive)."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


def _is_negated(text: str, keyword: str) -> bool:
    """Check if a keyword claim is negated in the text."""
    text_lower = text.lower()
    # Look for negation patterns near the keyword
    for pattern in NEGATION_PATTERNS:
        if pattern in text_lower and keyword in text_lower:
            # Check proximity (within 50 chars)
            idx_pattern = text_lower.find(pattern)
            idx_keyword = text_lower.find(keyword)
            if abs(idx_pattern - idx_keyword) < 50:
                return True
    return False


def _is_aspirational(text: str, keyword: str) -> bool:
    """Check if a keyword claim uses aspirational language."""
    text_lower = text.lower()
    for pattern in ASPIRATIONAL_PATTERNS:
        if pattern in text_lower and keyword in text_lower:
            idx_pattern = text_lower.find(pattern)
            idx_keyword = text_lower.find(keyword)
            if abs(idx_pattern - idx_keyword) < 50:
                return True
    return False


def _extract_evidence_snippet(text: str, keyword: str, context_len: int = 80) -> str:
    """Extract a text snippet around a keyword match."""
    text_lower = text.lower()
    idx = text_lower.find(keyword)
    if idx == -1:
        return ""
    start = max(0, idx - context_len)
    end = min(len(text), idx + len(keyword) + context_len)
    snippet = text[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet


class TrustEngine:
    """Scores facility capability claims against evidence."""

    def __init__(self, custom_keywords: dict[str, list[str]] | None = None):
        self.keywords = {**CAPABILITY_KEYWORDS}
        if custom_keywords:
            self.keywords.update(custom_keywords)

    def score_facility(self, facility: dict) -> dict:
        """
        Score a single facility record.

        Returns:
            {
                "overall_trust": float (0-100),
                "overall_signal": str,
                "capabilities": {
                    "icu": {
                        "signal": str,
                        "score": float,
                        "evidence": [{"field": str, "text": str, "weight": float}],
                        "gaps": [str],
                    },
                    ...
                },
                "metadata": {
                    "fields_with_data": int,
                    "fields_empty": int,
                    "total_claims": int,
                    "corroborated_claims": int,
                }
            }
        """
        # Parse all evidence fields
        description = str(facility.get("description", "") or "")
        capability_items = _parse_json_field(facility.get("capability"))
        procedure_items = _parse_json_field(facility.get("procedure"))
        equipment_items = _parse_json_field(facility.get("equipment"))
        specialties_items = _parse_json_field(facility.get("specialties"))

        all_items = {
            "description": [description.lower()] if description else [],
            "capability": capability_items,
            "procedure": procedure_items,
            "equipment": equipment_items,
            "specialties": specialties_items,
        }

        # Combine all items into one searchable text per field
        field_texts = {
            "description": description,
            "capability": " ".join(capability_items),
            "procedure": " ".join(procedure_items),
            "equipment": " ".join(equipment_items),
            "specialties": " ".join(specialties_items),
        }

        # Score each known capability
        capabilities = {}
        total_claims = 0
        corroborated_claims = 0

        for cap_name, cap_keywords in self.keywords.items():
            evidence = []
            negated = False
            aspirational = False
            matched_fields = set()

            # Check each field for this capability
            for field_name, field_text in field_texts.items():
                if not field_text:
                    continue

                for kw in cap_keywords:
                    if _text_matches_keyword(field_text, [kw]):
                        # Check negation
                        if _is_negated(field_text, kw):
                            negated = True
                            continue

                        # Check aspirational
                        if _is_aspirational(field_text, kw):
                            aspirational = True

                        # Add evidence
                        snippet = _extract_evidence_snippet(field_text, kw)
                        evidence.append({
                            "field": field_name,
                            "text": snippet or kw,
                            "weight": SOURCE_WEIGHTS.get(field_name, 0.5),
                        })
                        matched_fields.add(field_name)
                        break  # One match per field is enough

            # Determine trust signal
            if not evidence:
                signal = SIGNAL_UNKNOWN
                score = 0.0
            elif negated:
                signal = SIGNAL_WEAK
                score = 0.1
            elif aspirational:
                signal = SIGNAL_WEAK
                score = 0.3
            elif len(matched_fields) >= 2:
                signal = SIGNAL_CORROBORATED
                score = min(1.0, 0.7 + len(matched_fields) * 0.1)
                corroborated_claims += 1
            else:
                signal = SIGNAL_CLAIMED_ONLY
                score = 0.5

            total_claims += 1

            capabilities[cap_name] = {
                "signal": signal,
                "score": round(score, 2),
                "evidence": evidence,
                "gaps": [f"Not found in {f}" for f in ["description", "capability", "procedure", "equipment", "specialties"] if f not in matched_fields],
            }

        # Calculate overall trust
        if not capabilities:
            overall_score = 0.0
            overall_signal = SIGNAL_UNKNOWN
        else:
            scores = [c["score"] for c in capabilities.values()]
            overall_score = sum(scores) / len(scores) * 100
            signals = [c["signal"] for c in capabilities.values()]
            if SIGNAL_CORROBORATED in signals:
                overall_signal = SIGNAL_CORROBORATED
            elif SIGNAL_CLAIMED_ONLY in signals:
                overall_signal = SIGNAL_CLAIMED_ONLY
            elif SIGNAL_WEAK in signals:
                overall_signal = SIGNAL_WEAK
            else:
                overall_signal = SIGNAL_UNKNOWN

        # Metadata
        fields_with_data = sum(1 for v in field_texts.values() if v)
        fields_empty = sum(1 for v in field_texts.values() if not v)

        result = {
            "overall_trust": round(overall_score, 1),
            "overall_signal": overall_signal,
            "capabilities": capabilities,
            "metadata": {
                "fields_with_data": fields_with_data,
                "fields_empty": fields_empty,
                "total_claims": total_claims,
                "corroborated_claims": corroborated_claims,
            },
        }

        if MLFLOW_AVAILABLE:
            try:
                facility_id = facility.get("unique_id", "unknown")
                with mlflow.start_run(run_name=f"score_{facility_id}", nested=True):
                    mlflow.log_param("facility_id", facility_id)
                    mlflow.log_param("facility_name", facility.get("name", "Unknown")[:200])
                    mlflow.log_param("state", facility.get("address_stateOrRegion", ""))
                    mlflow.log_param("city", facility.get("address_city", ""))
                    mlflow.log_metric("trust_score", overall_score)
                    mlflow.log_metric("total_claims", total_claims)
                    mlflow.log_metric("corroborated_claims", corroborated_claims)
                    mlflow.log_metric("fields_with_data", fields_with_data)
                    mlflow.log_metric("fields_empty", fields_empty)
                    mlflow.set_tag("overall_signal", overall_signal)
                    mlflow.log_dict(result, "trust_result.json")
            except Exception:
                pass

        return result

    def score_batch(self, facilities: list[dict]) -> list[dict]:
        """Score multiple facilities."""
        return [self.score_facility(f) for f in facilities]

    def get_capability_summary(self, facilities: list[dict]) -> dict:
        """Get summary statistics for a batch of facilities."""
        summaries = []
        for f in facilities:
            result = self.score_facility(f)
            summaries.append({
                "name": f.get("name", "Unknown"),
                "trust": result["overall_trust"],
                "signal": result["overall_signal"],
                "claims": result["metadata"]["total_claims"],
                "corroborated": result["metadata"]["corroborated_claims"],
            })

        if not summaries:
            return {"total": 0, "avg_trust": 0, "distribution": {}}

        avg_trust = sum(s["trust"] for s in summaries) / len(summaries)
        distribution = {}
        for s in summaries:
            signal = s["signal"]
            distribution[signal] = distribution.get(signal, 0) + 1

        return {
            "total": len(summaries),
            "avg_trust": round(avg_trust, 1),
            "distribution": distribution,
            "facilities": summaries,
        }
