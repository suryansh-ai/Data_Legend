"""
Desert Classifier — Classifies districts into coverage categories.

Uses facility data + NFHS-5 health indicators to identify:
- LIKELY_UNDERSERVED: Low facility coverage + poor health indicators
- DATA_DESERT: Few records but NFHS-5 shows adequate indicators
- NO_DATA: No facility records AND no NFHS-5 match
- COVERED: Adequate facility coverage + good indicators
"""

import pandas as pd
from typing import Optional


# NFHS-5 indicators that suggest healthcare access (lower = worse)
ACCESS_INDICATORS = [
    "Institutional births in public facility",
    "Skilled birth attendance",
    "Full immunization coverage",
    "Antenatal care (4+ visits)",
    "Children with diarrhea treated with ORS",
]

# Thresholds for classification
FACILITY_COUNT_THRESHOLD = 3  # Minimum facilities for "covered"
HEALTH_SCORE_THRESHOLD = 0.5  # Normalized score (0-1) for "adequate" indicators


class DesertClassifier:
    """Classifies districts into healthcare coverage categories."""

    def __init__(self, nfhs5_path: str):
        """
        Load NFHS-5 district health data.

        Args:
            nfhs5_path: Path to NFHS_5_India_Districts_Factsheet_Data.xlsx
        """
        self.nfhs5 = pd.read_excel(nfhs5_path)

        # Normalize district names for matching
        if "District" in self.nfhs5.columns:
            self.nfhs5["district_lower"] = self.nfhs5["District"].str.lower().str.strip()
        elif "District Name" in self.nfhs5.columns:
            self.nfhs5["district_lower"] = self.nfhs5["District Name"].str.lower().str.strip()
        else:
            # Find the district column
            for col in self.nfhs5.columns:
                if "district" in col.lower():
                    self.nfhs5["district_lower"] = self.nfhs5[col].str.lower().str.strip()
                    break

        # Calculate health access score per district
        self._calculate_health_scores()

    def _calculate_health_scores(self):
        """Calculate normalized health access score for each district."""
        available_indicators = []
        for indicator in ACCESS_INDICATORS:
            # Find column containing this indicator
            for col in self.nfhs5.columns:
                if indicator.lower() in col.lower():
                    available_indicators.append(col)
                    break

        if not available_indicators:
            # If no indicators found, create default scores
            self.nfhs5["health_score"] = 0.5
            self.district_scores = {}
            return

        # Normalize each indicator to 0-1 scale
        for col in available_indicators:
            if col in self.nfhs5.columns:
                numeric = pd.to_numeric(self.nfhs5[col], errors="coerce")
                min_val = numeric.min()
                max_val = numeric.max()
                if max_val > min_val:
                    self.nfhs5[f"{col}_norm"] = (numeric - min_val) / (max_val - min_val)
                else:
                    self.nfhs5[f"{col}_norm"] = 0.5

        # Average normalized scores
        norm_cols = [f"{col}_norm" for col in available_indicators if f"{col}_norm" in self.nfhs5.columns]
        if norm_cols:
            self.nfhs5["health_score"] = self.nfhs5[norm_cols].mean(axis=1)
        else:
            self.nfhs5["health_score"] = 0.5

        # Build district → score lookup
        self.district_scores = {}
        for _, row in self.nfhs5.iterrows():
            district = row.get("district_lower", "")
            score = row.get("health_score", 0.5)
            if district and pd.notna(score):
                self.district_scores[district] = float(score)

    def classify(
        self,
        district: str,
        facility_count: int = 0,
        capability_coverage: float = 0.0,
    ) -> str:
        """
        Classify a district into a coverage category.

        Args:
            district: District name
            facility_count: Number of facilities in this district
            capability_coverage: Average capability coverage (0-1)

        Returns:
            Classification string
        """
        district_lower = district.lower().strip() if district else ""

        # Check if we have NFHS-5 data for this district
        health_score = self.district_scores.get(district_lower, None)

        # Classification logic
        if facility_count == 0 and health_score is None:
            return "NO_DATA"
        elif facility_count == 0 and health_score is not None:
            if health_score < HEALTH_SCORE_THRESHOLD:
                return "LIKELY_UNDERSERVED"
            else:
                return "DATA_DESERT"
        elif facility_count < FACILITY_COUNT_THRESHOLD:
            if health_score is not None and health_score < HEALTH_SCORE_THRESHOLD:
                return "LIKELY_UNDERSERVED"
            elif health_score is not None and health_score >= HEALTH_SCORE_THRESHOLD:
                return "DATA_DESERT"
            else:
                return "DATA_DESERT"
        else:
            # We have facilities
            if health_score is not None and health_score < HEALTH_SCORE_THRESHOLD:
                # Facilities exist but health indicators are poor
                return "LIKELY_UNDERSERVED"
            else:
                return "COVERED"

    def classify_batch(self, districts: list[dict]) -> list[dict]:
        """
        Classify multiple districts.

        Args:
            districts: List of {district, facility_count, capability_coverage}

        Returns:
            List of {district, classification, health_score}
        """
        results = []
        for d in districts:
            classification = self.classify(
                district=d.get("district", ""),
                facility_count=d.get("facility_count", 0),
                capability_coverage=d.get("capability_coverage", 0.0),
            )
            health_score = self.district_scores.get(
                d.get("district", "").lower().strip(), None
            )
            results.append({
                "district": d.get("district"),
                "classification": classification,
                "health_score": health_score,
            })
        return results

    def get_summary(self) -> dict:
        """Get summary statistics of NFHS-5 data."""
        return {
            "total_districts": len(self.district_scores),
            "avg_health_score": round(
                sum(self.district_scores.values()) / len(self.district_scores), 3
            )
            if self.district_scores
            else 0,
            "min_health_score": round(min(self.district_scores.values()), 3)
            if self.district_scores
            else 0,
            "max_health_score": round(max(self.district_scores.values()), 3)
            if self.district_scores
            else 0,
        }
