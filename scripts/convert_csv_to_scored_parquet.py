"""
Convert the full 10K Databricks Marketplace CSV to scored parquet.
Computes trust scores for all facilities and saves as facilities_scored.parquet.
"""
import sys
import os
import time
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.trust_engine import score_facility

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "Explore_databricks_virtue_foundation_dataset_dais_2026_virtue_foundation_dataset_facilities_2026_07_ (1).csv",
)
OUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "facilities_scored.parquet",
)


def main():
    print(f"Reading CSV: {CSV_PATH}")
    t0 = time.time()
    df = pd.read_csv(CSV_PATH, low_memory=False)
    print(f"Loaded {len(df)} rows in {time.time() - t0:.1f}s")

    print("Scoring trust for each facility...")
    t1 = time.time()
    scores = []
    for i, row in df.iterrows():
        result = score_facility(row.to_dict())
        scores.append(result)
        if (i + 1) % 1000 == 0:
            print(f"  Scored {i + 1}/{len(df)} ({time.time() - t1:.1f}s)")

    df["_trust_score"] = [s.get("overall_trust", 0) for s in scores]
    df["_trust_signal"] = [s.get("overall_signal", "UNKNOWN") for s in scores]
    df["_total_claims"] = [s.get("metadata", {}).get("total_claims", 0) for s in scores]
    df["_corroborated"] = [s.get("metadata", {}).get("corroborated_claims", 0) for s in scores]

    print(f"Scoring complete in {time.time() - t1:.1f}s")
    print(f"Trust distribution: {df['_trust_signal'].value_counts().to_dict()}")
    print(f"Avg trust score: {df['_trust_score'].mean():.1f}")

    df.to_parquet(OUT_PATH, index=False)
    print(f"Saved to {OUT_PATH} ({os.path.getsize(OUT_PATH)} bytes)")
    print(f"Columns: {list(df.columns)}")
    print(f"Total time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
