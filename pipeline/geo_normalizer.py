"""
Geo Normalizer — Maps facility postcodes to districts and states.

Uses India Post PIN Directory to resolve postcodes to geographic regions.
"""

import pandas as pd
from typing import Optional


class GeoNormalizer:
    """Maps facility postcodes to districts and states."""

    def __init__(self, pin_directory_path: str):
        """
        Load and index the India Post PIN Directory.

        Args:
            pin_directory_path: Path to india_post_pin_directory.csv
        """
        self.pin_data = pd.read_csv(pin_directory_path, dtype={"pincode": str})
        self.pin_data["pincode"] = self.pin_data["pincode"].str.strip()

        # Create lookup dictionaries
        self.pin_to_district = {}
        self.pin_to_state = {}
        self.pin_to_city = {}
        self.pin_to_lat = {}
        self.pin_to_lon = {}

        for _, row in self.pin_data.iterrows():
            pin = str(row.get("pincode", "")).strip()
            if not pin:
                continue

            district = str(row.get("district", "")).strip()
            state = str(row.get("statename", "")).strip()
            city = str(row.get("officename", "")).strip()
            lat = row.get("lat")
            lon = row.get("lon")

            if pin not in self.pin_to_district:
                self.pin_to_district[pin] = district
                self.pin_to_state[pin] = state
                self.pin_to_city[pin] = city
                if pd.notna(lat):
                    self.pin_to_lat[pin] = float(lat)
                if pd.notna(lon):
                    self.pin_to_lon[pin] = float(lon)

        # Build district index for fuzzy matching
        self.districts = sorted(set(self.pin_to_district.values()))
        self.states = sorted(set(self.pin_to_state.values()))

    def normalize(self, postcode: str) -> dict:
        """
        Map a postcode to geographic information.

        Args:
            postcode: Indian postal code (6 digits)

        Returns:
            {
                "district": str or None,
                "state": str or None,
                "city": str or None,
                "latitude": float or None,
                "longitude": float or None,
                "confidence": float (0-1),
            }
        """
        if not postcode:
            return {
                "district": None,
                "state": None,
                "city": None,
                "latitude": None,
                "longitude": None,
                "confidence": 0.0,
            }

        postcode = str(postcode).strip()

        if postcode in self.pin_to_district:
            return {
                "district": self.pin_to_district.get(postcode),
                "state": self.pin_to_state.get(postcode),
                "city": self.pin_to_city.get(postcode),
                "latitude": self.pin_to_lat.get(postcode),
                "longitude": self.pin_to_lon.get(postcode),
                "confidence": 1.0,
            }

        # Try partial match (first 3 digits for broader region)
        if len(postcode) >= 3:
            prefix = postcode[:3]
            matches = [
                (pin, district)
                for pin, district in self.pin_to_district.items()
                if pin.startswith(prefix)
            ]
            if matches:
                # Return most common district for this prefix
                district_counts = {}
                for _, district in matches:
                    district_counts[district] = district_counts.get(district, 0) + 1
                best_district = max(district_counts, key=district_counts.get)

                # Find a sample pin for this district
                for pin, district in matches:
                    if district == best_district:
                        return {
                            "district": best_district,
                            "state": self.pin_to_state.get(pin),
                            "city": self.pin_to_city.get(pin),
                            "latitude": self.pin_to_lat.get(pin),
                            "longitude": self.pin_to_lon.get(pin),
                            "confidence": 0.6,
                        }

        return {
            "district": None,
            "state": None,
            "city": None,
            "latitude": None,
            "longitude": None,
            "confidence": 0.0,
        }

    def normalize_batch(self, postcodes: list[str]) -> list[dict]:
        """Map multiple postcodes to geographic information."""
        return [self.normalize(pin) for pin in postcodes]

    def get_all_districts(self) -> list[str]:
        """Get sorted list of all districts."""
        return self.districts

    def get_all_states(self) -> list[str]:
        """Get sorted list of all states."""
        return self.states

    def get_district_count(self) -> int:
        """Get total number of unique districts."""
        return len(self.districts)

    def get_state_count(self) -> int:
        """Get total number of unique states."""
        return len(self.states)
