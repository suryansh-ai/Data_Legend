"""
build_master_dataset.py
=======================
Builds organized, clean master datasets from raw Databricks + NFHS-5 + India Post data.

Outputs:
  - data/facilities_master.parquet  (clean facilities with trust + NFHS district data)
  - data/district_health.parquet     (NFHS-5 normalized for Medical Desert track)
"""

import os
import sys
import json
import time
import re
import pandas as pd
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
sys.path.insert(0, ROOT)

# ============================================================
# 1. STATE NORMALIZATION MAP
# ============================================================
# canonical: (official name, official abbreviation, type=state|ut)
STATE_CANONICAL = {
    "maharashtra":       ("Maharashtra",       "MH", "state"),
    "mh":                ("Maharashtra",       "MH", "state"),
    "gujarat":           ("Gujarat",           "GJ", "state"),
    "gj":                ("Gujarat",           "GJ", "state"),
    "uttar pradesh":     ("Uttar Pradesh",     "UP", "state"),
    "up":                ("Uttar Pradesh",     "UP", "state"),
    "u.p":               ("Uttar Pradesh",     "UP", "state"),
    "u.p.":              ("Uttar Pradesh",     "UP", "state"),
    "u p":               ("Uttar Pradesh",     "UP", "state"),
    "up.":               ("Uttar Pradesh",     "UP", "state"),
    "uttar prades h":    ("Uttar Pradesh",     "UP", "state"),
    "uttarpradesh":      ("Uttar Pradesh",     "UP", "state"),
    "tamil nadu":        ("Tamil Nadu",        "TN", "state"),
    "tamilnadu":         ("Tamil Nadu",        "TN", "state"),
    "tn":                ("Tamil Nadu",        "TN", "state"),
    "karnataka":         ("Karnataka",         "KA", "state"),
    "ka":                ("Karnataka",         "KA", "state"),
    "kerala":            ("Kerala",            "KL", "state"),
    "kl":                ("Kerala",            "KL", "state"),
    "west bengal":       ("West Bengal",       "WB", "state"),
    "wb":                ("West Bengal",       "WB", "state"),
    "punjab":            ("Punjab",            "PB", "state"),
    "pb":                ("Punjab",            "PB", "state"),
    "punjab region":     ("Punjab",            "PB", "state"),
    "haryana":           ("Haryana",           "HR", "state"),
    "hr":                ("Haryana",           "HR", "state"),
    "telangana":         ("Telangana",         "TS", "state"),
    "telengana":         ("Telangana",         "TS", "state"),
    "ts":                ("Telangana",         "TS", "state"),
    "tl":                ("Telangana",         "TS", "state"),
    "rajasthan":         ("Rajasthan",         "RJ", "state"),
    "rj":                ("Rajasthan",         "RJ", "state"),
    "andhra pradesh":    ("Andhra Pradesh",    "AP", "state"),
    "ap":                ("Andhra Pradesh",    "AP", "state"),
    "madhya pradesh":    ("Madhya Pradesh",    "MP", "state"),
    "mp":                ("Madhya Pradesh",    "MP", "state"),
    "m.p.":              ("Madhya Pradesh",    "MP", "state"),
    "m.p":               ("Madhya Pradesh",    "MP", "state"),
    "m p":               ("Madhya Pradesh",    "MP", "state"),
    "madhyapradesh":     ("Madhya Pradesh",    "MP", "state"),
    "madhya":            ("Madhya Pradesh",    "MP", "state"),
    "bihar":             ("Bihar",             "BR", "state"),
    "br":                ("Bihar",             "BR", "state"),
    "jharkhand":         ("Jharkhand",         "JH", "state"),
    "jh":                ("Jharkhand",         "JH", "state"),
    "chhattisgarh":      ("Chhattisgarh",      "CG", "state"),
    "chattisgarh":       ("Chhattisgarh",      "CG", "state"),
    "cg":                ("Chhattisgarh",      "CG", "state"),
    "ch":                ("Chhattisgarh",      "CG", "state"),
    "uttarakhand":       ("Uttarakhand",       "UK", "state"),
    "uttaranchal":       ("Uttarakhand",       "UK", "state"),
    "uttranchal":        ("Uttarakhand",       "UK", "state"),
    "uk":                ("Uttarakhand",       "UK", "state"),
    "u.k.":              ("Uttarakhand",       "UK", "state"),
    "assam":             ("Assam",             "AS", "state"),
    "as":                ("Assam",             "AS", "state"),
    "odisha":            ("Odisha",            "OD", "state"),
    "orissa":            ("Odisha",            "OD", "state"),
    "jammu and kashmir": ("Jammu & Kashmir",   "JK", "ut"),
    "jammu & kashmir":   ("Jammu & Kashmir",   "JK", "ut"),
    "jammu, j&k":        ("Jammu & Kashmir",   "JK", "ut"),
    "kashmir":           ("Jammu & Kashmir",   "JK", "ut"),
    "j&k":               ("Jammu & Kashmir",   "JK", "ut"),
    "jammu":             ("Jammu & Kashmir",   "JK", "ut"),
    "srinagar":          ("Jammu & Kashmir",   "JK", "ut"),
    "srinagar kashmir":  ("Jammu & Kashmir",   "JK", "ut"),
    "himachal pradesh":  ("Himachal Pradesh",  "HP", "state"),
    "hp":                ("Himachal Pradesh",  "HP", "state"),
    "goa":               ("Goa",               "GA", "state"),
    "ga":                ("Goa",               "GA", "state"),
    "meghalaya":         ("Meghalaya",         "ML", "state"),
    "manipur":           ("Manipur",           "MN", "state"),
    "tripura":           ("Tripura",           "TR", "state"),
    "west tripura":      ("Tripura",           "TR", "state"),
    "nagaland":          ("Nagaland",          "NL", "state"),
    "sikkim":            ("Sikkim",            "SK", "state"),
    "arunachal pradesh": ("Arunachal Pradesh", "AR", "state"),
    "mizoram":           ("Mizoram",           "MZ", "state"),
    # UTs
    "delhi":             ("Delhi",             "DL", "ut"),
    "nct of delhi":      ("Delhi",             "DL", "ut"),
    "nct delhi":         ("Delhi",             "DL", "ut"),
    "nct":               ("Delhi",             "DL", "ut"),
    "new delhi":         ("Delhi",             "DL", "ut"),
    "dl":                ("Delhi",             "DL", "ut"),
    "delhi/ncr":         ("Delhi",             "DL", "ut"),
    "ncr-delhi":         ("Delhi",             "DL", "ut"),
    "ncr delhi":         ("Delhi",             "DL", "ut"),
    "delhi ncr":         ("Delhi",             "DL", "ut"),
    "ncr":               ("Delhi",             "DL", "ut"),
    "chandigarh":        ("Chandigarh",        "CH", "ut"),
    "chandigarh (ut)":   ("Chandigarh",        "CH", "ut"),
    "puducherry":        ("Puducherry",        "PY", "ut"),
    "pondicherry":       ("Puducherry",        "PY", "ut"),
    "u.t of puducherry": ("Puducherry",        "PY", "ut"),
    "andaman and nicobar islands": ("Andaman & Nicobar Islands", "AN", "ut"),
    "andaman & nicobar islands":   ("Andaman & Nicobar Islands", "AN", "ut"),
    "dadra and nagar haveli and daman and diu": ("Dadra & Nagar Haveli and Daman & Diu", "DD", "ut"),
    "dadra & nagar haveli & daman & diu":       ("Dadra & Nagar Haveli and Daman & Diu", "DD", "ut"),
    "dadra & nagar haveli and daman & diu":     ("Dadra & Nagar Haveli and Daman & Diu", "DD", "ut"),
    "daman and diu":     ("Dadra & Nagar Haveli and Daman & Diu", "DD", "ut"),
    "dadra and nagar haveli": ("Dadra & Nagar Haveli and Daman & Diu", "DD", "ut"),
    "lakshadweep":       ("Lakshadweep",       "LD", "ut"),
    "ladakh":            ("Ladakh",            "LA", "ut"),
}

# NFHS-5 state name corrections
NFHS_STATE_FIX = {
    "maharastra": "Maharashtra",
    "nct of delhi": "Delhi",
    "dadra and nagar haveli & daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
}

# City -> state mapping (for cities found in state field)
CITY_TO_STATE = {
    "mumbai": "Maharashtra", "navi mumbai": "Maharashtra", "thane": "Maharashtra",
    "pune": "Maharashtra", "nagpur": "Maharashtra", "nashik": "Maharashtra",
    "aurangabad": "Maharashtra", "solapur": "Maharashtra", "amravati": "Maharashtra",
    "ahmednagar": "Maharashtra", "kolhapur": "Maharashtra", "sangli": "Maharashtra",
    "dhule": "Maharashtra", "palghar": "Maharashtra", "nanded": "Maharashtra",
    "latur": "Maharashtra", "buldhana": "Maharashtra", "chikhali": "Maharashtra",
    "new mondha": "Maharashtra", "malshiras": "Maharashtra", "tasgaon": "Maharashtra",
    "pimpri-chinchwad": "Maharashtra", "mira road": "Maharashtra",
    "chennai": "Tamil Nadu", "coimbatore": "Tamil Nadu", "madurai": "Tamil Nadu",
    "salem": "Tamil Nadu", "erode": "Tamil Nadu", "tiruvannamalai": "Tamil Nadu",
    "namakkal": "Tamil Nadu", "cuddalore": "Tamil Nadu", "thanjavur": "Tamil Nadu",
    "tenkasi": "Tamil Nadu", "valliyoor": "Tamil Nadu", "ambasamudram": "Tamil Nadu",
    "bangalore": "Karnataka", "bengaluru": "Karnataka", "mysore": "Karnataka",
    "mangalore": "Karnataka", "dharwad": "Karnataka", "gadag": "Karnataka",
    "hyderabad": "Telangana", "yadadri bhuvanagiri district": "Telangana",
    "kolkata": "West Bengal", "howrah": "West Bengal", "siliguri": "West Bengal",
    "hooghly": "West Bengal", "birbhum": "West Bengal", "nadia": "West Bengal",
    "midnapore": "West Bengal", "paschim medinipur": "West Bengal",
    "north 24 parganas": "West Bengal", "south 24 parganas": "West Bengal",
    "kanpur": "Uttar Pradesh", "lucknow": "Uttar Pradesh", "varanasi": "Uttar Pradesh",
    "agra": "Uttar Pradesh", "meerut": "Uttar Pradesh", "ghaziabad": "Uttar Pradesh",
    "allahabad": "Uttar Pradesh", "prayagraj": "Uttar Pradesh", "bareilly": "Uttar Pradesh",
    "aligarh": "Uttar Pradesh", "gorakhpur": "Uttar Pradesh", "noida": "Uttar Pradesh",
    "greater noida": "Uttar Pradesh", "kushinagar": "Uttar Pradesh",
    "indore": "Madhya Pradesh", "bhopal": "Madhya Pradesh", "gwalior": "Madhya Pradesh",
    "jabalpur": "Madhya Pradesh", "rewa": "Madhya Pradesh", "burhanpur": "Madhya Pradesh",
    "jaipur": "Rajasthan", "jodhpur": "Rajasthan", "udaipur": "Rajasthan",
    "kota": "Rajasthan", "ajmer": "Rajasthan", "barmer": "Rajasthan",
    "ahmedabad": "Gujarat", "surat": "Gujarat", "rajkot": "Gujarat",
    "vadodara": "Gujarat", "bhavnagar": "Gujarat", "gandhinagar": "Gujarat",
    "gandhidham": "Gujarat", "mehsana": "Gujarat", "kheda": "Gujarat",
    "kutch": "Gujarat", "kachchh": "Gujarat",
    "amritsar": "Punjab", "jalandhar": "Punjab", "ludhiana": "Punjab",
    "patiala": "Punjab", "bathinda": "Punjab", "mohali": "Punjab",
    "sangrur": "Punjab", "bhatinda": "Punjab",
    "faridabad": "Haryana", "gurgaon": "Haryana", "gurugram": "Haryana",
    "hisar": "Haryana", "rohtak": "Haryana", "sirsa": "Haryana", "jhajjar": "Haryana",
    "patna": "Bihar", "darbhanga": "Bihar", "budaun": "Bihar", "west champaran": "Bihar",
    "ranchi": "Jharkhand", "jamshedpur": "Jharkhand", "east singhbhum": "Jharkhand",
    "raipur": "Chhattisgarh", "bilaspur": "Chhattisgarh",
    "dehradun": "Uttarakhand", "almora": "Uttarakhand", "chamoli": "Uttarakhand",
    "guwahati": "Assam", "kamrup": "Assam",
    "bhubaneswar": "Odisha", "cuttack": "Odisha", "khordha": "Odisha", "ganjam": "Odisha",
    "trivandrum": "Kerala", "thiruvananthapuram": "Kerala", "kochi": "Kerala",
    "thrissur": "Kerala", "kozhikode": "Kerala", "palakkad": "Kerala",
    "malappuram": "Kerala", "alappuzha": "Kerala", "kottayam": "Kerala",
    "kollam": "Kerala", "ernakulam": "Kerala", "idukki": "Kerala",
    "kannur": "Kerala", "kasaragod": "Kerala",
    "vijayawada": "Andhra Pradesh", "visakhapatnam": "Andhra Pradesh",
    "guntur": "Andhra Pradesh", "tirupati": "Andhra Pradesh",
    "kadapa": "Andhra Pradesh", "west godavari": "Andhra Pradesh",
    "krishna": "Andhra Pradesh", "prakasam": "Andhra Pradesh",
    "sirmaur": "Himachal Pradesh",
}

# City name canonicalization
CITY_CANONICAL = {
    "bangalore": "Bengaluru", "bengaluru": "Bengaluru",
    "gurgaon": "Gurugram", "gurugram": "Gurugram",
    "delhi": "New Delhi", "new delhi": "New Delhi",
    "trivandrum": "Thiruvananthapuram", "thiruvananthapuram": "Thiruvananthapuram",
    "allahabad": "Prayagraj", "prayagraj": "Prayagraj",
    "pondicherry": "Puducherry", "puducherry": "Puducherry",
    "mysore": "Mysuru", "mangalore": "Mangaluru",
    "calcutta": "Kolkata", "bombay": "Mumbai", "madras": "Chennai",
    "cochin": "Kochi",
}

# Neighborhoods to parent city
NEIGHBORHOOD_MAP = {
    "borivali east": "Mumbai", "borivali (east)": "Mumbai", "borivali west": "Mumbai",
    "goregaon west": "Mumbai", "goregaon east": "Mumbai", "kalyan west": "Mumbai",
    "kalyan east": "Mumbai", "matunga east": "Mumbai", "nalasopara west": "Mumbai",
    "bhayandar east": "Mumbai", "bhayandar west": "Mumbai", "badlapur west": "Mumbai",
    "badlapur east": "Mumbai", "navi-mumbai": "Navi Mumbai", "pimpri-chinchwad": "Pune",
    "pimpri": "Pune", "chinchwad": "Pune", "punit nagar palghar": "Palghar",
    "safdarjung development area": "New Delhi", "new rajender nagar": "New Delhi",
    "rohini sector 3": "New Delhi", "rohini": "New Delhi", "saket": "New Delhi",
    "dwarka": "New Delhi", "karol bagh": "New Delhi", "lajpat nagar": "New Delhi",
    "greater kailash": "New Delhi", "vasant kunj": "New Delhi",
    "basaveshwaranagar": "Bengaluru", "jayanagar": "Bengaluru",
    "koramangala": "Bengaluru", "hsr layout": "Bengaluru",
    "indiranagar": "Bengaluru", "whitefield": "Bengaluru",
    "electronic city": "Bengaluru", "hebbal": "Bengaluru",
    "marathahalli": "Bengaluru", "sarjapur road": "Bengaluru",
    "bengaluru east": "Bengaluru", "bengaluru north": "Bengaluru",
    "bengaluru south": "Bengaluru", "bengaluru west": "Bengaluru",
    "adyar": "Chennai", "velachery": "Chennai", "t.nagar": "Chennai",
    "anna nagar": "Chennai", "annanagar": "Chennai", "chromepet": "Chennai",
    "porur": "Chennai", "nungambakkam": "Chennai", "madurai east": "Madurai",
    "salt lake": "Kolkata", "new town": "Kolkata", "bidhannagar": "Kolkata",
    "baranagar": "Kolkata", "konnagar": "Kolkata",
    "gachibowli": "Hyderabad", "madhapur": "Hyderabad", "secunderabad": "Hyderabad",
    "banjara hills": "Hyderabad", "jubilee hills": "Hyderabad",
    "kothrud": "Pune", "hinjewadi": "Pune", "viman nagar": "Pune",
    "maninagar": "Ahmedabad", "satellite": "Ahmedabad",
    "sas nagar": "Mohali", "jalandhar-east": "Jalandhar",
    "gautam buddha nagar": "Noida", "ramnagar": "Varanasi",
    "krishnanagar": "Kolkata", "ashoknagarh-kalyangarh kachua more": "Kolkata",
    "ezhupunna south": "Alappuzha", "chatrapati sambhaji nagar": "Aurangabad",
    "areacode": None, "nagar": None,
}

# Garbage patterns for state field
GARBAGE_STATE_PATTERNS = [
    r'^\{.*coordinates.*\}',
    r'^\[.*\]$',
    r'^""',
    r'^\d+$',
    r'^\d+\.\d+$',
    r'^kie$',
    r'^(3|0|1|5|45|74|840|1088|1500)$',
    r'Tamil Nadu; Tamil Nadu',
]

# Garbage patterns for city field
GARBAGE_CITY_PATTERNS = [
    r'^\{.*coordinates.*\}',
    r'^\[.*\]$',
    r'^""',
    r'^\d+$',
    r'^\d+\.\d+$',
    r'^kie$',
    r'^(3|0|1|5|45|74|840|1088|1500)$',
    r'internalMedicine',
    r'dentistry',
]


# ============================================================
# 2. CLEANING FUNCTIONS
# ============================================================

def normalize_state(raw):
    """Normalize a state/UT name to (canonical_name, abbreviation, type)."""
    if pd.isna(raw) or not isinstance(raw, str):
        return None, None, None
    val = raw.strip()
    if not val:
        return None, None, None
    lower = val.lower().strip()

    # Check garbage
    for pat in GARBAGE_STATE_PATTERNS:
        if re.match(pat, val, re.IGNORECASE):
            return None, None, None

    # Compound entries: "Ghaziabad, Uttar Pradesh"
    if ", " in lower:
        parts = [p.strip() for p in lower.split(",")]
        for part in parts:
            if part in STATE_CANONICAL:
                return STATE_CANONICAL[part]

    # Semicolon-separated
    if ";" in lower:
        parts = [p.strip() for p in lower.split(";")]
        for part in parts:
            if part in STATE_CANONICAL:
                return STATE_CANONICAL[part]

    # Direct lookup
    if lower in STATE_CANONICAL:
        return STATE_CANONICAL[lower]

    # City -> state lookup
    if lower in CITY_TO_STATE:
        state_name = CITY_TO_STATE[lower]
        key = state_name.lower()
        if key in STATE_CANONICAL:
            return STATE_CANONICAL[key]

    return None, None, None


def normalize_city(raw):
    """Normalize a city name."""
    if pd.isna(raw) or not isinstance(raw, str):
        return None
    val = raw.strip()
    if not val:
        return None
    lower = val.lower().strip()

    # Garbage
    for pat in GARBAGE_CITY_PATTERNS:
        if re.match(pat, val, re.IGNORECASE):
            return None
    if val.startswith("{") or val.startswith("["):
        return None
    if '""' in val:
        return None

    # Neighborhood map first
    if lower in NEIGHBORHOOD_MAP:
        return NEIGHBORHOOD_MAP[lower]

    # Compound "City, State"
    if ", " in lower:
        parts = [p.strip() for p in lower.split(",")]
        city_part = parts[0]
        if city_part in CITY_CANONICAL:
            return CITY_CANONICAL[city_part]
        if city_part in NEIGHBORHOOD_MAP:
            return NEIGHBORHOOD_MAP[city_part]
        return city_part.title()

    # Direct canonical lookup
    if lower in CITY_CANONICAL:
        return CITY_CANONICAL[lower]

    # Strip district suffixes
    cleaned = lower
    for suffix in [" district", " dist", " dt", ", kerala", ", karnataka",
                   ", maharashtra", ", tamil nadu", ", uttar pradesh",
                   ", rajasthan", ", gujarat", ", west bengal",
                   ", andhra pradesh", ", telangana"]:
        cleaned = cleaned.replace(suffix, "").strip()
    if cleaned in CITY_CANONICAL:
        return CITY_CANONICAL[cleaned]

    return val.strip().title()


def normalize_facility_type(raw):
    """Normalize facility type."""
    if pd.isna(raw) or not isinstance(raw, str):
        return "unknown"
    lower = raw.strip().lower()
    valid = {"hospital", "clinic", "dentist", "doctor", "pharmacy", "nursing_home"}
    if lower in valid:
        return lower
    return "unknown"


def normalize_operator_type(raw):
    """Normalize operator type."""
    if pd.isna(raw) or not isinstance(raw, str):
        return "unknown"
    lower = raw.strip().lower()
    if lower in ("private", "public", "government"):
        return lower
    return "unknown"


def parse_json_list(val):
    """Parse a JSON array field into a Python list."""
    if pd.isna(val) or not isinstance(val, str):
        return []
    val = val.strip()
    if not val or val == "null":
        return []
    try:
        parsed = json.loads(val)
        if isinstance(parsed, list):
            return [str(v).strip() for v in parsed if v]
    except (json.JSONDecodeError, TypeError):
        pass
    return [v.strip() for v in val.split(",") if v.strip()]


def is_valid_coord(val):
    """Check if a coordinate value is valid."""
    if pd.isna(val):
        return False
    try:
        v = float(val)
        return -90 <= v <= 90
    except (ValueError, TypeError):
        return False


def is_valid_lat(val):
    if pd.isna(val):
        return False
    try:
        v = float(val)
        return -90 <= v <= 90
    except:
        return False


def is_valid_lng(val):
    if pd.isna(val):
        return False
    try:
        v = float(val)
        return -180 <= v <= 180
    except:
        return False


# ============================================================
# 3. MAIN PIPELINE
# ============================================================

def build_facilities_master():
    """Build the organized facilities master dataset."""
    t0 = time.time()

    # --- Load raw CSV ---
    csv_path = os.path.join(DATA_DIR, "Explore_databricks_virtue_foundation_dataset_dais_2026_virtue_foundation_dataset_facilities_2026_07_ (1).csv")
    print(f"[1/7] Loading raw CSV: {csv_path}")
    raw = pd.read_csv(csv_path, low_memory=False)
    print(f"  Loaded {len(raw)} rows, {len(raw.columns)} columns")

    # --- Normalize states ---
    print("[2/7] Normalizing states...")
    state_data = raw["address_stateOrRegion"].apply(normalize_state)
    raw["_state_name"] = [s[0] for s in state_data]
    raw["_state_code"] = [s[1] for s in state_data]
    raw["_state_type"] = [s[2] for s in state_data]

    valid_states = raw["_state_name"].notna().sum()
    invalid_states = raw["_state_name"].isna().sum()
    print(f"  Valid states: {valid_states}, Invalid: {invalid_states}")

    # --- Normalize cities ---
    print("[3/7] Normalizing cities...")
    raw["_city_clean"] = raw["address_city"].apply(normalize_city)
    valid_cities = raw["_city_clean"].notna().sum()
    print(f"  Valid cities: {valid_cities}")

    # --- Clean facility/operator types ---
    print("[4/7] Cleaning facility types...")
    raw["_facility_type"] = raw["facilityTypeId"].apply(normalize_facility_type)
    raw["_operator_type"] = raw["operatorTypeId"].apply(normalize_operator_type)

    # --- Validate coordinates ---
    raw["_valid_lat"] = raw["latitude"].apply(is_valid_lat)
    raw["_valid_lng"] = raw["longitude"].apply(is_valid_lng)
    raw["_valid_coords"] = raw["_valid_lat"] & raw["_valid_lng"]
    print(f"  Valid coordinates: {raw['_valid_coords'].sum()}/{len(raw)}")

    # --- Quality flags ---
    print("[5/7] Computing quality flags...")
    raw["_has_name"] = raw["name"].notna() & (raw["name"].astype(str).str.len() > 0)
    raw["_has_description"] = raw["description"].notna() & (raw["description"].astype(str).str.len() > 10)
    raw["_has_capability"] = raw["capability"].notna() & (raw["capability"].astype(str).str.len() > 5)
    raw["_has_procedure"] = raw["procedure"].notna() & (raw["procedure"].astype(str).str.len() > 5)
    raw["_has_equipment"] = raw["equipment"].notna() & (raw["equipment"].astype(str).str.len() > 5)
    raw["_has_specialties"] = raw["specialties"].notna() & (raw["specialties"].astype(str).str.len() > 5)
    raw["_has_doctors"] = raw["numberDoctors"].notna() & (raw["numberDoctors"].astype(str).str.len() > 0)
    raw["_has_capacity"] = raw["capacity"].notna() & (raw["capacity"].astype(str).str.len() > 0)
    raw["_has_phone"] = (raw["phone_numbers"].notna() | raw["officialPhone"].notna())
    raw["_has_email"] = raw["email"].notna() & (raw["email"].astype(str).str.contains("@", na=False))
    raw["_has_website"] = raw["officialWebsite"].notna() | raw["websites"].notna()

    # --- Remove rows with no valid state (garbage) ---
    before = len(raw)
    raw = raw.dropna(subset=["_state_name"]).copy()
    dropped = before - len(raw)
    print(f"  Dropped {dropped} rows with no valid state")

    # --- Compute trust scores ---
    print("[6/7] Computing trust scores...")
    from server.trust_engine import score_facility
    scores = []
    for _, row in raw.iterrows():
        result = score_facility(row.to_dict())
        scores.append(result)
    raw["_trust_score"] = [s.get("overall_trust", 0) for s in scores]
    raw["_trust_signal"] = [s.get("overall_signal", "UNKNOWN") for s in scores]
    raw["_total_claims"] = [s.get("metadata", {}).get("total_claims", 0) for s in scores]
    raw["_corroborated"] = [s.get("metadata", {}).get("corroborated_claims", 0) for s in scores]
    print(f"  Trust distribution: {raw['_trust_signal'].value_counts().to_dict()}")

    # --- Select organized columns ---
    print("[7/7] Building organized dataset...")
    master_cols = {
        # Core identity
        "unique_id": raw["unique_id"],
        "name": raw["name"],
        "_facility_type": raw["_facility_type"],
        "_operator_type": raw["_operator_type"],
        "yearEstablished": raw["yearEstablished"],
        "acceptsVolunteers": raw["acceptsVolunteers"],

        # Description & capabilities
        "description": raw["description"],
        "capability": raw["capability"],
        "procedure": raw["procedure"],
        "equipment": raw["equipment"],
        "specialties": raw["specialties"],

        # Contact
        "phone_numbers": raw["phone_numbers"],
        "officialPhone": raw["officialPhone"],
        "email": raw["email"],
        "officialWebsite": raw["officialWebsite"],
        "websites": raw["websites"],
        "facebookLink": raw["facebookLink"],

        # Location (cleaned)
        "address_line1": raw["address_line1"],
        "address_line2": raw["address_line2"],
        "address_line3": raw["address_line3"],
        "city": raw["_city_clean"],
        "state": raw["_state_name"],
        "state_code": raw["_state_code"],
        "state_type": raw["_state_type"],
        "pincode": raw["address_zipOrPostcode"],
        "country": raw["address_country"],
        "country_code": raw["address_countryCode"],
        "latitude": raw["latitude"],
        "longitude": raw["longitude"],
        "has_valid_coords": raw["_valid_coords"],

        # Capacity
        "numberDoctors": raw["numberDoctors"],
        "capacity": raw["capacity"],
        "area": raw["area"],

        # Digital presence
        "distinct_social_media_presence_count": raw["distinct_social_media_presence_count"],
        "affiliated_staff_presence": raw["affiliated_staff_presence"],
        "custom_logo_presence": raw["custom_logo_presence"],
        "number_of_facts_about_the_organization": raw["number_of_facts_about_the_organization"],
        "post_metrics_most_recent_social_media_post_date": raw["post_metrics_most_recent_social_media_post_date"],
        "post_metrics_post_count": raw["post_metrics_post_count"],
        "engagement_metrics_n_followers": raw["engagement_metrics_n_followers"],
        "engagement_metrics_n_likes": raw["engagement_metrics_n_likes"],
        "engagement_metrics_n_engagements": raw["engagement_metrics_n_engagements"],

        # Source
        "source": raw["source"],
        "source_urls": raw["source_urls"],
        "source_types": raw["source_types"],
        "cluster_id": raw["cluster_id"],

        # Trust scores
        "_trust_score": raw["_trust_score"],
        "_trust_signal": raw["_trust_signal"],
        "_total_claims": raw["_total_claims"],
        "_corroborated": raw["_corroborated"],

        # Quality flags
        "_has_name": raw["_has_name"],
        "_has_description": raw["_has_description"],
        "_has_capability": raw["_has_capability"],
        "_has_procedure": raw["_has_procedure"],
        "_has_equipment": raw["_has_equipment"],
        "_has_specialties": raw["_has_specialties"],
        "_has_doctors": raw["_has_doctors"],
        "_has_capacity": raw["_has_capacity"],
        "_has_phone": raw["_has_phone"],
        "_has_email": raw["_has_email"],
        "_has_website": raw["_has_website"],
    }

    master = pd.DataFrame(master_cols)

    # Save
    out_path = os.path.join(DATA_DIR, "facilities_master.parquet")
    master.to_parquet(out_path, index=False)

    print(f"\n{'='*60}")
    print(f"FACILITIES MASTER DATASET BUILT")
    print(f"{'='*60}")
    print(f"Rows: {len(master)}")
    print(f"Columns: {len(master.columns)}")
    print(f"States: {master['state'].nunique()}")
    print(f"Cities: {master['city'].nunique()}")
    print(f"Facility types: {master['_facility_type'].value_counts().to_dict()}")
    print(f"Operator types: {master['_operator_type'].value_counts().to_dict()}")
    print(f"Trust: {master['_trust_signal'].value_counts().to_dict()}")
    print(f"Avg trust: {master['_trust_score'].mean():.1f}")
    print(f"Saved: {out_path} ({os.path.getsize(out_path)} bytes)")
    print(f"Time: {time.time()-t0:.1f}s")

    return master


def build_district_health():
    """Build normalized district health dataset from NFHS-5."""
    print("\n[NFHS-5] Building district health dataset...")

    nfhs_path = os.path.join(DATA_DIR, "nfhs5_district_health.xlsx")
    nfhs = pd.read_excel(nfhs_path)

    # Fix state name typos
    nfhs["State/UT"] = nfhs["State/UT"].apply(
        lambda x: NFHS_STATE_FIX.get(str(x).lower().strip(), x) if pd.notna(x) else x
    )

    # Rename key columns for consistency
    rename_map = {
        "District Names": "district",
        "State/UT": "state",
    }
    nfhs = nfhs.rename(columns=rename_map)

    # Select most useful columns for Medical Desert analysis
    keep_cols = [
        "district", "state",
        "Number of Households surveyed",
        "Institutional births (in the 5 years before the survey) (%)",
        "Births attended by skilled health personnel (in the 5 years before the survey)",
        "Mothers who had at least 4 antenatal care visits  (for last birth in the 5 years before the survey) (%)",
        "Children age 12-23 months fully vaccinated based on information from either vaccination card or mother's recall",
        "Households with any usual member covered under a health insurance/financing scheme (%)",
        "Women (age 15-49 years) who are anaemic (%)",
        "Children under age 5 years who are stunted (height-for-age) (%)",
        "Children under age 5 years who are wasted (weight-for-height) (%)",
        "Children under age 5 years who are underweight (weight-for-age) (%)",
        "Total Unmet need for Family Planning (Currently Married Women Age 15-49  years)",
        "Mothers who had an antenatal check-up in the first trimester  (for last birth in the 5 years before the survey) (%)",
        "Average out-of-pocket expenditure per delivery in a public health facility (for last birth in the 5 years before the survey) (Rs.)",
        "Households using clean fuel for cooking (%)",
        "Women (age 15-49) who are literate (%)",
        "Population living in households with electricity (%)",
        "Population living in households with an improved drinking-water source",
        "Population living in households that use an improved sanitation facility",
    ]

    # Short names for readability
    short_names = {
        "Number of Households surveyed": "households_surveyed",
        "Institutional births (in the 5 years before the survey) (%)": "institutional_births_pct",
        "Births attended by skilled health personnel (in the 5 years before the survey)": "skilled_birth_attendance_pct",
        "Mothers who had at least 4 antenatal care visits  (for last birth in the 5 years before the survey) (%)": "anc_4plus_visits_pct",
        "Children age 12-23 months fully vaccinated based on information from either vaccination card or mother's recall": "full_vaccination_pct",
        "Households with any usual member covered under a health insurance/financing scheme (%)": "health_insurance_pct",
        "Women (age 15-49 years) who are anaemic (%)": "women_anemia_pct",
        "Children under age 5 years who are stunted (height-for-age) (%)": "child_stunting_pct",
        "Children under age 5 years who are wasted (weight-for-height) (%)": "child_wasting_pct",
        "Children under age 5 years who are underweight (weight-for-age) (%)": "child_underweight_pct",
        "Total Unmet need for Family Planning (Currently Married Women Age 15-49  years)": "unmet_fp_need_pct",
        "Mothers who had an antenatal check-up in the first trimester  (for last birth in the 5 years before the survey) (%)": "anc_first_trimester_pct",
        "Average out-of-pocket expenditure per delivery in a public health facility (for last birth in the 5 years before the survey) (Rs.)": "oop_delivery_cost_rs",
        "Households using clean fuel for cooking (%)": "clean_fuel_pct",
        "Women (age 15-49) who are literate (%)": "women_literacy_pct",
        "Population living in households with electricity (%)": "electricity_pct",
        "Population living in households with an improved drinking-water source": "improved_water_pct",
        "Population living in households that use an improved sanitation facility": "improved_sanitation_pct",
    }

    available = [c for c in keep_cols if c in nfhs.columns]
    nfhs_clean = nfhs[available].copy()
    nfhs_clean = nfhs_clean.rename(columns={k: v for k, v in short_names.items() if k in nfhs_clean.columns})

    # Drop rows with no district name
    nfhs_clean = nfhs_clean.dropna(subset=["district"])

    # Convert numeric columns
    for col in nfhs_clean.columns:
        if col not in ("district", "state"):
            nfhs_clean[col] = pd.to_numeric(nfhs_clean[col], errors="coerce")

    out_path = os.path.join(DATA_DIR, "district_health.parquet")
    nfhs_clean.to_parquet(out_path, index=False)

    print(f"  Rows: {len(nfhs_clean)}")
    print(f"  Districts: {nfhs_clean['district'].nunique()}")
    print(f"  States: {nfhs_clean['state'].nunique()}")
    print(f"  Columns: {len(nfhs_clean.columns)}")
    print(f"  Saved: {out_path}")

    return nfhs_clean


def join_facilities_districts(master, district_health):
    """Join facilities with district health data."""
    print("\n[JOIN] Matching facilities to district health data...")

    # Build district lookup from district_health
    district_health["_district_lower"] = district_health["district"].str.lower().str.strip()
    district_health["_state_lower"] = district_health["state"].str.lower().str.strip()

    # Create a mapping: (state_lower, district_lower) -> row index
    district_lookup = {}
    for idx, row in district_health.iterrows():
        key = (row["_state_lower"], row["_district_lower"])
        district_lookup[key] = idx

    # For each facility, try to match by city -> district
    matched = 0
    nfhs_cols = [c for c in district_health.columns if c not in ("district", "state", "_district_lower", "_state_lower")]

    for col in nfhs_cols:
        master[f"nfhs_{col}"] = np.nan

    for i, fac_row in master.iterrows():
        fac_state = str(fac_row["state"]).lower().strip() if pd.notna(fac_row["state"]) else ""
        fac_city = str(fac_row["city"]).lower().strip() if pd.notna(fac_row["city"]) else ""

        # Try exact city match first
        key = (fac_state, fac_city)
        if key in district_lookup:
            idx = district_lookup[key]
            for col in nfhs_cols:
                master.at[i, f"nfhs_{col}"] = district_health.at[idx, col]
            matched += 1
            continue

        # Try partial city match (city name is part of district or vice versa)
        for dkey, didx in district_lookup.items():
            if dkey[0] == fac_state:
                district_name = dkey[1]
                if fac_city in district_name or district_name in fac_city:
                    for col in nfhs_cols:
                        master.at[i, f"nfhs_{col}"] = district_health.at[didx, col]
                    matched += 1
                    break

    match_pct = matched / len(master) * 100
    print(f"  Matched: {matched}/{len(master)} ({match_pct:.1f}%)")

    return master


if __name__ == "__main__":
    # Step 1: Build organized facilities master
    master = build_facilities_master()

    # Step 2: Build normalized district health
    district_health = build_district_health()

    # Step 3: Join them
    master = join_facilities_districts(master, district_health)

    # Save final master with NFHS columns
    out_path = os.path.join(DATA_DIR, "facilities_master.parquet")
    master.to_parquet(out_path, index=False)
    print(f"\nFinal master: {len(master)} rows, {len(master.columns)} columns")
    print(f"Saved: {out_path} ({os.path.getsize(out_path)} bytes)")
