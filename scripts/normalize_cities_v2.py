"""
Second pass: more aggressive city normalization.
Strip neighborhood suffixes, merge into parent cities, clean garbage.
"""
import pandas as pd
import re
import os

PARQUET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "facilities_scored.parquet")

# Known neighborhood -> parent city mappings
NEIGHBORHOOD_TO_CITY = {
    # Mumbai neighborhoods
    "borivali east": "Mumbai", "borivali (east)": "Mumbai",
    "borivali west": "Mumbai", "goregaon west": "Mumbai",
    "goregaon east": "Mumbai", "kalyan west": "Mumbai",
    "matunga east": "Mumbai", "nalasopara west": "Mumbai",
    "bhayandar east": "Mumbai", "bhayandar west": "Mumbai",
    "kalyan east": "Mumbai", "badlapur west": "Mumbai",
    "badlapur east": "Mumbai", "navi mumbai": "Navi Mumbai",
    "mira road": "Mumbai", "miraroad": "Mumbai",
    "punit nagar palghar": "Palghar",
    "pimpri-chinchwad": "Pune", "pimpri": "Pune", "chinchwad": "Pune",

    # Delhi neighborhoods
    "safdarjung development area": "New Delhi",
    "new rajender nagar": "New Delhi", "rohini sector 3": "New Delhi",
    "rohini": "New Delhi", "saket": "New Delhi",
    "dwarka": "New Delhi", "karol bagh": "New Delhi",
    "lajpat nagar": "New Delhi", "greater kailash": "New Delhi",
    "vasant kunj": "New Delhi", "munirka": "New Delhi",
    "kalkaji": "New Delhi", "nehru place": "New Delhi",
    "sarojini nagar": "New Delhi", "laxmi nagar": "New Delhi",
    "preet vihar": "New Delhi", "janakpuri": "New Delhi",
    "tilak nagar": "New Delhi", "moti nagar": "New Delhi",
    "rajinagar": "New Delhi",

    # Bangalore neighborhoods
    "basaveshwaranagar": "Bengaluru", "jayanagar": "Bengaluru",
    "koramangala": "Bengaluru", "hsr layout": "Bengaluru",
    "indiranagar": "Bengaluru", "whitefield": "Bengaluru",
    "electronic city": "Bengaluru", "hebbal": "Bengaluru",
    "bannerghatta": "Bengaluru", "marathahalli": "Bengaluru",
    "sarjapur road": "Bengaluru", "kr puram": "Bengaluru",
    "bengaluru east": "Bengaluru", "bengaluru north": "Bengaluru",
    "bengaluru south": "Bengaluru", "bengaluru west": "Bengaluru",

    # Chennai neighborhoods
    "adyar": "Chennai", "velachery": "Chennai",
    "t.nagar": "Chennai", "anna nagar": "Chennai",
    "annanagar": "Chennai", "chromepet": "Chennai",
    "porur": "Chennai", "nungambakkam": "Chennai",
    "madurai east": "Madurai",

    # Kolkata neighborhoods
    "salt lake": "Kolkata", "sector 1 salt lake city sector 1": "Kolkata",
    "new town": "Kolkata", "salt lake city": "Kolkata",
    "bidhannagar": "Kolkata", "baranagar": "Kolkata",
    "konnagar": "Kolkata",

    # Hyderabad neighborhoods
    "gachibowli": "Hyderabad", "madhapur": "Hyderabad",
    "kondapur": "Hyderabad", "jubilee hills": "Hyderabad",
    "banjara hills": "Hyderabad", "secunderabad": "Hyderabad",
    "HITEC city": "Hyderabad",

    # Pune neighborhoods
    "kothrud": "Pune", "hinjewadi": "Pune",
    "viman nagar": "Pune", "kharadi": "Pune",

    # Ahmedabad neighborhoods
    "maninagar": "Ahmedabad", "satellite": "Ahmedabad",
    "odia": "Ahmedabad", "sg highway": "Ahmedabad",

    # Other
    "sas nagar": "Mohali", "s.a.s nagar": "Mohali",
    "surendranagar": "Surendranagar",
    "ramnagar": "Varanasi",
    "allinagaram": "Madurai",
    "ashoknagarh-kalyangarh kachua more": "Kolkata",
    "ezhupunna south": "Alappuzha",
    "chatrapati sambhaji nagar": "Aurangabad",
    "krishnanagar": "Kolkata",
    "nagar": None,  # too vague
    "gautam buddha nagar": "Noida",
    "areacode": None,  # garbage
    "jalandhar-east": "Jalandhar",
}

# Strip "East", "West", "North", "South" city suffixes for known cities
SUFFIX_STRIP = {
    " east": "", " west": "", " north": "", " south": "",
    " central": "", " east)": "", " west)": "",
}


def normalize_city_v2(raw):
    if pd.isna(raw) or not isinstance(raw, str):
        return raw
    val = raw.strip()
    if not val:
        return val

    lower = val.lower().strip()

    # Check neighborhood map first
    if lower in NEIGHBORHOOD_TO_CITY:
        return NEIGHBORHOOD_TO_CITY[lower]

    # Try stripping directional suffixes for known cities
    cleaned = lower
    for suffix, replacement in SUFFIX_STRIP.items():
        if cleaned.endswith(suffix):
            candidate = cleaned[:-len(suffix)] + replacement
            # Check if this is a known city
            if candidate in [c.lower() for c in [
                "Mumbai", "Pune", "Delhi", "Bengaluru", "Chennai",
                "Kolkata", "Hyderabad", "Ahmedabad", "Jaipur",
                "Lucknow", "Patna", "Nagpur", "Indore", "Bhopal",
                "Coimbatore", "Ludhiana", "Agra", "Kanpur",
                "Vadodara", "Surat", "Rajkot", "Thiruvananthapuram",
            ]]:
                cleaned = candidate
                break

    return val  # Return original if no match (don't change valid cities)


def main():
    df = pd.read_parquet(PARQUET_PATH)
    print(f"Loaded {len(df)} rows")

    # Apply neighborhood normalization
    df["address_city"] = df["address_city"].apply(normalize_city_v2)

    # Remove rows with no valid state (garbage entries)
    before = len(df)
    df = df.dropna(subset=["address_stateOrRegion"])
    after = len(df)
    print(f"Dropped {before - after} rows with no valid state")

    # Final counts
    states = df["address_stateOrRegion"].value_counts()
    cities = df["address_city"].value_counts()

    print(f"\nFinal: {len(states)} states/UTs, {len(cities)} unique cities")
    print(f"Cities with 1 facility: {(cities == 1).sum()}")
    print(f"Cities with >10 facilities: {(cities > 10).sum()}")

    print(f"\nStates/UTs:")
    for s, c in states.items():
        print(f"  {c:>5}  {s}")

    print(f"\nTop 40 cities:")
    for s, c in cities.head(40).items():
        print(f"  {c:>5}  {s}")

    # Save
    df.to_parquet(PARQUET_PATH, index=False)
    print(f"\nSaved {len(df)} rows to {PARQUET_PATH}")


if __name__ == "__main__":
    main()
