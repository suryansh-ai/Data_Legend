"""Check all data sources."""
import pandas as pd
import sqlite3
import os

DATA_DIR = r"C:\Users\Ghanshyam\Desktop\Data_Legend\data"

# 1. Facilities parquet
print("=== FACILITIES SCORED PARQUET ===")
df = pd.read_parquet(os.path.join(DATA_DIR, "facilities_scored.parquet"))
print(f"Rows: {len(df)}, Cols: {len(df.columns)}")
print(f"States: {df['address_stateOrRegion'].nunique()}")
print(f"Cities: {df['address_city'].nunique()}")
print(f"Trust dist: {df['_trust_signal'].value_counts().to_dict()}")
print()

# 2. NFHS-5
print("=== NFHS-5 DISTRICT HEALTH ===")
nfhs = pd.read_excel(os.path.join(DATA_DIR, "nfhs5_district_health.xlsx"))
print(f"Rows: {len(nfhs)}, Cols: {len(nfhs.columns)}")
print(f"States: {nfhs['State/UT'].nunique()}")
print(f"Sample columns (first 10):")
for c in nfhs.columns[:10]:
    print(f"  {c}")
print()

# 3. Raw CSV
print("=== RAW DATABRICKS CSV ===")
raw_csv = os.path.join(DATA_DIR, "Explore_databricks_virtue_foundation_dataset_dais_2026_virtue_foundation_dataset_facilities_2026_07_ (1).csv")
if os.path.exists(raw_csv):
    raw = pd.read_csv(raw_csv, nrows=5)
    print(f"Columns: {list(raw.columns)}")
    print(f"Sample row name: {raw.iloc[0]['name']}")
    print(f"Sample row description length: {len(str(raw.iloc[0]['description']))}")
print()

# 4. India post pin directory
print("=== INDIA POST PIN DIRECTORY ===")
pin = pd.read_csv(os.path.join(DATA_DIR, "india_post_pin_directory.csv"), nrows=5)
print(f"Columns: {list(pin.columns)}")
print(f"First 3 rows:")
print(pin.head(3).to_string())
