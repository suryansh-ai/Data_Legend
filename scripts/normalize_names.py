"""
Normalize Indian state/UT and city names in the healthcare facilities dataset.
Fixes abbreviations, misspellings, old names, and data quality issues.
"""
import pandas as pd
import re
import json
import os

PARQUET_IN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "facilities_scored.parquet")
PARQUET_OUT = PARQUET_IN  # overwrite

# ============================================================
# STATE/UT NORMALIZATION
# ============================================================
# Key: variant (lowercase) -> canonical name
STATE_MAP = {
    # Standard 28 States
    "maharashtra": "Maharashtra",
    "mh": "Maharashtra",
    "gujarat": "Gujarat",
    "gj": "Gujarat",
    "uttar pradesh": "Uttar Pradesh",
    "up": "Uttar Pradesh",
    "u.p": "Uttar Pradesh",
    "u.p.": "Uttar Pradesh",
    "u p": "Uttar Pradesh",
    "up.": "Uttar Pradesh",
    "uttar pradesh region": "Uttar Pradesh",
    "uttar prades h": "Uttar Pradesh",
    "uttarpradesh": "Uttar Pradesh",
    "tamil nadu": "Tamil Nadu",
    "tamilnadu": "Tamil Nadu",
    "tn": "Tamil Nadu",
    "karnataka": "Karnataka",
    "ka": "Karnataka",
    "kerala": "Kerala",
    "kl": "Kerala",
    "west bengal": "West Bengal",
    "wb": "West Bengal",
    "punjab": "Punjab",
    "pb": "Punjab",
    "punjab region": "Punjab",
    "haryana": "Haryana",
    "hr": "Haryana",
    "telangana": "Telangana",
    "ts": "Telangana",
    "telengana": "Telangana",
    "tl": "Telangana",
    "rajasthan": "Rajasthan",
    "rj": "Rajasthan",
    "andhra pradesh": "Andhra Pradesh",
    "ap": "Andhra Pradesh",
    "madhya pradesh": "Madhya Pradesh",
    "mp": "Madhya Pradesh",
    "m.p.": "Madhya Pradesh",
    "m.p": "Madhya Pradesh",
    "m p": "Madhya Pradesh",
    "madhyapradesh": "Madhya Pradesh",
    "madhya": "Madhya Pradesh",
    "bihar": "Bihar",
    "br": "Bihar",
    "jharkhand": "Jharkhand",
    "jh": "Jharkhand",
    "chhattisgarh": "Chhattisgarh",
    "chattisgarh": "Chhattisgarh",
    "cg": "Chhattisgarh",
    "ch": "Chhattisgarh",
    "uttarakhand": "Uttarakhand",
    "uttaranchal": "Uttarakhand",
    "uttranchal": "Uttarakhand",
    "uk": "Uttarakhand",
    "u.k.": "Uttarakhand",
    "uk.": "Uttarakhand",
    "assam": "Assam",
    "as": "Assam",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "od": "Odisha",
    "or": "Odisha",
    "jammu and kashmir": "Jammu & Kashmir",
    "jammu & kashmir": "Jammu & Kashmir",
    "jammu, j&k": "Jammu & Kashmir",
    "jammu & kashmir": "Jammu & Kashmir",
    "kashmir": "Jammu & Kashmir",
    "j&k": "Jammu & Kashmir",
    "himachal pradesh": "Himachal Pradesh",
    "hp": "Himachal Pradesh",
    "goa": "Goa",
    "ga": "Goa",
    "meghalaya": "Meghalaya",
    "ml": "Meghalaya",
    "manipur": "Manipur",
    "mn": "Manipur",
    "tripura": "Tripura",
    "tr": "Tripura",
    "west tripura": "Tripura",
    "nagaland": "Nagaland",
    "nl": "Nagaland",
    "sikkim": "Sikkim",
    "sk": "Sikkim",
    "arunachal pradesh": "Arunachal Pradesh",
    "ar": "Arunachal Pradesh",
    "mizoram": "Mizoram",
    "mz": "Mizoram",

    # 8 Union Territories
    "delhi": "Delhi",
    "nct of delhi": "Delhi",
    "nct delhi": "Delhi",
    "nct": "Delhi",
    "new delhi": "Delhi",
    "dl": "Delhi",
    "delhi/ncr": "Delhi",
    "ncr-delhi": "Delhi",
    "ncr delhi": "Delhi",
    "delhi ncr": "Delhi",
    "ncr": "Delhi",
    "chandigarh": "Chandigarh",
    "chandigarh (ut)": "Chandigarh",
    "ch": "Chandigarh",  # note: ambiguous with Chhattisgarh but chhattisgarh is more common
    "puducherry": "Puducherry",
    "pondicherry": "Puducherry",
    "u.t of puducherry": "Puducherry",
    "py": "Puducherry",
    "andaman and nicobar islands": "Andaman & Nicobar Islands",
    "andaman & nicobar islands": "Andaman & Nicobar Islands",
    "dadra and nagar haveli and daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra & nagar haveli & daman & diu": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra & nagar haveli and daman & diu": "Dadra & Nagar Haveli and Daman & Diu",
    "daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra and nagar haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "ld": "Lakshadweep",
    "lakshadweep": "Lakshadweep",
    "jammu": "Jammu & Kashmir",
    "srinagar": "Jammu & Kashmir",
    "srinagar kashmir": "Jammu & Kashmir",
}

# States that are valid but need to be kept
VALID_STATES = {
    "Maharashtra", "Gujarat", "Uttar Pradesh", "Tamil Nadu", "Karnataka",
    "Kerala", "West Bengal", "Punjab", "Haryana", "Telangana", "Rajasthan",
    "Andhra Pradesh", "Madhya Pradesh", "Bihar", "Jharkhand", "Chhattisgarh",
    "Uttarakhand", "Assam", "Odisha", "Jammu & Kashmir", "Himachal Pradesh",
    "Goa", "Meghalaya", "Manipur", "Tripura", "Nagaland", "Sikkim",
    "Arunachal Pradesh", "Mizoram",
    "Delhi", "Chandigarh", "Puducherry", "Andaman & Nicobar Islands",
    "Dadra & Nagar Haveli and Daman & Diu", "Lakshadweep",
    # Also accept districts that sometimes appear
    "Kerala Region",
}

# Map known city names that appear in the state column back to their states
CITY_TO_STATE = {
    "mumbai": "Maharashtra",
    "navi mumbai": "Maharashtra",
    "navi-mumbai": "Maharashtra",
    "thane": "Maharashtra",
    "pune": "Maharashtra",
    "nagpur": "Maharashtra",
    "nashik": "Maharashtra",
    "aurangabad": "Maharashtra",
    "solapur": "Maharashtra",
    "amravati": "Maharashtra",
    "ahmednagar": "Maharashtra",
    "kolhapur": "Maharashtra",
    "sangli": "Maharashtra",
    "dhule": "Maharashtra",
    "palghar": "Maharashtra",
    "nanded": "Maharashtra",
    "latur": "Maharashtra",
    "satara district, maharashtra": "Maharashtra",
    "buldhana": "Maharashtra",
    "jalna": "Maharashtra",
    "wardha": "Maharashtra",
    "chikhali": "Maharashtra",
    "new mondha": "Maharashtra",
    "malshiras": "Maharashtra",
    "tasgaon": "Maharashtra",
    "pimpri-chinchwad": "Maharashtra",
    "indore": "Madhya Pradesh",
    "bhopal": "Madhya Pradesh",
    "gwalior": "Madhya Pradesh",
    "jabalpur": "Madhya Pradesh",
    "rewa": "Madhya Pradesh",
    "burhanpur": "Madhya Pradesh",
    "chennai": "Tamil Nadu",
    "coimbatore": "Tamil Nadu",
    "madurai": "Tamil Nadu",
    "salem": "Tamil Nadu",
    "erode": "Tamil Nadu",
    "tiruvannamalai": "Tamil Nadu",
    "namakkal": "Tamil Nadu",
    "cuddalore": "Tamil Nadu",
    "thanjavur": "Tamil Nadu",
    "tenkasi": "Tamil Nadu",
    "kanyakumari district": "Tamil Nadu",
    "bangalore": "Karnataka",
    "bengaluru": "Karnataka",
    "mysore": "Karnataka",
    "mangalore": "Karnataka",
    "dharwad": "Karnataka",
    "gadag": "Karnataka",
    "bijapur-karnataka": "Karnataka",
    "dakshin kannad": "Karnataka",
    "ramanagara district, karnataka": "Karnataka",
    "hyderabad": "Telangana",
    "khammam": "Telangana",
    "yadadri bhuvanagiri district": "Telangana",
    "kolkata": "West Bengal",
    "howrah": "West Bengal",
    "siliguri": "West Bengal",
    "hooghly": "West Bengal",
    "hoogly": "West Bengal",
    "birbhum": "West Bengal",
    "birbhum, west bengal": "West Bengal",
    "nadia": "West Bengal",
    "midnapore": "West Bengal",
    "paschim medinipur": "West Bengal",
    "west medinipur": "West Bengal",
    "north 24 parganas": "West Bengal",
    "south 24 parganas": "West Bengal",
    "north cachar hills": "West Bengal",
    "uttar dinajpur": "West Bengal",
    "west champaran": "Bihar",
    "darbhanga": "Bihar",
    "budaun": "Bihar",
    "kanpur": "Uttar Pradesh",
    "lucknow": "Uttar Pradesh",
    "varanasi": "Uttar Pradesh",
    "agra": "Uttar Pradesh",
    "meerut": "Uttar Pradesh",
    "ghaziabad": "Uttar Pradesh",
    "ghaziabad, uttar pradesh": "Uttar Pradesh",
    "allahabad": "Uttar Pradesh",
    "prayagraj": "Uttar Pradesh",
    "bareilly": "Uttar Pradesh",
    "aligarh": "Uttar Pradesh",
    "gorakhpur": "Uttar Pradesh",
    "kushinagar": "Uttar Pradesh",
    "noida": "Uttar Pradesh",
    "greater noida": "Uttar Pradesh",
    "jaipur": "Rajasthan",
    "jodhpur": "Rajasthan",
    "udaipur": "Rajasthan",
    "kota": "Rajasthan",
    "ajmer": "Rajasthan",
    "barmer": "Rajasthan",
    "ahmedabad": "Gujarat",
    "surat": "Gujarat",
    "rajkot": "Gujarat",
    "vadodara": "Gujarat",
    "bhavnagar": "Gujarat",
    "gandhinagar": "Gujarat",
    "gandhidham": "Gujarat",
    "mehsana": "Gujarat",
    "kheda": "Gujarat",
    "banas kantha": "Gujarat",
    "kutch": "Gujarat",
    "kachchh": "Gujarat",
    "kutch, gujarat": "Gujarat",
    "amritsar": "Punjab",
    "jalandhar": "Punjab",
    "ludhiana": "Punjab",
    "ludhiana-1": "Punjab",
    "patiala": "Punjab",
    "bathinda": "Punjab",
    "mohali": "Punjab",
    "jalandhar-east": "Punjab",
    "sangrur": "Punjab",
    "bhatinda": "Punjab",
    "faridabad": "Haryana",
    "gurgaon": "Haryana",
    "gurugram": "Haryana",
    "gurugram, haryana": "Haryana",
    "hisar": "Haryana",
    "rohtak": "Haryana",
    "sirsa, haryana": "Haryana",
    "sirsa": "Haryana",
    "jhajjar": "Haryana",
    "patna": "Bihar",
    "ranchi": "Jharkhand",
    "jamshedpur": "Jharkhand",
    "east singhbhum": "Jharkhand",
    "raipur": "Chhattisgarh",
    "bilaspur": "Chhattisgarh",
    "dehradun": "Uttarakhand",
    "haridwar, uttarakhand": "Uttarakhand",
    "almora": "Uttarakhand",
    "chamoli": "Uttarakhand",
    "sirmaur": "Himachal Pradesh",
    "guwahati": "Assam",
    "kamrup": "Assam",
    "bhubaneswar": "Odisha",
    "cuttack": "Odisha",
    "khordha": "Odisha",
    "ganjam": "Odisha",
    "srinagar": "Jammu & Kashmir",
    "jammu": "Jammu & Kashmir",
    "kupwara": "Jammu & Kashmir",
    "samba": "Jammu & Kashmir",
    "jammu, j&k": "Jammu & Kashmir",
    "chandigarh": "Chandigarh",
    "trivandrum": "Kerala",
    "thiruvananthapuram": "Kerala",
    "kochi": "Kerala",
    "thrissur": "Kerala",
    "kozhikode": "Kerala",
    "palakkad": "Kerala",
    "malappuram": "Kerala",
    "alappuzha": "Kerala",
    "kottayam": "Kerala",
    "kollam": "Kerala",
    "ernakulam": "Kerala",
    "ernakulam district, kerala": "Kerala",
    "idukki": "Kerala",
    "kannur": "Kerala",
    "kasaragod": "Kerala",
    "vijayawada": "Andhra Pradesh",
    "visakhapatnam": "Andhra Pradesh",
    "guntur": "Andhra Pradesh",
    "guntur district, andhra pradesh": "Andhra Pradesh",
    "tirupati": "Andhra Pradesh",
    "kadapa, andhra pradesh": "Andhra Pradesh",
    "west godavari": "Andhra Pradesh",
    "krishna": "Andhra Pradesh",
    "prakasam": "Andhra Pradesh",
    "pallikulam, post chirakkal, kannur district, kerala": "Kerala",
    "valliyoor": "Tamil Nadu",
    "ambasamudram": "Tamil Nadu",
    "pallom": "Kerala",
    "st.thomas mount": "Tamil Nadu",
    "annanagar east": "Tamil Nadu",
    "sigra": "Uttar Pradesh",
    "sikandra": "Uttar Pradesh",
    "azad nagar": "Madhya Pradesh",
    "gomtinagar": "Uttar Pradesh",
    "gomti nagar": "Uttar Pradesh",
    "panchvati": "Maharashtra",
    "karan nagar": "Delhi",
    "green city": "Punjab",
    "anchal": "Kerala",
    "elanthoor": "Kerala",
    "bigbara": "Maharashtra",
    "sarna": "Punjab",
    "khambha": "Gujarat",
    "chadayamangalam": "Tamil Nadu",
    "sector 1 salt lake city sector 1": "West Bengal",
    "south delhi": "Delhi",
    "north west delhi": "Delhi",
    "west delhi": "Delhi",
    "east delhi": "Delhi",
    "south east delhi area": "Delhi",
    "north goa": "Goa",
    "south goa": "Goa",
    "mira road": "Maharashtra",
    "governorpet": "Andhra Pradesh",
    "balrampur": "Uttar Pradesh",
    "nagladeena fatehgarh": "Punjab",
    "uttaranchal": "Uttarakhand",
    "north goa": "Goa",
    "south goa": "Goa",
}

# Garbage patterns to clear the state field for
GARBAGE_PATTERNS = [
    r'^\{.*coordinates.*\}',  # JSON coordinates
    r'^\[.*\]$',  # JSON arrays
    r'^""',  # quoted strings
    r'^\d+$',  # pure numbers
    r'^\d+\.\d+$',  # decimal numbers
    r'^kie$',  # garbage
    r'^(3|0|1|5|45|74|840|1088|1500)$',  # single numbers
    r'Tamil Nadu; Tamil Nadu',  # semicolon-separated duplicates
]


def normalize_state(raw_state):
    """Normalize a state/UT name to canonical form."""
    if pd.isna(raw_state) or not isinstance(raw_state, str):
        return None

    val = raw_state.strip()
    if not val:
        return None

    # Check for garbage patterns
    for pat in GARBAGE_PATTERNS:
        if re.match(pat, val, re.IGNORECASE):
            return None

    # Try direct state map lookup (lowercase)
    lower = val.lower().strip()

    # Handle compound entries like "Ghaziabad, Uttar Pradesh" -> extract state
    if ", " in lower:
        parts = [p.strip() for p in lower.split(",")]
        for part in parts:
            if part in STATE_MAP:
                return STATE_MAP[part]

    # Semicolon-separated
    if ";" in lower:
        parts = [p.strip() for p in lower.split(";")]
        for part in parts:
            if part in STATE_MAP:
                return STATE_MAP[part]

    # Direct lookup
    if lower in STATE_MAP:
        return STATE_MAP[lower]

    # Try city-to-state lookup
    if lower in CITY_TO_STATE:
        return CITY_TO_STATE[lower]

    # Check if it's a known valid state
    for valid in VALID_STATES:
        if lower == valid.lower():
            return valid

    # Last resort: check if any valid state name is contained
    for valid in VALID_STATES:
        if valid.lower() in lower:
            return valid

    # Unknown - return None (will be cleaned)
    return None


# ============================================================
# CITY NORMALIZATION
# ============================================================
CITY_MAP = {
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
    "bengaluru/bangalore": "Bengaluru",
    "gurgaon": "Gurugram",
    "gurugram": "Gurugram",
    "delhi": "New Delhi",
    "new delhi": "New Delhi",
    "ncr": "New Delhi",
    "delhi ncr": "New Delhi",
    "trivandrum": "Thiruvananthapuram",
    "thiruvananthapuram": "Thiruvananthapuram",
    "allahabad": "Prayagraj",
    "prayagraj": "Prayagraj",
    "pondicherry": "Puducherry",
    "puducherry": "Puducherry",
    "calcutta": "Kolkata",
    "kolkata": "Kolkata",
    "bombay": "Mumbai",
    "mumbai": "Mumbai",
    "navi-mumbai": "Navi Mumbai",
    "madras": "Chennai",
    "chennai": "Chennai",
    "cochin": "Kochi",
    "kochi": "Kochi",
    "mysuru": "Mysuru",
    "mysore": "Mysuru",
    "mangaluru": "Mangaluru",
    "mangalore": "Mangaluru",
    "vishakhapatnam": "Visakhapatnam",
    "vizag": "Visakhapatnam",
    "lucknow": "Lucknow",
    "patna": "Patna",
    "jaipur": "Jaipur",
    "ahmedabad": "Ahmedabad",
    "surat": "Surat",
    "pune": "Pune",
    "hyderabad": "Hyderabad",
    "kota": "Kota",
    "nagpur": "Nagpur",
    "nashik": "Nashik",
    "raipur": "Raipur",
    "dehradun": "Dehradun",
    "patiala": "Patiala",
    "jammu": "Jammu",
    "srinagar": "Srinagar",
    "cuttack": "Cuttack",
    "bhubaneswar": "Bhubaneswar",
    "guwahati": "Guwahati",
    "imphal": "Imphal",
    "shillong": "Shillong",
    "aizawl": "Aizawl",
    "kohima": "Kohima",
    "itanagar": "Itanagar",
    "gangtok": "Gangtok",
    "panaji": "Panaji",
    "chandigarh": "Chandigarh",
}

# District-in-city suffixes to strip
DISTRICT_SUFFIXES = [
    " district", " dist", " dt",
    " district, kerala", " district, karnataka",
    " district, maharashtra", " district, tamil nadu",
    ", kerala", ", karnataka", ", maharashtra",
    ", tamil nadu", ", uttar pradesh", ", rajasthan",
    ", gujarat", ", west bengal", ", andhra pradesh",
    ", telangana", ", bihar", ", jharkhand",
    ", chhattisgarh", ", uttarakhand", ", punjab",
    ", haryana", ", himachal pradesh", ", odisha",
    ", assam", ", jammu & kashmir", ", goa",
]


def normalize_city(raw_city):
    """Normalize a city name."""
    if pd.isna(raw_city) or not isinstance(raw_city, str):
        return None

    val = raw_city.strip()
    if not val:
        return None

    # Skip garbage
    for pat in GARBAGE_PATTERNS:
        if re.match(pat, val, re.IGNORECASE):
            return None

    # Check for JSON garbage
    if val.startswith("{") or val.startswith("["):
        return None
    if '""' in val:
        return None

    lower = val.lower().strip()

    # Handle compound "City, State" entries
    if ", " in lower:
        parts = [p.strip() for p in lower.split(",")]
        # If the first part looks like a city, use it
        city_part = parts[0]
        if city_part in CITY_MAP:
            return CITY_MAP[city_part]
        # Try just using the first part cleaned
        for suffix in DISTRICT_SUFFIXES:
            city_part = city_part.replace(suffix, "").strip()
        if city_part in CITY_MAP:
            return CITY_MAP[city_part]
        # Return the first part as the city (it's likely the city name)
        result = city_part.title()
        if result in CITY_MAP:
            return CITY_MAP[result]
        return result

    # Direct lookup
    if lower in CITY_MAP:
        return CITY_MAP[lower]

    # Strip district suffixes
    cleaned = lower
    for suffix in DISTRICT_SUFFIXES:
        cleaned = cleaned.replace(suffix, "").strip()

    if cleaned in CITY_MAP:
        return CITY_MAP[cleaned]

    # Title case it
    result = val.strip().title()
    return result


def main():
    print("Loading parquet...")
    df = pd.read_parquet(PARQUET_IN)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

    # Store originals for comparison
    old_states = df["address_stateOrRegion"].value_counts()
    old_cities = df["address_city"].value_counts()
    print(f"Before: {len(old_states)} unique states, {len(old_cities)} unique cities")

    # Normalize states
    print("\nNormalizing states...")
    df["address_stateOrRegion"] = df["address_stateOrRegion"].apply(normalize_state)

    # Normalize cities
    print("Normalizing cities...")
    df["address_city"] = df["address_city"].apply(normalize_city)

    # Drop rows with no valid state
    invalid_state = df["address_stateOrRegion"].isna().sum()
    print(f"\nRows with no valid state after normalization: {invalid_state}")

    # Show new counts
    new_states = df["address_stateOrRegion"].value_counts()
    new_cities = df["address_city"].value_counts()
    print(f"\nAfter: {len(new_states)} unique states/UTs, {len(new_cities)} unique cities")
    print("\nStates/UTs:")
    for s, c in new_states.items():
        print(f"  {c:>5}  {s}")

    print(f"\nTop 30 cities:")
    for s, c in new_cities.head(30).items():
        print(f"  {c:>5}  {s}")

    # Save
    df.to_parquet(PARQUET_OUT, index=False)
    print(f"\nSaved to {PARQUET_OUT} ({os.path.getsize(PARQUET_OUT)} bytes)")

    # Trust distribution unchanged?
    if "_trust_signal" in df.columns:
        print(f"\nTrust distribution: {df['_trust_signal'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
